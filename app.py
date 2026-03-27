from flask import Flask, request, redirect, session, render_template_string
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"

# =====================
# DATABASE
# =====================
conn = sqlite3.connect('database.db', check_same_thread=False)
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS clientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT,
    email TEXT UNIQUE,
    senha TEXT,
    plano TEXT,
    etapa INTEGER DEFAULT 1
)''')
conn.commit()

# =====================
# ETAPAS
# =====================
etapas = [
    "Pagamento confirmado",
    "Desenvolvimento do bot",
    "Testes e validação",
    "Entrega final"
]

# =====================
# ROTAS
# =====================

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        senha = request.form.get("senha")

        c.execute("SELECT * FROM clientes WHERE email=? AND senha=?", (email, senha))
        user = c.fetchone()

        if user:
            session["user_id"] = user[0]
            return redirect("/dashboard")
        else:
            return "Login inválido"

    return render_template_string("""
        <h2>Login</h2>
        <form method="post">
            Email: <input name="email"><br><br>
            Senha: <input name="senha" type="password"><br><br>
            <button>Entrar</button>
        </form>
    """)


@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/")

    c.execute("SELECT * FROM clientes WHERE id=?", (session["user_id"],))
    user = c.fetchone()

    html = f"<h2>Bem-vindo {user[1]}</h2>"
    html += "<h3>Status do Projeto:</h3>"

    for i, etapa in enumerate(etapas, start=1):
        if i < user[5]:
            html += f"<p>✅ {etapa}</p>"
        elif i == user[5]:
            html += f"<p>🔄 {etapa}</p>"
        else:
            html += f"<p>⏳ {etapa}</p>"

    return html


@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        cid = request.form.get("id")
        c.execute("UPDATE clientes SET etapa = etapa + 1 WHERE id=?", (cid,))
        conn.commit()

    c.execute("SELECT * FROM clientes")
    clientes = c.fetchall()

    html = "<h2>Painel Admin</h2>"

    for cliente in clientes:
        html += f"""
        <p>{cliente[1]} - Etapa {cliente[5]}</p>
        <form method='post'>
            <input type='hidden' name='id' value='{cliente[0]}'>
            <button>Avançar etapa</button>
        </form>
        <hr>
        """

    return html


# =====================
# TESTE AUTOMÁTICO
# =====================
def testes():
    c.execute("INSERT OR IGNORE INTO clientes (nome,email,senha,plano) VALUES (?,?,?,?)",
              ("Teste", "teste@email.com", "123", "Basico"))
    conn.commit()

    c.execute("SELECT * FROM clientes WHERE email=?", ("teste@email.com",))
    user = c.fetchone()

    assert user is not None, "Erro ao criar cliente"
    assert user[2] == "teste@email.com", "Email incorreto"

    print("✅ Testes OK")


if __name__ == "__main__":
    testes()
    app.run(debug=True)
import tkinter as tk
from tkinter import messagebox
import sqlite3
import hashlib
from datetime import datetime, timedelta

# ==========================
# BASE DE DATOS
# ==========================

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    username TEXT PRIMARY KEY,
    password TEXT
)
""")

conn.commit()

# ==========================
# VARIABLES DE SEGURIDAD
# ==========================

failed_attempts = 0
lock_until = None

# ==========================
# FUNCIONES
# ==========================

def log_event(event):
    with open("logs.txt", "a", encoding="utf-8") as log:
        log.write(f"[{datetime.now()}] {event}\n")

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register():

    username = entry_user.get().strip()
    password = entry_pass.get()

    if not username or not password:
        messagebox.showwarning("Error", "Completa todos los campos")
        return

    hashed = hash_password(password)

    try:
        cursor.execute(
            "INSERT INTO users VALUES (?, ?)",
            (username, hashed)
        )

        conn.commit()

        log_event(f"Usuario registrado: {username}")

        messagebox.showinfo(
            "Registro",
            "Usuario registrado correctamente"
        )

    except sqlite3.IntegrityError:
        messagebox.showerror(
            "Error",
            "Ese usuario ya existe"
        )

def login():

    global failed_attempts
    global lock_until

    if lock_until and datetime.now() < lock_until:

        remaining = int(
            (lock_until - datetime.now()).total_seconds()
        )

        messagebox.showerror(
            "Bloqueado",
            f"Demasiados intentos.\nEspera {remaining} segundos."
        )

        return

    username = entry_user.get().strip()
    password = entry_pass.get()

    hashed = hash_password(password)

    cursor.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username, hashed)
    )

    result = cursor.fetchone()

    if result:

        failed_attempts = 0

        log_event(
            f"LOGIN EXITOSO -> {username}"
        )

        messagebox.showinfo(
            "Acceso concedido",
            f"Bienvenido {username}"
        )

    else:

        failed_attempts += 1

        log_event(
            f"LOGIN FALLIDO -> {username}"
        )

        remaining = 5 - failed_attempts

        if failed_attempts >= 5:

            lock_until = datetime.now() + timedelta(minutes=1)

            log_event(
                "SISTEMA BLOQUEADO POR 1 MINUTO"
            )

            messagebox.showerror(
                "Bloqueado",
                "5 intentos fallidos.\nSistema bloqueado por 1 minuto."
            )

        else:

            messagebox.showerror(
                "Error",
                f"Usuario o contraseña incorrectos.\nIntentos restantes: {remaining}"
            )

# ==========================
# INTERFAZ
# ==========================

root = tk.Tk()
root.title("Secure Login System")
root.geometry("420x300")
root.resizable(False, False)

title = tk.Label(
    root,
    text="SECURE LOGIN SYSTEM",
    font=("Arial", 16, "bold")
)

title.pack(pady=15)

tk.Label(
    root,
    text="Usuario"
).pack()

entry_user = tk.Entry(
    root,
    width=30
)

entry_user.pack(pady=5)

tk.Label(
    root,
    text="Contraseña"
).pack()

entry_pass = tk.Entry(
    root,
    show="*",
    width=30
)

entry_pass.pack(pady=5)

btn_login = tk.Button(
    root,
    text="Iniciar Sesión",
    width=20,
    command=login
)

btn_login.pack(pady=10)

btn_register = tk.Button(
    root,
    text="Registrar Usuario",
    width=20,
    command=register
)

btn_register.pack()

footer = tk.Label(
    root,
    text="SQLite + SHA256 + Login Protection",
    fg="gray"
)

footer.pack(side="bottom", pady=10)

root.mainloop()
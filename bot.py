import telebot
import sqlite3
import time
import random

TOKEN = "8545476361:AAGRIYIp70HTPKF8YIWyWpmDY6G4IMsk65A"

ADMIN_ID = 5266944014

bot = telebot.TeleBot(TOKEN)

conn = sqlite3.connect("faucet.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    balance REAL DEFAULT 0,
    last_claim INTEGER DEFAULT 0
)
""")
conn.commit()

CLAIM_TIME = 60  # 1 minuto para teste

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id

    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
        conn.commit()

    bot.reply_to(message,
    "💰 Bem-vindo à sua Torneira!\n\n"
    "/claim - Receber recompensa\n"
    "/balance - Ver saldo")

@bot.message_handler(commands=['claim'])
def claim(message):
    user_id = message.from_user.id
    now = int(time.time())

    cursor.execute("SELECT last_claim FROM users WHERE user_id=?", (user_id,))
    last_claim = cursor.fetchone()[0]

    if now - last_claim < CLAIM_TIME:
        bot.reply_to(message, "⏳ Espere 1 minuto para novo claim.")
        return

    reward = round(random.uniform(0.000001, 0.000005), 8)

    cursor.execute("UPDATE users SET balance = balance + ?, last_claim=? WHERE user_id=?",
                   (reward, now, user_id))
    conn.commit()

    bot.reply_to(message, f"🎉 Você ganhou {reward} BTC!")

@bot.message_handler(commands=['balance'])
def balance(message):
    user_id = message.from_user.id
    cursor.execute("SELECT balance FROM users WHERE user_id=?", (user_id,))
    balance = cursor.fetchone()[0]
    bot.reply_to(message, f"💎 Seu saldo: {balance} BTC")

@bot.message_handler(commands=['admin'])
def admin_panel(message):
    bot.reply_to(message, "ADMIN FUNCIONANDO 🔥")

    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(balance) FROM users")
    total_balance = cursor.fetchone()[0]

    if total_balance is None:
        total_balance = 0

    texto = f"""
👑 PAINEL ADMIN

👥 Total de usuários: {total_users}
💰 Saldo total no sistema: {round(total_balance, 4)}
    """

    bot.send_message(message.chat.id, texto)

print("Bot rodando...")
bot.polling()


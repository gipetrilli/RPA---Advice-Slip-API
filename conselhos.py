import requests
import sqlite3
import time
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

conn = sqlite3.connect("projeto_rpa.db")
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS conselhos (
    id INTEGER PRIMARY KEY,
    texto TEXT NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS dados_processados (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_conselho INTEGER,
    palavras_longas TEXT,
    FOREIGN KEY(id_conselho) REFERENCES conselhos(id)
)
''')
conn.commit()

# Função para buscar conselho da API
def buscar_conselho():
    url = "https://api.adviceslip.com/advice"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data['slip']['id'], data['slip']['advice']
    else:
        return None, None

def inserir_conselho(advice_id, advice_text):
    try:
        cursor.execute("INSERT OR IGNORE INTO conselhos (id, texto) VALUES (?, ?)", (advice_id, advice_text))
        conn.commit()
        print(f"Conselho inserido: {advice_id}")
    except Exception as e:
        print("Erro ao inserir:", e)

def extrair_palavras(texto):
    return ', '.join(re.findall(r'\b\w{7,}\b', texto))

for i in range(10):
    aid, texto = buscar_conselho()
    if aid and texto:
        inserir_conselho(aid, texto)
    time.sleep(1.5)

cursor.execute("SELECT id, texto FROM conselhos")
conselhos = cursor.fetchall()

for cid, texto in conselhos:
    palavras = extrair_palavras(texto)
    cursor.execute('''
        INSERT INTO dados_processados (id_conselho, palavras_longas)
        VALUES (?, ?)
    ''', (cid, palavras))
    conn.commit()
    print(f"Processado conselho {cid}: {palavras}")

cursor.execute("SELECT id, texto FROM conselhos")
conselhos = cursor.fetchall()

cursor.execute("SELECT id_conselho, palavras_longas FROM dados_processados")
processados = cursor.fetchall()

conn.close()

texto_email = "Resumo dos Conselhos Coletados:\n\n"
for cid, texto in conselhos:
    texto_email += f"[{cid}] {texto}\n"

texto_email += "\nPalavras com mais de 6 letras (processadas):\n\n"
for pid, palavras in processados:
    texto_email += f"Conselho {pid}: {palavras}\n"

remetente = "giovanna.venditti@aluno.faculdadeimpacta.com.br"
senha = "abcdefghijklmnop"  # senha de app do Gmail (substitua pela real)
destinatario = "vanderson.bossi@faculdadeimpacta.com.br"
assunto = "Relatório Automatizado - Projeto RPA"

mensagem = MIMEMultipart()
mensagem["From"] = remetente
mensagem["To"] = destinatario
mensagem["Subject"] = assunto
mensagem.attach(MIMEText(texto_email, "plain"))

try:
    servidor = smtplib.SMTP("smtp.gmail.com", 587)
    servidor.starttls()
    servidor.login(remetente, senha)
    servidor.send_message(mensagem)
    servidor.quit()
    print("E-mail enviado com sucesso!")
except Exception as e:
    print("Erro ao enviar e-mail:", e)

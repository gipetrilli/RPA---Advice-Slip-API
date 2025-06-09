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
    except Exception as e:
        print(f"Erro ao inserir conselho no DB:", e)

def extrair_palavras(texto):
    palavras_encontradas = re.findall(r'\b\w{7,}\b', texto)
    return ','.join(palavras_encontradas)

print("Iniciando coleta de conselhos da API...")
for i in range(10):
    aid, texto = buscar_conselho()
    if aid and texto:
        inserir_conselho(aid, texto)
    time.sleep(1.5)

print("\nIniciando processamento de palavras longas dos conselhos...")
cursor.execute("SELECT id, texto FROM conselhos")
conselhos_salvos = cursor.fetchall()

for cid, texto_conselho in conselhos_salvos:
    palavras_longas_extraidas = extrair_palavras(texto_conselho)
    try:
        cursor.execute('''
            INSERT INTO dados_processados (id_conselho, palavras_longas)
            VALUES (?, ?)
        ''', (cid, palavras_longas_extraidas))
        conn.commit()
    except Exception as e:
        print(f"Erro ao inserir dados processados para o conselho {cid}:", e)

print("\nPreparando relatório para envio por e-mail...")

cursor.execute("SELECT id, texto FROM conselhos")
conselhos_para_email = cursor.fetchall()

cursor.execute("SELECT id_conselho, palavras_longas FROM dados_processados")
processados_para_email = cursor.fetchall()

texto_email = "Relatório do Projeto RPA - Conselhos e Palavras Processadas\n\n"
texto_email += "--- Resumo dos Conselhos Coletados ---\n"
for cid, texto in conselhos_para_email:
    texto_email += f"ID: {cid}\nConselho: {texto}\n\n"

texto_email += "--- Palavras com 7+ letras (Processadas) ---\n"
for pid, palavras in processados_para_email:
    texto_email += f"ID do Conselho: {pid}\nPalavras Longas: {palavras if palavras else 'Nenhuma'}\n\n"

remetente = "giovanna.venditti@aluno.faculdadeimpacta.com" 
senha = "abcd efgh ijkl mnop" #senha ficticia alterada por questões de segurança
destinatario = "vanderson.bossi@faculdadeimpacta.com.br"
assunto = "Relatório Automatizado - Projeto RPA: Conselhos"

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
    print("E-Mail de relatório enviado com sucesso!")
except Exception as e:
    print(f"Erro ao enviar e-mail de relatório: {e}")

conn.close()
print("Conexão com o banco de dados fechada.")

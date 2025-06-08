import requests
import sqlite3
import time
import re

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
        return new_func()

def new_func():

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

conn.close()

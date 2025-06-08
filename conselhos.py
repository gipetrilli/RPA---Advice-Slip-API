import requests
import sqlite3
import time

conn = sqlite3.connect("projeto_rpa.db")
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS conselhos (
    id INTEGER PRIMARY KEY,
    texto TEXT NOT NULL
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
        print("Erro ao acessar API.")
        return None, None

def inserir_conselho(advice_id, advice_text):
    try:
        cursor.execute("INSERT OR IGNORE INTO conselhos (id, texto) VALUES (?, ?)", (advice_id, advice_text))
        conn.commit()
        print(f"Conselho inserido: {advice_id} - {advice_text}")
    except Exception as e:
        print("Erro ao inserir:", e)

for i in range(10):
    aid, texto = buscar_conselho()
    if aid and texto:
        inserir_conselho(aid, texto)
    time.sleep(1.5)  

conn.close()

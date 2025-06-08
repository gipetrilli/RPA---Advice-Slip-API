import requests

url = "https://api.adviceslip.com/advice"

response = requests.get(url)

if response.status_code == 200:
    data = response.json() 
    advice_id = data['slip']['id']
    advice_text = data['slip']['advice']
    print(f"ID: {advice_id}\nConselho: {advice_text}")
else:
    print(f"Erro ao acessar a API: {response.status_code}")

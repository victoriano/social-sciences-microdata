import requests
import pandas as pd

# Define the URL and headers
url = 'https://www.cis.es/o/cis/estudios'
headers = {
    'accept': '*/*',
    'accept-language': 'en,es-ES;q=0.9,es;q=0.8,de;q=0.7,fr;q=0.6,it;q=0.5,ca;q=0.4,gl;q=0.3',
    'cache-control': 'no-cache',
    'content-type': 'application/x-www-form-urlencoded;charset=UTF-8',
    'cookie': 'COOKIE_SUPPORT=true; GUEST_LANGUAGE_ID=es_ES; klaro={"liferayPortal":false,"googleAnalytics":true}; JSESSIONID=B867713B21C2C1F97B55C7586580EFF9; SERVER_ID=ed536456d9033063; LFR_SESSION_STATE_20100=1720337424046',
    'origin': 'https://www.cis.es',
    'pragma': 'no-cache',
    'priority': 'u=1, i',
    'referer': 'https://www.cis.es/catalogo-estudios/resultados-definidos/barometros',
    'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'no-cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
}

# Define the payload
payload = {
    'cndColeccionCod': '2',
    'cndColeccion': 'Barómetros CIS',
    'registrosPorPagina': '-1',
    'cndFechaEstudioDesde': '',
    'cndFechaEstudioHasta': '',
    'cndFiltroArbol': '',
    'cndTematicoCod': '',
    'cndTematico': ''
}

# Make the request
response = requests.post(url, headers=headers, data=payload)

# Check if the request was successful
if response.status_code == 200:
    data = response.json()
    # Extract the 'lista' field directly
    lista = data['lista']
    # Create a DataFrame with the specific fields
    df = pd.DataFrame(lista, columns=['id', 'codigo', 'titulo', 'fecha', 'ficheros'])
    # Filter rows where 'titulo' starts with "BARÓMETRO"
    df = df[df['titulo'].str.startswith('BARÓMETRO')]
    # Convert 'fecha' to datetime and sort by 'fecha' in descending order
    df['fecha'] = pd.to_datetime(df['fecha'], format='%d-%m-%Y')
    df = df.sort_values(by='fecha', ascending=False)
    # Save the DataFrame to a CSV file
    df.to_csv('barometros_index.csv', index=False)
    print("CSV file created successfully.")
else:
    print(f"Failed to retrieve data: {response.status_code}")
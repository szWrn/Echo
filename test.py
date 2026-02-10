import requests

response = requests.get('https://localhost:443/report')
print(response.json())
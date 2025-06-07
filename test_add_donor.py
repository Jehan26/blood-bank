import requests

url = 'http://localhost:5000/donors'
headers = {'Content-Type': 'application/json'}
data = {
    "name": "John Doe",
    "age": 30,
    "gender": "Male",
    "blood_group": "A+",
    "contact": "1234567890",
    "last_donation_date": "2023-01-01"
}

response = requests.post(url, json=data, headers=headers)
print('Status Code:', response.status_code)
print('Response:', response.json())

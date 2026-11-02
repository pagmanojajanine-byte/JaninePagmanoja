import requests

partner_url = "https://jarellkrismagarso-1.onrender.com/api/students"

record = {
    "student_id": "EXT-001",
    "name": "Sample Exchange Record",
    "program": "BSIT",
    "year": 1,
    "section": "A",
    "source": "Partner API"
}

response = requests.post(partner_url, json=record, timeout=15)
print(response.status_code)
print(response.text)
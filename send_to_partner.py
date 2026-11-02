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

try:
    response = requests.post(
        partner_url,
        json=record,
        timeout=30
    )

    print("Status Code:", response.status_code)
    print("Response:", response.text)

except requests.exceptions.RequestException as e:
    print("Error:", e)
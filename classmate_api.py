import requests
num1 = float(input("Enter first number: "))
num2 = float(input("Enter Second number: "))

url = "https://jarellkrismagarso.onrender.com/multiply"

params = {
    "num1": num1,
    "num2": num2
}
response = requests.get(url, params=params)
if response.status_code == 200:
    data = response.json()
    print("First Number:", data["number1"])
    print("Second Number:", data["number2"])
    print("Result:", data["result"])
else:
    print("Request failed.")
    print("Status Code:", response.status_code)
    print(response.text)

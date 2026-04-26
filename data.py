import requests

URL = "https://www.ntpf.ie/home/csv/op_waiting_list.csv"

response = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"})
response.raise_for_status()

with open("ntpf_outpatient.csv", "w", encoding="utf-8") as f:
    f.write(response.text)

print("Saved to ntpf_outpatient.csv")
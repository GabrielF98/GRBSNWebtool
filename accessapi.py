import requests

payload = {'event': 'SN2023lcr'}
user_agent = {'User-agent': 'Mozilla/5.0'}
r = requests.get("http://127.0.0.1:5000/api/get-event",
                 params=payload, allow_redirects=True, stream=True, headers=user_agent)

print(r.content)
with open('download.zip', 'wb') as f:
    f.write(r.content)

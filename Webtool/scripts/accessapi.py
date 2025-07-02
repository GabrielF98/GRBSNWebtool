"""
Communicate with the GRBSN Webtool via the api.
"""

import requests

payload = {"event": "SN2023lcr"}
user_agent = {"User-agent": "Mozilla/5.0"}
r = requests.get(
    "https://grbsn.watchertelescope.ie/api/get-event",
    params=payload,
    allow_redirects=True,
    stream=True,
    headers=user_agent,
)

with open(payload["event"] + ".zip", "wb") as f:
    f.write(r.content)

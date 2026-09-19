import os 
from dotenv import load_dotenv
from fetch_pr import fetch_pull_requests
import requests

load_dotenv() 

API_ROOT = "https://api.github.com"
TIMEOUT = 30

def fetch_pr_diff(token, owner, repo, pr_number):
    headers = {
        "Authorization" : f"Bearer {token}",
        "Accept" : "application/vnd.github.v3.diff",
        "X-Github-Api-Version": "2022-11-28",
    } 

    url = f"{API_ROOT}/repos/{owner}/{repo}/pulls/{pr_number}"

    try: 
        response = requests.get(url,headers=headers,timeout=TIMEOUT)
    except requests.RequestException as e : 
        print(f"[fetch_diff] Network error fetching diff: {e}")
        return None

    if not response.ok : 
        print(f"[fetch_diff] Failed to fetch diff: {response.status_code} {response.text[:300]}")
        return None

    return response.text


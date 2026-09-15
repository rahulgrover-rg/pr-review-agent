import os 
import requests
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
OWNER = os.environ.get("OWNER")
REPO = os.environ.get("REPO")



def fetch_pull_requests(GITHUB_TOKEN, OWNER, REPO, branch):    
    headers = {
        "Authorization" : f"Bearer {GITHUB_TOKEN}",
        "Accept" : "application/vnd.github+json"
    }
    params = {
        "state": "open", 
        "branch": branch
    }

    url = f"https://api.github.com/repos/{OWNER}/{REPO}/pulls"
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch pull requests: {response.status_code}")
        return None

if __name__ == "__main__":
    headers = {
        "Authorization" : f"Bearer {GITHUB_TOKEN}",
        "Accept" : "application/vnd.github+json"
    }

    url = f"https://api.github.com/repos/{OWNER}/{REPO}/pulls"
    print(url)

    response = requests.get(url, headers=headers)

    print(response.status_code)
    print(response.json())
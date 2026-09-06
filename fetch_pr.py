import os 
import requests
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
OWNER = os.environ.get("OWNER")
REPO = os.environ.get("REPO")

headers = {
    "Authorization" : f"Bearer {GITHUB_TOKEN}",
    "Accept" : "application/vnd.github+json"
}

url = f"https://api.github.com/repos/{OWNER}/{REPO}/pulls"
print(url)
response = requests.get(url, headers=headers)

print(response.status_code)
print(response.json())
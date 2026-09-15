import os 
from dotenv import load_dotenv
from fetch_pr import fetch_pull_requests
import requests

load_dotenv() 

OWNER = os.environ.get("OWNER") 
REPO = os.environ.get("REPO") 
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")


def fetch_pr_diff(GITHUB_TOKEN,OWNER, REPO, pr_number):
    headers = {
        "Authorization" : f"Bearer {GITHUB_TOKEN}",
        "Accept" : "application/vnd.github.v3.diff"
    } 
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/pulls/{pr_number}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.text    
    else :
        print(f"Failed to fetch PR diff: {response.status_code}")
        return None

if __name__ == "__main__":
    PR = fetch_pull_requests(GITHUB_TOKEN, OWNER, REPO, "test_branch_1")
    PR_NUMBER = PR[0]["number"] if PR else None 

    headers = {
        "Authorization" : f"Bearer {GITHUB_TOKEN}",
        "Accept" : "application/vnd.github.v3.diff"
    }

    url = f"https://api.github.com/repos/{OWNER}/{REPO}/pulls/{PR_NUMBER}"
    print(url)

    response = requests.get(url, headers=headers) 
    print(response.status_code)
    print(response.text)
import requests 
from dotenv import load_dotenv
import os 
from fetch_pr import fetch_pull_requests
from fetch_diff import fetch_pr_diff

load_dotenv() 

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
OWNER = os.environ.get("OWNER")
REPO = os.environ.get("REPO")
BRANCH = "test_branch_1"

def post_review(GITHUB_TOKEN, OWNER, REPO, pr_number, review_body, review_event= "COMMENT"):
    headers = {
        "Authorization" : f"Bearer {GITHUB_TOKEN}",
        "Accept" : "application/vnd.github+json"
    }

    url = f"https://api.github.com/repos/{OWNER}/{REPO}/pulls/{pr_number}/reviews"
    payload = {
        "body" : review_body,
        "event" : review_event
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        print(f"Successfully posted review for PR #{pr_number}")
    else:
        print(f"Failed to post review for PR #{pr_number}: {response.status_code}")

if __name__ == "__main__":
    pr_number = 1  
    review_body = "This is a test review comment."  
    post_review(GITHUB_TOKEN, OWNER, REPO, pr_number, review_body)


import requests 
from dotenv import load_dotenv
import os 

load_dotenv() 

API_ROOT = "https://api.github.com" 
TIMEOUT = 30

EVENT_MAP = {
    "approve" : "APPROVE",
    "request_changes": "REQUEST_CHANGES",
    "comment": "COMMENT"
}

def post_review(token, owner, repo, pr_number, body, action="COMMENT"):
    event = EVENT_MAP.get(action.lower(), "COMMENT")

    headers = {
        "Authorization" : f"Bearer {token}",
        "Accept" : "application/vnd.github+json", 
        "X-Github-Api-Version": "2022-11-28", 
    }

    url = f"{API_ROOT}/repos/{owner}/{repo}/pulls/{pr_number}/reviews"

    def _send(evt, text) : 
        try: 
            return requests.post(url, headers=headers, json= {
                "body": text,
                "event": evt
            }, timeout=TIMEOUT)
        except requests.RequestException as e : 
            print(f"[post_review] Network error posting review: {e}")
            return None

    response = _send(evt=event, text=body)

    if response is None: 
        return False

    if response.ok : 
        print(f"[post_review] Posted {event} review on PR #{pr_number}")
        return True 

    if response.status_code == 422 and event != "COMMENT": 
        print(f"[post_review] {event} rejected (422) - likely self-review " 
              f"restiction. Falling back to COMMENT")
        note = (f"\n\n The agent intended to post **{event}** but Github " 
                f"rejected it (an account cannot formally review its own PR). " 
                f"Posted a comment instead.")

        retry = _send("COMMENT", body+note) 
        if retry is not None and retry.ok : 
            return True

    print(f"[post_review] Failed: {response.status_code} {response.text[:300]}")
    return False
    

if __name__ == "__main__":
    a=1


import os 
import requests
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
OWNER = os.environ.get("OWNER")
REPO = os.environ.get("REPO")
API_ROOT = "https://api.github.com"
TIMEOUT = 30

def _headers(token) : 
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-Github-Api-Version": "2022-11-28"
    }

def choose_pr_interactively(prs) : 
    if not prs: 
        return None 
    if len(prs) == 1 : 
        pr = prs[0] 
        print(f"One open PR found: #{pr['number']} - {pr['title']}")
        return pr['number']

    print("\nOpen Pull Requests:")
    for i, pr in enumerate(prs,1) :
        head = pr.get("head", {}).get("ref", "?") 
        print(f" [{i}] #{pr['number']} - {pr['title']}  ({head})")
    print(" [a] all of them")

    while True: 
        choice = input("\nWhich PR? ").strip().lower() 
        if choice == 'a': 
            return "ALL" 
        if choice.isdigit() and 1 <= int(choice) <= len(prs) : 
            return prs[int(choice) - 1]['number'] 
        print("Invalid choice - enter a number from the list, or 'a'.") 



def fetch_pull_requests(token, owner, repo, branch=None):    

    params = {"state": "open"}

    if branch: 
        params["head"] = f"{owner}:{branch}"

    url = f"{API_ROOT}/repos/{owner}/{repo}/pulls"

    try: 
        response = requests.get(url, headers=_headers(token), params=params, timeout=TIMEOUT)
    except requests.RequestException as e: 
        print(f"[fetch_pr] Network error listing PRs: {e}")
        return None

    if not response.ok: 
        print(f"[fetch_pr] Failed to list PRs: {response.status_code} {response.text[:300]}")
        return None

    return response.json()

def fetch_pr_files(token, owner, repo, pr_number): 
    file_paths, additions, deletions, page = [], 0, 0, 1

    while True: 
        url = f"{API_ROOT}/repos/{owner}/{repo}/pulls/{pr_number}/files"
        try: 
            response = requests.get(url, headers=_headers(token), params={"per_page": 100, "page": page}, timeout=TIMEOUT)
        except requests.RequestException as e :
            print(f"[fetch_pr] Network error fetching PR files: {e}")
            return None  

        if not response.ok: 
            print(f"[fetch_pr] Failed to fetch PR files: {response.status_code} {response.text[:300]}")
            return None

        batch = response.json() 
        if not batch : 
            break 

        for f in batch: 
            file_paths.append(f.get("filename", ""))
            additions += f.get("additions", 0)
            deletions += f.get("deletions", 0)

        if len(batch) < 100 : 
            break 

        page += 1 
        if page > 30 : 
            print("[fetch_pr] Stopping pagination at 3000 files")
            break

    return file_paths,additions,deletions

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
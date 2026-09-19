import os 
import sys 
import argparse
from dotenv import load_dotenv 
from audit import build_entry, log_action, render_markdown 
from decide_action import decide_action
from fetch_diff import fetch_pr_diff
from fetch_pr import choose_pr_interactively, fetch_pr_files, fetch_pull_requests
from generate_review import analyze_diff, format_review_body 
from kill_switch import agent_enabled 
from post_review import post_review 
from risk import risk_band, score_pr
from branch_utils import resolve_branch 

load_dotenv()

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
OWNER = os.environ.get("OWNER") 
BRANCH = os.environ.get("BRANCH") 
REPO = os.environ.get("REPO") 
DEFAULT_MODE = "COMMENT_ONLY" 
PR_NUMBER_ENV = os.environ.get("PR_NUMBER")

def parse_args() : 
    parser = argparse.ArgumentParser(description="AI Pull Request Review Agent")
    parser.add_argument("--mode", choices=["COMMENT_ONLY", "FULL_CONTROL"], help="choose the agent_mode")
    parser.add_argument("--branch", help="Review PRs opened from this branch") 
    parser.add_argument("--pr", type=int, help="Review one specific PR number") 
    parser.add_argument("--all", action="store_true", help="Review every open PR, ignoring branch filters")
    parser.add_argument("--interactive", "-i", action="store_true", help="pick from the list of open PRs")
    return parser.parse_args()

def resolve_mode(cli_mode) :
    if cli_mode: 
        return cli_mode.strip().upper(), "--mode flag"
    env_mode = os.environ.get("AGENT_MODE").strip().upper()
    if env_mode: 
        return env_mode, "AGENT_MODE env var" 
    return DEFAULT_MODE

def select_targets(args): 
    pr_env = os.environ.get("PR_NUMBER")
    if args.pr: 
        return [args.pr] 
    if pr_env: 
        return [int(pr_env)]
    if args.all: 
        branch, source = None, "--all flag" 
    else : 
        branch, source = resolve_branch(args.branch)

    if branch: 
        print(f"Branch filter: '{branch}' ({source})")
    else : 
        print(f"No branch filter - reviewing all open PRs ({source})")

    prs = fetch_pull_requests(token=GITHUB_TOKEN, owner=OWNER, repo=REPO, branch=branch)
    if prs is None: 
        print("Failed to list pull requests.")
        return None 

    if not prs : 
        if branch : 
            print(f"No open pull requests from branch '{branch}'")
            print(f"Use --all to review every open PR, or --branch to pick another branch.")
        else : 
            print(f"No open pull requests found.")
        return []

    if args.interactive: 
        chosen = choose_pr_interactively(prs) 
        if chosen is None: 
            return []
        else : 
            return [chosen] 

    return [pr["number"] for pr in prs]
    

def review_single_pr(pr_number, mode) : 
    print(f"\n=== Reviewing PR #{pr_number} ===")

    #1 Deterministic Review

    files_result = fetch_pr_files(token=GITHUB_TOKEN, owner=OWNER, repo=REPO, pr_number=pr_number)
    if files_result is None: 
        print("Could not fetch changed files - skipping (failing closed).")
        return False 

    file_paths, additions, deletions = files_result 
    risk_score, risk_reasons = score_pr(file_paths, additions=additions, deletions=deletions) 
    band = risk_band(risk_score) 
    print(f"Risk: {risk_score}/100 ({band}) across {len(file_paths)} file(s), "
          f"+{additions}/-{deletions}")

    #2 LLM review 
    diff = fetch_pr_diff(token=GITHUB_TOKEN, owner=OWNER, repo=REPO, pr_number=pr_number) 
    analysis, llm_verdict = analyze_diff(diff) 
    print(f"LLM verdict: {llm_verdict}") 

    #3. Permission gate 
    action, ratoionale = decide_action(mode=mode, risk_score=risk_score, llm_verdict=llm_verdict) 
    print(f"Action: {action} - {ratoionale}") 

    #4. Comment + audit 
    entry = build_entry(pr_number=pr_number, mode=mode, risk_score=risk_score, risk_band_label=band, reasons=risk_reasons, llm_verdict=llm_verdict, final_action=action, rationale=ratoionale)
    log_action(entry) 

    body = format_review_body(analysis=analysis, risk_score=risk_score, risk_band_label=band, risk_reasons=risk_reasons) 
    body += render_markdown(entry) 

    return post_review(token=GITHUB_TOKEN, owner=OWNER, repo=REPO, pr_number=pr_number, body=body, action=action)


def main() : 
    args = parse_args() 

    missing = [n for n,v in [("GITHUB_TOKEN", GITHUB_TOKEN), ("OWNER", OWNER), ("REPO", REPO)] if not v] 
    if missing: 
        print(f"Missing required environment variables: {', '.join(missing)}") 
        sys.exit(1)

    enabled, reason = agent_enabled() 
    if not enabled: 
        print(f"Agent disabled - {reason}. Exiting without takinga any action.") 
        sys.exit(0) 

    AGENT_MODE, mode_source = resolve_mode(args.mode)
    print(f"Mode: {AGENT_MODE} from {mode_source}")
    if AGENT_MODE != "FULL_CONTROL" : 
        print(f"(Comment-Only: agent cannot approve or request changes)") 

    targets = select_targets(args= args)
    if targets is None: 
        sys.exit(1)
    if not targets:
        sys.exit(0)

    print(f"Found {len(targets)} PR(s) to review: {targets}") 

    failures = 0 
    for pr_number in targets : 
        try: 
            if not review_single_pr(pr_number=pr_number, mode=AGENT_MODE): 
                failures += 1 
        except Exception as e: 
            print(f"Unexpected error reviewing PR #{pr_number}: {e}") 
            failures += 1 

    print(f"\nDone. {len(targets) - failures} suceeded, {failures} failed.")
    sys.exit(1 if failures else 0) 


if __name__ == "__main__" : 
    main()

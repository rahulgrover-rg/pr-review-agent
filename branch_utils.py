import os 
import subprocess 

def in_ci(): 
    return os.environ.get("GITHUB_ACTIONS", "").lower() == True or os.environ.get("CI", "").lower() == True 

def current_git_branch() : 
    try: 
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True, text=True, timeout=5, check=False
        )
    except (FileNotFoundError, subprocess.SubprocessError): 
        return None 

    if result.returncode != 0 : 
        return None 

    branch = result.stdout.strip() 
    return branch or None

def resolve_branch(cli_branch = None) : 
    if cli_branch: 
        return cli_branch, "--branch argument"

    env_branch = (os.environ.get("BRANCH") or "").strip() 
    if env_branch : 
        return env_branch, "BRANCH environment variable" 
    if in_ci() : 
        return None, "CI run (auto detect skipped)" 
    detected = current_git_branch()
    if detected: 
        return detected, "auto-detected from current git checkout"

    return None, "no branch specified - all open PRs"


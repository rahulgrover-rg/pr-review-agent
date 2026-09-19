import os 

DISABLE_FILE = ".agent_disabled"

def agent_enabled(repo_root = None) :

    if repo_root is None: 
        repo_root = os.path.dirname(os.path.abspath(__file__))
     
    if os.path.exists(os.path.join(repo_root, DISABLE_FILE)) : 
        return False, f"Kill Switch active: {DISABLE_FILE} file present in repo"

    if os.environ.get("AGENT_DISABLED","").strip().lower() == "true" :
        return False, "Kill Switch active: AGENT_DISABLED env variable SET"

    return True, None 
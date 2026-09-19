import os 

def agent_enabled() : 
    if os.path.exists(".agent_disabled") : 
        return False, "Kill switch file present in repo"
    if os.environ.get("AGENT_DISABLED","").lower() == "true" :
        return False, "Disabled via environment variable"
    return True, None 
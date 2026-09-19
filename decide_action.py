from risk import risk_band
from dotenv import load_dotenv
import os 

load_dotenv()

AGENT_MODE = os.environ.get("AGENT_MODE","COMMENT_ONLY").upper()

def decide_action(mode, risk_score, llm_verdict) : 
    if mode == "COMMENT_ONLY": 
        return "comment", "Agent restricted to comment only mode."

    band = risk_band(risk_score)

    if band == "HIGH" : 
        return "comment", f"Risk {risk_score} recedes autonomy threshold - leaving for developer review."

    if band == "MEDIUM" :
        if llm_verdict == "approve" : 
            return "comment", f"Risk {risk_score}: not auto approving, leaving for developer review."
        return "request_changes", f"Risk {risk_score}: Flagged issues"

    return llm_verdict, f"Risk {risk_score}: within autonomous threshold"



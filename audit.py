import json
import datetime 

def log_action(pr_number, mode, risk_score, reasons, llm_verdict, final_action, rationale): 
    entry = {
        "timestamp" : datetime.datetime.now(datetime.timezone.utc).isoformat(), 
        "pr_number" : pr_number, 
        "mode" : mode,
        "risk_score" : risk_score,
        "reasons" : reasons,
        "llm_recommended" : llm_verdict,
        "action_taken" : final_action,
        "rationale" : rationale
    }

    with open("audit_log.jsonl", "a") as f: 
        f.write(json.dumps(entry) + "\n")


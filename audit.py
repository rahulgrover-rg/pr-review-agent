import json
import datetime 
import os 

LOG_PATH = os.environ.get("AUDIT_LOG_PATH", "audit_log.jsonl")

def build_entry(pr_number, mode, risk_score, reasons, llm_verdict, final_action, rationale) : 
    return {
        "timestamp" : datetime.datetime.now(datetime.timezone.utc).isoformat(), 
        "pr_number" : pr_number, 
        "mode" : mode,
        "risk_score" : risk_score,
        "risk_reasons" : reasons,
        "llm_recommended" : llm_verdict,
        "action_taken" : final_action,
        "rationale" : rationale
    }

def log_action(entry): 
    try : 
        with open(LOG_PATH, "a", encoding="utf-8") as f: 
            f.write(json.dumps(entry) + "\n")
    except OSError as e :
        print(f"[audit] Warning: could not write audit log: {e}")

    return entry

def render_markdown(entry) : 
    reasons = entry.get("risk_reasons") or []
    reasons_lines = "\n".join(f"- {r}" for r in reasons) or "- none"
    return (
        "\n\n<details>\n<summary> Agent audit trail</summary>\n\n"
        f"- **Timestamp (UTC): ** {entry['timestamp']} \n"
        f"- **Mode: ** `{entry['mode']}` \n"
        f"- **Risk Score: ** {entry['risk_score']}/100 ({entry['risk_score']}) \n"
        f"- **LLM Recommended: ** `{entry['llm_recommended']}` \n"
        f"- **Action taken: ** `{entry['action_taken']}` \n"
        f"- **Rationale: ** {entry['rationale']} \n"
        f"- **Risk Signals: ** \n{reasons_lines}\n \n"
        "</details>"
    )

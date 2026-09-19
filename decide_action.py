from risk import risk_band

VALID_VERDICTS = {"approve", "request_changes", "comment"}
FULL_CONTROL = "FULL_CONTROL"


def decide_action(mode, risk_score, llm_verdict):
    
    verdict = (llm_verdict or "").strip().lower()
    if verdict not in VALID_VERDICTS:
        verdict = "comment"

    normalised_mode = (mode or "").strip().upper()

    if normalised_mode != FULL_CONTROL:
        return "comment", "Agent restricted to comment-only mode."

    band = risk_band(risk_score)

    if band == "HIGH":
        return "comment", (
            f"Risk {risk_score}/100 (HIGH) exceeds autonomy threshold — "
            "leaving for developer review."
        )

    if band == "MEDIUM":
        if verdict == "approve":
            return "comment", (
                f"Risk {risk_score}/100 (MEDIUM): withholding auto-approval, "
                "leaving for developer review."
            )
        return "request_changes", f"Risk {risk_score}/100 (MEDIUM): flagged issues"

    return verdict, f"Risk {risk_score}/100 (LOW): within autonomy threshold"
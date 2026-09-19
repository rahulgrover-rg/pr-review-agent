SENSITIVE_PATTERNS = ["auth", "login","password", "secret", "token", "key", "credential", "payment", "billing", "migration", ".env", "config", "Dockerfile", ".github/workflows",]

def score_pr(files_changed, additions, deletions):
    score = 0 
    reasons = [] 

    total_lines = additions + deletions 
    if total_lines > 500 : 
        score += 40 
        reasons.append(f"Very large PR ({total_lines} lines changed)")
    elif total_lines > 150 : 
        score += 20 
        reasons.append(f"Large PR ({total_lines} lines changed)")

    if len(files_changed) > 20 :
        score += 15 
        reasons.append(f"Touches many files ({len(files_changed)})")

    for path in files_changed:
        lowered = path.lower()
        for pattern in SENSITIVE_PATTERNS:
            if pattern in lowered:
                score += 30 
                reasons.append(f"Sensitive file or path detected: {path}")
                break

    has_code = any(not is_test_file(f) for f in files_changed)
    has_tests = any(is_test_file(f) for f in files_changed)
    if has_code and not has_tests:
        score += 15 
        reasons.append("Code changed but no test files modified")

    return min(score, 100), reasons


def is_test_file(file_path):
    lowered = file_path.lower()
    return (
        "test" in lowered or 
        "spec" in lowered 
        # or 
        # "unittest" in lowered or 
        # "tests/" in lowered or 
        # "specs/" in lowered
    )

def risk_band(score): 
    if score >= 60 : 
        return "HIGH"
    elif score >= 30 : 
        return "MEDIUM"
    return "LOW"
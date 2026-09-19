SENSITIVE_PATTERNS = [
    "auth", "login", "password", "secret", "token", "key", "credential", 
    "payment", "billing", "migration", ".env", "config", "dockerfile", 
    ".github/workflows", ".pem", "api_key", "api-key"
]

SENSITIVE_FILE_POINTS = 30 
SENSITIVE_MAX_POINTS = 60


def is_test_file(file_path: str) -> bool:
    """Accurately identifies if a string file path is a test/spec file."""
    if not isinstance(file_path, str):
        file_path = getattr(file_path, "path", str(file_path))

    lowered = file_path.lower().replace("\\", "/")
    filename = lowered.split("/")[-1]

    # Directory checks
    if "/tests/" in lowered or lowered.startswith("tests/") or "/spec/" in lowered or lowered.startswith("spec/"):
        return True

    # Filename checks
    if filename.startswith(("test_", "spec_")) or filename.endswith(("_test.py", "_spec.py")):
        return True

    if "_test." in filename or ".test." in filename or "_spec." in filename or ".spec." in filename:
        return True

    return False


def score_pr(files_changed: list[str], additions: int, deletions: int) -> tuple[int, list[str]]:
    """Calculates a deterministic risk score (0-100) and returns associated risk signals."""
    score = 0
    reasons = []

    # 1. PR Size Scoring
    total_lines = additions + deletions
    if total_lines > 500:
        score += 40
        reasons.append(f"Very large PR ({total_lines} lines changed)")
    elif total_lines > 150:
        score += 20
        reasons.append(f"Large PR ({total_lines} lines changed)")

    # 2. File Count Scoring
    if len(files_changed) > 20:
        score += 15
        reasons.append(f"Touches many files ({len(files_changed)} files)")

    # 3. Sensitive Path Scoring (Capped at SENSITIVE_MAX_POINTS)
    sensitive_score = 0
    detected_sensitive_files = []

    for path_obj in files_changed:
        path = path_obj if isinstance(path_obj, str) else getattr(path_obj, "path", str(path_obj))
        lowered = path.lower()
        
        for pattern in SENSITIVE_PATTERNS:
            if pattern in lowered:
                sensitive_score += SENSITIVE_FILE_POINTS
                detected_sensitive_files.append(path)
                break

    if sensitive_score > 0:
        applied_sensitive_score = min(sensitive_score, SENSITIVE_MAX_POINTS)
        score += applied_sensitive_score
        reasons.append(
            f"Sensitive files/paths detected ({len(detected_sensitive_files)} file(s)): "
            f"{', '.join(detected_sensitive_files[:3])}{'...' if len(detected_sensitive_files) > 3 else ''}"
        )

    # 4. Test Coverage Heuristic
    has_code = any(not is_test_file(f) for f in files_changed)
    has_tests = any(is_test_file(f) for f in files_changed)
    if has_code and not has_tests:
        score += 15
        reasons.append("Code changes detected without corresponding test modifications")

    return min(score, 100), reasons


def risk_band(score: int) -> str:
    if score >= 60:
        return "HIGH"
    elif score >= 30:
        return "MEDIUM"
    return "LOW"
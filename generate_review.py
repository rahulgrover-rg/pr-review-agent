import os 
from dotenv import load_dotenv
from fetch_pr import fetch_pull_requests
from fetch_diff import fetch_pr_diff
from post_review import post_review
from groq import Groq 
import requests 

load_dotenv()

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
OWNER = os.environ.get("OWNER")
REPO = os.environ.get("REPO")
BRANCH = "test_branch_1"
AGENT_MODE = os.environ.get("AGENT_MODE","COMMENT").upper()
GROQ_API_KEY = os.environ.get("LLM_API_KEY")

GROQ_CLIENT = Groq(api_key=GROQ_API_KEY)

def analyze_diff(diff_text):
    system_prompt = """
    You are a Senior Software Engineer conducting a thorough PR code review.
    Analyze the provided Git diff and output ONLY a valid JSON object matching this structure:

    {
      "risk_level": "OKAY_TO_MERGE" | "MEDIUM_RISK" | "CRITICAL_RISK",
      "risk_percentage": 0-100 (integer),
      "confidence_score": "High" | "Medium" | "Low",
      "primary_reason": "Summary of overall assessment",
      "affected_locations": [
        {
          "file_path": "path/to/file",
          "line_reference": "Line X or Lines X-Y",
          "potential_risk": "Description of risk",
          "mitigation": "Actionable fix"
        }
      ]
    }
    """

    user_prompt = f"Analyze the following Git Diff:\n\n{diff_text}"

    chat_completion = GROQ_CLIENT.chat.completions.create(
        model = "llama-3.3-70b-versatile",
        messages = [
            {"role" : "system", "content": system_prompt},
            {"role" : "user", "content": user_prompt}
        ],
        response_format = {"type" : "json_object"},
        temperature = 0.2    
    )

    raw_response = chat_completion.choices[0].message.content
    return raw_response
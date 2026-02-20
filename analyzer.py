#Resume text + Job Description
#        ↓
#analyzer.py builds a prompt
#        ↓
#Sends it to Claude API
#        ↓
#Claude returns JSON analysis
#        ↓
#analyzer.py parses and returns the result
from email.mime import message
import anthropic
import json
import os
from dotenv import load_dotenv

#Section 2: Loading the API key.
# Load API key from .env file
load_dotenv()

# Create Claude client
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

#Section 3 — The System Prompt.
SYSTEM_PROMPT = """You are an expert recruiter and HR assistant. 
Analyze the given resume against the job description and return a JSON object with exactly this structure:
{
    "candidate_name": "extracted full name from resume",
    "experience_level": "Entry / Mid / Senior / Executive",
    "overall_score": <number 0-100>,
    "score_reason": "brief reason for the score",
    "matched_skills": ["skill1", "skill2", "skill3"],
    "missing_skills": ["skill1", "skill2", "skill3"],
    "red_flags": ["red flag1", "red flag2"],
    "strengths": ["strength1", "strength2", "strength3"],
    "verdict": "Shortlist / Maybe / Reject",
    "verdict_reason": "brief reason for the verdict",
    "summary": "2-3 sentence overall impression of the candidate"
}
Return ONLY the JSON, no markdown, no explanation."""

#Section 4 — The analyze function 
def analyze_resume(resume_text, job_description=""):
    # Build the user message
    user_message = f"Resume:\n{resume_text}"
    
    if job_description.strip():
        user_message += f"\n\nJob Description:\n{job_description}"
    
    # Call Claude API
    message = client.messages.create(
        model="claude-haiku-4-5-20251001",#"claude-opus-4-6",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": user_message}
        ]
    )
    
    # Extract text from response
    raw_response = ""
    for block in message.content:
        if block.type == "text":
            raw_response = block.text
            break
    
    # Clean and parse JSON
    clean_response = raw_response.replace("```json", "").replace("```", "").strip()
    result = json.loads(clean_response)
    
    return result

#Section 5 — Error Handling.
def safe_analyze_resume(resume_text, job_description=""):
    try:
        result = analyze_resume(resume_text, job_description)
        return result, None
    except json.JSONDecodeError:
        return None, "❌ Claude returned an unexpected response. Please try again."
    except anthropic.AuthenticationError:
        return None, "❌ Invalid API key. Please check your .env file."
    except anthropic.RateLimitError:
        return None, "❌ API rate limit reached. Please wait a moment and try again."
    except Exception as e:
        return None, f"❌ Unexpected error: {str(e)}"
import os
import json
import traceback
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

api_key = os.environ.get("GROQ_API_KEY")

if not api_key:
    print("❌ GROQ_API_KEY not found. Check your .env file")

client = Groq(api_key=api_key)


def safe_json_parse(text):
    """Attempt to safely extract JSON from LLM output."""
    try:
        return json.loads(text)
    except:
        try:
            start = text.find("{")
            end = text.rfind("}") + 1
            cleaned = text[start:end]
            return json.loads(cleaned)
        except:
            return None


def engage_and_evaluate(jd, resume_text):
    """Simulates a chat and returns transcript + reasoning + interest score."""

    # 🔒 Prevent huge inputs (important for stability)
    jd = jd[:1500]
    resume_text = resume_text[:3000]

    prompt = f"""
You are an AI Recruitment Agent.

Job Description:
{jd}

Candidate Resume:
{resume_text}

Instructions:
- Keep answers short and clear
- Return ONLY valid JSON
- Do NOT include any explanation outside JSON

Format:
{{
    "transcript": "AI: ...\\nCandidate: ...\\nAI: ...",
    "resume_reasoning": "...",
    "score_reasoning": "...",
    "interest_score": 0.0
}}
"""

    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant",
            temperature=0.3
        )

        raw_output = response.choices[0].message.content

        # 🔍 Debug log (check terminal)
        print("\n========== RAW LLM OUTPUT ==========")
        print(raw_output)
        print("===================================\n")

        parsed = safe_json_parse(raw_output)

        if not parsed:
            return {
                "transcript": "⚠️ Failed to parse AI response.",
                "resume_reasoning": raw_output,
                "score_reasoning": "Model did not return valid JSON.",
                "interest_score": 0.0
            }

        # Ensure all required keys exist
        return {
            "transcript": parsed.get("transcript", "No transcript generated."),
            "resume_reasoning": parsed.get("resume_reasoning", "No reasoning provided."),
            "score_reasoning": parsed.get("score_reasoning", "No score reasoning provided."),
            "interest_score": float(parsed.get("interest_score", 0.0))
        }

    except Exception as e:
        return {
            "transcript": f"❌ ERROR: {str(e)}",
            "resume_reasoning": traceback.format_exc(),
            "score_reasoning": "Execution failed",
            "interest_score": 0.0
        }
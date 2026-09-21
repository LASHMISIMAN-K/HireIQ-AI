import json
import os
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq


# ============================================================
# ENVIRONMENT
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise RuntimeError(
        "GROQ_API_KEY is not configured."
    )


# ============================================================
# GROQ CLIENT
# ============================================================

client = Groq(
    api_key=GROQ_API_KEY
)


# ============================================================
# JSON SCHEMA
# ============================================================

RESUME_SCHEMA = {
    "type": "object",

    "properties": {

        "ats_score": {
            "type": "integer"
        },

        "summary": {
            "type": "string"
        },

        "matched_skills": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },

        "missing_skills": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },

        "strengths": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },

        "weaknesses": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },

        "suggestions": {
            "type": "array",
            "items": {
                "type": "string"
            }
        }
    },

    "required": [
        "ats_score",
        "summary",
        "matched_skills",
        "missing_skills",
        "strengths",
        "weaknesses",
        "suggestions"
    ],

    "additionalProperties": False
}


# ============================================================
# RESUME ANALYZER
# ============================================================

def analyze_Resume(resume_text, job_role):

    """
    Analyze a resume using Groq GPT-OSS 20B.
    """

    # --------------------------------------------------------
    # Validate resume
    # --------------------------------------------------------

    if not resume_text:

        return {
            "error": "Resume text is empty."
        }

    resume_text = str(resume_text).strip()

    # Prevent extremely large prompts
    resume_text = resume_text[:15000]


    # --------------------------------------------------------
    # Validate job role
    # --------------------------------------------------------

    if not job_role:

        return {
            "error": "Target job role is required."
        }

    job_role = str(job_role).strip()


    # --------------------------------------------------------
    # PROMPT
    # --------------------------------------------------------

    prompt = f"""
You are HireIQ, an AI resume analyzer.

Analyze this resume for the target job role.

TARGET JOB ROLE:
{job_role}

RESUME:
{resume_text}

Return a concise professional analysis.

Rules:

- ATS score must be between 0 and 100.
- Maximum 5 items in each list.
- Keep every list item short.
- Keep the summary below 80 words.
- matched_skills must come from the resume.
- missing_skills should be relevant to the target role.
- strengths must be supported by the resume.
- weaknesses should identify genuine gaps.
- suggestions must be practical.
- Do not invent experience.
"""


    # --------------------------------------------------------
    # GROQ REQUEST
    # --------------------------------------------------------

    try:

        response = client.chat.completions.create(

            model="openai/gpt-oss-20b",

            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            # Important for GPT-OSS:
            # use low reasoning so the model doesn't consume
            # the completion budget on unnecessary reasoning.
            reasoning_effort="low",

            # Don't return reasoning content.
            include_reasoning=False,

            temperature=0.1,

            # Use current Groq parameter.
            max_completion_tokens=4096,

            # Strict structured output.
            response_format={
                "type": "json_schema",

                "json_schema": {
                    "name": "hireiq_resume_analysis",

                    "strict": True,

                    "schema": RESUME_SCHEMA
                }
            }
        )


    except Exception as e:

        print()
        print("=" * 60)
        print("GROQ API ERROR")
        print("=" * 60)
        print(str(e))
        print("=" * 60)
        print()

        return {
            "error": f"Groq API error: {str(e)}"
        }


    # --------------------------------------------------------
    # GET CONTENT
    # --------------------------------------------------------

    try:

        result = response.choices[0].message.content

    except Exception as e:

        print("Failed to read Groq response:")
        print(str(e))

        return {
            "error": "Failed to read AI response."
        }


    # --------------------------------------------------------
    # EMPTY RESPONSE
    # --------------------------------------------------------

    if not result:

        return {
            "error": "Groq returned an empty response."
        }


    print()
    print("=" * 60)
    print("GROQ RESPONSE")
    print("=" * 60)
    print(result)
    print("=" * 60)
    print()


    # --------------------------------------------------------
    # PARSE JSON
    # --------------------------------------------------------

    try:

        analysis = json.loads(result)

    except json.JSONDecodeError as e:

        print("JSON ERROR:")
        print(str(e))

        return {
            "error": "AI returned invalid JSON."
        }


    # --------------------------------------------------------
    # VALIDATE ATS SCORE
    # --------------------------------------------------------

    try:

        ats_score = int(
            analysis.get("ats_score", 0)
        )

    except (ValueError, TypeError):

        ats_score = 0


    ats_score = max(
        0,
        min(
            100,
            ats_score
        )
    )


    # --------------------------------------------------------
    # VALIDATE LISTS
    # --------------------------------------------------------

    list_fields = [
        "matched_skills",
        "missing_skills",
        "strengths",
        "weaknesses",
        "suggestions"
    ]


    for field in list_fields:

        value = analysis.get(field, [])

        if not isinstance(value, list):

            value = []


        # Maximum 5 items
        analysis[field] = [
            str(item)
            for item in value[:5]
        ]


    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    summary = analysis.get(
        "summary",
        ""
    )

    if not isinstance(summary, str):

        summary = str(summary)


    # --------------------------------------------------------
    # FINAL RESULT
    # --------------------------------------------------------

    final_result = {

        "ats_score": ats_score,

        "summary": summary,

        "matched_skills":
            analysis["matched_skills"],

        "missing_skills":
            analysis["missing_skills"],

        "strengths":
            analysis["strengths"],

        "weaknesses":
            analysis["weaknesses"],

        "suggestions":
            analysis["suggestions"]
    }


    print()
    print("=" * 60)
    print("FINAL HIREIQ RESULT")
    print("=" * 60)
    print(
        json.dumps(
            final_result,
            indent=2
        )
    )
    print("=" * 60)
    print()


    return final_result
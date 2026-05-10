"""
CV Tailoring Service — LLM rewrites a base CV and generates a cover letter
tailored to a specific job description.
"""

import json
from loguru import logger
from utils.llm_factory import call_llm

CV_TAILOR_PROMPT = """You are an expert CV/resume writer and career coach.
Given a base CV and a job description, rewrite the CV to be perfectly tailored for the role.

Rules:
- Emphasize relevant experience and skills that match the job requirements
- Use keywords from the job description naturally
- Quantify achievements where possible
- Keep it concise (max 2 pages worth of content)
- Maintain truthfulness — only reframe existing experience, never fabricate

Respond in JSON format ONLY:
{
  "name": "Full Name",
  "title": "Professional Title",
  "contact": {"email": "...", "phone": "...", "location": "...", "linkedin": "..."},
  "summary": "2-3 sentence professional summary tailored to the role",
  "experience": [{"role": "...", "company": "...", "period": "...", "bullets": ["..."]}],
  "education": [{"degree": "...", "institution": "...", "year": "..."}],
  "skills": ["..."],
  "certifications": ["..."]
}"""

COVER_LETTER_PROMPT = """You are an expert cover letter writer.
Given a tailored CV and job description, write a compelling cover letter.

Rules:
- Address specific requirements from the job posting
- Show enthusiasm for the company/role
- Reference 2-3 key achievements from the CV that are most relevant
- Keep it to 3-4 paragraphs
- Professional but personable tone

Respond with the cover letter text only (no JSON)."""


async def tailor_cv(base_cv: str, job_description: str) -> dict:
    """
    Rewrite a CV tailored to a job description.
    Returns: {"cv": dict, "cover_letter": str}
    """
    try:
        # Step 1: Tailor the CV
        cv_text = await call_llm(
            CV_TAILOR_PROMPT,
            f"BASE CV:\n{base_cv}\n\nJOB DESCRIPTION:\n{job_description}",
            temperature=0.4,
        )
        if cv_text.startswith("```"):
            cv_text = cv_text.split("\n", 1)[1].rsplit("```", 1)[0]
        cv_data = json.loads(cv_text)

        # Step 2: Generate cover letter
        cover_letter = await call_llm(
            COVER_LETTER_PROMPT,
            f"TAILORED CV:\n{cv_text}\n\nJOB DESCRIPTION:\n{job_description}",
            temperature=0.4,
        )

        logger.info("[CareerOps] CV tailored and cover letter generated")
        return {"cv": cv_data, "cover_letter": cover_letter}

    except json.JSONDecodeError as e:
        logger.error(f"[CareerOps] Failed to parse CV JSON: {e}")
        return {"error": f"CV parsing failed: {e}"}

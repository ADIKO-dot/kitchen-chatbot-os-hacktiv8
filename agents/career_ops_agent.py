"""
Career Ops Agent — CV tailoring, cover letter generation, and PDF output.
"""

from services.cv_tailor import tailor_cv
from services.cv_pdf_gen import generate_cv_pdf, generate_cover_letter_pdf


async def handle_career_ops(message: str, context: dict) -> dict:
    """
    Process career operations requests.
    Requires context with 'base_cv' and 'job_description'.
    """
    base_cv = context.get("base_cv")
    job_description = context.get("job_description")

    if not base_cv or not job_description:
        return {
            "message": "Career Ops agent ready. Provide context with 'base_cv' (your CV text) "
                       "and 'job_description' (target job posting) to generate a tailored CV + cover letter."
        }

    # Tailor CV + generate cover letter
    result = await tailor_cv(base_cv, job_description)

    if "error" in result:
        return {"message": f"Error: {result['error']}", "data": result}

    # Generate PDFs
    cv_pdf = await generate_cv_pdf(result["cv"])
    cl_pdf = await generate_cover_letter_pdf(result["cover_letter"], result["cv"].get("name", "Candidate"))

    return {
        "message": "Tailored CV and cover letter generated successfully.",
        "files": {"cv_pdf": cv_pdf, "cover_letter_pdf": cl_pdf},
        "data": result,
    }

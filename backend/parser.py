import json
import openai
import pdfplumber
import spacy
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

# Load the English NLP model
nlp = spacy.load("en_core_web_sm")

# Function to extract plain text from a PDF
def extract_text_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())

    # Ensure proper UTF-8 encoding
    return text.encode("utf-8", "ignore").decode("utf-8", "ignore")

# Function to extract key skills and keywords using spaCy
def extract_keywords(text):
    doc = nlp(text)
    keywords = set()

    for token in doc:
        if token.pos_ in ["NOUN", "PROPN"]:
            keywords.add(token.text.lower())

    return list(keywords)

def analyze_resume(text, job_category):
    """Sends resume text to AI and returns an optimized version."""
    
    if not text.strip():
        return {"error": "Resume text is empty or could not be extracted."}

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            # Lower temperature → less "creativity" in rewording/omitting
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": """
        You are an AI resume expert. 
        Your job is to analyze resumes and optimize them strictly in JSON format.
        Do NOT remove or omit any important sections or bullet points from the original resume 
        (e.g., Technical Skills, Leadership Experience). 
        If you must shorten text for a one-page layout, do so minimally 
        (but do not remove entire sections or bullet points).
        """
                },
                {
                    "role": "user",
                    "content": f"""
        Here is a resume:
        {text}

        Optimize this resume for a '{job_category}' position.

        **Return the response ONLY as a valid JSON object** with these fields:
        - "optimized_resume" (string): The fully rewritten resume in a professional format, 
        retaining ALL bullet points and sections from the original (including Technical Skills, Leadership Experience, etc.).
        Keep it to roughly one page if possible by condensing wording, but do NOT remove sections.
        - "overall_score" (integer): A rating from 1 to 10.
        - "strengths" (list): Key strengths of the resume.
        - "improvements" (list): Areas that need improvement.
        - "actionable_changes" (list): Specific action points to improve the resume.

        **IMPORTANT:**
        - DO NOT return text explanations, only JSON.
        - DO NOT return Markdown or code blocks.
        - The "optimized_resume" should be a string, formatted as a real resume 
        with headings for 'Technical Skills', 'Leadership Experience', etc. 
        """
                }
            ]
        )

        raw_response = response["choices"][0]["message"]["content"]
        feedback_json = json.loads(raw_response)

    except json.JSONDecodeError:
        feedback_json = {"error": "AI response formatting issue."}

    return feedback_json

# Run the program
if __name__ == "__main__":
    test_resume = "data/sample_resume.pdf"
    resume_text = extract_text_from_pdf(test_resume)
    ai_feedback = analyze_resume(resume_text, "Project Management")
    print("\n✅ AI Feedback:\n", ai_feedback)

    if "optimized_resume" in ai_feedback:
        optimized_resume = ai_feedback["optimized_resume"]

        # Check if it's already a string
        if isinstance(optimized_resume, str):
            print("\n✅ Optimized Resume:\n")
            print(optimized_resume)
        else:
            # If it's still a dictionary (unlikely at this stage), format it manually
            formatted_resume = """
            {name}
            {contact_info}

            Objective:
            {objective}

            Experience:
            {experience}

            Skills:
            {skills}

            Education:
            {education}
            """.format(
                name=optimized_resume.get('name', ''),
                contact_info=optimized_resume.get('contact_information', ''),
                objective=optimized_resume.get('objective', ''),
                experience="\n".join([
                    f"- {exp['role']} at {exp['company']} ({exp['duration']}, {exp['location']})\n  {exp['description']}"
                    for exp in optimized_resume.get('experiences', [])
                ]),
                skills=", ".join(optimized_resume.get('skills', [])),
                education="\n".join([
                    f"- {edu.get('degree', 'Unknown Degree')} from {edu.get('institution', 'Unknown Institution')} ({edu.get('date', 'Unknown Date')})\n Achievements: {', '.join(edu.get('achievements', []))}"
                    for edu in optimized_resume.get('education', [])
                ])
            )

            print(formatted_resume)

    else:
        print("\n❌ No optimized resume was generated. Check the AI response formatting.")

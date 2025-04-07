import pdfplumber 
import re 
import nltk
from nltk.tokenize import word_tokenize 
from nltk.corpus import stopwords 
from nltk.stem import WordNetLemmatizer 

from sklearn.feature_extraction.text import TfidfVectorizer 
from sklearn.metrics.pairwise import cosine_similarity 

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('wordnet')
nltk.download('stopwords')

def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z\s]', '', text)
    words = word_tokenize(text, language='english')
    stop_words = set(stopwords.words('english'))
    words = [word for word in words if word not in stop_words]
    lemmatizer = WordNetLemmatizer()
    words = [lemmatizer.lemmatize(word) for word in words]
    return ' '.join(words)

def extract_text_from_pdf(pdf_path):
    try:
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"

        if not text.strip():
            raise ValueError("No text extracted from PDF. Please check the file.")

        return preprocess_text(text)

    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return None

def extract_skills(text):
    predefined_skills = [
        "Python", "Java", "C++", "JavaScript", "SQL", "Machine Learning", 
        "Data Science", "Django", "Flask", "HTML", "CSS", "React", "Node.js", 
        "AWS", "Azure", "Docker", "Kubernetes", "Git", "PostgreSQL", "MongoDB", 
        "Agile", "Leadership", "Teamwork"
    ]
    text = text.lower()
    matching_skills = [skill for skill in predefined_skills if skill.lower() in text]
    return matching_skills

def extract_education(text):
    predefined_degrees = [
        "bachelor", "master", "phd", "associate", "bsc", "msc", "mba", "bba",
        "mca", "btech", "mtech", "be", "me", "computer science", "information technology"
    ]
    text = text.lower()
    matching_degrees = [degree for degree in predefined_degrees if degree in text]
    return matching_degrees

def extract_experience(text):
    experience_years = re.findall(r'(\d+)\s*(?:years?|yrs?)\s*(?:of)?\s*experience', text, re.IGNORECASE)
    if experience_years:
        return max(map(int, experience_years))  # Take the maximum years of experience found
    return 0  # Default to 0 if no experience is found

def calculate_similarity(resume_text, jd_text):
    try:
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform([resume_text, jd_text])
        similarity_matrix = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
        match_percentage = similarity_matrix[0][0] * 100

        resume_skills = extract_skills(resume_text)
        jd_skills = extract_skills(jd_text)

        matching_skills = list(set(resume_skills) & set(jd_skills))
        missing_skills = list(set(jd_skills) - set(resume_skills))
        extra_skills = list(set(resume_skills) - set(jd_skills))
        skills_match_percentage = len(matching_skills) / len(jd_skills) * 100 if jd_skills else 0

        # Education Match Percentage
        resume_education = extract_education(resume_text)
        jd_education = extract_education(jd_text)
        education_match_percentage = len(set(resume_education) & set(jd_education)) / len(jd_education) * 100 if jd_education else 0

        # Experience Match Percentage
        resume_experience = extract_experience(resume_text)
        jd_experience = extract_experience(jd_text)
        experience_match_percentage = min(resume_experience / jd_experience, 1) * 100 if jd_experience else 0

        analysis_results = {
            "overall_match_percentage": match_percentage,
            "skills_match_percentage": skills_match_percentage,
            "education_match_percentage": education_match_percentage,
            "experience_match_percentage": experience_match_percentage,
            "matching_skills": matching_skills,
            "missing_skills": missing_skills,
            "extra_skills": extra_skills,
            "job_description_summary": jd_text[:300],
            "resume_summary": resume_text[:300],
            "analysis_details": "Further analysis can be done on experience and education matching."
        }

        return analysis_results
    except Exception as e:
        print(f"Error calculating similarity: {e}")
        return None

@csrf_exempt
@require_http_methods(["POST"])
def analyze_resume(request):
    resume_file = request.FILES.get("resume_pdf")
    jd_file = request.FILES.get("job_description_pdf")
    jd_text = request.POST.get("job_description_text")

    if not resume_file:
        return JsonResponse({"success": False, "message": "Resume PDF is required"}, status=400)

    if not (jd_file or jd_text):
        return JsonResponse({"success": False, "message": "Job Description PDF or Text is required"}, status=400)

    resume_text = extract_text_from_pdf(resume_file)

    if resume_text is None:
        return JsonResponse({"success": False, "message": "Error extracting text from Resume PDF"}, status=400)

    if jd_file:
        jd_text_from_pdf = extract_text_from_pdf(jd_file)

        if jd_text_from_pdf is None:
            return JsonResponse({"success": False, "message": "Error extracting text from Job Description PDF"}, status=400)

        jd_text = jd_text_from_pdf

    analysis_results = calculate_similarity(resume_text, jd_text)

    if analysis_results is None:
        return JsonResponse({"success": False, "message": "Internal Server Error"}, status=500)

    return JsonResponse({"success": True, "message": "Analysis completed successfully", **analysis_results}, status=200)

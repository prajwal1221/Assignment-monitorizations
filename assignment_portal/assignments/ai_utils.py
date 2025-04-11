import fitz  # PyMuPDF
from django.core.files.storage import default_storage

def extract_text_from_pdf(submission):
    file_path = submission.file.name
    full_path = default_storage.path(file_path)
    
    text = ""
    try:
        with fitz.open(full_path) as doc:
            for page in doc:
                text += page.get_text()
    except Exception as e:
        text = f"Error reading PDF: {e}"

    return text

import re
from .constants import KEYWORDS


def count_keyword_occurrences(text, keyword):
    pattern = r'\b' + re.escape(keyword) + r'\b'
    return len(re.findall(pattern, text, flags=re.IGNORECASE))



def grade_submission(text):
    """
    Grades the submission based on the presence of predefined keywords.
    :param text: Extracted text from the PDF submission.
    :return: Grade as an integer between 0 and 100.
    """
    total_points = sum(KEYWORDS.values())
    obtained_points = 0

    for keyword, points in KEYWORDS.items():
        # Simple case-insensitive search for keyword presence
        if re.search(r'\b' + re.escape(keyword) + r'\b', text, re.IGNORECASE):
            obtained_points += points

    # Calculate percentage
    grade = (obtained_points / total_points) * 100
    return round(grade)

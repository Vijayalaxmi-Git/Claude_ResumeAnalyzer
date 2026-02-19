#Recruiter uploads a PDF or Word file
#        ↓
#utils.py opens the file
#        ↓
#Extracts all the text from it
#        ↓
#Returns plain text to the rest of the app

import pdfplumber
from docx import Document
import streamlit as st

#Section 2: PDF extraction function.
#defines a function that takes a file as input
def extract_text_from_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() #extracts text from that page
            if page_text:
                text += page_text + "\n"
    return text.strip() #returns all text with no extra spaces

#Section 3 — Word file extraction.
def extract_text_from_docx(file):
    text = ""
    doc = Document(file)
    for paragraph in doc.paragraphs:
        if paragraph.text.strip():
            text += paragraph.text + "\n"
    return text.strip()

#Section 4 — Main function that decides which extractor to use.
def extract_text(file):
    if file.name.endswith(".pdf"):
        return extract_text_from_pdf(file)
    elif file.name.endswith(".docx"):
        return extract_text_from_docx(file)
    else:
        st.error("❌ Unsupported file type. Please upload a PDF or Word file.")
        return None

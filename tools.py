import PyPDF2
import streamlit as st
from io import BytesIO

def resume_parser(resume_file, file_type):

    text = ''
    try:
        pdf_reader = PyPDF2.PdfReader(BytesIO(resume_file))
        for page in pdf_reader.pages:
            text += page.extract_text()
    except Exception as e:
        st.error(f'Error parsing resume : {e}')
        return None 

    return text


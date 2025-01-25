from dotenv import load_dotenv
from typing import TypedDict, Optional
from groq import Groq
from langgraph.graph import StateGraph, START, END
from core import Workflow, EmailState
from tools import resume_parser
import os 
import streamlit as st

load_dotenv()

def main():

    st.title("Automated Email composer")
    st.write("This app helps you to send your resume to companies via email")
    agent = Workflow()

    company_name = st.text_input('Company name', key="company_name")
    company_email = st.text_input('Company Email', key="company_email")
    company_site = st.text_input('Company site', key="company_site")

    resume_file = None
    st.subheader('Upload your resume')
    resume_file= st.file_uploader(
        "Choose a file(PDF, DOCX or TXT)",
        type=["pdf", "docx", "txt"],
        key=resume_file
    )

    if resume_file is not None:
        st.session_state.resume_file = resume_file.read()
        st.success("Resume upload successfully!")

    else:
        st.session_state.resume_file = None

    if st.button("Send Email"):

        if not company_name or not company_email:
            st.error("Please fill out all the fields.")
        else:
            initial_state = EmailState(
                company_name=company_name,
                company_email=company_email,
                company_url=company_site,
                company_web_scrapped_data=None,
                email_content=None,
                resume_file=resume_parser(st.session_state.resume_file, 'pdf'),
                status=None
            )

            final_state = agent.invoke(initial_state)

            st.success("Email sent successfully.")
            st.write("** Email content **")
            st.write(final_state["email_component"])
            st.write(final_state)
if __name__ == '__main__':
    main()

        





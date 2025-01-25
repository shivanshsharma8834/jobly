from groq import Groq 
from typing import TypedDict, Optional
from langgraph.graph import StateGraph, START, END
from bs4 import BeautifulSoup
import requests
import os 
import streamlit as st

class EmailState(TypedDict):
    company_name : str 
    company_email : str 
    company_url : str
    company_web_scrapped_data : Optional[str]
    email_component : Optional[str]
    resume_file : Optional[str]
    status : Optional[str]


class Workflow:

    def __init__(self):
        self.workflow_state_graph = StateGraph(EmailState)
        self.workflow_state_graph.add_node('fetch_company_info', self.fetch_company_info)
        self.workflow_state_graph.add_node('compose_email', self.compose_email)

        self.workflow_state_graph.add_edge(START, 'fetch_company_info')
        self.workflow_state_graph.add_edge('fetch_company_info' , 'compose_email')
        self.workflow_state_graph.add_edge('compose_email', END)
        self.workflow_state_graph = self.workflow_state_graph.compile()

    def invoke(self, state : EmailState) -> EmailState:
        return self.workflow_state_graph.invoke(state)

    @staticmethod
    def fetch_company_info(state : EmailState):
        try:
            response = requests.get(state['company_url'])
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            text = soup.get_text(separator="\n", strip=True)
            state['company_web_scrapped_data'] = text 
        except Exception as e:
            st.error(f"Error scraping website {e}")
        
        return state

    @staticmethod
    def compose_email(state : EmailState):
        groq_client = Groq(api_key=os.environ.get('GROQ_API_KEY'))
        response = groq_client.chat.completions.create(
            messages=[
                {
                    "role" : "system",
                    "content" : "You are an Email composer agent who will use the user's info provided in it's prompt and generate an email to be sent. You will only send the final email and nothing else"
                },
                {
                    "role" : "user",
                    "content" : f"Write a professional email to {state['company_name']} applying for a job. Make the language sound more humane than artificial"
                },
                {
                    "role" : "user",
                    "content" : f"Use the follow as the resume template for the app \n {state['resume_file']}"
                },
                {
                    "role" : "user",
                    "content" : f"Using the following scrapped data from the company site, generate the necessary mail \n{state['company_web_scrapped_data']}"
                }
            ],
                model='llama-3.3-70b-versatile',
                max_tokens=500
        )

        state['email_component'] = response.choices[0].message.content

        return state
        
        




    
    
import streamlit as st
import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Function to fetch research papers from IEEE website
def fetch_ieee_papers(query):
    url = "https://ieeexplore.ieee.org/search/searchresult.jsp"
    params = {
        "newsearch": "true",
        "queryText": query,
        "highlight": "true",
        "returnFacets": "ALL",
        "returnType": "SEARCH",
        "pageNumber": 1
    }

    response = requests.get(url, params=params)
    soup = BeautifulSoup(response.text, "html.parser")

    papers = []
    for result in soup.find_all(class_="List-results-items"):
        title = result.find(class_="title").text.strip()
        authors = result.find(class_="authors").text.strip()
        abstract = result.find(class_="description").text.strip()
        papers.append((title, authors, abstract))

    return papers


def fetch_springer_papers(query):
    url = "https://link.springer.com/search"
    params = {
        "query": query
    }

    response = requests.get(url, params=params)
    soup = BeautifulSoup(response.text, "html.parser")

    papers = []
    for result in soup.find_all(class_="result-item"):
        title = result.find(class_="title").text.strip()
        authors = result.find(class_="authors").text.strip()
        abstract = result.find(class_="snippet").text.strip()
        papers.append((title, authors, abstract))

    return papers

# Function to send recommendation email
def send_recommendation_email(user_email, recommendations):
    # Configure email details
    sender_email = st.secrets["Email"]
    sender_password = st.secrets["Password"]

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = user_email
    msg['Subject'] = 'Research Paper Recommendations'

    # Create the HTML content of the email
    html_content = f'''
    <html>
    <body>
        <h1>Research Paper Recommendations</h1>
        <p>Here are some research papers based on your interests:</p>
        <ul>
    '''

    for paper in recommendations:
        html_content += f'<li>{paper}</li>'

    html_content += '''
        </ul>
    </body>
    </html>
    '''

    # Attach the HTML content to the email
    msg.attach(MIMEText(html_content, 'html'))

    # Send the email
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)

# Streamlit web application
def app():
    st.title('Research Paper Recommendation System')

    user_email = st.text_input('Enter your email address:')
    user_interests = st.text_input('Enter your research interests (comma-separated):')

    if st.button('Get Recommendations'):
        interests = [interest.strip() for interest in user_interests.split(',')]


        ieee_papers = fetch_ieee_papers()
        springer_papers = fetch_springer_papers()

        recommendations = []
        for paper in ieee_papers + springer_papers:
            for interest in interests:
                if interest.lower() in paper.lower():
                    recommendations.append(paper)

        send_recommendation_email(user_email, recommendations)
        st.success('Recommendation email sent!')

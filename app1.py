import streamlit as st    
import requests
import bs4
from bs4 import BeautifulSoup
import smtplib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

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

def send_email(recipient, subject, body):
    # Replace with your SMTP server details
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    #smtp_username =  st.secrets["Username"]
    smtp_password =  st.secrets["Password"]

    sender =  st.secrets["Email"]

    message = f"Subject: {subject}\n\n{body}"

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(sender, smtp_password)
        server.sendmail(sender, recipient, message)
        
        
def app():
    st.title("Research Paper Recommender")
    interests = st.text_input("Enter your interests (comma-separated):")
    email = st.text_input("Enter your email address:")
    submit_button = st.button("Get Recommendations")

    if submit_button:
        ieee_papers = fetch_ieee_papers(interests)
        springer_papers = fetch_springer_papers(interests)

        # Combine and vectorize the papers' abstracts
        all_papers = ieee_papers + springer_papers
        abstracts = [paper[2] for paper in all_papers]
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(abstracts)

        # Calculate similarity between user interests and papers
        user_vector = vectorizer.transform([interests])
        similarities = cosine_similarity(user_vector, tfidf_matrix)
        sorted_indices = similarities.argsort()[0][::-1]
        recommendations = []
        for index in sorted_indices:
            title = all_papers[index][0]
            authors = all_papers[index][1]
            abstract = all_papers[index][2]
            recommendations.append((title, authors, abstract))
        body = ""
        for recommendation in recommendations[:5]:  # Sending top 5 recommendations
            title, authors, abstract = recommendation
            body += f"Title: {title}\n"
            body += f"Authors: {authors}\n"
            body += f"Abstract: {abstract}\n"
            body += "\n"

        send_email(email, "Research Paper Recommendations", body)
        st.success("Recommendation email has been sent!")
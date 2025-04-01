import streamlit as st
import pandas as pd
import smtplib
import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect("training.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT,
                    topic TEXT,
                    presenter TEXT,
                    teams_link TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE,
                    password TEXT)''')
    conn.commit()
    conn.close()

def add_session(date, topic, presenter, teams_link):
    conn = sqlite3.connect("training.db")
    c = conn.cursor()
    c.execute("INSERT INTO sessions (date, topic, presenter, teams_link) VALUES (?, ?, ?, ?)", (date, topic, presenter, teams_link))
    conn.commit()
    conn.close()

def get_sessions():
    conn = sqlite3.connect("training.db")
    df = pd.read_sql_query("SELECT * FROM sessions", conn)
    conn.close()
    return df

def send_email(to_email, subject, body):
    try:
        server = smtplib.SMTP("smtp.example.com", 587)
        server.starttls()
        server.login("your_email@example.com", "your_password")
        message = f"Subject: {subject}\n\n{body}"
        server.sendmail("your_email@example.com", to_email, message)
        server.quit()
        st.success("Email sent successfully!")
    except Exception as e:
        st.error(f"Error sending email: {e}")

init_db()
st.sidebar.title("Learning & Development Portal")
page = st.sidebar.radio("Navigate to", ["Training Sessions", "Submit Training Idea", "Add Training Session", "Resources", "Login", "Register"])

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

if page == "Login":
    st.title("User Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        conn = sqlite3.connect("training.db")
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()
        if user:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success("Login successful!")
        else:
            st.error("Invalid credentials")

elif page == "Register":
    st.title("User Registration")
    username = st.text_input("Choose a Username")
    password = st.text_input("Choose a Password", type="password")
    if st.button("Register"):
        try:
            conn = sqlite3.connect("training.db")
            c = conn.cursor()
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            conn.close()
            st.success("Registration successful! You can now log in.")
        except sqlite3.IntegrityError:
            st.error("Username already taken. Choose a different one.")

elif page == "Training Sessions":
    st.title("Upcoming Training Sessions")
    st.write("Here are the upcoming training sessions:")
    st.table(get_sessions())

elif page == "Submit Training Idea":
    st.title("Submit a Training Idea")
    with st.form("idea_form"):
        name = st.text_input("Your Name")
        email = st.text_input("Your Email")
        topic = st.text_input("Training Topic")
        details = st.text_area("Describe the Idea")
        submit = st.form_submit_button("Submit Idea")
        
        if submit:
            if name and email and topic and details:
                st.success("Your idea has been submitted!")
                send_email("sme@example.com", f"New Training Idea: {topic}", f"From: {name}\nEmail: {email}\n\nIdea:\n{details}")
            else:
                st.error("Please fill in all fields.")

elif page == "Add Training Session" and st.session_state.logged_in:
    st.title("Add a New Training Session")
    with st.form("session_form"):
        date = st.date_input("Select Date")
        topic = st.text_input("Training Topic")
        presenter = st.text_input("Presenter Name")
        teams_link = st.text_input("Teams Meeting Link")
        add_session = st.form_submit_button("Add Session")

        if add_session:
            if date and topic and presenter and teams_link:
                add_session(date.strftime("%Y-%m-%d"), topic, presenter, teams_link)
                st.success("New training session added!")
            else:
                st.error("Please fill in all fields.")

elif page == "Resources":
    st.title("Resources & Guides")
    with st.expander("AI & ML Guide"):
        st.markdown("[Click here](https://example.com/ai-ml)")
    with st.expander("Cloud Computing Resources"):
        st.markdown("[Click here](https://example.com/cloud)")
    with st.expander("Cybersecurity Handbook"):
        st.markdown("[Click here](https://example.com/cyber)")
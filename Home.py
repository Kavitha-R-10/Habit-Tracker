import streamlit as st
import sqlite3
import bcrypt

# Connect to the SQLite database (or create it if not exists)
conn = sqlite3.connect('users.db', check_same_thread=False)
c = conn.cursor()

# Create the users table if it doesn't exist
def create_usertable():
    c.execute('''
        CREATE TABLE IF NOT EXISTS users(
            username TEXT PRIMARY KEY,
            password BLOB
        )
    ''')
    conn.commit()

# Add a new user
def add_userdata(username, password):
    c.execute('INSERT INTO users(username, password) VALUES (?, ?)', (username, password))
    conn.commit()

# Verify user credentials
def login_user(username, password):
    c.execute('SELECT * FROM users WHERE username = ?', (username,))
    data = c.fetchone()
    if data and bcrypt.checkpw(password.encode(), data[1]):
        return True
    return False

# Streamlit App Layout
def main():
    st.set_page_config(page_title="Habit Tracker Login", page_icon="🔐", layout="centered")
    st.title("🔐 Habit Tracker Login")

    menu = ["Login", "Register"]
    choice = st.sidebar.selectbox("Menu", menu)

    create_usertable()  # Ensure table exists

    if choice == "Login":
        st.subheader("Login to Your Account")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if login_user(username, password):
                st.success(f"✅ Welcome {username}!")
                st.session_state['logged_in'] = True
                st.session_state['username'] = username

                st.info("You can now access your habit dashboard.")
                st.page_link("pages/simple_habit_app.py", label="Go to Habit Tracker 🚀", icon="📊")
            else:
                st.error("❌ Invalid username or password.")

    elif choice == "Register":
        st.subheader("Create a New Account")
        new_user = st.text_input("Username")
        new_password = st.text_input("Password", type="password")

        if st.button("Register"):
            if not new_user or not new_password:
                st.warning("⚠️ Please fill in all fields.")
            else:
                hashed_pw = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt())
                try:
                    add_userdata(new_user, hashed_pw)
                    st.success("🎉 Account created successfully!")
                    st.info("Go to Login to access your account.")
                except sqlite3.IntegrityError:
                    st.warning("⚠️ Username already exists. Please choose another.")

if __name__ == '__main__':
    main()

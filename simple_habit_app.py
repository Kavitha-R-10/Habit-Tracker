import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta

# ---------- Database Setup ----------
def init_db():
    conn = sqlite3.connect("habit_tracker.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS weekly_goals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT,
                    habit TEXT,
                    goal INTEGER,
                    start_time TEXT,
                    end_time TEXT,
                    week_start_date TEXT,
                    day_of_week TEXT,
                    date TEXT,
                    completed INTEGER DEFAULT 0
                )''')
    conn.commit()
    conn.close()

# ---------- Add Weekly Goal ----------
def set_weekly_goal(username, habit, goal, start_time, end_time, week_start_date, day_of_week, selected_date):
    conn = sqlite3.connect("habit_tracker.db")
    c = conn.cursor()
    c.execute('''INSERT INTO weekly_goals
                 (username, habit, goal, start_time, end_time, week_start_date, day_of_week, date)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
              (username, habit, goal, start_time, end_time, week_start_date, day_of_week, selected_date))
    conn.commit()
    conn.close()

# ---------- Fetch Weekly Goals ----------
def get_weekly_goals(username):
    conn = sqlite3.connect("habit_tracker.db")
    c = conn.cursor()
    c.execute('''SELECT id, habit, goal, start_time, end_time, day_of_week, date, completed
                 FROM weekly_goals
                 WHERE username = ?
                 ORDER BY date''', (username,))
    rows = c.fetchall()
    conn.close()
    return rows

# ---------- Mark as Completed ----------
def mark_goal_completed(goal_id):
    conn = sqlite3.connect("habit_tracker.db")
    c = conn.cursor()
    c.execute('UPDATE weekly_goals SET completed = 1 WHERE id = ?', (goal_id,))
    conn.commit()
    conn.close()

# ---------- Weekly Goals Display ----------
def show_weekly_goals(username):
    st.header("📆 Weekly Goals")
    goals = get_weekly_goals(username)

    if not goals:
        st.info("No goals set for this week.")
    else:
        for goal in goals:
            goal_id, habit, minutes, start, end, day, date, completed = goal
            status = "✅ Completed" if completed else "❌ Not Completed"
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"**{habit}**: {minutes} min  \n📅 {day}, {date}  \n⏰ {start} - {end}  \nStatus: {status}")
            with col2:
                if not completed:
                    if st.button("Mark Completed", key=f"complete_{goal_id}"):
                        mark_goal_completed(goal_id)
                        st.rerun()  # Use st.rerun() instead of experimental_rerun()

# ---------- Set Weekly Goal Page ----------
def set_weekly_goals_ui(username):
    st.header("➕ Set Weekly Habit Goal")
    habit = st.text_input("Habit Name")
    goal = st.number_input("Target Minutes", min_value=1, step=1)
    start_time = st.time_input("Start Time")
    end_time = st.time_input("End Time")
    selected_date = st.date_input("Select Date")

    if st.button("Save Weekly Goal"):
        if habit:
            start_str = start_time.strftime("%I:%M %p")
            end_str = end_time.strftime("%I:%M %p")
            day_of_week = selected_date.strftime("%A")
            week_start = (selected_date - timedelta(days=selected_date.weekday())).strftime("%Y-%m-%d")
            set_weekly_goal(username, habit, goal, start_str, end_str, week_start, day_of_week, selected_date.strftime("%Y-%m-%d"))
            st.success("Habit goal saved successfully!")
        else:
            st.warning("Please enter a habit name.")

# ---------- Weekly Analysis ----------
def show_analysis(username):
    st.header("📊 Weekly Analysis")
    conn = sqlite3.connect("habit_tracker.db")
    df = pd.read_sql_query("SELECT * FROM weekly_goals WHERE username = ?", conn, params=(username,))
    conn.close()

    if df.empty:
        st.info("No data available for analysis.")
    else:
        df['date'] = pd.to_datetime(df['date'])
        completed_count = df['completed'].sum()
        total = len(df)

        st.metric("Total Goals", total)
        st.metric("Completed", completed_count)
        st.metric("Not Completed", total - completed_count)

        st.bar_chart(df.groupby('completed')['habit'].count())

# ---------- Main ----------
def main():
    init_db()
    st.sidebar.title("🗂️ Menu")
    menu = st.sidebar.radio("Go to", ["Set Weekly Goals", "View Weekly Goals", "Weekly Analysis"])
    username = st.sidebar.text_input("Enter Username", value="default_user")

    if username:
        if menu == "Set Weekly Goals":
            set_weekly_goals_ui(username)
        elif menu == "View Weekly Goals":
            show_weekly_goals(username)
        elif menu == "Weekly Analysis":
            show_analysis(username)
    else:
        st.warning("Please enter a username to continue.")

if __name__ == "__main__":
    main()

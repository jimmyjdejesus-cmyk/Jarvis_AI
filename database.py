import sqlite3
import json
from datetime import datetime

DB_NAME = 'janus_database.db'


def init_db():
    """Initializes the database and creates all necessary tables if they don't exist."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS chat_sessions
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       username
                       TEXT
                       NOT
                       NULL,
                       project_name
                       TEXT
                       NOT
                       NULL,
                       session_name
                       TEXT
                       NOT
                       NULL,
                       timestamp
                       DATETIME
                       DEFAULT
                       CURRENT_TIMESTAMP
                   )
                   ''')
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS chat_logs
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       session_id
                       INTEGER
                       NOT
                       NULL,
                       role
                       TEXT
                       NOT
                       NULL,
                       content
                       TEXT
                       NOT
                       NULL,
                       sources
                       TEXT,
                       timestamp
                       DATETIME
                       DEFAULT
                       CURRENT_TIMESTAMP,
                       FOREIGN
                       KEY
                   (
                       session_id
                   ) REFERENCES chat_sessions
                   (
                       id
                   )
                       )
                   ''')
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS pending_users
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       username
                       TEXT
                       UNIQUE
                       NOT
                       NULL,
                       name
                       TEXT
                       NOT
                       NULL,
                       email
                       TEXT
                       NOT
                       NULL,
                       hashed_password
                       TEXT
                       NOT
                       NULL
                   )
                   ''')
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS projects
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       username
                       TEXT
                       NOT
                       NULL,
                       project_name
                       TEXT
                       NOT
                       NULL,
                       UNIQUE
                   (
                       username,
                       project_name
                   )
                       )
                   ''')
    conn.commit()
    conn.close()


def get_projects(username):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT project_name FROM projects WHERE username = ?", (username,))
    projects = [row[0] for row in cursor.fetchall()]
    if not projects:
        add_project(username, "default")
        projects = ["default"]
    conn.close()
    return projects


def add_project(username, project_name):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO projects (username, project_name) VALUES (?, ?)", (username, project_name))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    finally:
        conn.close()


def create_new_session(username, project_name):
    session_name = f"Session - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO chat_sessions (username, project_name, session_name) VALUES (?, ?, ?)",
        (username, project_name, session_name)
    )
    session_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return session_id


def get_sessions_for_project(username, project_name):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, session_name FROM chat_sessions WHERE username = ? AND project_name = ? ORDER BY timestamp DESC",
        (username, project_name)
    )
    sessions = [{"id": row[0], "name": row[1]} for row in cursor.fetchall()]
    conn.close()
    return sessions


def save_message(session_id, role, content, sources=None):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    sources_json = json.dumps(sources) if sources else None
    cursor.execute(
        "INSERT INTO chat_logs (session_id, role, content, sources) VALUES (?, ?, ?, ?)",
        (session_id, role, content, sources_json)
    )
    conn.commit()
    conn.close()


def load_session_history(session_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT role, content, sources FROM chat_logs WHERE session_id = ? ORDER BY timestamp ASC",
        (session_id,)
    )
    history = []
    for row in cursor.fetchall():
        sources_list = json.loads(row[2]) if row[2] else []
        history.append({"role": row[0], "content": row[1], "sources": sources_list})
    conn.close()
    return history


def add_pending_user(username, name, email, hashed_password):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO pending_users (username, name, email, hashed_password) VALUES (?, ?, ?, ?)",
            (username, name, email, hashed_password)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def get_pending_users():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT username, name, email, hashed_password FROM pending_users")
    users = [{"username": row[0], "name": row[1], "email": row[2], "hashed_password": row[3]} for row in
             cursor.fetchall()]
    conn.close()
    return users


def remove_pending_user(username):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM pending_users WHERE username = ?", (username,))
    conn.commit()
    conn.close()

def rename_session(session_id, new_name):
    """Rename a chat session given its ID."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE chat_sessions SET session_name = ? WHERE id = ?", (new_name, session_id))
    conn.commit()
    conn.close()
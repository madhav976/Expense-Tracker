import os
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import g
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.environ.get("DATABASE_URL")

def get_connection():
    """Centralized database connection helper"""
    return psycopg2.connect(DATABASE_URL)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = get_connection()
    return db

def init_db(app):
    with app.app_context():
        db = get_db()
        cursor = db.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            balance REAL NOT NULL,
            created_date DATE NOT NULL
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id SERIAL PRIMARY KEY,
            account_id INTEGER,
            transaction_type TEXT,
            item_name TEXT,
            amount REAL,
            category TEXT,
            purchase_date DATE,
            FOREIGN KEY(account_id)
                REFERENCES accounts(id)
        )
        """)
        
        db.commit()

def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

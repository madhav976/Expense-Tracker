import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash, g
from database.db import get_db, init_db, close_connection

# Load environment variables
load_dotenv()

app = Flask(__name__)
# Use environment variable for secret key, with a fallback for local dev
app.secret_key = os.environ.get('SECRET_KEY', 'super_secret_key_for_expense_tracker')

# Initialize DB
init_db(app)

@app.teardown_appcontext
def teardown_db(exception):
    close_connection(exception)

@app.route('/')
def index():
    if 'account_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        balance = float(request.form['balance'])
        created_date = datetime.now().strftime('%Y-%m-%d')

        db = get_db()
        cursor = db.cursor(cursor_factory=RealDictCursor)
        
        # Check if account already exists
        cursor.execute("SELECT * FROM accounts WHERE name = %s", (name,))
        if cursor.fetchone():
            flash("Account with this name already exists.", "danger")
            return redirect(url_for('signup'))
        
        try:
            cursor.execute("""
                INSERT INTO accounts (name, balance, created_date)
                VALUES (%s, %s, %s)
            """, (name, balance, created_date))
            db.commit()
            
            flash("Account created successfully. Please login.", "success")
            return redirect(url_for('login'))
        except psycopg2.Error:
            db.rollback()
            flash("An error occurred while creating your account. Please try again.", "danger")
            return redirect(url_for('signup'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form['name']
        
        db = get_db()
        cursor = db.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT id, name FROM accounts WHERE name = %s", (name,))
        account = cursor.fetchone()
        
        if account:
            session['account_id'] = account['id']
            session['account_name'] = account['name']
            flash(f"Welcome back, {account['name']}!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Account not found. Please check your name or sign up.", "danger")
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('account_id', None)
    session.pop('account_name', None)
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'account_id' not in session:
        return redirect(url_for('login'))
        
    db = get_db()
    cursor = db.cursor(cursor_factory=RealDictCursor)
    account_id = session['account_id']
    
    cursor.execute("SELECT balance FROM accounts WHERE id = %s", (account_id,))
    account = cursor.fetchone()
    current_balance = account['balance'] if account else 0.0
    
    cursor.execute("SELECT SUM(amount) as total_expenses FROM transactions WHERE account_id = %s AND transaction_type = 'purchase'", (account_id,))
    expenses_row = cursor.fetchone()
    total_expenses = expenses_row['total_expenses'] if expenses_row['total_expenses'] else 0.0
    
    cursor.execute("SELECT SUM(amount) as total_deposits FROM transactions WHERE account_id = %s AND transaction_type = 'deposit'", (account_id,))
    deposits_row = cursor.fetchone()
    total_deposits = deposits_row['total_deposits'] if deposits_row['total_deposits'] else 0.0

    return render_template('dashboard.html', 
                           balance=current_balance, 
                           total_expenses=total_expenses, 
                           total_deposits=total_deposits)

@app.route('/add_expense', methods=['GET', 'POST'])
def add_expense():
    if 'account_id' not in session:
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        item_name = request.form['item_name']
        amount = float(request.form['amount'])
        category = request.form['category']
        purchase_date = request.form['purchase_date']
        account_id = session['account_id']
        
        db = get_db()
        cursor = db.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("SELECT balance FROM accounts WHERE id = %s", (account_id,))
        current_balance = cursor.fetchone()['balance']
        
        if current_balance >= amount:
            try:
                new_balance = current_balance - amount
                cursor.execute("UPDATE accounts SET balance = %s WHERE id = %s", (new_balance, account_id))
                cursor.execute("""
                    INSERT INTO transactions (account_id, transaction_type, item_name, amount, category, purchase_date)
                    VALUES (%s, 'purchase', %s, %s, %s, %s)
                """, (account_id, item_name, amount, category, purchase_date))
                db.commit()
                flash("Expense added successfully!", "success")
                return redirect(url_for('dashboard'))
            except psycopg2.Error:
                db.rollback()
                flash("An error occurred while processing your expense. Please try again.", "danger")
        else:
            flash("Insufficient balance for this expense.", "danger")
            
    return render_template('add_expense.html')

@app.route('/add_balance', methods=['GET', 'POST'])
def add_balance():
    if 'account_id' not in session:
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        amount = float(request.form['amount'])
        deposit_date = request.form['deposit_date']
        account_id = session['account_id']
        
        db = get_db()
        cursor = db.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("SELECT balance FROM accounts WHERE id = %s", (account_id,))
        current_balance = cursor.fetchone()['balance']
        
        try:
            new_balance = current_balance + amount
            cursor.execute("UPDATE accounts SET balance = %s WHERE id = %s", (new_balance, account_id))
            
            cursor.execute("""
                INSERT INTO transactions (account_id, transaction_type, item_name, amount, category, purchase_date)
                VALUES (%s, 'deposit', 'Balance Deposit', %s, 'Deposit', %s)
            """, (account_id, amount, deposit_date))
            
            db.commit()
            flash("Balance added successfully!", "success")
            return redirect(url_for('dashboard'))
        except psycopg2.Error:
            db.rollback()
            flash("An error occurred while adding balance. Please try again.", "danger")
        
    return render_template('add_balance.html')

@app.route('/transactions')
def transactions():
    if 'account_id' not in session:
        return redirect(url_for('login'))
        
    db = get_db()
    cursor = db.cursor(cursor_factory=RealDictCursor)
    account_id = session['account_id']
    
    # Simple filtering
    category_filter = request.args.get('category')
    date_filter = request.args.get('date')
    search_query = request.args.get('search')
    
    query = "SELECT * FROM transactions WHERE account_id = %s"
    params = [account_id]
    
    if category_filter:
        query += " AND category = %s"
        params.append(category_filter)
    if date_filter:
        query += " AND purchase_date = %s"
        params.append(date_filter)
    if search_query:
        query += " AND item_name LIKE %s"
        params.append(f"%{search_query}%")
        
    query += " ORDER BY purchase_date DESC, id DESC"
    
    cursor.execute(query, params)
    transactions_list = cursor.fetchall()
    
    return render_template('transactions.html', transactions=transactions_list)

@app.route('/reports')
def reports():
    if 'account_id' not in session:
        return redirect(url_for('login'))
        
    db = get_db()
    cursor = db.cursor(cursor_factory=RealDictCursor)
    account_id = session['account_id']
    
    # Category summary for purchases
    cursor.execute("""
        SELECT category, SUM(amount) as total 
        FROM transactions 
        WHERE account_id = %s AND transaction_type = 'purchase' 
        GROUP BY category
    """, (account_id,))
    category_summary = cursor.fetchall()
    
    # Monthly summary for purchases
    cursor.execute("""
        SELECT TO_CHAR(purchase_date::date, 'YYYY-MM') as month, SUM(amount) as total 
        FROM transactions 
        WHERE account_id = %s AND transaction_type = 'purchase' 
        GROUP BY TO_CHAR(purchase_date::date, 'YYYY-MM')
        ORDER BY month DESC
    """, (account_id,))
    monthly_summary = cursor.fetchall()
    
    return render_template('reports.html', category_summary=category_summary, monthly_summary=monthly_summary)

if __name__ == '__main__':
    # Use environment variable for debug mode
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    app.run(debug=debug_mode)

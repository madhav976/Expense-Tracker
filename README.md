# Expense Tracker

A full-stack Expense Tracker web application built with Python, Flask, SQLite, HTML, and CSS.

This project was developed as part of my journey into software development before starting my B.Tech in Computer Science Engineering (AI/ML). The goal was to build a practical application that combines Object-Oriented Programming, SQL databases, backend development, reporting, and web development.

---

## Features

### Account Management

* User Signup
* User Login
* Account Creation Date Tracking
* Balance Management

### Expense Tracking

* Add Expenses
* Categorize Expenses
* Track Purchase Dates
* Automatic Balance Updates

### Transaction Management

* Transaction History
* Expense Records
* Deposit Records
* Database Storage

### Reports

* Monthly Expense Reports
* Category-wise Expense Reports
* Spending Analysis

### Database Features

* SQLite Integration
* Accounts Table
* Transactions Table
* Foreign Key Relationships
* Persistent Data Storage

---

## Tech Stack

### Backend

* Python
* Flask

### Database

* SQLite

### Frontend

* HTML
* CSS
* Jinja2 Templates

### Development Tools

* VS Code
* Git
* GitHub

---

## Database Schema

### Accounts Table

| Column       | Type    |
| ------------ | ------- |
| id           | INTEGER |
| name         | TEXT    |
| balance      | REAL    |
| created_date | TEXT    |

#### Purpose

Stores user account information and current balance.

---

### Transactions Table

| Column           | Type    |
| ---------------- | ------- |
| id               | INTEGER |
| account_id       | INTEGER |
| transaction_type | TEXT    |
| item_name        | TEXT    |
| amount           | REAL    |
| category         | TEXT    |
| purchase_date    | TEXT    |

#### Purpose

Stores all expense and deposit records linked to an account.

---

## Categories Supported

* Food
* Transport
* Entertainment
* Utilities
* Others

---

## Project Structure

```text
Expense Tracker/
│
├── app.py
├── expense_tracker.db
│
├── templates/
│   ├── login.html
│   ├── signup.html
│   ├── dashboard.html
│   ├── transactions.html
│   ├── reports.html
│
├── static/
│   ├── css/
│   └── js/
│
└── database/
    └── db.py
```

---

## What I Learned

Through this project I gained hands-on experience with:

* Object-Oriented Programming (OOP)
* Python Classes and Methods
* SQL and Database Design
* SQLite Integration
* CRUD Operations
* Foreign Keys
* Flask Routing
* HTML Forms
* Jinja2 Templating
* Web Application Architecture
* Debugging and Error Handling

---

## Challenges Faced

Some of the challenges encountered during development included:

* Designing relational database tables
* Managing account and transaction relationships
* Implementing category-based reporting
* Converting a CLI application into a web application
* Handling Flask template errors
* Building reusable backend logic

---

## Future Improvements

Planned enhancements include:

* Supabase/PostgreSQL Migration
* Data Visualization Charts
* User Authentication with Passwords
* Profile Management
* Budget Tracking
* Spending Goals
* Export Reports (CSV/PDF)
* Dark Mode
* Deployment

---

## AI Usage Disclosure

AI tools were used during development as learning and productivity assistants.

AI assistance was used for:

* Debugging Python code
* Reviewing SQL queries
* Explaining Flask concepts
* Identifying architectural improvements
* UI/UX implementation guidance
* Code review and optimization suggestions

All project requirements, feature planning, database design decisions, implementation choices, testing, integration, debugging, and final code assembly were completed by the developer.

---

## Running Locally

### 1. Clone the repository

```bash
git clone <repository-url>
```

### 2. Navigate into the project

```bash
cd expense-tracker
```

### 3. Install dependencies

```bash
pip install flask
```

### 4. Run the application

```bash
python app.py
```

### 5. Open in browser

```text
http://127.0.0.1:5000
```

---

## Author

**Madhav Saini**

B.Tech CSE (AI/ML) Student

Built as a learning project to strengthen Python, SQL, Flask, Database Design, and Full-Stack Development skills.

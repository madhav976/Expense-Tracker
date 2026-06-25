from database.db import get_connection

# Establish PostgreSQL connection using the centralized helper
conn = get_connection()
cursor = conn.cursor()

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

conn.commit()

class Expense :
    def create_account(self , name , balance , date = None ):
        self.name = name
        self.date = date
        self.balance = balance
        cursor.execute("""
        INSERT INTO accounts
        (name, balance, created_date)
        VALUES (%s, %s, %s) RETURNING id
        """, (name, balance, date))
        self.account_id = cursor.fetchone()[0]

        conn.commit()


    def purchase(self, thing, amount, category, purchase_date):
        self.purchase_date = purchase_date
        if self.balance >= amount:
            self.balance -= amount
            print(f"Purchase successful! - {thing} of category {category}, Remaining balance: {self.balance} at {self.purchase_date}")
            cursor.execute("""
            UPDATE accounts
            SET balance = %s
            WHERE id = %s
            """, (self.balance, self.account_id))
            cursor.execute("""
            INSERT INTO transactions
            (account_id, transaction_type,
            item_name, amount, category, purchase_date)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
           (
            self.account_id,
            "purchase",
            thing,
            amount,
            category,
            self.purchase_date
            ))
            conn.commit()
        else:
            print("Insufficient balance.")


    def show_bal(self):
        return self.balance
    
    def add_bal(self , amount , add_bal_date):
        self.balance += amount
        self.add_bal_date = add_bal_date
        print(f"Balance added! New balance: {self.balance} at {self.add_bal_date}")
        cursor.execute("""
        UPDATE accounts
        SET balance = %s
        WHERE id = %s
        """, (self.balance, self.account_id))
        cursor.execute("""
        INSERT INTO transactions
        (account_id,
        transaction_type,
        item_name,
        amount,
        purchase_date)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (
        self.account_id,
        "deposit",
        None,
        amount,
        self.add_bal_date
       ))
        conn.commit()
    def account_info(self):
        return f"Account Name: {self.name}, Balance: {self.balance}, Date: {self.date}, purchase date : {getattr(self, 'purchase_date', None)}, add_bal_date: {getattr(self, 'add_bal_date', None)}"
    
    def show_transactions(self):
        cursor.execute("""
        SELECT *
        FROM transactions
        WHERE account_id = %s
        """, (self.account_id,))
        rows = cursor.fetchall()
        for row in rows:
            print(f"""
                  Transaction id = {row[0]}
                  type = {row[2]}
                  item = {row[3]}
                  amount = {row[4]}
                  category = {row[5]}
                  purchase_date = {row[6]}
                  """)

if __name__ == "__main__":
    print("Welcome to the Expense Tracker!")
    print("===== LOGIN/SIGNUP =====")
    print("1. Signup")
    print("2. Login")

    a = input("Enter your choice (1 or 2): ")
    expense = None

    if a == "1":
        name = input("Enter your name: ")
        try:
            balance = float(input("Enter initial balance: "))
        except ValueError:
            print("Invalid input. Please enter a numeric value for balance.")
            exit()
        date = input("Enter the date of account creation (YYYY-MM-DD): ")
        expense = Expense()
        expense.create_account(name, balance, date)
        print(f"Account created successfully! Welcome, {name}.")

    elif a == "2":
        name = input("Enter your name: ")
        cursor.execute("""
        SELECT id, balance, created_date
        FROM accounts
        WHERE name = %s
        """, (name,))
        account = cursor.fetchone()
        if account:
            expense = Expense()
            expense.account_id = account[0]
            expense.name = name
            expense.balance = account[1]
            expense.date = account[2]
            print(f"Login successful! Welcome back, {name}.")
        else:
            print("Account not found. Please sign up first.")
            exit()

    if expense:
        while True:
            print("\n===== MENU =====")
            print("1. Purchase")
            print("2. Add Balance")
            print("3. Show Balance")
            print("4. Account Info")
            print("5. Show Transactions")
            print("6. Exit")

            choice = input("Enter your choice (1-6): ")

            if choice == "1":
                thing = input("Enter the item you want to purchase :")
                try:
                    amount = float(input("Enter the amount : "))
                except ValueError:
                    print("Invalid input. Please enter a numeric value for amount.")
                    continue
                print("Available categories: Food, Transport, Entertainment, Utilities, Others")
                category = input("Enter the category : ")
                if category.lower() not in ["food", "transport", "entertainment", "utilities", "others"]:
                    print("Invalid category. Please choose from the available categories.")
                    continue

                purchase_date = input("Enter the purchase date (YYYY-MM-DD): ")
                expense.purchase(thing, amount, category, purchase_date)

            elif choice == "2":
                try :
                    amount = float(input("Enter the amount to add :"))
                except ValueError:
                    print("Invalid input. Please enter a numeric value for amount.")
                    continue
                add_bal_date = input("Enter the date of adding balance (YYYY-MM-DD): ")
                expense.add_bal(amount, add_bal_date)

            elif choice == "3":
                print(f"Current balance: {expense.show_bal()}")

            elif choice == "4":
                print(expense.account_info())

            elif choice == "5":
                expense.show_transactions()

            elif choice == "6":
                print("Exiting the Expense Tracker. Goodbye!")
                break

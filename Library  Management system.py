
CREATE DATABASE IF NOT EXISTS library_db;
USE library_db;

-- 1. Books Table
CREATE TABLE IF NOT EXISTS books (
    book_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    author VARCHAR(255) NOT NULL,
    status VARCHAR(50) DEFAULT 'Available'
);

-- 2. Students Table
CREATE TABLE IF NOT EXISTS students (
    student_id INT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    department VARCHAR(100)
);

-- 3. Issue Records Table
CREATE TABLE IF NOT EXISTS issue_records (
    issue_id INT AUTO_INCREMENT PRIMARY KEY,
    book_id INT,
    student_id INT,
    issue_date DATE,
    FOREIGN KEY (book_id) REFERENCES books(book_id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
);


________________________________________
3. Python Source Code (main.py)
Prerequisites
Before running the application, make sure you have installed the official MySQL connector library:

Bash

pip install mysql-connector-python


Application Script
Save the code below as main.py. Update the database connection credentials (host, user, and password) inside the connect_db() function to match your local setup.

Python

import mysql.connector
from mysql.connector import Error
from datetime import date

def connect_db():
    """Establishes and returns a connection to the MySQL database."""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",          # Replace with your MySQL username
            password="password",  # Replace with your MySQL password
            database="library_db"
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def add_book():
    title = input("Enter book title: ")
    author = input("Enter author name: ")
    
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        query = "INSERT INTO books (title, author) VALUES (%s, %s)"
        cursor.execute(query, (title, author))
        conn.commit()
        print(f"✔️ Book '{title}' added successfully!")
        cursor.close()
        conn.close()

def add_student():
    try:
        student_id = int(input("Enter unique Student ID (Integer): "))
        name = input("Enter student name: ")
        dept = input("Enter department: ")
    except ValueError:
        print("❌ Invalid input. Student ID must be an integer.")
        return

    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        query = "INSERT INTO students (student_id, name, department) VALUES (%s, %s, %s)"
        try:
            cursor.execute(query, (student_id, name, dept))
            conn.commit()
            print(f"✔️ Patron profile created for {name}.")
        except Error as e:
            print(f"❌ Could not add student: {e}")
        finally:
            cursor.close()
            conn.close()

def issue_book():
    try:
        book_id = int(input("Enter Book ID to issue: "))
        student_id = int(input("Enter Student ID: "))
    except ValueError:
        print("❌ Input IDs must be integers.")
        return

    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        
        # Verify book availability
        cursor.execute("SELECT status FROM books WHERE book_id = %s", (book_id,))
        book = cursor.fetchone()
        
        # Verify student existence
        cursor.execute("SELECT name FROM students WHERE student_id = %s", (student_id,))
        student = cursor.fetchone()

        if not book:
            print("❌ Error: Book ID does not exist.")
        elif not student:
            print("❌ Error: Student ID is not registered.")
        elif book[0] != 'Available':
            print("❌ Error: This book is already checked out.")
        else:
            # Transaction execution
            today = date.today().strftime('%Y-%m-%d')
            cursor.execute("INSERT INTO issue_records (book_id, student_id, issue_date) VALUES (%s, %s, %s)", 
                           (book_id, student_id, today))
            cursor.execute("UPDATE books SET status = 'Issued' WHERE book_id = %s", (book_id,))
            conn.commit()
            print(f"✔️ Book ID {book_id} successfully issued to {student[0]}.")
            
        cursor.close()
        conn.close()

def return_book():
    try:
        book_id = int(input("Enter Book ID being returned: "))
    except ValueError:
        print("❌ Book ID must be an integer.")
        return

    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        
        # Check if book is actually issued
        cursor.execute("SELECT status FROM books WHERE book_id = %s", (book_id,))
        book = cursor.fetchone()

        if not book:
            print("❌ Error: Book ID does not exist.")
        elif book[0] == 'Available':
            print("⚠️ Alert: This book is already marked inside the archive system.")
        else:
            # Complete return transaction records
            cursor.execute("DELETE FROM issue_records WHERE book_id = %s", (book_id,))
            cursor.execute("UPDATE books SET status = 'Available' WHERE book_id = %s", (book_id,))
            conn.commit()
            print(f"✔️ Book ID {book_id} successfully returned to stock.")
            
        cursor.close()
        conn.close()

def view_books():
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM books")
        books = cursor.fetchall()
        
        print("\n--- LIBRARY CATLOG INTERFACE ---")
        print(f"{'ID':<6} {'Title':<30} {'Author':<25} {'Status':<12}")
        print("-" * 75)
        for row in books:
            print(f"{row[0]:<6} {row[1]:<30} {row[2]:<25} {row[3]:<12}")
        print("-" * 75 + "\n")
        
        cursor.close()
        conn.close()

def main_menu():
    while True:
        print("\n=== SYSTEM MANAGEMENT INTERFACE ===")
        print("1. View Library Catalog")
        print("2. Add New Book Asset")
        print("3. Register New Student Patron")
        print("4. Term Outbound Asset (Issue Book)")
        print("5. Term Inbound Asset (Return Book)")
        print("6. Shutdown Terminal")
        
        choice = input("Select operation handler module (1-6): ").strip()
        
        if choice == '1': view_books()
        elif choice == '2': add_book()
        elif choice == '3': add_student()
        elif choice == '4': issue_book()
        elif choice == '5': return_book()
        elif choice == '6':
            print("Shutting down terminal connection modules safely...")
            break
        else:
            print("❌ Invalid runtime selection flag. Please try again.")

if __name__ == "__main__":
    main_menu()


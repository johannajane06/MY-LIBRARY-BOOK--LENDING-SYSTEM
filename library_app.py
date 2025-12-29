import streamlit as st
import pandas as pd
import os

st.write("Hello! Streamlit is now connected correctly.")

# --- File Constants ---
BOOKS_FILE = "books.txt"
BORROWERS_FILE = "borrowers.txt"

# --- Helper Functions (Your Logic) ---
def read_file(filename):
    if not os.path.exists(filename):
        return []
    with open(filename, "r") as f:
        return [line.strip().split("|") for line in f]

def write_file(filename, data_list):
    with open(filename, "w") as f:
        for item in data_list:
            f.write("|".join(map(str, item)) + "\n")

def update_book_status(book_id, new_status):
    books = read_file(BOOKS_FILE)
    for b in books:
        if b[0] == book_id:
            b[4] = new_status
    write_file(BOOKS_FILE, books)

# --- Streamlit UI ---
st.set_page_config(page_title="Library Management System", layout="wide")
st.title("Library Book-Lending System")

# Sidebar Menu (Replaces your main_menu while loop)
menu = st.sidebar.selectbox("Main Menu", ["View Books", "Manage Books", "Manage Borrowers", "Borrow/Return"])

# 1. View Books
if menu == "View Books":
    st.header("Current Collection")
    books = read_file(BOOKS_FILE)
    if books:
        df = pd.DataFrame(books, columns=["ID", "Title", "Author", "Year", "Status"])
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("No books found.")

# 2. Manage Books (Add/Delete/Update)
elif menu == "Manage Books":
    st.header("Book Management")
    tab1, tab2, tab3 = st.tabs(["Add Book", "Update Book", "Delete Book"])

    with tab1:
        with st.form("add_book_form"):
            b_id = st.text_input("New Book ID")
            title = st.text_input("Title")
            author = st.text_input("Author")
            year = st.text_input("Year")
            if st.form_submit_button("Add Book"):
                with open(BOOKS_FILE, "a") as f:
                    f.write(f"{b_id}|{title}|{author}|{year}|Available\n")
                st.success("Book added!")

    with tab3:
        book_to_del = st.text_input("Enter Book ID to Delete")
        if st.button("Confirm Delete"):
            books = [b for b in read_file(BOOKS_FILE) if b[0] != book_to_del]
            write_file(BOOKS_FILE, books)
            st.warning(f"Book {book_to_del} deleted.")

# 3. Manage Borrowers
elif menu == "Manage Borrowers":
    st.header("Borrower Records")
    borrowers = read_file(BORROWERS_FILE)
    if borrowers:
        df_b = pd.DataFrame(borrowers, columns=["Student ID", "Name", "Book ID", "Days"])
        st.table(df_b)
    
    st.divider()
    st.subheader("Add New Borrower")
    with st.form("add_borrower"):
        s_id = st.text_input("Student ID")
        s_name = st.text_input("Full Name")
        if st.form_submit_button("Register"):
            with open(BORROWERS_FILE, "a") as f:
                f.write(f"{s_id}|{s_name}|None|0\n")
            st.success("Registered!")

# 4. Borrow/Return Logic
elif menu == "Borrow/Return":
    st.header("Transaction Desk")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Borrow a Book")
        student_id = st.text_input("Student ID", key="bor_sid")
        book_id = st.text_input("Book ID to Borrow", key="bor_bid")
        days = st.number_input("Days", min_value=1, value=7)
        if st.button("Process Loan"):
            # Update borrower record
            borrowers = read_file(BORROWERS_FILE)
            for b in borrowers:
                if b[0] == student_id:
                    b[2], b[3] = book_id, str(days)
            write_file(BORROWERS_FILE, borrowers)
            update_book_status(book_id, "Borrowed")
            st.success("Loan recorded!")

    with col2:
        st.subheader("Return a Book")
        r_sid = st.text_input("Student ID", key="ret_sid")
        r_bid = st.text_input("Book ID to Return", key="ret_bid")
        if st.button("Process Return"):
            # Late fee logic
            borrowers = read_file(BORROWERS_FILE)
            for b in borrowers:
                if b[0] == r_sid and b[2] == r_bid:
                    days_borrowed = int(b[3])
                    late_fee = max(0, days_borrowed - 7) * 1
                    if late_fee > 0:
                        st.error(f"Late Fee: RM{late_fee}")
                    else:
                        st.success("Returned on time!")
                    b[2], b[3] = "None", "0"
            write_file(BORROWERS_FILE, borrowers)
            update_book_status(r_bid, "Available")
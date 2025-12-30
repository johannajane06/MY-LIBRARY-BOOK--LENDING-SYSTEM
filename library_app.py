import streamlit as st
import pandas as pd
import os

st.write("Hello! Streamlit is now connected correctly.")

# --- File Constants ---
BOOKS_FILE = "books.txt"
BORROWERS_FILE = "borrowers.txt"

# --- Helper Functions ---
def read_file(filename):
    if not os.path.exists(filename):
        return []
    with open(filename, "r") as f:
        return [line.strip().split("|") for line in f if line.strip()]

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
st.title(" 📖Library Book-Lending System")

# Sidebar Menu
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

# 2. Manage Books (Add/Update/Delete)
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
                st.success(f"Book '{title}' added!")

    with tab2:
        st.subheader("Edit Existing Book")
        u_id = st.text_input("Enter Book ID to Update", key="update_bid")
        if u_id:
            books = read_file(BOOKS_FILE)
            book_found = next((b for b in books if b[0] == u_id), None)
            
            if book_found:
                new_title = st.text_input("Title", value=book_found[1])
                new_author = st.text_input("Author", value=book_found[2])
                new_year = st.text_input("Year", value=book_found[3])
                new_status = st.selectbox("Status", ["Available", "Borrowed"], 
                                         index=0 if book_found[4] == "Available" else 1)
                
                if st.button("Save Changes"):
                    for b in books:
                        if b[0] == u_id:
                            b[1], b[2], b[3], b[4] = new_title, new_author, new_year, new_status
                    write_file(BOOKS_FILE, books)
                    st.success("Book details updated successfully!")
            else:
                st.error("Book ID not found.")

    with tab3:
        book_to_del = st.text_input("Enter Book ID to Delete")
        if st.button("Confirm Delete Book"):
            books = [b for b in read_file(BOOKS_FILE) if b[0] != book_to_del]
            write_file(BOOKS_FILE, books)
            st.warning(f"Book {book_to_del} removed from system.")

# 3. Manage Borrowers (Add/Update/Delete)
elif menu == "Manage Borrowers":
    st.header("Borrower Records")
    tab_b1, tab_b2, tab_b3 = st.tabs(["View & Add", "Update Borrower", "Delete Borrower"])
    
    with tab_b1:
        borrowers = read_file(BORROWERS_FILE)
        if borrowers:
            df_b = pd.DataFrame(borrowers, columns=["Student ID", "Name", "Book ID", "Days"])
            st.table(df_b)
        
        st.divider()
        st.subheader("Register New Borrower")
        with st.form("add_borrower"):
            s_id = st.text_input("Student ID")
            s_name = st.text_input("Full Name")
            if st.form_submit_button("Register"):
                with open(BORROWERS_FILE, "a") as f:
                    f.write(f"{s_id}|{s_name}|None|0\n")
                st.success(f"Borrower {s_name} registered!")

    with tab_b2:
        st.subheader("Edit Borrower Details")
        ub_id = st.text_input("Enter Student ID to Update")
        if ub_id:
            borrowers = read_file(BORROWERS_FILE)
            borrower_found = next((b for b in borrowers if b[0] == ub_id), None)
            
            if borrower_found:
                new_name = st.text_input("Update Name", value=borrower_found[1])
                if st.button("Update Borrower"):
                    for b in borrowers:
                        if b[0] == ub_id:
                            b[1] = new_name
                    write_file(BORROWERS_FILE, borrowers)
                    st.success("Borrower name updated!")
            else:
                st.error("Student ID not found.")

    with tab_b3:
        st.subheader("Delete Borrower")
        db_id = st.text_input("Enter Student ID to Delete")
        if st.button("Confirm Delete Borrower"):
            borrowers = [b for b in read_file(BORROWERS_FILE) if b[0] != db_id]
            write_file(BORROWERS_FILE, borrowers)
            st.warning(f"Borrower {db_id} deleted.")

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
import sqlite3
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

class LibraryManagementSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("📚 Library Management System")
        self.root.geometry("550x650")
        self.root.config(bg="#e6f2ff")

        self.borrowed_books = []
        self.returned_books = []
        self.book_status = {}
        self.last_action_stack = []

        # --- Database Setup ---
        self.conn = sqlite3.connect("library.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS books (
                name TEXT PRIMARY KEY,
                status TEXT
            )
        """)
        self.conn.commit()

        # Load existing data into dictionaries
        self.load_books_from_db()

        # Header Frame
        header = tk.Frame(root, height=50, bg="#3399ff")
        header.pack(fill="x")
        tk.Label(header, text="📖 Library Management System", font=("Verdana", 20, "bold"),
                 bg="#3399ff", fg="white").pack(pady=5)

        # Borrow Section
        borrow_frame = tk.LabelFrame(root, text="📘 Borrow Book", padx=10, pady=10,
                                     bg="#ffffff", fg="#003366", font=("Arial", 10, "bold"))
        borrow_frame.pack(padx=15, pady=10, fill="x")

        tk.Label(borrow_frame, text="Book Name:", bg="#ffffff").grid(row=0, column=0, padx=5, pady=5)
        self.borrow_entry = ttk.Entry(borrow_frame, width=30, style="Rounded.TEntry")
        self.borrow_entry.grid(row=0, column=1, padx=5, pady=5)
        borrow_btn = self._styled_button(borrow_frame, "Borrow", self.borrow_book)
        borrow_btn.grid(row=0, column=2, padx=5)
        self.add_hover_effect(borrow_btn)

        # Return Section
        return_frame = tk.LabelFrame(root, text="📗 Return Book", padx=10, pady=10,
                                     bg="#ffffff", fg="#003366", font=("Arial", 10, "bold"))
        return_frame.pack(padx=15, pady=10, fill="x")

        tk.Label(return_frame, text="Book Name:", bg="#ffffff").grid(row=0, column=0, padx=5, pady=5)
        self.return_entry = ttk.Entry(return_frame, width=30, style="Rounded.TEntry")
        self.return_entry.grid(row=0, column=1, padx=5, pady=5)
        return_btn = self._styled_button(return_frame, "Return", self.return_book)
        return_btn.grid(row=0, column=2, padx=5)
        self.add_hover_effect(return_btn)

        # Book Lists Section
        list_frame = tk.LabelFrame(root, text="📋 Book Lists", padx=10, pady=10,
                                   bg="#ffffff", fg="#003366", font=("Arial", 10, "bold"))
        list_frame.pack(padx=15, pady=10, fill="both", expand=True)

        btn1 = self._styled_button(list_frame, "Show Borrowed Books", self.display_borrowed_books)
        btn1.grid(row=0, column=0, pady=5)
        self.add_hover_effect(btn1)

        btn2 = self._styled_button(list_frame, "Show Returned Books", self.display_returned_books)
        btn2.grid(row=0, column=1, pady=5)
        self.add_hover_effect(btn2)

        btn3 = self._styled_button(list_frame, "Undo Last Action", self.undo_last_action)
        btn3.grid(row=0, column=2, pady=5)
        self.add_hover_effect(btn3)

        self.listbox = tk.Listbox(list_frame, height=15, width=65, bg="#f7fbff", font=("Courier New", 10))
        self.listbox.grid(row=1, column=0, columnspan=3, pady=10)

        # Search Section
        search_frame = tk.LabelFrame(root, text="🔎 Search Book", padx=10, pady=10,
                                     bg="#ffffff", fg="#003366", font=("Arial", 10, "bold"))
        search_frame.pack(padx=15, pady=10, fill="x")

        search_btn = self._styled_button(search_frame, "Search Book Status", self.search_book_status)
        search_btn.pack(pady= 0)
        self.add_hover_effect(search_btn)

        # Status Bar
        self.status_var = tk.StringVar()
        self.status_var.set("Welcome to the Library!")
        status_bar = tk.Label(root, textvariable=self.status_var, bd=1, relief="sunken",
                              anchor="w", bg="#cce6ff", fg="#003366", font=("Arial", 9))
        status_bar.pack(side="bottom", fill="x")

        style = ttk.Style()
        style.configure("Rounded.TEntry", padding=5, relief="flat", borderwidth=5)

    def _styled_button(self, parent, text, command):
        btn = tk.Button(parent, text=text, command=command, font=("Arial", 9, "bold"),
                        bg="#3399ff", fg="white", activebackground="#006bb3", activeforeground="white",
                        relief="raised", bd=2, padx=10, pady=2, cursor="hand2")
        return btn

    def add_hover_effect(self, widget):
        widget.bind("<Enter>", lambda e: widget.config(bg="#66b3ff"))
        widget.bind("<Leave>", lambda e: widget.config(bg="#3399ff"))

    def borrow_book(self):
        book = self.borrow_entry.get().strip().title()
        if not book:
            messagebox.showwarning("Input Error", "Please enter a book name.")
            return
        if self.book_status.get(book) == "Borrowed":
            messagebox.showwarning("Unavailable", f"'{book}' is already borrowed.")
            return
        self.borrowed_books.append(book)
        self.book_status[book] = "Borrowed"
        self.cursor.execute("INSERT OR REPLACE INTO books (name, status) VALUES (?, ?)", (book, "Borrowed"))
        self.conn.commit()

        self.last_action_stack.append(("borrow", book))
        self.borrow_entry.delete(0, tk.END)
        self.status_var.set(f"'{book}' has been borrowed.")
        messagebox.showinfo("Success", f"'{book}' has been borrowed.")

    def return_book(self):
        book = self.return_entry.get().strip().title()
        if not book:
            messagebox.showwarning("Input Error", "Please enter a book name.")
            return
        if self.book_status.get(book) != "Borrowed":
            messagebox.showwarning("Invalid", f"'{book}' is not marked as borrowed.")
            return
        self.returned_books.append(book)
        self.book_status[book] = "Available"
        self.cursor.execute("UPDATE books SET status = ? WHERE name = ?", ("Available", book))
        self.conn.commit()

        self.last_action_stack.append(("return", book))
        self.return_entry.delete(0, tk.END)
        self.status_var.set(f"'{book}' has been returned.")
        messagebox.showinfo("Success", f"'{book}' has been returned.")

    def display_borrowed_books(self):
        self.listbox.delete(0, tk.END)
        if self.borrowed_books:
            # Sort the list of borrowed books using QuickSort
            self.borrowed_books = self.quick_sort(self.borrowed_books)
            for book in self.borrowed_books:
                self.listbox.insert(tk.END, f"📕 {book} (Borrowed)")
        else:
            self.listbox.insert(tk.END, "No borrowed books.")
        self.status_var.set("Showing borrowed books.")

    def display_returned_books(self):
        self.listbox.delete(0, tk.END)
        if self.returned_books:
            # Sort the list of returned books using QuickSort
            self.returned_books = self.quick_sort(self.returned_books)
            for book in self.returned_books:
                self.listbox.insert(tk.END, f"📗 {book} (Returned)")
        else:
            self.listbox.insert(tk.END, "No returned books.")
        self.status_var.set("Showing returned books.")

    def undo_last_action(self):
        if not self.last_action_stack:
            messagebox.showinfo("Undo", "No actions to undo.")
            return
        action, book = self.last_action_stack.pop()
        if action == "borrow" and book in self.borrowed_books:
            self.borrowed_books.remove(book)
            self.book_status.pop(book, None)
            self.cursor.execute("DELETE FROM books WHERE name = ?", (book,))
            self.conn.commit()
            self.status_var.set(f"Undo: Borrowing of '{book}' removed.")
            messagebox.showinfo("Undo", f"Undid borrowing of '{book}'.")
        elif action == "return" and book in self.returned_books:
            self.returned_books.remove(book)
            self.book_status[book] = "Borrowed"
            self.cursor.execute("UPDATE books SET status = ? WHERE name = ?", ("Borrowed", book))
            self.conn.commit()
            self.status_var.set(f"Undo: Returning of '{book}' removed.")
            messagebox.showinfo("Undo", f"Undid return of '{book}'.")
        else:
            messagebox.showwarning("Undo Error", "No previous actions to undo.")

    def search_book_status(self):
        book = simpledialog.askstring("Search", "Enter book name to search:")
        if not book:
            return
        book = book.strip().title()
        status = self.book_status.get(book, "Not Found")
        messagebox.showinfo("Book Status", f"The status of '{book}' is: {status}")

    def quick_sort(self, books):
        if len(books) <= 1:
            return books
        pivot = books[len(books) // 2]
        left = [book for book in books if book < pivot]
        middle = [book for book in books if book == pivot]
        right = [book for book in books if book > pivot]
        return self.quick_sort(left) + middle + self.quick_sort(right)

    def load_books_from_db(self):
        self.cursor.execute("SELECT name, status FROM books")
        rows = self.cursor.fetchall()
        for row in rows:
            book_name, status = row
            if status == "Borrowed":
                self.borrowed_books.append(book_name)
            else:
                self.returned_books.append(book_name)
            self.book_status[book_name] = status

# Running the program
root = tk.Tk()
library_system = LibraryManagementSystem(root)
root.mainloop()

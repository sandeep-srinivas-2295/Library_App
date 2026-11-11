import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'super_secret_key_for_flash_messages'

def get_db_connection():
    conn = sqlite3.connect('library.db')
    conn.row_factory = sqlite3.Row  # Enables column access by name
    return conn

@app.route('/')
def index():
    search_query = request.args.get('search', '').strip()
    conn = get_db_connection()
    
    if search_query:
        books = conn.execute(
            "SELECT * FROM books WHERE title LIKE ? OR author LIKE ? OR isbn LIKE ?",
            (f'%{search_query}%', f'%{search_query}%', f'%{search_query}%')
        ).fetchall()
    else:
        books = conn.execute("SELECT * FROM books").fetchall()
        
    conn.close()
    return render_template('index.html', books=books, search_query=search_query)

@app.route('/add', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        title = request.form['title'].strip()
        author = request.form['author'].strip()
        isbn = request.form['isbn'].strip()

        if not title or not author or not isbn:
            flash('All fields are required!', 'danger')
            return redirect(url_for('add_book'))

        conn = get_db_connection()
        try:
            conn.execute(
                "INSERT INTO books (title, author, isbn, status) VALUES (?, ?, ?, 'Available')",
                (title, author, isbn)
            )
            conn.commit()
            flash('Book added successfully!', 'success')
            return redirect(url_for('index'))
        except sqlite3.IntegrityError:
            flash('Error: Book with this ISBN already exists.', 'danger')
        finally:
            conn.close()

    return render_template('add_book.html')

@app.route('/issue/<int:book_id>', methods=['POST'])
def issue_book(book_id):
    issued_to = request.form.get('issued_to', '').strip()
    if not issued_to:
        flash('Borrower name is required to issue a book.', 'danger')
        return redirect(url_for('index'))

    conn = get_db_connection()
    conn.execute(
        "UPDATE books SET status = 'Issued', issued_to = ? WHERE id = ?",
        (issued_to, book_id)
    )
    conn.commit()
    conn.close()
    flash('Book issued successfully.', 'info')
    return redirect(url_for('index'))

@app.route('/return/<int:book_id>', methods=['POST'])
def return_book(book_id):
    conn = get_db_connection()
    conn.execute(
        "UPDATE books SET status = 'Available', issued_to = NULL WHERE id = ?",
        (book_id,)
    )
    conn.commit()
    conn.close()
    flash('Book returned successfully.', 'success')
    return redirect(url_for('index'))

@app.route('/delete/<int:book_id>', methods=['POST'])
def delete_book(book_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM books WHERE id = ?", (book_id,))
    conn.commit()
    conn.close()
    flash('Book record deleted.', 'warning')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
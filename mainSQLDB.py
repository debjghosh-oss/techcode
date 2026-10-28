
from pathlib import Path
import sqlite3

from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel

app = FastAPI(title="Book Management API")

# Store the database beside this Python file.
DB_PATH = Path(__file__).with_name("books.db")


class BookCreate(BaseModel):
    title: str
    author: str


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL
            )
        """)

        # Add starter books only when the table is empty.
        count = conn.execute(
            "SELECT COUNT(*) FROM books"
        ).fetchone()[0]

        if count == 0:
            conn.executemany(
                "INSERT INTO books (title, author) VALUES (?, ?)",
                [
                    ("Clean Code", "Robert Martin"),
                    ("Atomic Habits", "James Clear"),
                ],
            )


initialize_database()


@app.get("/")
def home():
    return {"message": "My first API is running!"}


@app.get("/books")
def get_books():
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, title, author FROM books ORDER BY id"
        ).fetchall()

        return [dict(row) for row in rows]


@app.get("/books/{book_id}")
def get_book(book_id: int):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT id, title, author FROM books WHERE id = ?",
            (book_id,),
        ).fetchone()

        if row is None:
            raise HTTPException(
                status_code=404, detail="Book not found"
            )

        return dict(row)


@app.post("/books", status_code=201)
def create_book(book: BookCreate):
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO books (title, author) VALUES (?, ?)",
            (book.title, book.author),
        )

        new_id = cursor.lastrowid

        row = conn.execute(
            "SELECT id, title, author FROM books WHERE id = ?",
            (new_id,),
        ).fetchone()

        return dict(row)


@app.put("/books/{book_id}")
def update_book(book_id: int, book: BookCreate):
    with get_connection() as conn:
        cursor = conn.execute(
            "UPDATE books SET title = ?, author = ? WHERE id = ?",
            (book.title, book.author, book_id),
        )

        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=404, detail="Book not found"
            )

        row = conn.execute(
            "SELECT id, title, author FROM books WHERE id = ?",
            (book_id,),
        ).fetchone()

        return dict(row)


@app.delete("/books/{book_id}", status_code=204)
def delete_book(book_id: int):
    with get_connection() as conn:
        cursor = conn.execute(
            "DELETE FROM books WHERE id = ?",
            (book_id,),
        )

        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=404, detail="Book not found"
            )

    return Response(status_code=204)

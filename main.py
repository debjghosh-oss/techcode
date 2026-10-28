
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()


class BookCreate(BaseModel):
    title: str
    author: str


books = [
    {"id": 1, "title": "Clean Code", "author": "Robert Martin"},
    {"id": 2, "title": "Atomic Habits", "author": "James Clear"}
]


@app.get("/")
def home():
    return {"message": "My first API is running!"}


@app.get("/books")
def get_books():
    return books


@app.get("/books/{book_id}")
def get_book(book_id: int):
    for book in books:
        if book["id"] == book_id:
            return book

    from fastapi import HTTPException
    raise HTTPException(status_code=404, detail="Book not found")



@app.post("/books", status_code=201)
def create_book(book: BookCreate):
    new_id = max((b["id"] for b in books), default=0) + 1

    new_book = {
        "id": new_id,
        "title": book.title,
        "author": book.author
    }

    books.append(new_book)
    return new_book




@app.put("/books/{book_id}")
def update_book(book_id: int, updated_book: BookCreate):
    for book in books:
        if book["id"] == book_id:
            book["title"] = updated_book.title
            book["author"] = updated_book.author
            return book

    raise HTTPException(status_code=404, detail="Book not found")


@app.delete("/books/{book_id}", status_code=204)
def delete_book(book_id: int):
    for index, book in enumerate(books):
        if book["id"] == book_id:
            books.pop(index)
            return

    raise HTTPException(status_code=404, detail="Book not found")
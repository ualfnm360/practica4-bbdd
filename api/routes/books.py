from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from database import get_db
import mysql.connector

router = APIRouter()

# --- MODELOS PYDANTIC PARA VALIDAR EL JSON DE ENTRADA ---
class BookCreate(BaseModel):
    title: str
    author: str
    publisher: str
    year: int
    category: str

class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    publisher: Optional[str] = None
    year: Optional[int] = None
    category: Optional[str] = None

# --- ENDPOINTS ---

@router.get("/", status_code=status.HTTP_200_OK)
def get_books(db = Depends(get_db)):
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Libro")
    books = cursor.fetchall()
    cursor.close()
    
    # Mapeamos los campos de la BD al formato JSON en inglés que pide la práctica
    return [{
        "id": b["id"],
        "title": b["titulo"],
        "author": b["autor"],
        "publisher": b["editorial"],
        "year": b["publicadoEn"],
        "category": b["categoria"]
    } for b in books]

@router.get("/{id}", status_code=status.HTTP_200_OK)
def get_book(id: int, db = Depends(get_db)):
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Libro WHERE id = %s", (id,))
    book = cursor.fetchone()
    cursor.close()
    
    if not book:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
        
    return {
        "id": book["id"],
        "title": book["titulo"],
        "author": book["autor"],
        "publisher": book["editorial"],
        "year": book["publicadoEn"],
        "category": book["categoria"]
    }

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_book(book: BookCreate, db = Depends(get_db)):
    cursor = db.cursor()
    query = "INSERT INTO Libro (titulo, autor, editorial, publicadoEn, categoria) VALUES (%s, %s, %s, %s, %s)"
    cursor.execute(query, (book.title, book.author, book.publisher, book.year, book.category))
    db.commit()
    new_id = cursor.lastrowid
    cursor.close()
    
    return {**book.model_dump(), "id": new_id}

@router.put("/{id}", status_code=status.HTTP_200_OK)
def update_book(id: int, book: BookUpdate, db = Depends(get_db)):
    cursor = db.cursor()
    update_data = book.model_dump(exclude_unset=True)
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No hay campos para actualizar")
        
    # Diccionario para mapear del inglés (API) al español (BD)
    field_mapping = {
        "title": "titulo", "author": "autor", 
        "publisher": "editorial", "year": "publicadoEn", "category": "categoria"
    }
    
    set_clauses = []
    values = []
    for key, value in update_data.items():
        set_clauses.append(f"{field_mapping[key]} = %s")
        values.append(value)
        
    values.append(id)
    query = f"UPDATE Libro SET {', '.join(set_clauses)} WHERE id = %s"
    
    cursor.execute(query, tuple(values))
    db.commit()
    
    if cursor.rowcount == 0:
        cursor.close()
        raise HTTPException(status_code=404, detail="Libro no encontrado o sin cambios")
        
    cursor.close()
    return {"message": "Libro actualizado correctamente"}

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(id: int, db = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("DELETE FROM Libro WHERE id = %s", (id,))
    db.commit()
    
    if cursor.rowcount == 0:
        cursor.close()
        raise HTTPException(status_code=404, detail="Libro no encontrado")
        
    cursor.close()
    return None
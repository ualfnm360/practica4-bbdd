from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from database import get_db
import mysql.connector

router = APIRouter()

class LoanRequest(BaseModel):
    userId: int
    inventoryNumber: str

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_loan(req: LoanRequest, db = Depends(get_db)):
    cursor = db.cursor()
    try:
        # Llamamos al procedimiento de la Práctica 3
        cursor.callproc('RealizarPrestamo', [req.userId, req.inventoryNumber])
        db.commit()
        return {"message": "Préstamo realizado con éxito"}
    except mysql.connector.Error as err:
        db.rollback()
        # Si el procedure lanza un error (ej. usuario sancionado), lo enviamos al cliente
        raise HTTPException(status_code=400, detail=str(err.msg))
    finally:
        cursor.close()

@router.post("/return", status_code=status.HTTP_200_OK)
def return_loan(req: LoanRequest, db = Depends(get_db)):
    cursor = db.cursor()
    try:
        # Llamamos al procedimiento de la Práctica 3
        cursor.callproc('DevolverLibro', [req.userId, req.inventoryNumber])
        db.commit()
        return {"message": "Devolución realizada con éxito"}
    except mysql.connector.Error as err:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(err.msg))
    finally:
        cursor.close()
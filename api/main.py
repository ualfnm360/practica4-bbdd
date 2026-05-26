from fastapi import FastAPI
from routes import base, books, loans

# Initialize FastAPI app
app = FastAPI(
    title="Products API",
    description="API for managing products using FastAPI and MySQL",
    version="1.0.0"
)

# Registramos las rutas
app.include_router(base.router)
app.include_router(books.router, prefix="/books", tags=["Books"])
app.include_router(loans.router, prefix="/loans", tags=["Loans"])
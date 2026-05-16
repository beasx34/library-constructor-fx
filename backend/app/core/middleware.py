import os
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from .config import settings
from ..api.v2 import (
    exhibitions_router,
    sections_router,
    contents_router,
    users_router,
    admins_router,
    library_books_router,
    books_router,
)

origins = [
    "http://localhost:3000",
    "http://26.0.197.27:3000",
    "https://rapidstream.ru",
    "https://www.rapidstream.ru",
    "https://192.168.0.101:3000"
]

# Дополнительные origins, передаваемые через переменную окружения
# ALLOWED_ORIGINS (через запятую). Удобно для GitHub Codespaces,
# где публичный URL фронтенда зависит от имени codespace.
_extra = os.getenv("ALLOWED_ORIGINS", "")
if _extra:
    origins.extend(o.strip() for o in _extra.split(",") if o.strip())

def setup_middleware(app):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    # Затем SessionMiddlew``are
    app.add_middleware(
        SessionMiddleware, 
        secret_key=settings.SECRET_KEY,
        session_cookie="session", 
        https_only=True,       
        same_site="none",        
    )
    # app.add_middleware(
    #     SessionMiddleware, 
    #     secret_key=settings.SECRET_KEY,
    #     session_cookie="session", 
    #     https_only=True,       
    #     same_site="none",        
    #     )
    
    
    
    # Подключаем роутеры
    app.include_router(exhibitions_router, prefix="/v2", tags=["Выставка"])
    app.include_router(sections_router, prefix="/v2", tags=["Разделы"])
    app.include_router(contents_router, prefix="/v2", tags=["Контент"])
    app.include_router(library_books_router, prefix="/v2/library", tags=["Книги"])
    app.include_router(books_router, prefix="/v2", tags=["Книги для раздела"])
    app.include_router(users_router, prefix="/users", tags=["Пользователи"])
    app.include_router(admins_router, prefix="/admin", tags=["Админ"])
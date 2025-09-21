from pathlib import Path
import re
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .db import init_db, get_conn

BASE_DIR = Path(__file__).resolve().parent.parent
app = FastAPI()
app.mount(
    "/static", 
    StaticFiles(directory=str(BASE_DIR / "static")), name="static"
)

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# Simple email shape check Pydantic EmailStr later
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/", response_class=HTMLResponse)
def home(request: Request, success: str | None = None, error: str | None = None):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "success": success, "error": error, "page": "home"},
    )

    

@app.get("/contact", response_class=HTMLResponse)
def contact(request: Request):
    return templates.TemplateResponse(
        "contact.html",
        {"request": request, "page": "contact"},    
    )

@app.get("/engage", response_class=HTMLResponse)
def engage(request: Request):
    return templates.TemplateResponse(
        "engage.html",
        {"request": request, "page": "engage"},
    )

@app.get("/partners", response_class=HTMLResponse)
def partners(request: Request):
    partners = [
        {"name":"Kyle Keane","org":"Example University","logo_url":"/static/logos/exu.svg",
         "photo_url":"/static/people/kyle.jpg","description":"Accessible tech researcher","url":"#"}
    ]
    return templates.TemplateResponse(
        "partners.html",
        {"request": request, "page": "partners", "partners": partners},
    )

@app.post("/register")
def register(
    full_name: str = Form(...),
    email: str = Form(...),
    year_of_study: int = Form(...),
    course_name: str = Form(...)
):
    # Minimal validations make more robust later
    if len(full_name.strip()) < 2:
        return RedirectResponse("/?error=Name%20too%20short", status_code=303)
    if not EMAIL_RE.match(email):
        return RedirectResponse("/?error=Invalid%20email", status_code=303)
    if year_of_study < 1 or year_of_study > 10:
        return RedirectResponse("/?error=Year%20of%20study%20invalid", status_code=303)
    if len(course_name.strip()) < 2:
        return RedirectResponse("/?error=Course%20name%20too%20short", status_code=303)

    email_norm = email.strip().lower()
    full_name_norm = full_name.strip()
    course_name_norm = course_name.strip()

    with get_conn() as conn:
        cur = conn.cursor()
        is_pg = hasattr(cur, "mogrify")  # crude psycopg2 detection
        # Optional: pre-check to avoid relying on exception for duplicates
        try:
            if is_pg:
                cur.execute("SELECT 1 FROM registrations WHERE email = %s", (email_norm,))
            else:
                cur.execute("SELECT 1 FROM registrations WHERE email = ?", (email_norm,))
            if cur.fetchone():
                return RedirectResponse("/?error=Email%20already%20registered", status_code=303)
            # Insert with the correct placeholder style
            if is_pg:
                cur.execute(
                    "INSERT INTO registrations (full_name, email, year_of_study, course_name) VALUES (%s, %s, %s, %s)",
                    (full_name_norm, email_norm, int(year_of_study), course_name_norm)
                )
            else:
                cur.execute(
                    "INSERT INTO registrations (full_name, email, year_of_study, course_name) VALUES (?, ?, ?, ?)",
                    (full_name_norm, email_norm, int(year_of_study), course_name_norm)
                )
            conn.commit()
            return RedirectResponse("/?success=Registration%20received", status_code=303)
        except Exception:
            # Fall back to duplicate error for any integrity issue; add logging if needed
            return RedirectResponse("/?error=Email%20already%20registered", status_code=303)

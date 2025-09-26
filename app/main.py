from pathlib import Path
import re
from fastapi import FastAPI, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Optional

from .db import init_db, get_conn

BASE_DIR = Path(__file__).resolve().parent.parent
app = FastAPI()
app.mount(
    "/static",
    StaticFiles(directory=str(BASE_DIR / "static")), name="static"
)

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# Simple email shape check Pydantic EmailStr later
EMAIL_RE = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/", response_class=HTMLResponse)
def home(request: Request, success: str | None = None, error: str | None = None):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "success": success, "error": error, "page": "home", "form_data": {}},
    )

@app.get("/events", response_class=HTMLResponse)
def events(request: Request):
    return templates.TemplateResponse(
        "events.html",
        {"request": request, "page": "events"},
    )

@app.get("/partners", response_class=HTMLResponse)
def partners(request: Request):
    partners = [
        {
            "name": "Kyle Keane",
            "org": "University of Bristol",
            "logo_url": "https://jobs.opensafely.org/uploads/org_logos/uob.png",
            "photo_url": "https://media.licdn.com/dms/image/v2/D4E03AQFDCm-L1a8u1g/profile-displayphoto-shrink_800_800/profile-displayphoto-shrink_800_800/0/1730579720100?e=1761782400&v=beta&t=rWOBMlsEk34b70TVaASj6yoQFe0IXbiesIkhmtkcDTI",
            "description": "Accessible tech researcher",
            "url": "https://www.bristol.ac.uk/people/person/Kyle-Keane-3b30cecb-458f-429d-9686-1a6ef5bc6518/"
        }
    ]
    return templates.TemplateResponse(
        "partners.html",
        {"request": request, "page": "partners", "partners": partners},
    )

@app.post("/register")
def register(
    request: Request,
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...),
    is_student: Optional[str] = Form(None),
    year_of_study: Optional[str] = Form(None), # Accept as string
    course_name: Optional[str] = Form(None),
    additional_info: Optional[str] = Form(None)
):
    # Minimal validations make more robust later
    if len(first_name.strip()) < 1:
        return RedirectResponse("/?error=First%20name%20is%20required", status_code=303)
    if len(last_name.strip()) < 1:
        return RedirectResponse("/?error=Last%20name%20is%20required", status_code=303)
    if not EMAIL_RE.match(email):
        return RedirectResponse("/?error=Invalid%20email", status_code=303)

    year_of_study_int = None
    if is_student:
        if not year_of_study or not year_of_study.isdigit():
            return RedirectResponse("/?error=Valid%20year%20of%20study%20is%20required%20for%20students", status_code=303)
        year_of_study_int = int(year_of_study)
        if year_of_study_int < 1 or year_of_study_int > 10:
             return RedirectResponse("/?error=Year%20of%20study%20invalid", status_code=303)
        if not course_name or len(course_name.strip()) < 2:
            return RedirectResponse("/?error=Course%20name%20is%20required%20for%20students", status_code=303)


    email_norm = email.strip().lower()
    first_name_norm = first_name.strip()
    last_name_norm = last_name.strip()
    course_name_norm = course_name.strip() if course_name else None
    additional_info_norm = additional_info.strip() if additional_info else None

    with get_conn() as conn:
        cur = conn.cursor()
        is_pg = hasattr(cur, "mogrify")  # crude psycopg2 detection
        
        # Check for duplicate email
        if is_pg:
            cur.execute("SELECT 1 FROM registrations WHERE email = %s", (email_norm,))
        else:
            cur.execute("SELECT 1 FROM registrations WHERE email = ?", (email_norm,))
        
        if cur.fetchone():
            form_data = {
                "first_name": first_name_norm,
                "last_name": last_name_norm,
                "email": email_norm,
                "is_student": is_student,
                "year_of_study": year_of_study,
                "course_name": course_name_norm,
                "additional_info": additional_info_norm
            }
            return templates.TemplateResponse(
                "index.html",
                {
                    "request": request,
                    "error": "Email already registered",
                    "form_data": form_data,
                    "page": "home"
                },
            )
        # Insert with the correct placeholder style
        try:
            if is_pg:
                cur.execute(
                    """
                    INSERT INTO registrations (first_name, last_name, email, year_of_study, course_name, additional_info)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (first_name_norm, last_name_norm, email_norm, year_of_study_int, course_name_norm, additional_info_norm)
                )
            else:
                cur.execute(
                    """
                    INSERT INTO registrations (first_name, last_name, email, year_of_study, course_name, additional_info)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (first_name_norm, last_name_norm, email_norm, year_of_study_int, course_name_norm, additional_info_norm)
                )
            conn.commit()
            return RedirectResponse("/?success=Registration%20received", status_code=303)
        except Exception as e:
            # Fall back to duplicate error for any integrity issue; add logging if needed
            print(e)
            return RedirectResponse("/?error=Email%20already%20registered", status_code=303)
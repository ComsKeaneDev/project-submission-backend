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

@app.get("/schedule", response_class=HTMLResponse)
def schedule(request: Request):
    return templates.TemplateResponse(
        "schedule.html",
        {"request": request, "page": "schedule"},
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

@app.get("/philosophy", response_class=HTMLResponse)
def philosophy(request: Request):
    return templates.TemplateResponse(
        "philosophy.html",
        {"request": request, "page": "philosophy"},
    )

@app.get("/resources", response_class=HTMLResponse)
def resources(request: Request):
    return templates.TemplateResponse(
        "resources.html",
        {"request": request, "page": "resources"},
    )

@app.get("/privacy", response_class=HTMLResponse)
def privacy(request: Request):
    return templates.TemplateResponse(
        "privacy.html",
        {"request": request, "page": "privacy"}
    )

@app.get("/confirmation", response_class=HTMLResponse)
def confirmation(request: Request):
    return templates.TemplateResponse(
        "confirmation.html",
        {"request": request, "page": "confirmation"}
    )

@app.post("/register")
def register(
    request: Request,
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...),
    is_student: Optional[str] = Form(None),
    year_of_study: Optional[str] = Form(None),
    course_name: Optional[str] = Form(None),
    additional_info: Optional[str] = Form(None),
    mailing_list_consent: Optional[str] = Form(None),
    gdpr_consent: Optional[str] = Form(None)
):
    # This is the server-side check
    if not gdpr_consent:
        form_data = {
            "first_name": first_name, "last_name": last_name, "email": email,
            "is_student": is_student, "year_of_study": year_of_study,
            "course_name": course_name, "additional_info": additional_info,
            "mailing_list_consent": mailing_list_consent
        }
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "error": "You must agree to the terms to register.", "form_data": form_data, "page": "home"}
        )

    if not EMAIL_RE.match(email):
        return RedirectResponse("/?error=Invalid%20email", status_code=303)

    year_of_study_int = None
    if is_student:
        if not year_of_study or not year_of_study.isdigit():
            return RedirectResponse("/?error=Valid%20year%20of%20study%20is%20required%20for%20students", status_code=303)
        year_of_study_int = int(year_of_study)

    email_norm = email.strip().lower()
    first_name_norm = first_name.strip()
    last_name_norm = last_name.strip()
    course_name_norm = course_name.strip() if course_name else None
    additional_info_norm = additional_info.strip() if additional_info else None
    mailing_list_bool = True if mailing_list_consent else False

    with get_conn() as conn:
        cur = conn.cursor()
        is_pg = hasattr(cur, "mogrify")

        query = "SELECT 1 FROM registrations WHERE email = %s" if is_pg else "SELECT 1 FROM registrations WHERE email = ?"
        cur.execute(query, (email_norm,))

        if cur.fetchone():
            form_data = { "first_name": first_name_norm, "last_name": last_name_norm, "email": email_norm, "is_student": is_student, "year_of_study": year_of_study, "course_name": course_name_norm, "additional_info": additional_info_norm, "mailing_list_consent": mailing_list_consent }
            return templates.TemplateResponse("index.html", {"request": request, "error": "Email already registered", "form_data": form_data, "page": "home"})

        insert_query = "INSERT INTO registrations (first_name, last_name, email, year_of_study, course_name, additional_info, mailing_list_consent) VALUES (%s, %s, %s, %s, %s, %s, %s)" if is_pg else "INSERT INTO registrations (first_name, last_name, email, year_of_study, course_name, additional_info, mailing_list_consent) VALUES (?, ?, ?, ?, ?, ?, ?)"
        params = (first_name_norm, last_name_norm, email_norm, year_of_study_int, course_name_norm, additional_info_norm, mailing_list_bool)
        cur.execute(insert_query, params)
        conn.commit()

    return RedirectResponse(url="/confirmation", status_code=303)
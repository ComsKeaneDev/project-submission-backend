from pathlib import Path
import re
from fastapi import FastAPI, Request, Form, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
import time

from .db import init_db, get_conn

BASE_DIR = Path(__file__).resolve().parent.parent
app = FastAPI()
app.mount(
    "/static",
    StaticFiles(directory=str(BASE_DIR / "static")), name="static"
)

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# --- CORRECTED CODE: Dependency to inject common context ---
def get_context(request: Request):
    """
    Returns a dictionary with common context variables for templates.
    """
    return {
        "request": request,
        "timestamp": int(time.time())
    }

EMAIL_RE = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/", response_class=HTMLResponse)
def home(context: dict = Depends(get_context), success: str | None = None, error: str | None = None):
    context.update(success=success, error=error, page="home", form_data={})
    return templates.TemplateResponse("index.html", context)

@app.get("/schedule", response_class=HTMLResponse)
def schedule(context: dict = Depends(get_context)):
    context.update(page="schedule")
    return templates.TemplateResponse("schedule.html", context)

@app.get("/partners", response_class=HTMLResponse)
def partners(context: dict = Depends(get_context)):
    uob_logo_url = "https://jobs.opensafely.org/uploads/org_logos/uob.png"
    uob_alt_text = "University of Bristol logo with the university crest and name."
    
    organisers = [
        {
            "name": "Kyle Keane",
            "org": "University of Bristol",
            "logo_url": uob_logo_url,
            "org_logo_alt": uob_alt_text,
            "photo_url": "https://media.licdn.com/dms/image/v2/D4E03AQFDCm-L1a8u1g/profile-displayphoto-shrink_800_800/profile-displayphoto-shrink_800_800/0/1730579720100?e=1761782400&v=beta&t=rWOBMlsEk34b70TVaASj6yoQFe0IXbiesIkhmtkcDTI",
            "description": "Accessible tech researcher",
            "url": "https://www.bristol.ac.uk/people/person/Kyle-Keane-3b30cecb-458f-429d-9686-1a6ef5bc6518/"
        },
        {
            "name": "Dixant Pant",
            "org": "University of Bristol",
            "logo_url": uob_logo_url,
            "org_logo_alt": uob_alt_text,
            "photo_url": "https://media.licdn.com/dms/image/v2/D4E03AQGiw1BQAsaPMg/profile-displayphoto-shrink_400_400/profile-displayphoto-shrink_400_400/0/1686739668271?e=1762992000&v=beta&t=_8gWbv3jr5L05P7mdcr9uZW0tOFGyMSPWgjBsXTL5mA",
            "description": "Final year Computer Science BS student",
            "url": "https://www.linkedin.com/in/dixant/"
        }
    ]
    sponsors = [
        {
            "name": "GitHub",
            "org": "Sponsor",
            "logo_url": "https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png",
            "alt_text": "The GitHub logo, showing the white 'Octocat' silhouette.",
            "url": "https://github.com",
            "description": "Title sponsor and keynote speaker."
        },
        {
            "name": "Smartbox",
            "org": "Sponsor",
            "logo_url": "https://media.licdn.com/dms/image/v2/C4D0BAQG9jNesP_Vllw/company-logo_200_200/company-logo_200_200/0/1630559422052?e=1762992000&v=beta&t=HDKahCosh2w-bBFuOkuvKf1wfu-8382hIwU-9LU3aGI",
            "alt_text": "Smartbox logo, a colorful speech bubble with the company name.",
            "url": "https://thinksmartbox.com",
            "description": "Providing expertise in assistive technology and technical mentors"
        },
        {
            "name": "University of Bristol",
            "org": "Sponsor",
            "logo_url": uob_logo_url,
            "alt_text": uob_alt_text,
            "url": "https://www.bristol.ac.uk"
        },
    ]
    partners_list = [
        {
            "name": "Senmag Robotics",
            "org": "Partner",
            "logo_url": "https://media.licdn.com/dms/image/v2/C4E0BAQGFXir39Y3TCw/company-logo_200_200/company-logo_200_200/0/1630636150687?e=2147483647&v=beta&t=Hy27NFKr_fxl9lCYJZJlgH_LVfvCo6fkctUkeIyU6nM",
            "alt_text": "Senmag Robotics logo, a stylized orange 'S' with a circle.",
            "url": "https://senmag-haptics.com",
            "description": "Providing expertise in assistive technology and technical mentors"
        },
        {
            "name": "Microsoft Inclusive Tech Lab",
            "org": "Partner",
            "logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Microsoft_logo.svg/2048px-Microsoft_logo.svg.png",
            "alt_text": "Microsoft logo, showing four colored squares: red, green, blue, and yellow.",
            "url": "https://www.microsoft.com/en-us/inclusive-tech-lab",
            "description": "Providing expertise in assistive technology and technical mentors"
        },
        {
            "name": "Hodr",
            "org": "Partner",
            "logo_url": "/static/HodrEngineLogo.jpeg",
            "alt_text": "Hodr Engine logo with a blue, rune-like H edged in gold, framed by two gold arrows. The top arrow points right and the bottom points left, set on a dark blue background.",
            "url": "#",
            "description": "Providing expertise in assistive technology and technical mentors"
        },
        {
            "name": "Red Nought",
            "org": "Partner",
            "logo_url": "/static/RedNoughtLogo.jpeg",
            "alt_text": "Red Nought logo with a black robot silhouette against four red vertical bars, over the text 'RED NOUGHT' in white and redd.",
            "url": "#",
            "description": "Providing expertise in assistive technology and technical mentors"
        },
        {
            "name": "Immersion Sound Studio",
            "org": "Partner",
            "logo_url": "https://static.wixstatic.com/media/20c75c_60100a7be2904c6498a72b7f32957b4f~mv2.png/v1/fill/w_284,h_118,al_c,q_85,usm_0.66_1.00_0.01,enc_auto/Immersion%20Sound%20Studio%20Logo%20White%20Text.png",
            "alt_text": "Immersion Sound Studio logo placeholder",
            "url": "https://www.facebook.com/immersionsoundstudio/",
            "description": "Providing expertise in assistive technology and technical mentors"
        }
    ]
    context.update(page="partners", organisers=organisers, sponsors=sponsors, partners=partners_list)
    return templates.TemplateResponse("partners.html", context)

@app.get("/approach", response_class=HTMLResponse)
def approach(context: dict = Depends(get_context)):
    context.update(page="approach")
    return templates.TemplateResponse("approach.html", context)

@app.get("/what-to-expect", response_class=HTMLResponse)
def what_to_expect(context: dict = Depends(get_context)):
    context.update(page="what-to-expect")
    return templates.TemplateResponse("what-to-expect.html", context)

@app.get("/faq", response_class=HTMLResponse)
def faq(context: dict = Depends(get_context)):
    context.update(page="faq")
    return templates.TemplateResponse("faq.html", context)

@app.get("/privacy", response_class=HTMLResponse)
def privacy(context: dict = Depends(get_context)):
    context.update(page="privacy")
    return templates.TemplateResponse("privacy.html", context)

@app.get("/confirmation", response_class=HTMLResponse)
def confirmation(context: dict = Depends(get_context)):
    context.update(page="confirmation")
    return templates.TemplateResponse("confirmation.html", context)

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
    if not gdpr_consent:
        form_data = {
            "first_name": first_name, "last_name": last_name, "email": email,
            "is_student": is_student, "year_of_study": year_of_study,
            "course_name": course_name, "additional_info": additional_info,
            "mailing_list_consent": mailing_list_consent
        }
        # Manually create the context for the error response
        context = {
            "request": request,
            "timestamp": int(time.time()),
            "error": "You must agree to the terms to register.",
            "form_data": form_data,
            "page": "home"
        }
        return templates.TemplateResponse("index.html", context)

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
            # Manually create context for the error response
            context = {
                "request": request,
                "timestamp": int(time.time()),
                "error": "Email already registered",
                "form_data": form_data,
                "page": "home"
            }
            return templates.TemplateResponse("index.html", context)

        insert_query = "INSERT INTO registrations (first_name, last_name, email, year_of_study, course_name, additional_info, mailing_list_consent) VALUES (%s, %s, %s, %s, %s, %s, %s)" if is_pg else "INSERT INTO registrations (first_name, last_name, email, year_of_study, course_name, additional_info, mailing_list_consent) VALUES (?, ?, ?, ?, ?, ?, ?)"
        params = (first_name_norm, last_name_norm, email_norm, year_of_study_int, course_name_norm, additional_info_norm, mailing_list_bool)
        cur.execute(insert_query, params)
        conn.commit()

    return RedirectResponse(url="/confirmation", status_code=303)
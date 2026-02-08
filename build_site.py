import os
from jinja2 import Environment, FileSystemLoader
import time

# --- CONFIGURATION ---
OUTPUT_DIR = "."  # Generate files in the current directory
TEMPLATE_DIR = "templates"

# --- DATA PREPARATION ---

uob_logo_url = "https://jobs.opensafely.org/uploads/org_logos/uob.png"
uob_alt_text = "University of Bristol logo with the university crest and name."

context_data = {
    "timestamp": int(time.time()),
    "organisers": [
        {
            "name": "Kyle Keane",
            "org": "University of Bristol",
            "logo_url": uob_logo_url,
            "org_logo_alt": uob_alt_text,
            "photo_url": "https://media.licdn.com/dms/image/v2/D4E03AQFDCm-L1a8u1g/profile-displayphoto-shrink_800_800/profile-displayphoto-shrink_800_800/0/1730579720100?e=1761782400&v=beta&t=rWOBMlsEk34b70TVaASj6yoQFe0IXbiesIkhmtkcDTI",
            "description": "Senior Lecturer in Assistive Technologies",
            "url": "https://www.bristol.ac.uk/people/person/Kyle-Keane-3b30cecb-458f-429d-9686-1a6ef5bc6518/"
        },
        {
            "name": "Dixant Pant",
            "org": "University of Bristol",
            "logo_url": uob_logo_url,
            "org_logo_alt": uob_alt_text,
            "photo_url": "https://media.licdn.com/dms/image/v2/D4E03AQGiw1BQAsaPMg/profile-displayphoto-shrink_400_400/profile-displayphoto-shrink_400_400/0/1686739668271?e=1762992000&v=beta&t=_8gWbv3jr5L05P7mdcr9uZW0tOFGyMSPWgjBsXTL5mA",
            "description": "Final Year Computer Science BSc Student",
            "url": "https://www.linkedin.com/in/dixant/"
        }
    ],
    "sponsors": [
        {
            "name": "GitHub",
            "org": "Sponsor",
            "logo_url": "https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png",
            "alt_text": "The GitHub logo, showing the white 'Octocat' silhouette.",
            "url": "https://github.com",
            "description": "Title sponsor and keynote speaker."
        },
        {
            "name": "CodeRabbit",
            "org": "Sponsor",
            "logo_url": "static/CodeRabbit.png",
            "alt_text": "CodeRabbit logo, an illustrated rabbit face wearing glasses.",
            "url": "https://www.coderabbit.ai/",
            "description": "Automated software audits and AI code suggestions."
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
        }
    ],
    "partners": [
        {
            "name": "Senmag Robotics",
            "org": "Partner",
            "logo_url": "https://media.licdn.com/dms/image/v2/C4E0BAQGFXir39Y3TCw/company-logo_200_200/company-logo_200_200/0/1630636150687?e=2147483647&v=beta&t=Hy27NFKr_fxl9lCYJZJlgH_LVfvCo6fkctUkeIyU6nM",
            "alt_text": "Senmag Robotics logo, a stylized 'S' with a circle.",
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
            "logo_url": "static/HodrEngineLogo.jpeg",
            "alt_text": "Hodr Engine logo.",
            "url": "https://www.hodrengine.com",
            "description": "Providing expertise in assistive technology and technical mentors"
        },
        {
            "name": "Red Nought",
            "org": "Partner",
            "logo_url": "static/RedNoughtLogo.jpeg",
            "alt_text": "Red Nought logo.",
            "url": "https://www.rednought.com",
            "description": "Providing expertise in assistive technology and technical mentors"
        },
        {
            "name": "EmpressVR",
            "org": "Partner",
            "logo_url": "static/EmpressVR.jpeg",
            "alt_text": "EmpressVR logo.",
            "url": "https://www.empressvr.com/",
            "description": "Providing expertise in assistive technology and technical mentors"
        }
    ]
}

# --- BUILD LOGIC ---

def url_for(endpoint, path):
    """Mock fastapi's url_for to return simple relative paths."""
    if endpoint == 'static':
        return f"static/{path}"
    return path

def build():
    # 1. Setup Jinja2 Environment
    file_loader = FileSystemLoader(TEMPLATE_DIR)
    env = Environment(loader=file_loader)
    env.globals['url_for'] = url_for  # Inject the mock function

    # 2. List of pages to render (REMOVED confirmation.html)
    pages = [
        {'template': 'index.html', 'output': 'index.html', 'page_name': 'home'},
        {'template': 'schedule.html', 'output': 'schedule.html', 'page_name': 'schedule'},
        {'template': 'partners.html', 'output': 'partners.html', 'page_name': 'partners'},
        {'template': 'approach.html', 'output': 'approach.html', 'page_name': 'approach'},
        {'template': 'what-to-expect.html', 'output': 'what-to-expect.html', 'page_name': 'what-to-expect'},
        {'template': 'faq.html', 'output': 'faq.html', 'page_name': 'faq'},
        {'template': 'privacy.html', 'output': 'privacy.html', 'page_name': 'privacy'},
        {'template': 'sponsorship.html', 'output': 'sponsorship.html', 'page_name': 'sponsorship'},
        {'template': 'outcomes.html', 'output': 'outcomes.html', 'page_name': 'outcomes'},
    ]

    print(f"🔨 Building site from '{TEMPLATE_DIR}'...")

    # 3. Render loop
    for page in pages:
        try:
            template = env.get_template(page['template'])
            
            # Combine global data with page-specific data
            render_context = context_data.copy()
            render_context['page'] = page['page_name']
            
            # Render content
            output_content = template.render(render_context)
            
            # Write to file
            output_path = os.path.join(OUTPUT_DIR, page['output'])
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(output_content)
            
            print(f"  ✅ Generated {page['output']}")
            
        except Exception as e:
            print(f"  ❌ Error generating {page['output']}: {e}")

    print("Build complete! Upload the .html files and 'static' folder to GitHub.")

if __name__ == "__main__":
    build()
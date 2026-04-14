# project-submission-backend
A FastAPI backend to support project submissions for the Accessibility Hackathon

# Developer instructions
To run a local version of the web app follow these steps:
1. Create a virtual environment (via venv or anaconda)
`python -m venv venv`

# Activate the virtual environment
```
# On macOS and Linux:
source venv/bin/activate

# On Windows:
.\\venv\\Scripts\\activate
```

2. Install dependencies
`pip install -r requirements.txt`

3. Run the server
`uvicorn app.main:app --reload`

4. You should see output in your terminal tellin you that the server is running. Open a browser and go to `http://127.0.0.1:8000` to see the web app.


# GitHub Pages
### Update the site
1. Edit the files in the `templates/` folder.
2. Run the build script in the root directory: `python build_site.py`
3. Push the updated .html files to GitHub
**GitHub pages deploys the dev branch** 
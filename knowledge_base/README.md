# Resume Agent

This workspace contains a knowledge base of your experience, skills, and projects, plus a generator that tailors a LaTeX resume to any job description.

How it works:

- Reads JSON under `profile_summary.json`, `skills/`, `work_experience/`, and `github_projects/`.
- Ingests a Job Description (JD) text/Markdown file.
- Extracts JD keywords for ATS alignment.
- Selects best-matching experience and projects.
- Keeps Skills mostly the same and appends missing JD keywords.
- Writes a 2-line role-specific Summary.
- Emits a `.tex` and optional `.pdf` under `output/`.

Quick start:

1. Save the JD to a file, e.g., `jd.txt`.
2. Run the generator (PDF is optional if LaTeX is installed):

   python3 knowledge_base/generate_resume.py --jd jd.txt --title "Software Engineer" --slug company-role

3. Find output in `knowledge_base/output/`.

Notes:

- If `pdflatex` isn't installed, use `--no-pdf` and compile later.
- Use `--debug` to inspect selections and added skills.

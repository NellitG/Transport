<!--
  This file is generated to help AI coding agents (Copilot, Code LLMs) be quickly productive
  in this repository. Keep it concise and actionable — only include patterns and commands
  you can infer from the repository contents.
-->

# Copilot / AI agent instructions — Django template repo

This repository is a minimal Django template (no app code yet). Use the notes and examples
below to make productive, repo-appropriate edits and to scaffold real Django projects/apps.

Key facts discovered from the repo:
- The repo contains a README.md with quick setup steps and a `requirements.txt`.
- Dependencies: Django==5.2.4, djangorestframework==3.16.0, asgiref, sqlparse, tzdata.
- There is currently no Python/Django project code checked-in; this is a template scaffolding.

How to set up a working dev environment (examples you should follow in PRs):

1. Create and activate a virtual environment from the repository root (Windows example):

   ```powershell
   python -m venv env; .\env\Scripts\activate
   pip install -r requirements.txt
   ```

2. Typical scaffold flow (the README shows these commands):

   - Create the Django project in-place:
     ```powershell
     django-admin startproject <project_name> .
     ```

   - Add an app:
     ```powershell
     python manage.py startapp <appname>
     ```

3. Register apps in settings.py: add the app package and third-party apps to INSTALLED_APPS.
   - Note: the README contains the token `restframework` — the correct Django REST framework
     app string is `rest_framework`.

Project-specific guidance for agents editing this repo:
- Keep changes consistent with Django 5.2 and the DRF version listed in requirements.txt.
- Because this is a template, prefer to add runnable examples + tests (minimal, focused) so
  consumers can validate scaffolding quickly (e.g., simple model + serializer + viewset + tests).
- Ensure all new code is importable from the repository root and that `manage.py` commands
  (migrate, runserver, test) work after your change.

Commands an agent can run locally (verify before pushing):

  - Make migrations and apply them:

    ```powershell
    python manage.py makemigrations
    python manage.py migrate
    ```

  - Run the dev server:

    ```powershell
    python manage.py runserver
    ```

  - Create an admin user (for manual verification):

    ```powershell
    python manage.py createsuperuser
    ```

What not to assume — avoid these pitfalls:
- There are currently no tests or project files in the repository — do not make assumptions about
  an existing project layout (apps, modules) beyond what a newly-generated project would create.
- Do not change the Django/DRF versions without reason — keep changes aligned with
  `requirements.txt` unless the PR explicitly upgrades dependencies and updates README.

Where to document changes and examples:
- README.md — keep setup instructions accurate and correct mistakes (e.g. the `restframework` token).
- Add a small `examples/` or `project/` directory with one complete, runnable minimal project or
  an example app when adding longer examples.

If you modify or add code, also show how to run it quickly in the README and include minimal tests
so reviewers and automated tools can validate the scaffold.

If anything here is unclear or you want more detail (testing preferences, preferred app layout,
CI configuration), ask for clarification in the issue or PR description. Keep updates short and concrete.

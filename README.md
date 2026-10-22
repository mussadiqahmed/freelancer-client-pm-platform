# Freelancer-Client Project Management Platform

A small web application where a client and a freelancer keep one project in one place. The client posts the work, sets a budget, and breaks it into milestones. The freelancer can see published projects. Tasks, invoices, and in-project chat are still backlog work.

This repository continues the CS4002 project from Assignment #01. The Jira project is [Freelancer-Client PM Platform (FCPP)](https://mussadiqahmed90.atlassian.net/browse/FCPP).

## Problem

Freelance work is often split across email, chat apps, and spreadsheets. Scope, deadlines, and payment stages get lost. This platform keeps the project record, the milestones, and later the tasks and messages together.

## Objectives

- Let a freelancer or a client register and log in.
- Let a client post a project with a scope, budget, and deadline.
- Let a client define milestones on a project they own.
- Keep real money transfer, escrow, matching, and a mobile app out of this version.

## What works now

The shared `main` branch contains the application shell: database setup, password hashing, page layout, and the health check.

These stories are implemented on their own branches and are waiting for review before they are merged:

| Story | Branch | What it does |
| --- | --- | --- |
| FCPP-5 | `FCPP-5-user-registration` | Register as a freelancer or a client |
| FCPP-6 | `FCPP-6-user-login` | Log in with a salted password check |
| FCPP-7 | `FCPP-7-post-project` | Post a draft or published project |
| FCPP-8 | `FCPP-8-project-milestones` | Add milestones to a project you own |

Until those pull requests are merged, `main` does not serve registration, login, projects, or milestones.

## Planned, not built

- FCPP-9 Create and update tasks
- FCPP-10 Move a task through To Do, In Progress, and Done
- FCPP-11 Record an invoice for a finished milestone
- FCPP-12 Project messages

Invoices in this project only record a request. They do not transfer money.

## Technology

- Python 3
- FastAPI and Jinja templates
- SQLite
- pytest

Passwords are stored with PBKDF2-HMAC-SHA256. Sessions use a signed cookie. A successful login clears that session and issues a new CSRF token. An unknown email still runs one password-hash check, so it is not obviously faster than a wrong password. Forms send a CSRF token. The database is a local SQLite file.

## Repository structure

```text
app/            application code, templates, and styles
tests/          pytest tests
requirements.txt
.env.example    required settings, with no real secrets
```

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Set `SESSION_SECRET` in `.env` to a long random string before you share a running instance. If it is unset, the process generates a temporary secret and sessions end when the process restarts.

## Run

```bash
source .venv/bin/activate
export SESSION_SECRET=local-dev-secret-change-me
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000`.

## Tests

```bash
source .venv/bin/activate
python -m pytest
```

## Group

- Ahmed Mussadiq — project manager and backend. Jira account: Ahmed Mussadiq.
- Awais Qarni — frontend and QA. The Jira account already used for Awais's stories is displayed as **owais shahid**. Student IDs are not recorded yet.

## Development workflow

1. Take a Jira story from the active sprint.
2. Create a branch named `ISSUE-KEY-short-description`.
3. Commit with the issue key in the message.
4. Open a pull request that names the issue key.
5. The other group member reviews it before it is merged.
6. Move the Jira issue to Done only after the work is merged and the acceptance criteria pass.

Registration has no dependency. Login is reviewed against the registration branch, project posting against login, and milestones against project posting. Each pull request therefore shows one story. They merge in that order.

## Jira

https://mussadiqahmed90.atlassian.net/jira/software/projects/FCPP/boards/35

# FastAPI Todo API

A production-ready Todo REST API built with **FastAPI**, fully tested and delivered through an automated **CI/CD
pipeline**.  
The project focuses on **code quality, automation, and deployment practices**, not just API functionality.

---

## ✨ Features

- CRUD operations for todo items
- Input validation with Pydantic
- SQLite persistence
- Unit tests with coverage
- Dockerized application
- Static code analysis with SonarQube
- Docker image hosting with Nexus Repository
- Automated CI/CD pipeline using GitHub Actions
- Deployment to a remote server

---

## 🧱 Tech Stack

- **Backend**: Python, FastAPI
- **Database**: SQLite
- **Testing**: Pytest, Coverage
- **CI/CD**: GitHub Actions
- **Code Quality**: SonarQube
- **Artifact Repository**: Nexus
- **Containerization**: Docker, Docker Compose
- **Reverse Proxy**: Traefik
- **Scanning the image**: Trivy

---


---

## 🔁 CI/CD Pipeline

Each push to the repository triggers the following steps:

1. **Checkout repository** (full git history for SCM analysis)
2. **Install dependencies**
3. **Run unit tests with coverage**
4. **SonarQube scan**
    - Coverage reporting
    - Static analysis
    - Quality gate enforcement
5. **Build Docker image (only on main)**
6. **Push image to Nexus (only on main)**
7. **Deploy to remote server (only on main)**

The pipeline fails fast if:

- tests fail
- coverage or quality gates are not met

---

## 📊 Code Quality

- Test coverage is generated during CI
- SonarQube analyzes:
    - bugs
    - vulnerabilities
    - code smells
    - duplicated code
- SCM integration is enabled to support:
    - issue attribution
    - new code detection

---

## 🐳 Running Locally

### Prerequisites

- Docker

### Start the stack

```bash

docker build -t todo:alpine .
docker run -d --rm --name todo -p {PORT}:8000 todo:alpine

```

## Endpoints

Endpoints are available at `http://localhost:{PORT}/api/v1/docs` and `http://localhost:{PORT}/api/v1/redoc`.
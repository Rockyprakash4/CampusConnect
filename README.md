# CampusConnect

**CampusConnect** is a full-stack, responsive peer-to-peer placement preparation portal designed for college students. It allows final-year and placed students to share placement experiences, coding round timelines, technical interview questions, preparation roadmaps, and aptitude tips. 

The application is structured as a final-year MCA Major Project, featuring a modular architecture, JWT-based security controls, and responsive styling.

---

## 🏛️ System Architecture

```mermaid
graph TD
    A[Bootstrap 5 / Vanilla JS Frontend] -->|AJAX Fetch with JWT| B[FastAPI Backend Server]
    B -->|SQLAlchemy ORM| C[(Database Engine: MySQL/SQLite)]
    B -->|File Storage| D[Cloudinary / Local Uploads]
    B -->|ReportLab| E[PDF Export Stream]
    B -->|SMTP/Console| F[Simulated Email Notifications]
```

---

## 📁 Project Structure

```text
CampusConnect/
├── database/
│   └── campusconnect.sql     # Complete DDL and sample seed data for MySQL
├── backend/
│   ├── main.py               # Application entry point & static mounts
│   ├── database.py           # SQLAlchemy setup (MySQL / SQLite switcher)
│   ├── models.py             # Entity models (Users, Companies, Posts, etc.)
│   ├── schemas.py            # Pydantic schemas for data validation
│   ├── auth.py               # JWT & bcrypt password hashing
│   ├── run_tests.py          # Automated integration test suite
│   ├── routers/              # Modular API controllers
│   │   ├── auth.py           # Authentication routes
│   │   ├── users.py          # Profiles, followers, and files
│   │   ├── companies.py      # Company listings
│   │   ├── experiences.py    # Placement experiences & PDF generators
│   │   ├── questions.py      # Category question banks
│   │   ├── roadmaps.py       # Study roadmaps & PDF notes
│   │   ├── interactions.py   # Likes, Comments, Bookmarks, Reports
│   │   ├── notifications.py  # User notifications
│   │   └── admin.py          # Account controls & placement analytics
│   ├── utils/                # Helper utilities
│   │   ├── cloudinary_helper.py # Cloudinary / Local filesystem fallback
│   │   ├── pdf_generator.py     # ReportLab placement report compiler
│   │   └── email_helper.py      # SMTP / Console log fallback
│   └── uploads/              # Local storage for fallback uploads
└── frontend/
    ├── index.html            # Landing / Hero page
    ├── login.html            # Login, forgot & reset password gateway
    ├── register.html         # Signup & email verification status
    ├── dashboard.html        # Main student feed, question forum, and charts
    ├── companies.html        # Recruiter directory and statistics
    ├── experience.html       # Full strategical interview reports reader
    ├── add_experience.html   # Report creation form (multi-part details)
    ├── questions.html        # Categories interview questions
    ├── roadmap.html          # Study plan scheduler
    ├── profile.html          # Student portfolios and bookmarks
    ├── admin.html            # Moderation panel and user role editor
    ├── css/
    │   └── style.css         # Theme stylesheet (Dark/Light variables)
    ├── js/
    │   └── app.js            # Core AJAX fetch client & global navbar controller
    └── images/
        └── default-avatar.png # Generated default profile avatar
```

---

## 🚀 Installation & Setup

### Prerequisites
- **Python 3.12+** (tested up to Python 3.14)
- **MySQL Server** (Optional, SQLite is supported out-of-the-box for development)

### 1. Clone or Copy the Files
Navigate into your project folder:
```bash
cd E:\CampusConnect
```

### 2. Configure Environment Variables
Copy `backend/.env.example` to `backend/.env` and configure your settings:
```bash
cp backend/.env.example backend/.env
```

By default, `DATABASE_URL` is set to SQLite (`sqlite:///./campusconnect.db`) for immediate zero-setup execution. To use MySQL, uncomment the MySQL line in `.env` and configure your credentials:
```ini
DATABASE_URL=mysql+pymysql://username:password@localhost:3306/campusconnect
```

### 3. Install Dependencies
Install all required packages from your terminal:
```bash
py -m pip install -r backend/requirements.txt httpx email-validator passlib
```

---

## 🛠️ Running the Application

Start the FastAPI local development server using `uvicorn`:
```bash
py -m uvicorn backend.main:app --reload --port 8000
```

Once running:
- **Web Application Portal**: Open [http://localhost:8000](http://localhost:8000) in your web browser.
- **Interactive Swagger API Documentation**: Visit [http://localhost:8000/docs](http://localhost:8000/docs).

---

## 🧪 Testing and Verification

To verify that all backend modules, databases, JWT auth, likes, comments, and ReportLab PDF streaming work correctly:
```bash
py backend/run_tests.py
```
This runs 8 automated integration tests using FastAPI's `TestClient` and reports the results.

---

## 🔑 Default Credentials for Testing

The database seeding file automatically registers accounts with verified emails for testing. 

| User Role | Email / Username | Password | Purpose |
| :--- | :--- | :--- | :--- |
| **Administrator** | `admin` / `admin@campusconnect.com` | `adminpassword` | Account moderation, approving posts, analytics |
| **Placed Student** | `anasharma` / `anasharma@college.edu` | `password123` | Writing experiences, creating roadmaps, adding questions |
| **Student** | `johndoe` / `johndoe@college.edu` | `password123` | Reading reports, asking questions, liking/commenting |

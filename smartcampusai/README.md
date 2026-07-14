# SmartCampusAI

SmartCampusAI is a production-ready, AI-powered Smart Campus Management System built using Python and Streamlit. It leverages the Google Gemini API to offer an intelligent campus assistant alongside robust academic dashboarding, role-based database operations, class timelines, placement cells, and metrics visualization.

---

## Key Features

1. **Role-Based Authentication**: Custom sign-ups and logins separating **Admin**, **Faculty**, and **Student** scopes. Passwords are securely hashed using `bcrypt` and verified through session management hooks.
2. **Dynamic Operations Hub**: 
   * **Admin & Faculty**: Full CRUD actions on Student databases and attendance charts, event creation, and announcements management.
   * **Students**: Interactive directory viewing, job cell applications, upcoming event timelines, and customized attendance reports.
3. **Conversational AI Assistant**: Integrated with **Google Gemini 1.5 Flash** REST APIs supporting conversation memory threads, history log downloads, and simulation fallbacks.
4. **Interactive Data Analytics**: Custom Plotly pie charts, bar charts, area charts, and linear timelines illustrating class demographics, attendance metrics, and recruitment compensation ranges.
5. **Polished Design System**: Theme-responsive custom CSS stylesheets featuring premium modern layouts, Glassmorphic component containers, and fluid micro-animations.

---

## Folder Structure

```text
SmartCampusAI/
│
├── .streamlit/
│   └── config.toml         # Theme styles & variables
│
├── styles/
│   └── style.css           # Custom Glassmorphism, animations, UI styles
│
├── helpers/
│   ├── json_handler.py     # Thread-safe JSON NoSQL database CRUD helper
│   ├── validators.py       # Email, phone, & password validation checking
│   └── security.py         # Secure Bcrypt password hashing modules
│
├── components/
│   ├── navbar.py           # Top navigation headers & session badge indicators
│   ├── sidebar.py          # Logo & sidebar session controllers (Log out)
│   ├── cards.py            # KPI metrics containers styling
│   ├── charts.py           # Reusable Plotly chart generators
│   └── footer.py           # Bottom system copyright disclaimers
│
├── modules/
│   ├── utils.py            # Load styling, access gates, & custom headers
│   ├── authentication.py   # Login & register panels
│   ├── dashboard.py        # KPI grids & bulletin board
│   ├── students.py         # Student records CRUD dashboards
│   ├── attendance.py       # Attendance markers & summaries
│   ├── announcements.py    # bulletins manager
│   ├── placements.py       # Job schedules & selected candidate trackers
│   ├── ai_chat.py          # Gemini AI Assistant panels
│   ├── analytics.py        # Detailed operations graphs
│   └── settings.py         # Profile & database diagnostics settings
│
├── data/                   # JSON databases (Self-initialized)
│   ├── users.json
│   ├── students.json
│   ├── attendance.json
│   ├── announcements.json
│   ├── events.json
│   ├── placements.json
│   └── chat_history.json
│
├── app.py                  # Core script & navigation router
├── requirements.txt        # Package dependencies
├── .env                    # Local environment config
├── .env.example            # Environment configurations template
├── render.yaml             # Render deployment blueprint
└── README.md               # Operation manual
```

---

## Local Setup & Installation

### Prerequisite
* Python 3.10 to 3.14
* PIP Package Manager

### 1. Clone & Initialize Workspace
Navigate to your project root folder:
```bash
cd smartcampusai
```

### 2. Create Virtual Environment
Create and activate a python virtual environment:
```powershell
# Windows PowerShell
python -m venv .venv
.venv\Scripts\Activate.ps1

# Linux / MacOS Bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
Install all required packages from `requirements.txt`:
```bash
pip install -r requirements.txt
```

### 4. Setup Environment Config
Create a copy of `.env.example` named `.env` and fill in your details:
```bash
# On Windows PowerShell
Copy-Item .env.example .env

# On Linux / MacOS Bash
cp .env.example .env
```
Open `.env` and configure your API key:
```env
GOOGLE_API_KEY=YOUR_GOOGLE_GEMINI_API_KEY
SECRET_KEY=A_RANDOM_SECRET_STRING_FOR_SECURE_VERIFICATION
APP_NAME=SmartCampusAI
```

### 5. Running the Application
Launch the local development server:
```bash
streamlit run app.py
```
Open the browser at `http://localhost:8501`.

---

## Out-of-the-Box Demo Accounts
The system initializes automatically with mock data. You can log in using these default profiles:

| Role | Username | Password |
|---|---|---|
| **Admin** | `admin` | `admin123` |
| **Faculty** | `faculty` | `faculty123` |
| **Student** | `student` | `student123` |

---

## Deployment to Render

This repository is optimized for deployment on Render.

1. Create a new Web Service on **Render.com**.
2. Connect your Git repository.
3. Render automatically picks up `render.yaml` configurations:
   * **Runtime**: Python
   * **Build Command**: `pip install -r requirements.txt`
   * **Start Command**: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`
4. Define your `GOOGLE_API_KEY` under the Environment Variables settings in the Render dashboard.

---

## Future Scope

1. **Real-time SQL Integrations**: Swapping JSON handlers with ORMs (SQLAlchemy, PostgreSQL) for heavier transaction scales.
2. **AI-driven Scheduling**: Automatic class timetable planning using Gemini agents.
3. **Biometrics Attendance**: Support for facial/QR verification marks.
4. **Push Notifications**: Live email notifications for class alerts, drive updates, and exams.

---

## License
Distributed under the MIT License.

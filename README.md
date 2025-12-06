# Swiftly

Swiftly is a realtime collaborative text editor built for quick scaffolding of MVP's

# Initial Setup

# Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Windows (CMD):
venv\Scripts\activate.bat
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install django channels daphne django-cors-headers

# Run database migrations
python manage.py migrate

# Start backend server (uses Daphne ASGI automatically)
python manage.py runserver
```

#### Frontend Setup

```bash
# Navigate to frontend directory (in a new terminal)
cd frontend

# Install dependencies (requires Node.js 20.19+ or 22.12+)
npm install

# Start development server
npm run dev  # Runs on http://localhost:5173
```

### Running the App (After Initial Setup)

```bash
# Terminal 1 - Backend (from /backend directory)
.\venv\Scripts\Activate.ps1  # Activate venv first
python manage.py runserver   # Runs on http://localhost:8000

# Terminal 2 - Frontend (from /frontend directory)
npm run dev  # Runs on http://localhost:5173
```

Open http://localhost:5173 in your browser to use the app.

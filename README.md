# Swiftly

A realtime collaborative code editor for teams. Create rooms, invite collaborators, and code together with live sync.

![Vue](https://img.shields.io/badge/Vue-3-4FC08D?logo=vue.js)
![Django](https://img.shields.io/badge/Django-5.2-092E20?logo=django)
![WebSocket](https://img.shields.io/badge/WebSocket-Channels-blue)

---

## Features

- **Real-time collaboration** — See changes instantly via WebSocket + Yjs CRDT
- **Team rooms** — Create password-protected rooms with shareable codes
- **Role-based access** — Owner, Editor, Viewer permissions
- **Virtual file system** — Organize code in folders and files
- **Monaco Editor** — VS Code-like editing with IntelliSense & Emmet
- **Live preview** — Instant HTML preview as you type
- **Version history** — Auto-saved snapshots with restore capability
- **Export** — Download entire project as ZIP

---

## How It Works

```
┌─────────────────┐     WebSocket      ┌─────────────────┐
│   Vue Frontend  │ ◄─────────────────►│  Django Backend │
│   Monaco + Yjs  │    Yjs updates     │  Channels ASGI  │
└─────────────────┘                    └─────────────────┘
        │                                       │
        ▼                                       ▼
   Local CRDT doc                        SQLite Database
   (conflict-free)                    (files, rooms, users)
```

1. Users join a **room** with a code + password
2. Each file has its own **Yjs document** for conflict-free sync
3. Changes broadcast to all room members via **WebSocket**
4. Files auto-save to database with **version snapshots**

---

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 20.19+ or 22.12+

### 1. Backend Setup

```bash
cd backend

# Create & activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows PowerShell
# source venv/bin/activate   # macOS/Linux

# Install dependencies
pip install django channels daphne django-cors-headers

# Run migrations
python manage.py migrate

# Start server (use 0.0.0.0 for LAN access)
python manage.py runserver              # localhost only
python manage.py runserver 0.0.0.0:8000 # LAN access
```

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev  # http://localhost:5173
```

### 3. Open App

Visit **http://localhost:5173** — Register, create a room, and start coding!

### 4. LAN Access (Multiple Devices)

To collaborate from other computers/phones on the same network:

1. Start backend with LAN binding:

   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```

2. Start frontend (automatically binds to all interfaces):

   ```bash
   npm run dev
   ```

3. Find your computer's IP address:

   ```powershell
   ipconfig  # Windows - look for IPv4 Address
   ```

4. Access from other devices using: `http://<your-ip>:5173`

**Note:** You may need to allow ports 5173 and 8000 through your firewall.

---

## Project Structure

```
Swiftly/
├── backend/
│   ├── collab_editor/
│   │   ├── models.py      # Room, VirtualFile, FileSnapshot
│   │   ├── views.py       # REST API endpoints
│   │   ├── consumers.py   # WebSocket handler (Yjs sync)
│   │   └── urls.py        # API routes
│   └── backend/
│       └── settings.py    # Django config
│
└── frontend/
    └── src/
        ├── components/
        │   ├── CollabEditor.vue   # Main editor
        │   ├── FileExplorer.vue   # File tree sidebar
        │   └── VersionHistory.vue # Snapshot panel
        └── App.vue                # Root component
```

---

## API Endpoints

| Endpoint                | Method   | Description         |
| ----------------------- | -------- | ------------------- |
| `/api/auth/register/`   | POST     | Create account      |
| `/api/auth/login/`      | POST     | Login               |
| `/api/rooms/`           | GET/POST | List/create rooms   |
| `/api/rooms/<id>/join/` | POST     | Join room with code |
| `/api/files/`           | GET      | Get file tree       |
| `/api/files/<id>/`      | PUT      | Update file content |
| `/api/snapshots/`       | GET      | Get version history |

---

## Tech Stack

**Frontend:** Vue 3, Vite, Monaco Editor, Yjs, y-monaco, TailwindCSS, shadcn/vue

**Backend:** Django 5.2, Django Channels, Daphne (ASGI), SQLite

---

## License

MIT

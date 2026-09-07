# Indian Standards AI

> **AI-Powered Recommendation Engine for Identifying Applicable Indian Standards for Procurement Specifications**

## Smart India Hackathon 2026

| | |
|---|---|
| **Problem Statement** | SIH26108 |
| **Category** | Software |
| **Theme** | Smart Automation |
| **Phase** | Phase 1 — Foundation |

---

> **⚠️ Phase 1 Notice:** Recommendation results are currently **mock data**. The real Indian Standards AI/RAG pipeline (LangChain.js + Gemini + pgvector + Neo4j) will be implemented in Phase 2.

---

## 📋 Project Overview

A user describes their procurement requirement in natural language. The system identifies applicable Bureau of Indian Standards (BIS) standards, ranks them by applicability, and explains why each standard was recommended.

**Example Query:**
> "I need 500 ergonomic office chairs for a government office with adjustable height and proper back support."

**System Response:**
- IS 1991:2020 — Office Work Chairs — Applicability Score: 96%
- IS 4680:2012 — Office Furniture — Applicability Score: 88%
- IS 15694:2018 — Ergonomic Requirements — Applicability Score: 81%
- … and more

---

## 🚀 Current Phase — Phase 1

### What is implemented:
- ✅ Frontend (React + Vite + Tailwind CSS v4)
- ✅ Backend (Node.js + Express.js)
- ✅ Google OAuth 2.0 Authentication
- ✅ MongoDB + Mongoose (Users, Chats, Messages)
- ✅ Chat interface (ChatGPT-style)
- ✅ Chat history (persisted across sessions)
- ✅ Mock Indian Standards recommendations (5–6 per query)
- ✅ Applicability scores with progress bars
- ✅ Recommendation cards with "Why recommended?" reasoning
- ✅ View Details modal (with Phase 2 placeholders)
- ✅ Tender PDF upload UI (placeholder — no processing)
- ✅ Responsive design (desktop, tablet, mobile)
- ✅ Protected routes (auth required for /chat)

### What is intentionally left for Phase 2:
- ❌ LangChain.js AI pipeline
- ❌ Google Gemini LLM integration
- ❌ Embeddings and semantic search
- ❌ PostgreSQL + pgvector
- ❌ Neo4j knowledge graph
- ❌ Real Indian Standards dataset
- ❌ PDF/OCR tender text extraction
- ❌ Applicability ranking with real AI

---

## 📁 Project Structure

```
Indian-Standards-AI/
├── frontend/                     # React + Vite + Tailwind CSS v4
│   ├── public/
│   │   └── favicon.svg
│   └── src/
│       ├── components/
│       │   ├── chat/             # ChatArea, MessageBubble, MessageInput, EmptyChat
│       │   ├── common/           # ProtectedRoute
│       │   ├── layout/           # Sidebar
│       │   └── recommendation/   # RecommendationCard, RecommendationList, ApplicabilityScore
│       ├── context/
│       │   └── AuthContext.jsx   # Global auth state
│       ├── pages/
│       │   ├── LoginPage.jsx
│       │   ├── ChatPage.jsx
│       │   └── SettingsPage.jsx
│       ├── services/             # API calls (api.js, authService, chatService, messageService)
│       ├── App.jsx               # Router + AuthProvider
│       └── index.css             # Tailwind + design system variables
│
├── backend/                      # Node.js + Express.js
│   └── src/
│       ├── config/
│       │   ├── db.js             # MongoDB connection
│       │   └── passport.js       # Google OAuth strategy
│       ├── controllers/          # authController, chatController, messageController, tenderController
│       ├── middleware/
│       │   └── auth.js           # requireAuth middleware
│       ├── models/               # User.js, Chat.js, Message.js
│       ├── routes/               # authRoutes, chatRoutes, messageRoutes, tenderRoutes
│       ├── services/
│       │   └── mockRecommendationService.js  # ← Replace with real AI in Phase 2
│       ├── app.js                # Express app setup
│       └── server.js             # Entry point
│
├── data/                         # Datasets (future phases)
├── docs/                         # Documentation
├── scripts/                      # Dev/ingestion scripts
└── README.md
```

---

## 🛠️ Technology Stack

### Phase 1 (Current)

| Layer | Technology |
|-------|-----------|
| Frontend | React 19, Vite 7, Tailwind CSS v4 |
| Backend | Node.js, Express.js 4 |
| Authentication | Google OAuth 2.0 via Passport.js |
| Database | MongoDB + Mongoose |
| Session | express-session + connect-mongo |
| API Client | Axios |
| Routing | React Router v6 |

### Phase 2 (Planned)

| Layer | Technology |
|-------|-----------|
| AI Orchestration | LangChain.js |
| LLM | Google Gemini |
| Vector Database | PostgreSQL + pgvector |
| Knowledge Graph | Neo4j |
| Document Processing | PDF Parser + OCR |
| Data Science | Python + Pandas + Scikit-learn |

---

## ⚙️ Setup & Running

### Prerequisites

- Node.js 18+
- MongoDB (local or MongoDB Atlas)
- Google OAuth credentials (optional for Phase 1 structure)

---

### 1. Clone the repository

```bash
git clone https://github.com/Nonu185/Indian-Standards-AI.git
cd Indian-Standards-AI
```

---

### 2. Backend Setup

```bash
cd backend
npm install
cp .env.example .env
```

Edit `backend/.env`:

```env
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_CALLBACK_URL=http://localhost:5000/api/auth/google/callback
MONGODB_URI=mongodb://localhost:27017/indian-standards-ai
SESSION_SECRET=your_strong_random_secret
CLIENT_URL=http://localhost:5173
PORT=5000
NODE_ENV=development
```

Start backend:
```bash
npm run dev
```

Backend runs on: `http://localhost:5000`

---

### 3. Frontend Setup

```bash
cd frontend
npm install
cp .env.example .env
```

Edit `frontend/.env` (optional, defaults work out of the box):
```env
VITE_API_URL=http://localhost:5000/api
```

Start frontend:
```bash
npm run dev
```

Frontend runs on: `http://localhost:5173`

---

### 4. Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable **Google OAuth 2.0 API**
4. Create **OAuth 2.0 credentials** (Web application)
5. Add authorized redirect URI:
   ```
   http://localhost:5000/api/auth/google/callback
   ```
6. Copy **Client ID** and **Client Secret** to `backend/.env`

> **Note:** If you don't have credentials yet, the app structure is fully implemented. The Google Login button will redirect to the backend, and the backend will return an error that the frontend handles gracefully.

---

## 📡 API Routes

### Authentication

| Method | Route | Description |
|--------|-------|-------------|
| `GET` | `/api/auth/google` | Initiate Google OAuth login |
| `GET` | `/api/auth/google/callback` | OAuth callback from Google |
| `GET` | `/api/auth/me` | Get current authenticated user |
| `POST` | `/api/auth/logout` | Log out and destroy session |

### Chats

| Method | Route | Description |
|--------|-------|-------------|
| `GET` | `/api/chats` | Get all chats for authenticated user |
| `POST` | `/api/chats` | Create a new chat |
| `GET` | `/api/chats/:chatId` | Get a specific chat |
| `DELETE` | `/api/chats/:chatId` | Delete a specific chat |

### Messages

| Method | Route | Description |
|--------|-------|-------------|
| `GET` | `/api/chats/:chatId/messages` | Get all messages in a chat |
| `POST` | `/api/chats/:chatId/messages` | Send a message, receive mock AI response |

### Tenders

| Method | Route | Description |
|--------|-------|-------------|
| `POST` | `/api/tenders/upload` | Tender PDF upload (placeholder — Phase 2) |

---

## 🗄️ Database Models

### User
```js
{ googleId, name, email, profileImage, createdAt }
```

### Chat
```js
{ userId, title, createdAt, updatedAt }
```

### Message
```js
{ chatId, userId, role: 'user'|'assistant', content, recommendations, createdAt }
```

---

## 🔐 Security

- Google Client Secret is never exposed to the frontend
- Session cookies are HTTP-only
- Every chat and message API verifies the `userId` matches the authenticated user
- `.env` is in `.gitignore` and never committed
- Use `SESSION_SECRET` with a strong random value in production

---

## 🏗️ Future AI/RAG Architecture (Phase 2)

```
User Query
    ↓
Requirement Extraction (Gemini)
    ↓
LangChain.js
    ↓
Text Embeddings
    ↓
PostgreSQL + pgvector (semantic search on Indian Standards)
    ↓
Applicability Ranking
    ↓
Top 5–6 Applicable Standards
    ↓
Neo4j Knowledge Graph
    ↓
Related / Normative Standards + Certification Rules
    ↓
Final Recommendation with Evidence
```

MongoDB continues to handle Users, Authentication, Chat History, and Messages in all phases.

---

## 🤝 Contributing

This is an SIH 2026 project. Team members should follow the established folder structure and coding conventions.

---

## 📄 License

Educational project — Smart India Hackathon 2026.
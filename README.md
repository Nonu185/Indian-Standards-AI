# Indian Standards AI

AI-Powered Recommendation Engine for Identifying Applicable Indian Standards for Procurement Specifications.

## Smart India Hackathon 2026

**Problem Statement:** SIH26108  
**Category:** Software  
**Theme:** Smart Automation

---

## 📁 Project Folder Structure

```text
Indian-Standards-AI/
│
├── frontend/                              # React + Tailwind CSS
│   │
│   ├── public/
│   │
│   └── src/
│       ├── assets/
│       │
│       ├── components/
│       │   ├── common/                    # Buttons, modals, loaders
│       │   ├── layout/                    # Navbar, sidebar, layouts
│       │   ├── procurement/               # Procurement UI
│       │   ├── standards/                 # Standards UI
│       │   ├── recommendation/            # AI recommendations
│       │   ├── graph/                     # Standards relationship graph
│       │   └── specification/             # Specification generator
│       │
│       ├── pages/
│       │   ├── Login.jsx
│       │   ├── Dashboard.jsx
│       │   ├── NewProcurement.jsx
│       │   ├── TenderUpload.jsx
│       │   ├── Requirements.jsx
│       │   ├── Recommendations.jsx
│       │   ├── StandardDetails.jsx
│       │   ├── KnowledgeGraph.jsx
│       │   └── Specification.jsx
│       │
│       ├── services/                      # API calls
│       ├── hooks/                         # Custom React hooks
│       ├── context/                       # Global state
│       ├── utils/                         # Helper functions
│       └── types/                         # Shared types
│
│
├── backend/                               # Node.js + Express.js
│   │
│   ├── src/
│   │   │
│   │   ├── config/                        # DB & environment config
│   │   ├── controllers/                   # Request controllers
│   │   ├── middleware/                    # Auth, upload, errors
│   │   ├── models/                        # Database models
│   │   ├── routes/                        # API routes
│   │   │
│   │   ├── services/
│   │   │   │
│   │   │   ├── ai/
│   │   │   │   ├── langchain/             # LangChain.js
│   │   │   │   ├── chains/                # AI chains
│   │   │   │   └── prompts/               # AI prompts
│   │   │   │
│   │   │   ├── standards/                 # Standards processing
│   │   │   ├── procurement/               # Procurement logic
│   │   │   ├── certification/             # Certification rules
│   │   │   ├── versioning/                # Version/amendment checks
│   │   │   ├── knowledgeGraph/             # Neo4j graph
│   │   │   └── specification/             # Specification generation
│   │   │
│   │   ├── validators/                    # Request validation
│   │   ├── utils/                         # Backend utilities
│   │   ├── jobs/                          # Automation/background jobs
│   │   ├── types/                         # Backend types
│   │   ├── app.js
│   │   └── server.js
│   │
│   └── tests/                             # Backend tests
│
│
├── data/                                  # Dataset & project data
│   ├── raw/                               # Original collected data
│   ├── processed/                         # Cleaned data
│   ├── standards/                         # Standards dataset
│   ├── embeddings/                        # Generated embeddings
│   ├── knowledge-graph/                   # Graph data
│   └── sample-tenders/                    # Sample tender documents
│
│
├── scripts/
│   ├── ingestion/                         # Data ingestion scripts
│   ├── database/                          # Database scripts
│   └── dev/                               # Development scripts
│
│
├── docs/
│   ├── architecture/                      # System architecture
│   ├── ai-pipeline/                       # AI/RAG documentation
│   ├── api/                               # API documentation
│   ├── database/                          # Database documentation
│   ├── team/                              # Team documentation
│   └── demo/                              # Demo documentation
│
│
├── .github/
│   └── workflows/                         # GitHub Actions / CI
│
│
├── .gitignore
├── docker-compose.yml
└── README.md





## 🛠️ Technology Stack

### 🎨 Frontend
- **React.js** — User interface
- **Vite** — Frontend build tool
- **Tailwind CSS** — Styling and responsive UI
- **React Router** — Application routing
- **Axios** — API communication

### ⚙️ Backend
- **Node.js** — Backend runtime
- **Express.js** — REST API and server
- **JWT** — Authentication
- **Multer** — Document/file uploads

### 🤖 AI & RAG
- **LangChain.js** — AI/RAG pipeline orchestration
- **Google Gemini** — Large Language Model
- **Embeddings** — Semantic representation of requirements and standards
- **RAG (Retrieval-Augmented Generation)** — Context-aware recommendations
- **Semantic Search** — Finding relevant Indian Standards

### 🗄️ Databases
- **PostgreSQL** — Application and standards metadata
- **pgvector** — Vector storage and similarity search
- **Neo4j** — Knowledge graph for relationships between standards

### 📄 Document Processing
- **PDF Parser** — Extract text from tender documents
- **OCR** — Extract information from scanned documents
- **Text Chunking** — Prepare documents for retrieval

### 📊 Data & ML
- **Python** — Data analysis and ML experimentation
- **Pandas** — Data cleaning and analysis
- **NumPy** — Numerical processing
- **Scikit-learn** — ML models and evaluation
- **Jupyter Notebook** — Data exploration and experiments

### 🔄 Automation
- **Node.js Background Jobs** — Automated processing
- **Scheduled Jobs** — Standards/data updates
- **GitHub Actions** — CI/CD and automation

### 🧰 Development & Deployment
- **Git** — Version control
- **GitHub** — Collaboration and repository
- **Docker** — Local development and services
- **Vercel** — Frontend deployment
- **Render / Railway** — Backend deployment





                    ┌──────────────────┐
                    │  React + Vite     │
                    │  Tailwind CSS     │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ Node.js + Express │
                    └────────┬─────────┘
                             │
             ┌───────────────┼────────────────┐
             ▼               ▼                ▼
      ┌─────────────┐ ┌──────────────┐ ┌─────────────┐
      │ LangChain.js│ │ PostgreSQL   │ │   Neo4j     │
      │ + Gemini    │ │ + pgvector   │ │ Knowledge   │
      │             │ │              │ │   Graph     │
      └─────────────┘ └──────────────┘ └─────────────┘
             │
             ▼
      AI Recommendation
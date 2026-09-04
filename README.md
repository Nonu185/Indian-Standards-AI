SIH26108-Indian-Standards-AI/
│
├── frontend/                              # React + Tailwind
│   ├── public/
│   │
│   └── src/
│       ├── assets/
│       │
│       ├── components/
│       │   ├── common/                    # Buttons, Modal, Loader, etc.
│       │   ├── layout/                    # Navbar, Sidebar, Layout
│       │   ├── procurement/               # Procurement input/upload UI
│       │   ├── standards/                 # Standard cards/details
│       │   ├── recommendation/            # AI recommendation UI
│       │   ├── graph/                     # Related standards graph
│       │   └── specification/             # Specification generator UI
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
│       ├── services/
│       │   ├── api.js
│       │   ├── auth.service.js
│       │   ├── procurement.service.js
│       │   └── standards.service.js
│       │
│       ├── hooks/
│       ├── context/
│       ├── utils/
│       └── types/
│
│
├── backend/                               # Node.js + Express
│   │
│   ├── src/
│   │   ├── config/
│   │   │   ├── db.js
│   │   │   ├── env.js
│   │   │   └── neo4j.js
│   │   │
│   │   ├── controllers/
│   │   │   ├── auth.controller.js
│   │   │   ├── procurement.controller.js
│   │   │   ├── standards.controller.js
│   │   │   └── recommendation.controller.js
│   │   │
│   │   ├── middleware/
│   │   │   ├── auth.middleware.js
│   │   │   ├── error.middleware.js
│   │   │   └── upload.middleware.js
│   │   │
│   │   ├── models/
│   │   │   ├── User.js
│   │   │   ├── Procurement.js
│   │   │   ├── Document.js
│   │   │   ├── Requirement.js
│   │   │   ├── Standard.js
│   │   │   └── Recommendation.js
│   │   │
│   │   ├── routes/
│   │   │   ├── auth.routes.js
│   │   │   ├── procurement.routes.js
│   │   │   ├── standards.routes.js
│   │   │   └── recommendation.routes.js
│   │   │
│   │   ├── services/
│   │   │   │
│   │   │   ├── ai/
│   │   │   │   ├── langchain/
│   │   │   │   │   ├── documentLoader.js
│   │   │   │   │   ├── textSplitter.js
│   │   │   │   │   ├── embeddings.js
│   │   │   │   │   ├── retriever.js
│   │   │   │   │   └── ragChain.js
│   │   │   │   │
│   │   │   │   ├── chains/
│   │   │   │   │   ├── requirementChain.js
│   │   │   │   │   └── recommendationChain.js
│   │   │   │   │
│   │   │   │   └── prompts/
│   │   │   │       ├── requirement.prompt.js
│   │   │   │       ├── recommendation.prompt.js
│   │   │   │       └── explanation.prompt.js
│   │   │   │
│   │   │   ├── standards/
│   │   │   │   ├── standardsService.js
│   │   │   │   └── standardsSearch.js
│   │   │   │
│   │   │   ├── procurement/
│   │   │   │   └── procurementService.js
│   │   │   │
│   │   │   ├── certification/
│   │   │   │   └── certificationEngine.js
│   │   │   │
│   │   │   ├── versioning/
│   │   │   │   └── versionChecker.js
│   │   │   │
│   │   │   ├── knowledgeGraph/
│   │   │   │   └── standardsGraph.js
│   │   │   │
│   │   │   └── specification/
│   │   │       └── specificationService.js
│   │   │
│   │   ├── validators/
│   │   ├── utils/
│   │   ├── jobs/
│   │   ├── types/
│   │   ├── app.js
│   │   └── server.js
│   │
│   └── tests/
│
│
├── data/                                  # Project data
│   ├── raw/                               # Original collected data
│   ├── processed/                         # Cleaned data
│   ├── standards/                         # Standards metadata
│   ├── embeddings/                        # Generated embeddings
│   ├── knowledge-graph/                   # Graph data
│   └── sample-tenders/                    # Sample PDFs
│
│
├── scripts/
│   ├── ingestion/                         # Import/clean standards
│   ├── database/                          # DB setup/migrations
│   └── dev/                               # Developer scripts
│
│
├── docs/
│   ├── architecture/
│   │   └── SYSTEM_FLOW.md
│   │
│   ├── ai-pipeline/
│   │   └── RAG_PIPELINE.md
│   │
│   ├── api/
│   │   └── API_DOCUMENTATION.md
│   │
│   ├── database/
│   │   └── DATABASE_SCHEMA.md
│   │
│   ├── team/
│   │   ├── TEAM_GUIDE.md
│   │   └── TASK_ASSIGNMENT.md
│   │
│   └── demo/
│       └── DEMO_FLOW.md
│
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── .env.example
├── .gitignore
├── docker-compose.yml
├── PROJECT_STRUCTURE.txt
└── README.md




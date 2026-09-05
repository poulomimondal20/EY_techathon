# DrugIQ - AI-Powered Pharmaceutical Intelligence Platform

DrugIQ is a comprehensive multi-agent AI platform designed for the pharmaceutical industry. It leverages advanced AI agents powered by Google Gemini and the Agno framework to provide intelligent insights across drug discovery, clinical trials, market analysis, and regulatory compliance.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

## Overview

DrugIQ addresses critical challenges in pharmaceutical research and development by providing AI-driven analysis across multiple domains:

- Accelerating drug discovery through target identification and lead optimization
- Analyzing clinical trial landscapes and predicting outcomes
- Monitoring competitor activities and market trends
- Validating medicine information and detecting counterfeits
- Generating ESG (Environmental, Social, Governance) compliance reports
- Conducting deep literature research and synthesis

## Features

### AI Agents

| Agent | Description |
|-------|-------------|
| **Drug Discovery** | Multi-stage pipeline for target discovery, lead identification, optimization, and preclinical evaluation |
| **Deep Research** | Comprehensive literature mining, clinical trial analysis, and evidence synthesis |
| **Clinical Trials** | Analysis of clinical trial landscapes, phase distributions, and outcome predictions |
| **Drug Repurposing** | Identification of new therapeutic applications for existing drugs |
| **Competitor Analysis** | Monitoring and analysis of competitor pipelines, patents, and market positioning |
| **Market Insights** | Market size estimation, growth projections, and trend analysis |
| **Medicine Validation** | Verification of medicine authenticity and regulatory compliance |
| **ESG Report Generator** | Automated generation of ESG compliance reports in PDF format |
| **News Aggregator** | Real-time pharmaceutical industry news with automatic caching |

### Tools and APIs

- **ADMET Properties**: Absorption, Distribution, Metabolism, Excretion, and Toxicity predictions
- **Molecular Design**: Structure-based drug design and optimization
- **PDB Query**: Protein Data Bank integration for structural analysis
- **UniProt API**: Protein sequence and functional information
- **StringDB API**: Protein-protein interaction network analysis
- **Clinical Trial Tool**: ClinicalTrials.gov data retrieval
- **Patent Search**: Patent landscape analysis
- **Literature Mining**: PubMed and scientific literature search

## Architecture

```
+------------------+     +------------------+     +------------------+
|                  |     |                  |     |                  |
|  React Frontend  |<--->|  FastAPI Backend |<--->|  AI Agents (Agno)|
|  (Vite + TS)     |     |  (Python)        |     |  (Gemini)        |
|                  |     |                  |     |                  |
+------------------+     +------------------+     +------------------+
                               |
                               v
              +--------------------------------+
              |         External APIs          |
              | - PubMed  - ClinicalTrials.gov |
              | - UniProt - PDB                |
              | - Tavily  - News APIs          |
              +--------------------------------+
```

## Tech Stack

### Backend
- Python 3.10+
- FastAPI (REST API framework)
- Agno (AI agent framework)
- Google Gemini (LLM provider)
- Pydantic (Data validation)
- Pandas / NumPy (Data processing)
- scikit-learn (Machine learning)
- FPDF2 / ReportLab (PDF generation)

### Frontend
- React 18
- TypeScript
- Vite (Build tool)
- Tailwind CSS (Styling)
- Radix UI (Component library)
- Recharts (Data visualization)
- React Markdown (Content rendering)
- Lucide React (Icons)

## Prerequisites

Before running the application, ensure you have the following installed:

- Python 3.10 or higher
- Node.js 18 or higher
- npm or yarn package manager
- Git

### Required API Keys

You will need API keys for the following services:

- Google Gemini API (required for AI agents)
- Tavily API (for web search functionality)
- News API (for news aggregation)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/SRINJOY59/EY_Techathon.git
cd EY_Techathon 
```

### 2. Backend Setup

Create and activate a Python virtual environment:

```bash
# Windows
python -m venv myenv
myenv\Scripts\activate

# macOS/Linux
python3 -m venv myenv
source myenv/bin/activate
```

Install Python dependencies:

```bash
pip install -r requirements.txt
```

### 3. Frontend Setup

Navigate to the frontend directory and install dependencies:

```bash
cd frontend
npm install
```

## Configuration

### 1. Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
# Google Gemini API
GOOGLE_API_KEY=your_gemini_api_key

# Tavily API (for web search)
TAVILY_API_KEY=your_tavily_api_key

# News API
NEWS_API_KEY=your_news_api_key

# Optional: OpenAI API (if using OpenAI models)
OPENAI_API_KEY=your_openai_api_key

# Optional: Groq API
GROQ_API_KEY=your_groq_api_key
```

### 2. API Configuration

The backend runs on `http://localhost:8000` by default. The frontend is configured to connect to this address. If you need to change the backend URL, update the `API_BASE_URL` constant in the frontend components.

## Running the Application

### Start the Backend Server

From the root directory with your virtual environment activated:

```bash
cd backend
python app.py
```

The backend server will start at `http://localhost:8000`.

Alternatively, you can use uvicorn directly:

```bash
cd backend
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### Start the Frontend Development Server

In a new terminal, navigate to the frontend directory:

```bash
cd frontend
npm run dev
```

The frontend will be available at `http://localhost:5173`.

### Access the Application

Open your browser and navigate to `http://localhost:5173` to access the PharmaIQ platform.

## API Documentation

Once the backend is running, you can access the interactive API documentation at:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Key API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/drug-discovery/execute` | POST | Execute drug discovery workflow |
| `/api/v1/deep-research/execute` | POST | Run comprehensive research analysis |
| `/api/v1/clinical-trials/analyze` | POST | Analyze clinical trial landscape |
| `/api/v1/drug-repurposing/analyze` | POST | Find drug repurposing opportunities |
| `/api/v1/competitor-analysis/analyze` | POST | Analyze competitor landscape |
| `/api/v1/market-insights/analyze` | POST | Generate market insights |
| `/api/v1/medicine-validation/validate` | POST | Validate medicine information |
| `/api/v1/esg/generate-report` | POST | Generate ESG compliance report |
| `/api/v1/news/latest` | GET | Get latest pharmaceutical news |

## Project Structure

```
pharmaiq/
├── backend/
│   ├── app.py                    # FastAPI application entry point
│   ├── Agents/                   # AI agent modules
│   │   ├── Clinical_Trials/      # Clinical trial analysis agent
│   │   ├── Competitor_analysis/  # Competitor analysis agent
│   │   ├── Drug_Discovery/       # Drug discovery workflow
│   │   ├── Drug_Repurposing/     # Drug repurposing agent
│   │   ├── ESG_Report_Generator/ # ESG report generation
│   │   ├── Market_Insights/      # Market analysis agent
│   │   ├── Medicine_Validation/  # Medicine validation agent
│   │   ├── News/                 # News aggregation agent
│   │   └── Web_search/           # Web search agent
│   ├── Deep_Research/            # Deep research orchestrator
│   ├── Tools/                    # Utility tools and API wrappers
│   │   ├── Admet_properties.py   # ADMET prediction tool
│   │   ├── clinical_trial_tool.py
│   │   ├── PDBQueryTool.py       # Protein Data Bank queries
│   │   ├── UniProtAPI.py         # UniProt integration
│   │   └── ...
│   ├── Datasets/                 # Data files and preprocessing
│   └── model/                    # ML models
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── App.tsx           # Main application component
│   │   │   └── components/
│   │   │       ├── AgentPage.tsx # Agent interface orchestrator
│   │   │       └── agents/       # Agent-specific view components
│   │   ├── main.tsx              # Application entry point
│   │   └── styles/               # CSS styles
│   ├── package.json
│   └── vite.config.ts
├── reports/                      # Generated reports output
├── requirements.txt              # Python dependencies
└── README.md
```

## Troubleshooting

### Common Issues

**Backend fails to start:**
- Ensure all required environment variables are set in the `.env` file
- Verify Python version is 3.10 or higher
- Check that all dependencies are installed correctly

**Frontend cannot connect to backend:**
- Verify the backend is running on port 8000
- Check CORS settings if running on different ports
- Ensure `API_BASE_URL` matches your backend address

**API key errors:**
- Double-check that API keys are correctly set in the `.env` file
- Ensure there are no extra spaces or quotes around the keys
- Verify API key permissions and quotas

### Getting Help

If you encounter issues not covered here, please:
1. Check the existing GitHub issues
2. Create a new issue with detailed reproduction steps
3. Include relevant error messages and logs

## Contributing

We welcome contributions to PharmaIQ. Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'Add your feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines for Python code
- Use TypeScript for all frontend code
- Write meaningful commit messages
- Add tests for new functionality
- Update documentation as needed

## License

This project is developed for the EY Techathon competition. All rights reserved.

---

For questions or support, please open an issue on the GitHub repository.

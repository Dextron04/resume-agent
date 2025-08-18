# AI Resume Generator

## Phase 1: Core Foundation & Job Analysis Engine

This is the implementation of Phase 1 of the AI Resume Generator system, powered by **Anthropic Claude**.

### Features Implemented

- ✅ Knowledge base loading from existing JSON format
- ✅ Job description analysis using Anthropic Claude
- ✅ Technology extraction from project summaries
- ✅ Semantic similarity preparation (sentence-transformers)
- ✅ FastAPI backend structure
- ✅ Comprehensive error handling and logging
- ✅ Test suite for Phase 1 functionality

### Setup

#### Quick Setup (Recommended)

```bash
cd ai-resume-generator
./setup.sh
```

#### Manual Setup

1. Install dependencies:

```bash
cd ai-resume-generator
pip install -r requirements.txt
```

2. Configure environment:

```bash
cp .env.example .env
# Edit .env and add your Anthropic API key
```

**Getting an Anthropic API Key:**

1. Visit [Anthropic Console](https://console.anthropic.com/)
2. Sign up or log in to your account
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key and add it to your `.env` file:

   ```
   ANTHROPIC_API_KEY=your_api_key_here
   ```

6. Test the setup:

```bash
python test_anthropic.py
```

4. Run Phase 1 tests:

```bash
pytest tests/test_phase1.py -v
```

5. Start the API server:

```bash
uvicorn app.main:app --reload
```

### API Endpoints

- `GET /` - Root endpoint
- `GET /health` - Health check
- `POST /api/analyze-job` - Analyze job description
- `GET /api/knowledge-base/summary` - Get knowledge base summary

### Testing

Run the Phase 1 tests to verify core functionality:

```bash
# Run all Phase 1 tests
pytest tests/test_phase1.py -v

# Run specific test
pytest tests/test_phase1.py::TestPhase1::test_knowledge_base_loading -v
```

### Success Criteria for Phase 1

- [x] All knowledge base files load correctly
- [x] Job descriptions are analyzed and keywords extracted
- [x] Technologies are properly extracted from project summaries
- [x] All tests pass
- [x] Basic logging is implemented

### Next Steps

Phase 2 will implement:

- Semantic similarity engine using sentence-transformers
- Project relevance scoring based on job requirements
- Smart project selection (top 3-4 most relevant projects)
- Keyword matching system

### Project Structure

```
ai-resume-generator/
├── app/
│   ├── main.py              # FastAPI application
│   ├── models/              # Pydantic models
│   │   └── __init__.py
│   ├── services/            # Business logic
│   │   └── resume_agent.py  # Core AI agent
│   └── templates/           # LaTeX templates (future)
├── tests/
│   └── test_phase1.py       # Phase 1 tests
├── static/                  # Web interface files (future)
├── output/                  # Generated resumes (future)
├── requirements.txt         # Python dependencies
├── .env.example            # Environment configuration
└── README.md              # This file
```

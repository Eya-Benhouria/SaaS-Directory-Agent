# SaaS Directory Submission Agent

An **automated SaaS directory submission system** that submits your SaaS product to hundreds of directories without manual work. Built with AI-powered form detection and browser automation.

![Architecture](docs/architecture.png)

## 🎯 Features

- **AI-Powered Form Detection**: Uses GPT-4 Vision or Claude to intelligently detect and map form fields
- **Automated Browser Submission**: Playwright-based automation for reliable form filling
- **Background Processing**: Queue-based submission worker with retry logic
- **Dashboard Analytics**: Real-time monitoring of submission status and success rates
- **Multi-Directory Support**: Pre-configured with 20+ popular SaaS directories
- **Screenshot Capture**: Automatic screenshots after each submission for verification
- **Retry Mechanism**: Configurable retry logic for failed submissions

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (React)                         │
│  Dashboard │ Products │ Directories │ Submissions │ Settings    │
└─────────────────────────────┬───────────────────────────────────┘
                              │ REST API
┌─────────────────────────────▼───────────────────────────────────┐
│                      Backend (FastAPI)                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   API Routes │  │   Services   │  │   Workers    │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                  │
│  ┌──────────────────────────────────────────────────┐           │
│  │             Automation Layer                      │           │
│  │  ┌─────────────────┐  ┌────────────────────┐    │           │
│  │  │  Form Detector  │  │ Browser Automation │    │           │
│  │  │   (LLM-based)   │  │    (Playwright)    │    │           │
│  │  └─────────────────┘  └────────────────────┘    │           │
│  └──────────────────────────────────────────────────┘           │
└─────────────────────────────┬───────────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────────┐
│                      PostgreSQL Database                         │
│  Products │ Directories │ Submissions │ Logs │ Form Mappings    │
└─────────────────────────────────────────────────────────────────┘
```

## 📋 Prerequisites

- Docker & Docker Compose
- OpenAI API key (for GPT-4 Vision) OR Anthropic API key (for Claude)
- Node.js 20+ (for local frontend development)
- Python 3.11+ (for local backend development)

## 🚀 Quick Start

### 1. Clone the repository

```bash
git clone <repository-url>
cd saas-directory-agent
```

### 2. Configure environment variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your API keys
# Required: Either OPENAI_API_KEY or ANTHROPIC_API_KEY
```

### 3. Start with Docker Compose

```bash
docker-compose up -d
```

### 4. Run database migrations

```bash
docker-compose exec backend alembic upgrade head
```

### 5. Seed the database with default directories

```bash
docker-compose exec backend python seed_data.py
```

### 6. Access the application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 💻 Local Development

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Set environment variables
export DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/saas_directory
export OPENAI_API_KEY=your-api-key

# Run migrations
alembic upgrade head

# Seed data
python seed_data.py

# Start the server
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

## 📖 API Documentation

### Products

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/products` | List all SaaS products |
| POST | `/api/products` | Create a new product |
| GET | `/api/products/{id}` | Get product details |
| PUT | `/api/products/{id}` | Update a product |
| DELETE | `/api/products/{id}` | Delete a product |

### Directories

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/directories` | List all directories |
| POST | `/api/directories` | Add a new directory |
| GET | `/api/directories/{id}` | Get directory details |
| PUT | `/api/directories/{id}` | Update a directory |
| DELETE | `/api/directories/{id}` | Delete a directory |
| POST | `/api/directories/{id}/test` | Test submission (dry run) |

### Submissions

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/submissions` | List all submissions |
| POST | `/api/submissions` | Create a submission |
| POST | `/api/submissions/batch` | Create batch submissions |
| GET | `/api/submissions/{id}` | Get submission details |
| POST | `/api/submissions/{id}/retry` | Retry a failed submission |
| DELETE | `/api/submissions/{id}` | Delete a submission |

### Dashboard

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/dashboard/stats` | Get dashboard statistics |
| GET | `/api/dashboard/recent-activity` | Get recent submission activity |

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | - |
| `OPENAI_API_KEY` | OpenAI API key for GPT-4 | - |
| `ANTHROPIC_API_KEY` | Anthropic API key for Claude | - |
| `LLM_PROVIDER` | LLM provider (`openai` or `anthropic`) | `openai` |
| `LLM_MODEL` | Model to use | `gpt-4o` |
| `BROWSER_HEADLESS` | Run browser in headless mode | `true` |
| `MAX_CONCURRENT_SUBMISSIONS` | Max parallel submissions | `3` |

### Pre-configured Directories

The seed script includes 20+ popular directories:

- **Tier 1 (High Priority)**: Product Hunt, BetaList, Capterra, G2, AppSumo
- **Tier 2 (Medium Priority)**: SaaSHub, AlternativeTo, Indie Hackers, StackShare, GetApp
- **Tier 3 (Standard)**: Startup Stash, SideProjectors, StartupBuffer, Launching Next
- **Tier 4 (Additional)**: Slant, Land-book, TechPluto, MicroConf Connect

## 📊 How It Works

### 1. Add Your SaaS Product

Enter your product details including name, description, website URL, logo, and other metadata.

### 2. Select Target Directories

Choose which directories to submit to from the pre-configured list, or add custom directories.

### 3. Automated Submission

The system:
1. Opens the directory submission page
2. Takes a screenshot and uses AI to detect form fields
3. Maps your product data to the form fields
4. Fills out and submits the form
5. Captures a confirmation screenshot
6. Logs the result and updates the status

### 4. Monitor Progress

Track submission status, view success/failure rates, and retry failed submissions from the dashboard.

## 🛠️ Adding Custom Directories

1. Go to **Directories** → **Add Directory**
2. Enter the directory details:
   - Name and URL
   - Submission page URL
   - Category and priority
   - Custom field mappings (optional)

3. Test the submission with the "Test Submission" button

### Field Mappings Format

```json
{
  "name": "input[name='product_name']",
  "description": "textarea#description",
  "website_url": "input[type='url']",
  "tagline": ".tagline-input"
}
```

## 🔒 Security Considerations

- API keys are stored in environment variables, never in code
- All form submissions are logged for auditing
- Screenshots are captured for verification
- Rate limiting prevents abuse of target directories

## 🐛 Troubleshooting

### Common Issues

**1. Submissions failing with timeout**
- Increase `BROWSER_TIMEOUT` in settings
- Check if the directory website is accessible

**2. Form fields not detected**
- Try adding manual field mappings
- Ensure the LLM API key is valid

**3. CAPTCHA blocking submissions**
- Some directories have anti-bot protection
- Consider using human verification for these

**4. Database connection errors**
- Verify PostgreSQL is running
- Check DATABASE_URL format

### Viewing Logs

```bash
# Backend logs
docker-compose logs -f backend

# All services
docker-compose logs -f
```

## 📈 Roadmap

- [ ] CAPTCHA solving integration
- [ ] Email verification automation
- [ ] Scheduled submission batches
- [ ] Webhook notifications
- [ ] Chrome extension for manual assist mode
- [ ] Multi-product support
- [ ] Export/import directory configurations

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Playwright](https://playwright.dev/) for browser automation
- [FastAPI](https://fastapi.tiangolo.com/) for the backend framework
- [React](https://react.dev/) and [Vite](https://vitejs.dev/) for the frontend
- [OpenAI](https://openai.com/) and [Anthropic](https://anthropic.com/) for AI capabilities


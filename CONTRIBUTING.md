# Contributing to Jarvis AI Chatbot

## Getting Started

1. Clone the repository:
   ```bash
   git clone https://github.com/SOUMYADIPKA/chatbot.git
   cd chatbot
   ```

2. Create and activate virtual environment:
   ```bash
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1  # Windows PowerShell
   # or
   source .venv/bin/activate  # Unix/Linux
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Before You Start Working

### Set up your Git account locally:
```bash
git config user.name "Your Name"
git config user.email "your.email@example.com"
```

### Create a branch for your feature:
```bash
git checkout -b feature/your-feature-name
```

## Development Workflow

1. **Always work on a feature branch**
   - Format: `feature/feature-name`, `fix/bug-name`, `docs/documentation-name`

2. **Make small, focused commits**
   ```bash
   git add .
   git commit -m "Brief description of changes"
   ```

3. **Push to your branch**
   ```bash
   git push origin feature/your-feature-name
   ```

4. **Create a Pull Request**
   - Describe what you changed and why
   - Reference any issue numbers
   - Request review from other team members

## Code Standards

- Use meaningful variable and function names
- Add comments for complex logic
- Follow PEP 8 for Python code
- Test changes before pushing

## Features You Can Work On

- **Voice Recognition**: Improve Whisper integration
- **NLP**: Enhance spaCy conversation templates
- **API Integration**: Add more weather/news/stock sources
- **Automation**: Expand PyAutoGUI/Selenium capabilities
- **UI/UX**: Improve Tkinter interface
- **Database**: Optimize SQLite command memory
- **Offline Mode**: Improve offline spaCy responses

## Team Members

- Sanjib Karan (Project Lead)
- 4 additional team members

## Questions?

Ask in the team chat or create an issue in GitHub.

Good luck and happy coding!

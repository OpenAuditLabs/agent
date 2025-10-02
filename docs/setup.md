# Setup Guide

This guide will help you set up the OAL Agent development env### 4. Install Pre-commit Hooks

```bash
pre-commit install
```

### 5. Configure Environment Variablest.

## Table of Contents

- [System Requirements](#system-requirements)
- [Initial Setup](#initial-setup)
- [Development Environment](#development-environment)
- [Running Tests](#running-tests)
- [IDE Configuration](#ide-configuration)
- [Troubleshooting](#troubleshooting)

## System Requirements

### Required

- **Python**: 3.9 or higher (3.11 recommended)
- **pip**: Latest version
- **Git**: For version control
- **Redis**: 6.0+ for queue management

### Recommended

- **Docker**: For containerized development
- **PostgreSQL**: 13+ for production database (SQLite works for development)
- **Solidity Compiler (solc)**: For smart contract compilation

### Operating Systems

- Linux (Ubuntu 20.04+, Debian 11+)
- macOS (11.0+)
- Windows (via WSL2)

## Initial Setup

### 1. Clone the Repository

```bash
git clone https://github.com/OpenAuditLabs/agent.git
cd agent
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate on Linux/macOS
source .venv/bin/activate

# Activate on Windows
.venv\Scripts\activate
```

### 3. Install Python Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install production dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt
```

### 4. Install Pre-commit Hooks

```bash
pre-commit install
```

### 6. Configure Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your settings
nano .env  # or your preferred editor
```

**Required environment variables:**

```bash
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Database
DATABASE_URL=sqlite:///./oal_agent.db

# Queue (Redis)
QUEUE_URL=redis://localhost:6379

# LLM Provider
LLM_PROVIDER=openai
LLM_API_KEY=your-api-key-here

# Security
SECRET_KEY=generate-a-random-secret-key

# Logging
LOG_LEVEL=INFO
```

### 6. Install External Tools

#### Slither (Static Analysis)

```bash
pip install slither-analyzer
```

#### Mythril (Symbolic Execution)

```bash
pip install mythril
```

#### Solc (Solidity Compiler)

```bash
# On Linux
sudo add-apt-repository ppa:ethereum/ethereum
sudo apt-get update
sudo apt-get install solc

# On macOS
brew tap ethereum/ethereum
brew install solidity

# Or use solc-select for version management
pip install solc-select
solc-select install 0.8.0
solc-select use 0.8.0
```

### 7. Start Redis

```bash
# On Linux
sudo systemctl start redis

# On macOS
brew services start redis

# Or run in foreground
redis-server
```

### 8. Verify Installation

```bash
# Run health check
python src/oal_agent/cli.py serve &
sleep 2
curl http://localhost:8000/health
```

## Development Environment

### Running the Development Server

```bash
# Start with auto-reload
python src/oal_agent/cli.py serve --host 0.0.0.0 --port 8000

# Access API docs at: http://localhost:8000/docs
```

### Running Tests

```bash
# Run all tests
bash scripts/test.sh

# Run specific test suites
pytest tests/unit/ -v
pytest tests/integration/ -v
pytest tests/e2e/ -v

# Run with coverage
pytest --cov=src/oal_agent --cov-report=html
```

### Code Quality Checks

```bash
# Format code
bash scripts/format.sh

# Run linters
bash scripts/lint.sh

# Run pre-commit checks
pre-commit run --all-files
```

## IDE Configuration

### VS Code

The project includes `.vscode/settings.json` with recommended settings.

**Recommended Extensions:**

- Python (ms-python.python)
- Pylance (ms-python.vscode-pylance)
- Black Formatter (ms-python.black-formatter)
- isort (ms-python.isort)
- GitLens (eamodio.gitlens)

### PyCharm

1. Open the project
2. Configure Python interpreter: Settings → Project → Python Interpreter
3. Select the `.venv` virtual environment
4. Enable Black formatter: Settings → Tools → Black
5. Enable pytest: Settings → Tools → Python Integrated Tools

## Troubleshooting

### Python Version Issues

```bash
# Check Python version
python --version

# If needed, use pyenv to manage Python versions
curl https://pyenv.run | bash
pyenv install 3.11
pyenv local 3.11
```

### Import Errors

```bash
# Ensure you're in the virtual environment
which python  # Should point to .venv/bin/python

# Add src to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:${PWD}/src"
```

### Redis Connection Issues

```bash
# Check if Redis is running
redis-cli ping

# Should return: PONG

# Check Redis logs
tail -f /var/log/redis/redis-server.log
```

### Permission Errors

```bash
# Make scripts executable
chmod +x scripts/*.sh

# Fix ownership if needed
sudo chown -R $USER:$USER .
```

### Database Issues

```bash
# For SQLite, simply delete and recreate
rm oal_agent.db

# For PostgreSQL
dropdb oal_agent
createdb oal_agent
```

### Dependency Conflicts

```bash
# Clear pip cache
pip cache purge

# Reinstall from scratch
pip uninstall -r requirements.txt -y
pip install -r requirements.txt
```

## Next Steps

- Read the [Architecture documentation](architecture.md)
- Explore the [API documentation](api.md)
- Check out [Contributing guidelines](../CONTRIBUTING.md)
- Join our [GitHub Discussions](https://github.com/OpenAuditLabs/agent/discussions)

## Getting Help

If you encounter issues not covered here:

1. Check [GitHub Issues](https://github.com/OpenAuditLabs/agent/issues)
2. Search [GitHub Discussions](https://github.com/OpenAuditLabs/agent/discussions)
3. Create a new issue with:
   - Your OS and Python version
   - Steps to reproduce
   - Error messages
   - What you've tried

---

**Last Updated**: October 2025

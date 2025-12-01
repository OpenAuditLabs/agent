# OAL Agent - Smart Contract Security Analysis System

[![License: AGPL v3](https://img.shield3. **Configure environment**

```bash
cp .env.example .env
# Edit .env with your configuration
```

**Key environment variables:**

- `API_HOST` / `API_PORT`: API server configuration
- `DATABASE_URL`: Database connection string
- `QUEUE_URL`: Redis connection string
- `LLM_PROVIDER`: LLM provider (openai, anthropic, etc.)
- `LLM_API_KEY`: API key for LLM provider
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)

4. **Install pre-commit hooks**nse-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
   [![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
   [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A multi-agent system for comprehensive smart contract security analysis using static analysis, dynamic testing, and machine learning.

## ⚠️ Project Status

**🚧 Under Active Development** - This project is currently in early development. APIs and features are subject to change.

## ✨ Features

- 🤖 **Multi-Agent Architecture**: Specialized agents for different analysis types
- 🔍 **Static Analysis**: Integration with Slither and other static analyzers
- 🧪 **Dynamic Analysis**: Symbolic execution and fuzzing capabilities
- 🧠 **ML-Powered Detection**: Machine learning models for vulnerability detection
- 🔌 **REST API**: Easy integration with existing workflows
- 📊 **Comprehensive Reporting**: Detailed vulnerability reports with severity classification
- 🔐 **Sandboxed Execution**: Safe contract analysis in isolated environments
- 📈 **Telemetry & Monitoring**: Built-in logging, metrics, and tracing

## 🏗️ Project Structure

```
agent/
├── .github/workflows/     # CI/CD workflows
├── .vscode/              # VS Code settings
├── scripts/              # Utility scripts (lint, test, format)
├── docs/                 # Documentation
│   ├── architecture.md   # System architecture
│   ├── agents.md        # Agent documentation
│   ├── api.md           # API documentation
│   ├── pipelines.md     # Pipeline documentation
│   └── research/        # Research papers and notes
├── models/              # ML models
│   ├── transformers/    # Transformer models
│   └── gnn/            # Graph Neural Network models
├── data/               # Data storage
│   ├── contracts/      # Smart contract samples
│   └── datasets/       # Training datasets
├── tests/              # Test suites
│   ├── unit/          # Unit tests
│   ├── integration/   # Integration tests
│   ├── e2e/           # End-to-end tests
│   ├── load/          # Load tests
│   └── fixtures/      # Test fixtures
├── src/oal_agent/     # Main source code
│   ├── app/           # FastAPI application
│   ├── core/          # Core orchestration
│   ├── agents/        # Analysis agents
│   ├── tools/         # External tool integrations
│   ├── services/      # Background services
│   ├── llm/           # LLM integration
│   ├── security/      # Security components
│   ├── telemetry/     # Logging & metrics
│   ├── utils/         # Utilities
│   └── cli.py         # Command-line interface
└── Configuration files (pyproject.toml, requirements.txt, etc.)
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9+ (3.11 recommended)
- Redis (for job queue management)
- PostgreSQL or SQLite (for result storage)
- Solidity compiler (solc) for contract analysis
- Optional: Docker for containerized deployment

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/OpenAuditLabs/agent.git
   cd agent
   ```

2. **Set up Python environment**

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

3. **Configure environment**

   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   # For profile-specific settings, create .env.<profile_name> files (e.g., .env.dev, .env.prod)
   ```

   **Key environment variables:**

   - `API_HOST` / `API_PORT`: API server configuration
   - `DATABASE_URL`: Database connection string
   - `QUEUE_URL`: Redis connection string
   - `LLM_PROVIDER`: LLM provider (openai, anthropic, etc.)
   - `LLM_API_KEY`: API key for LLM provider
   - `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)

4. **Install pre-commit hooks**
   ```bash
   pre-commit install
   ```

For detailed setup instructions, see the [Setup Guide](docs/setup.md).

### Running the Application

**Start the API server:**

```bash
# Using module notation
python -m src.oal_agent.cli serve

# Or directly
python src/oal_agent/cli.py serve

# With custom host/port
python src/oal_agent/cli.py serve --host 0.0.0.0 --port 8080

# With a specific configuration file
python src/oal_agent/cli.py --config ~/.oal_agent.env serve

# With a profile-specific configuration (e.g., .env.dev)
python src/oal_agent/cli.py --profile dev serve
```

**Analyze a contract:**

```bash
python src/oal_agent/cli.py analyze path/to/contract.sol
```

Access the API:



- API Documentation: [API Documentation](http://localhost:8000/docs)

- Health Check: [Health Check](http://localhost:8000/health)



### API Usage Example



```python

import httpx



# Submit a contract for analysis

async with httpx.AsyncClient() as client:

    response = await client.post(

        "http://localhost:8000/api/v1/analysis/",

        json={

            "contract_code": "pragma solidity ^0.8.0; contract Example { ... }",

            "pipeline": "standard"

        }

    )

    job = response.json()

    job_id = job["job_id"]



    # Check job status

    status_response = await client.get(f"http://localhost:8000/api/v1/analysis/{job_id}")

    print(status_response.json())



    # Get results when complete

    results_response = await client.get(f"http://localhost:8000/api/v1/analysis/{job_id}/results")

    print(results_response.json())

```



### CLI Quickstart (Under Development)







The `oal-agent analyze` CLI command is currently under development.







This feature will provide direct command-line access to the agent's analysis functionalities.







For current progress and details, please refer to the relevant GitHub issue or pull request (e.g., [#XXX](https://github.com/OpenAuditLabs/agent/issues/XXX)).

## 🧪 Testing

**Run all tests:**

```bash
bash scripts/test.sh
```

**Run specific test suites:**

```bash
pytest tests/unit/ -v
pytest tests/integration/ -v
pytest tests/e2e/ -v
```

**Run with coverage:**

```bash
pytest tests/ --cov=src/oal_agent --cov-report=html
```

## 🔧 Development

**Format code:**

```bash
bash scripts/format.sh
# Or manually:
black src/ tests/
isort src/ tests/
```

**Run linters:**

```bash
bash scripts/lint.sh
# Includes: black, isort, flake8, mypy
```

**Check code quality:**

```bash
# Run all checks
pre-commit run --all-files

# Run specific checks
black --check src/ tests/
flake8 src/ tests/
mypy src/
```

## 📦 Project Components

### Core Components

- **Orchestrator**: Manages the overall analysis workflow
- **Pipeline**: Defines analysis sequences
- **Config**: Centralized configuration management

### Agents

- **Coordinator Agent**: Routes tasks to specialized agents
- **Static Agent**: Static code analysis using Slither, etc.
- **Dynamic Agent**: Symbolic execution and fuzzing
- **ML Agent**: Machine learning-based vulnerability detection

### Tools Integration

- **Slither**: Static analysis
- **Mythril**: Symbolic execution
- **Sandbox**: Safe contract execution environment

### Services

- **Queue Service**: Job queue management
- **Results Sink**: Collects and stores results
- **Storage Service**: Persistent data storage

### LLM Integration

- **Provider**: LLM API integration
- **Prompts**: Specialized prompts for analysis
- **Guards**: Safety and validation guardrails

## 🔐 Security

- Input validation for all user inputs
- Sandboxed execution environment
- Security policies and permissions
- See [SECURITY.md](SECURITY.md) for details

## 📖 Documentation

- [Setup Guide](docs/setup.md) - Detailed installation and configuration
- [Architecture](docs/architecture.md) - System design and components
- [Agents](docs/agents.md) - Agent types and responsibilities
- [API](docs/api.md) - REST API documentation
- [Pipelines](docs/pipelines.md) - Analysis pipeline configurations
- [Research Papers](docs/research/) - Research documentation and papers

## ❓ Troubleshooting

### Common Issues

**Import errors after installation:**

```bash
# Make sure you're in the virtual environment
source .venv/bin/activate
# Reinstall dependencies
pip install -r requirements.txt
```

**Redis connection errors:**

```bash
# Check if Redis is running
redis-cli ping
# Start Redis if needed
redis-server
```

**Permission errors on scripts:**

```bash
# Make scripts executable
chmod +x scripts/*.sh
```

**Module not found errors:**

```bash
# Add src to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:${PWD}/src"
```

For more help, see [GitHub Issues](https://github.com/OpenAuditLabs/agent/issues) or contact the team.

## 🤝 Contributing

We welcome contributions! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

### Development Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and linters (`bash scripts/test.sh && bash scripts/lint.sh`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📊 Roadmap

- [ ] Complete core agent implementations
- [ ] Add support for more static analysis tools
- [ ] Implement ML model training pipeline
- [ ] Add support for multiple blockchain platforms
- [ ] Create web dashboard for analysis results
- [ ] Implement real-time analysis streaming
- [ ] Add plugin system for custom analyzers

## 🐛 Bug Reports & Feature Requests

Please use the [GitHub Issues](https://github.com/OpenAuditLabs/agent/issues) to report bugs or request features.

## 💬 Community & Support

- **GitHub Discussions**: [Join the conversation](https://github.com/OpenAuditLabs/agent/discussions)
- **Issues**: [Report bugs or request features](https://github.com/OpenAuditLabs/agent/issues)
- **Security**: See [SECURITY.md](SECURITY.md) for reporting security vulnerabilities

## 📄 License

This project is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0) - see the [LICENSE](LICENSE) file for details.

Key points:

- ✅ You can use, modify, and distribute this software
- ✅ You must disclose source code of any modifications
- ✅ Network use counts as distribution (you must share your modifications)
- ✅ You must license derivative works under AGPL-3.0

## 🙏 Acknowledgments

- [OpenAuditLabs](https://github.com/OpenAuditLabs) team and contributors
- Open source security tools community ([Slither](https://github.com/crytic/slither), [Mythril](https://github.com/ConsenSys/mythril), etc.)
- Smart contract security researchers and auditors worldwide

---

**Made with ❤️ by OpenAuditLabs**

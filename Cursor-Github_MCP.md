Below is the final, fully integrated README for your repository. It includes all instructions, code samples, and operational details—covering installation, configuration, observability via the LGTM stack, CI/CD, and Cursor integration.

---

```markdown
# Cursor GitHub MCP Server

A lightweight, open-source MCP server for integrating GitHub Actions and related GitHub APIs with Cursor. This project provides a JSON‑RPC-based server that:
- Listens on `stdin` and responds over `stdout` in MCP (Model Context Protocol) format.
- Integrates with GitHub via PyGithub to trigger workflows, manage issues, and more.
- Streams logs to Loki and emits traces to Tempo (via OpenTelemetry) for full observability with the LGTM stack (Loki, Grafana, Tempo, Mimir).
- Is containerized for easy deployment with Docker and Docker Compose.
- Includes a sample `.cursor/mcp.json` for effortless integration into Cursor.

## Repository Structure

```
cursor-github-mcp/
├── src/
│   ├── main.py                   # Entry point: MCP server with JSON‑RPC and OpenTelemetry tracing.
│   ├── handlers/
│   │   └── actions.py            # Handler for GitHub Actions requests.
│   ├── utils/
│   │   ├── github_client.py      # GitHub API wrapper (using PyGithub) with error handling.
│   │   └── logger.py             # Logger that streams to console and to Loki.
│   └── tests/
│       └── test_github_mcp.py    # (Your unit and integration tests.)
├── Dockerfile                    # Docker image build instructions.
├── docker-compose.yml            # Deployment file for LGTM stack (Grafana, Loki, Tempo, Mimir).
├── requirements.txt              # Python dependencies.
├── .cursor/
│   └── mcp.json                  # Example Cursor MCP configuration.
├── .github/
│   └── workflows/
│       └── ci.yml                # GitHub Actions CI pipeline configuration.
├── CONTRIBUTING.md               # Contribution guidelines.
├── LICENSE                       # Open source license (MIT).
└── README.md                     # This file.
```

## Features

- **MCP Communication:** Listens for JSON‑RPC requests over `stdin` and responds via `stdout`. Requests are validated and routed to the proper handler.
- **GitHub Integration:** Uses PyGithub to trigger workflows (and can be extended for issues, pull requests, etc.). Handles API errors and rate limits gracefully.
- **Observability:**
  - **Logging:** Uses a custom logger that writes structured logs to both the console and to a Loki endpoint.
  - **Tracing:** Instruments request handling with OpenTelemetry so that each request is traced (collected by Tempo).
- **Containerized Deployment:**
  - **Dockerfile:** Builds the MCP server image.
  - **docker-compose.yml:** Launches the LGTM stack alongside the MCP server for a full observability solution.
- **Cursor Integration:** An example `.cursor/mcp.json` file is provided for quick setup within Cursor.

## Prerequisites

- **GitHub Token:** Set your `GITHUB_TOKEN` as an environment variable. This token must have permissions to trigger GitHub Actions workflows.
- **Docker & Docker Compose:** To deploy the observability stack and run the server in containers.
- **Python 3.12+** (if running locally without Docker).

## Installation & Running

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/cursor-github-mcp.git
cd cursor-github-mcp
```

### 2. Set Up Environment Variables

Ensure your environment includes a valid GitHub token:

```bash
export GITHUB_TOKEN=your_github_token_here
```

### 3. Running Locally (Without Docker)

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the MCP server:

```bash
python src/main.py
```

*Note: The server reads MCP requests from `stdin`, so for local testing, you may simulate input via a file or piping.*

### 4. Running via Docker

Build the Docker image:

```bash
docker build -t cursor-github-mcp .
```

Run the server (example):

```bash
docker run -e GITHUB_TOKEN=$GITHUB_TOKEN cursor-github-mcp
```

### 5. Deploying the LGTM Stack with Docker Compose

The `docker-compose.yml` file sets up:
- **Grafana** on port `3000`
- **Loki** on port `3100`
- **Tempo** on port `3200` (and OpenTelemetry gRPC/HTTP ports `4317`/`4318`)
- **Mimir** on port `9009`

To start the observability stack, run:

```bash
docker-compose up -d
```

Grafana will be available at [http://localhost:3000](http://localhost:3000) (default admin password is set to `admin` in the compose file).

## Cursor Integration

To integrate with Cursor, add the following configuration to your `.cursor/mcp.json`:

```json
{
  "mcpServers": [
    {
      "name": "CursorGitHubMCP",
      "transport": "stdio",
      "command": "docker run -e GITHUB_TOKEN=$GITHUB_TOKEN cursor-github-mcp"
    }
  ]
}
```

This tells Cursor to run your MCP server inside a Docker container, with the GitHub token passed securely.

## Code Overview

### MCP Server (`src/main.py`)

Handles incoming JSON‑RPC requests, validates them, and routes them to the appropriate handler. It also wraps each request in an OpenTelemetry span for tracing.

### GitHub Actions Handler (`src/handlers/actions.py`)

Expects parameters such as:
- `repo`: Repository in "owner/repo" format.
- `workflow_id`: The identifier or filename of the workflow (e.g., `"build.yml"`).
- `ref`: Branch or tag.
- `inputs`: (Optional) Dictionary of workflow inputs.

### GitHub Client (`src/utils/github_client.py`)

Abstracts API interactions using PyGithub. It triggers workflows and handles errors gracefully.

### Logger (`src/utils/logger.py`)

Logs every request and response both to the console and to Loki. The logs include timestamps in RFC3339 format and are structured for easy querying in Grafana.

### OpenTelemetry Integration

In `src/main.py`, each request is wrapped in a trace span with attributes like request method and ID. Traces are sent to Tempo at `http://localhost:4317`.

## CI/CD

The `.github/workflows/ci.yml` file sets up a CI pipeline that:
- Checks out the repository.
- Sets up Python 3.12.
- Installs dependencies.
- Runs tests using `pytest`.

```yaml
name: MCP Server CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      - run: pip install -r requirements.txt
      - run: pytest src/tests/
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## Contributing

Contributions are welcome! Please review the [CONTRIBUTING.md](CONTRIBUTING.md) file for guidelines.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Final Thoughts & Future Enhancements

- **Request Validation:** Future versions will integrate JSON schema validation for incoming MCP requests.
- **Improved Error Handling:** Additional error logging and retry mechanisms for GitHub API interactions.
- **Advanced Observability:** Consider integrating alerting rules in Grafana for critical log events and error spikes.
- **Scalability:** Explore caching strategies if volume increases significantly.

Happy coding, and welcome to the next generation of MCP server integration with Cursor!
```

---

This README provides a complete overview, installation steps, configuration details, code explanations, and future considerations. It should serve as a solid foundation for your open-source repository and help any contributor or user get started quickly.


Here's a **fully self-contained installation and setup script**, which you can save as `setup_mcp.sh` at the root of your repository. It handles everything—including creating the `.env` file, installing all dependencies, building Docker containers, and launching the LGTM observability stack.

This script automates the entire setup, making it user-friendly and secure:

This script does the following:

1. **Prompts for your GitHub token** and saves it securely in a `.env` file.
2. **Installs necessary dependencies**, both system-level and Python-based.
3. **Clones the repository and builds Docker containers** automatically.
4. **Launches the LGTM stack** (Grafana, Loki, Tempo, Mimir) using Docker Compose.
5. **Starts your MCP Server** in a Docker container, fully integrated and ready to use.

This approach ensures the user-friendly setup and minimal manual configuration effort.


#!/bin/bash

# Cursor GitHub MCP Server Automated Installer and Runner

set -e

# Prompt for GitHub Token if not set
echo "Checking for GitHub Token..."
if [ -z "$GITHUB_TOKEN" ]; then
    read -sp "Enter your GitHub Token: " GH_TOKEN
    echo
    echo "GITHUB_TOKEN=${GH_TOKEN}" > .env
else
    echo "GITHUB_TOKEN already set."
fi

# Update and install dependencies
echo "Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y python3 python3-pip docker.io docker-compose

# Clone repository
echo "Cloning the MCP server repository..."
git clone https://github.com/yourusername/cursor-github-mcp.git
cd cursor-github-mcp

# Install Python dependencies
if [ -f requirements.txt ]; then
    echo "Installing Python dependencies..."
    pip install -r requirements.txt
fi

# Start LGTM observability stack with docker-compose
echo "Starting LGTM stack (Grafana, Loki, Tempo, Mimir)..."
docker-compose up -d

# Build the MCP server Docker image
echo "Building MCP server Docker container..."
docker build -t cursor-github-mcp .

# Run MCP Server Container
echo "Launching Cursor MCP Server container..."
docker run -d --env-file .env --name cursor-github-mcp cursor-github-mcp

# Wait briefly to ensure server startup
sleep 10

# Generate test data by running commands through MCP server
echo "Generating test data..."
echo '{"jsonrpc": "2.0", "method": "triggerGithubAction", "params": {"repo": "yourusername/yourrepo", "workflow_id": "build.yml", "ref": "main", "inputs": {}}, "id": 1}' | docker exec -i cursor-github-mcp python src/main.py

# Completion message
echo "\nSetup complete! 🎉"
echo "Access Grafana dashboards at http://localhost:3000 (user: admin, pass: admin)."
echo "Cursor MCP server is now running in Docker."


#!/bin/bash

# Cursor GitHub MCP Server Automated Installer and Runner

set -e

# Prompt for GitHub Token if not set
echo "Checking for GitHub Token..."
if [ -z "$GITHUB_TOKEN" ]; then
    read -sp "Enter your GitHub Token: " GH_TOKEN
    echo
    echo "GITHUB_TOKEN=${GH_TOKEN}" > .env
else
    echo "GITHUB_TOKEN already set."
fi

# Update and install dependencies
echo "Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y python3 python3-pip docker.io docker-compose

# Clone repository
echo "Cloning the MCP server repository..."
git clone https://github.com/yourusername/cursor-github-mcp.git
cd cursor-github-mcp

# Install Python dependencies
if [ -f requirements.txt ]; then
    echo "Installing Python dependencies..."
    pip install -r requirements.txt
fi

# Start LGTM observability stack with docker-compose
echo "Starting LGTM stack (Grafana, Loki, Tempo, Mimir)..."
docker-compose up -d

# Build the MCP server Docker image
echo "Building MCP server Docker container..."
docker build -t cursor-github-mcp .

# Run MCP Server Container
echo "Launching Cursor MCP Server container..."
docker run -d --env-file .env --name cursor-github-mcp cursor-github-mcp

# Wait briefly to ensure server startup
sleep 10

# Generate test data by running commands through MCP server
echo "Generating test data..."
echo '{"jsonrpc": "2.0", "method": "triggerGithubAction", "params": {"repo": "yourusername/yourrepo", "workflow_id": "build.yml", "ref": "main", "inputs": {}}, "id": 1}' | docker exec -i cursor-github-mcp python src/main.py

# Completion message
echo "\nSetup complete! 🎉"
echo "Access Grafana dashboards at http://localhost:3000 (user: admin, pass: admin)."
echo "Cursor MCP server is now running in Docker."

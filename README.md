# MAS Multi-Agents MVP
Multi-agent architecture using Magentic-One agent from Autogen

## Table of Contents
- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Architecture](#architecture)
- [Security](#security)
- [Contributing](#contributing)
- [License](#license)

## Overview
This project implements a multi-agent system using the Magentic-One agent from Autogen. It provides a framework for collaborative problem-solving using specialized AI agents that can interact with various services including Azure OpenAI, Azure Monitor, and Dynatrace.

## Prerequisites
- Python 3.13.2
- Docker (optional)
- Azure account with OpenAI service
- Dynatrace account (optional)
- Azure Monitor workspace (optional)

## Installation

### Local Development
1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Docker
1. Build the image:
   ```bash
   docker build -t mas-app .
   ```
2. Run the container:
   ```bash
   docker run --env-file .env -p 8080:8080 mas-app
   ```

## Configuration
Create a `.env` file based on `.env.example` with your configuration:

```bash
# Server Configuration
PORT=8080
ENVIRONMENT=dev

# Azure OpenAI Configuration
AZURE_OPENAI_DEPLOYMENT=your-deployment-name
AZURE_OPENAI_MODEL=your-model-name
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key
LLM_MODEL_SCOPE=https://cognitiveservices.azure.com/.default

# Azure Configuration
RESOURCE_GROUP=your-resource-group
AKS_CLUSTER_NAME=your-aks-cluster
AZURE_MONITOR_WORKSPACE_ID=your-workspace-id

# Dynatrace Configuration
DYNATRACE_API_KEY=your-api-key
DYNATRACE_API_ENDPOINT=https://your-environment.live.dynatrace.com
DYNATRACE_CLIENT_ID=your-client-id
DYNATRACE_CLIENT_SECRET=your-client-secret
DYNATRACE_ACCOUNT_URN=your-account-urn
```

## Usage

### API Endpoints
- POST `/`: Submit a task for the agents to process
  ```bash
  curl -X POST http://localhost:8080 \
    -H "Content-Type: application/json" \
    -d '{"task":"Write a Python script to fetch data from an API."}'
  ```

### Available Agents
- Dynatrace Specialist: Handles Dynatrace-related tasks
- AKS Specialist: Manages Kubernetes operations
- Azure Monitor Specialist: Handles Azure Monitor queries

## Architecture
The architecture runs the MAS in Azure Kubernetes Service as a deployment. It is a full stateless application at the Kubernetes level and relies on external services to persist any information such as secrets or AI Agents history. The agents use AKS workload identity model to access resources needed to perform their jobs.

## Security
- All sensitive information should be stored in environment variables
- Use Azure Key Vault for production secrets
- Follow the principle of least privilege
- Regularly rotate API keys and credentials
- Monitor and audit access to sensitive resources

## Contributing
Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
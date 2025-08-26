# Claude Code in AgentCore

Inspired by [xiehust/agentcore_demo](https://github.com/xiehust/agentcore_demo). This learning project contains scripts and tools to build, deploy, and invoke Claude Code using Amazon Bedrock AgentCore.

## 🚀 Quick Start

### Prerequisites

Before you begin, ensure you have:

- **AWS CLI** configured with appropriate permissions
- **Docker** with buildx support for ARM64 builds
- **Python 3.11+** for running deployment scripts
- **AWS Account** with Bedrock AgentCore access
- **IAM Role** named `AgentRuntimeRole` with necessary permissions

### Required AWS Permissions

Your AWS credentials need permissions for:
- Amazon ECR (create repositories, push images)
- Amazon Bedrock AgentCore (create and invoke agent runtimes)
- IAM (for the AgentRuntimeRole)

## 📁 Project Structure

```
claude-code-agentcore/
├── agent.py              # FastAPI agent implementation
├── scripts/              # Deployment and management scripts
│   ├── build_push.sh     # Build and push Docker image to ECR
│   ├── deploy_agent.py   # Deploy agent runtime to Bedrock AgentCore
│   └── invoke_agent.py   # Invoke the deployed agent
├── docker/               # Container configuration
│   ├── Dockerfile        # Container setup
│   └── requirements.txt  # Python dependencies
└── README.md             # This guide
```

## 🛠️ Step-by-Step Deployment

### Step 1: Build and Push Docker Image

Use the `build_push.sh` script to build your Docker image and push it to Amazon ECR:

```bash
# Basic usage (uses default region us-east-1)
./scripts/build_push.sh --account-id YOUR_ACCOUNT_ID

# With custom parameters
./scripts/build_push.sh \
  --account-id YOUR_ACCOUNT_ID \
  --region us-west-2 \
  --repository-name my-claude-agent \
  --version v1.0.0
```

**Script Parameters:**
- `--account-id` (required): Your AWS Account ID
- `--region` (optional): AWS Region (default: us-east-1)
- `--repository-name` (optional): ECR repository name (default: claude-code-agentcore)
- `--version` (optional): Docker image tag (default: latest)

**What this script does:**
1. Creates ECR repository if it doesn't exist
2. Authenticates Docker with ECR
3. Builds ARM64 Docker image (required by AgentCore)
4. Pushes image to ECR
5. Verifies successful deployment

### Step 2: Deploy Agent Runtime

Use the `deploy_agent.py` script to create an agent runtime in Bedrock AgentCore:

```bash
# Basic usage
python scripts/deploy_agent.py --account-id YOUR_ACCOUNT_ID

# With custom parameters
python scripts/deploy_agent.py \
  --account-id YOUR_ACCOUNT_ID \
  --region us-west-2 \
  --repository-name my-claude-agent \
  --version v1.0.0
```

**Script Parameters:**
- `--account-id` (required): Your AWS Account ID
- `--region` (optional): AWS Region (default: us-east-1)
- `--repository-name` (optional): ECR repository name (default: claude-code-agentcore)
- `--version` (optional): Docker image tag (default: latest)

**Important Notes:**
- The script assumes an IAM role named `AgentRuntimeRole` exists in your account
- The agent runtime name will be `claude_code_agentcore`
- Save the returned Agent Runtime ARN for the next step

### Step 3: Invoke Your Agent

Use the `invoke_agent.py` script to interact with your deployed agent:

```bash
# Basic usage with default prompt
python scripts/invoke_agent.py --agent-runtime-arn "YOUR_AGENT_RUNTIME_ARN"

# With custom prompt
python scripts/invoke_agent.py \
  --agent-runtime-arn "YOUR_AGENT_RUNTIME_ARN" \
  --prompt "What tools do you have available?"

# With all parameters
python scripts/invoke_agent.py \
  --agent-runtime-arn "YOUR_AGENT_RUNTIME_ARN" \
  --prompt "Help me analyze this data" \
  --region us-west-2 \
  --runtime-session-id "my-unique-session-id-12345678901234567890"
```

**Script Parameters:**
- `--agent-runtime-arn` (required): ARN returned from deploy_agent.py
- `--prompt` (optional): Message to send (default: "Show me tools you got.")
- `--region` (optional): AWS Region (default: us-east-1)
- `--runtime-session-id` (optional): Session ID (must be 33+ characters)

## 🏗️ Architecture

The Claude Code Agent follows the Amazon Bedrock AgentCore requirements:

- **ARM64 Architecture**: All containers must be built for linux/arm64
- **Required Endpoints**: 
  - `/invocations` (POST): Main agent interaction endpoint
  - `/ping` (GET): Health check endpoint
- **Port 8080**: Standard port for AgentCore applications
- **FastAPI Framework**: Lightweight, fast web framework for the agent server

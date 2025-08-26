#!/bin/bash

# Default values
DEFAULT_REGION="us-east-1"
DEFAULT_REPOSITORY_NAME="claude-code-agentcore"
DEFAULT_VERSION="latest"

# Function to display usage
usage() {
    echo "Usage: $0 --account-id ACCOUNT_ID [OPTIONS]"
    echo ""
    echo "Required arguments:"
    echo "  --account-id         AWS Account ID"
    echo ""
    echo "Optional arguments:"
    echo "  --region             AWS Region (default: $DEFAULT_REGION)"
    echo "  --repository-name    ECR Repository name (default: $DEFAULT_REPOSITORY_NAME)"
    echo "  --version           Docker image version/tag (default: $DEFAULT_VERSION)"
    echo "  --help              Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --account-id 123456789012"
    echo "  $0 --account-id 123456789012 --region us-west-2 --version v1.0.0"
    echo "  $0 --account-id 123456789012 --repository-name my-agent --version latest"
}

# Initialize variables with defaults
REGION="$DEFAULT_REGION"
REPOSITORY_NAME="$DEFAULT_REPOSITORY_NAME"
VERSION="$DEFAULT_VERSION"
ACCOUNT_ID=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --account-id)
            ACCOUNT_ID="$2"
            shift 2
            ;;
        --region)
            REGION="$2"
            shift 2
            ;;
        --repository-name)
            REPOSITORY_NAME="$2"
            shift 2
            ;;
        --version)
            VERSION="$2"
            shift 2
            ;;
        --help)
            usage
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

# Validate required arguments
if [[ -z "$ACCOUNT_ID" ]]; then
    echo "Error: --account-id is required"
    usage
    exit 1
fi

# Construct ECR URI
ECR_URI="${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com"
FULL_IMAGE_URI="${ECR_URI}/${REPOSITORY_NAME}:${VERSION}"

# Display configuration
echo "========================================="
echo "ECR Build and Push Configuration"
echo "========================================="
echo "Account ID:       $ACCOUNT_ID"
echo "Region:           $REGION"
echo "Repository Name:  $REPOSITORY_NAME"
echo "Version/Tag:      $VERSION"
echo "Full Image URI:   $FULL_IMAGE_URI"
echo "========================================="
echo ""

# Check if we're in the correct directory (project root)
if [[ ! -f "agent.py" ]] || [[ ! -f "docker/Dockerfile" ]]; then
    echo "Error: This script must be run from the project root directory"
    echo "Expected files: agent.py, docker/Dockerfile"
    echo "Current directory: $(pwd)"
    echo ""
    echo "Please run from project root:"
    echo "  cd /path/to/claude-code-agentcore"
    echo "  ./scripts/build_push.sh --account-id YOUR_ACCOUNT_ID"
    exit 1
fi

# Function to check if command succeeded
check_command() {
    if [[ $? -ne 0 ]]; then
        echo "Error: $1 failed"
        exit 1
    fi
}

# Step 1: Create ECR repository
echo "Step 1: Creating ECR repository..."
aws ecr create-repository --repository-name "$REPOSITORY_NAME" --region "$REGION" 2>/dev/null
if [[ $? -eq 0 ]]; then
    echo "✓ Repository created successfully"
else
    echo "ℹ Repository may already exist (this is normal)"
fi
echo ""

# Step 2: Get login token and login to ECR
echo "Step 2: Logging into ECR..."
aws ecr get-login-password --region "$REGION" | docker login --username AWS --password-stdin "$ECR_URI"
check_command "ECR login"
echo "✓ Successfully logged into ECR"
echo ""

# Step 3: Build and push Docker image
echo "Step 3: Building and pushing Docker image..."
echo "Building for linux/arm64 platform..."
docker buildx build --platform linux/arm64 -f docker/Dockerfile -t "$FULL_IMAGE_URI" --push .
check_command "Docker build and push"
echo "✓ Successfully built and pushed image"
echo ""

# Step 4: Describe images to verify
echo "Step 4: Verifying image in ECR..."
aws ecr describe-images --repository-name "$REPOSITORY_NAME" --region "$REGION"
check_command "ECR describe images"
echo ""

echo "========================================="
echo "✓ Build and push completed successfully!"
echo "Image URI: $FULL_IMAGE_URI"
echo "========================================="

import argparse
import boto3

def main():
    parser = argparse.ArgumentParser(description="Deploy Claude Code Agent Runtime")
    parser.add_argument(
        "--account-id", 
        required=True, 
        help="AWS Account ID"
    )
    parser.add_argument(
        "--region", 
        default="us-east-1", 
        help="AWS Region (default: us-east-1)"
    )
    parser.add_argument(
        "--repository-name", 
        default="claude-code-agentcore", 
        help="ECR Repository name (default: claude-code-agentcore)"
    )
    parser.add_argument(
        "--version", 
        default="latest", 
        help="Docker image version/tag (default: latest)"
    )
    
    args = parser.parse_args()
    
    # Create boto3 client with specified region
    client = boto3.client("bedrock-agentcore-control", region_name=args.region)
    
    # Construct ARNs and URIs using the provided parameters
    container_uri = f"{args.account_id}.dkr.ecr.{args.region}.amazonaws.com/{args.repository_name}:{args.version}"
    role_arn = f"arn:aws:iam::{args.account_id}:role/AgentRuntimeRole"
    
    print(f"Deploying agent runtime in region: {args.region}")
    print(f"Using account ID: {args.account_id}")
    print(f"Repository name: {args.repository_name}")
    print(f"Version: {args.version}")
    print(f"Container URI: {container_uri}")
    print(f"Role ARN: {role_arn}")
    print()
    
    try:
        response = client.create_agent_runtime(
            agentRuntimeName="claude_code_agentcore",
            agentRuntimeArtifact={
                "containerConfiguration": {
                    "containerUri": container_uri
                }
            },
            networkConfiguration={"networkMode": "PUBLIC"},
            roleArn=role_arn,
        )
        
        print(f"Agent Runtime created successfully!")
        print(f"Agent Runtime ARN: {response['agentRuntimeArn']}")
        print(f"Status: {response['status']}")
        
    except Exception as e:
        print(f"Error creating agent runtime: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())

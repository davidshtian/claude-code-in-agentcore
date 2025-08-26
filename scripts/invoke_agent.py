import argparse
import boto3
import json

def main():
    parser = argparse.ArgumentParser(description="Invoke Claude Code Agent Runtime")
    parser.add_argument(
        "--prompt", 
        default="Show me tools you got.", 
        help="Prompt to send to the agent (default: 'Show me tools you got.')"
    )
    parser.add_argument(
        "--agent-runtime-arn", 
        required=True, 
        help="ARN of the agent runtime to invoke"
    )
    parser.add_argument(
        "--region", 
        default="us-east-1", 
        help="AWS Region (default: us-east-1)"
    )
    parser.add_argument(
        "--runtime-session-id", 
        default="dfmeoagmreaklgmrkleafremoigrmtesogmtrskhmtkrlshm3", 
        help="Runtime session ID (default: dfmeoagmreaklgmrkleafremoigrmtesogmtrskhmtkrlshm3)"
    )
    
    args = parser.parse_args()
    
    # Validate runtime session ID length (must be 33+ chars)
    if len(args.runtime_session_id) < 33:
        print(f"Error: Runtime session ID must be at least 33 characters long. Current length: {len(args.runtime_session_id)}")
        return 1
    
    print(f"Invoking agent runtime in region: {args.region}")
    print(f"Agent Runtime ARN: {args.agent_runtime_arn}")
    print(f"Runtime Session ID: {args.runtime_session_id}")
    print(f"Prompt: {args.prompt}")
    print("-" * 50)
    
    try:
        # Create boto3 client with specified region
        agent_core_client = boto3.client("bedrock-agentcore", region_name=args.region)
        
        # Prepare payload
        payload = json.dumps({
            "input": {
                "prompt": args.prompt
            }
        })
        
        # Invoke agent runtime
        response = agent_core_client.invoke_agent_runtime(
            agentRuntimeArn=args.agent_runtime_arn,
            runtimeSessionId=args.runtime_session_id,
            payload=payload,
            qualifier="DEFAULT",
        )
        
        # Process and print the response
        if "text" in response.get("contentType", ""):
            # Handle streaming response
            content = []
            for line in response["response"].iter_lines(chunk_size=10):
                if line:
                    line = line.decode("utf-8")
                    if line.startswith("data: "):
                        line = line[6:]
                        print(line)
                        content.append(line)
            print("\nComplete response:", "\n".join(content))

        elif response.get("contentType") == "application/json":
            # Handle standard JSON response
            content = []
            for chunk in response.get("response", []):
                content.append(chunk.decode("utf-8"))
            print(json.loads("".join(content)))

        else:
            # Print raw response for other content types
            print(response)
            
    except Exception as e:
        print(f"Error invoking agent runtime: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())

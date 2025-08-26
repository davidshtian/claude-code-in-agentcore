from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Dict, Any, AsyncGenerator
from datetime import datetime
from claude_code_sdk import ClaudeSDKClient, ClaudeCodeOptions
import json
import asyncio

app = FastAPI(title="Claude Code on AgentCore", version="1.0.0")


class RequestModel(BaseModel):
    input: Dict[str, Any]


async def stream_agent_response(
    prompt: str, system_prompt: str = None, max_turns: int = 10
) -> AsyncGenerator[str, None]:
    """Stream agent responses using ClaudeSDKClient"""
    try:
        mcp_servers = {
            "playwright": {"command": "npx", "args": ["@playwright/mcp@latest"]}
        }
        options = ClaudeCodeOptions(
            mcp_servers=mcp_servers,
            system_prompt=system_prompt or "You are a helpful AI assistant",
            allowed_tools=[
                "mcp__playwright",
                "Bash",
                "Edit",
                "MultiEdit",
                "NotebookEdit",
                "WebFetch",
                "WebSearch",
                "Write",
            ],
            max_turns=max_turns,
        )

        async with ClaudeSDKClient(options=options) as client:
            print(f"Starting query: {prompt[:50]}...")

            # Send the query
            await client.query(prompt)

            # Stream responses
            async for message in client.receive_response():
                message_type = type(message).__name__

                if hasattr(message, "content"):
                    for block in message.content:
                        stream_data = {
                            "message_type": message_type,
                            "block_type": type(block).__name__,
                            "timestamp": datetime.now().isoformat(),
                        }

                        if hasattr(block, "text"):
                            stream_data["content"] = {"text": block.text}
                            print(f"Text: {block.text}")

                        elif hasattr(block, "name") and hasattr(block, "input"):
                            stream_data["content"] = {
                                "tool_name": block.name,
                                "tool_id": getattr(block, "id", "unknown"),
                                "tool_input": block.input,
                            }
                            print(f"Using tool: {block.name}")

                        elif hasattr(block, "tool_use_id") and hasattr(
                            block, "content"
                        ):
                            stream_data["content"] = {
                                "tool_use_id": block.tool_use_id,
                                "result": block.content,
                                "is_error": getattr(block, "is_error", False),
                            }
                            status = (
                                "ERROR"
                                if getattr(block, "is_error", False)
                                else "SUCCESS"
                            )
                            print(f"Tool result: {status}")

                        yield f"data: {json.dumps(stream_data)}\n\n"
                        await asyncio.sleep(0.01)

            print("Query completed")

    except Exception as e:
        print(f"Error: {str(e)}")
        error_data = {"error": str(e), "timestamp": datetime.now().isoformat()}
        yield f"data: {json.dumps(error_data)}\n\n"


@app.post("/invocations")
async def invoke_agent(request: RequestModel):
    """Main agent endpoint with ClaudeSDKClient"""
    prompt = request.input.get("prompt", "")
    system_prompt = request.input.get("system_prompt")
    max_turns = request.input.get("max_turns", 10)

    if not prompt:
        raise HTTPException(status_code=400, detail="No prompt provided")

    print(f"Processing request - Prompt length: {len(prompt)}, Max turns: {max_turns}")

    return StreamingResponse(
        stream_agent_response(prompt, system_prompt, max_turns),
        media_type="text/plain",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )


@app.get("/ping")
async def ping():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)

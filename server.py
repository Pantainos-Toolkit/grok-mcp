"""MCP server for xAI Grok – X/Twitter search."""

import os
from typing import Optional

import httpx
from dotenv import load_dotenv
from fastmcp import FastMCP

load_dotenv()

XAI_BASE_URL = "https://api.x.ai/v1"
API_KEY = os.environ.get("XAI_API_KEY", "")
DEFAULT_MODEL = os.environ.get("GROK_MODEL", "grok-4-1-fast")

mcp = FastMCP("Grok X Search")


async def _responses(
    query: str,
    tools: list[dict] | None = None,
    model: str | None = None,
    system_prompt: str | None = None,
    temperature: float | None = None,
) -> dict:
    """Call the xAI Responses API and return the parsed result."""
    model = model or DEFAULT_MODEL

    messages: list[dict] = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": query})

    payload: dict = {
        "model": model,
        "input": messages,
    }
    if tools:
        payload["tools"] = tools
    if temperature is not None:
        payload["temperature"] = temperature

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}",
    }

    async with httpx.AsyncClient(timeout=120) as client:
        resp = await client.post(
            f"{XAI_BASE_URL}/responses",
            json=payload,
            headers=headers,
        )
        resp.raise_for_status()
        return _extract_response(resp.json())


def _extract_response(raw: dict) -> dict:
    """Extract useful content from the Responses API output."""
    result: dict = {"model": raw.get("model", ""), "usage": raw.get("usage")}

    text_parts: list[str] = []
    citations: list[dict] = []

    for item in raw.get("output", []):
        if item.get("type") == "message":
            for block in item.get("content", []):
                if block.get("type") == "output_text":
                    text_parts.append(block.get("text", ""))
                    for ann in block.get("annotations", []):
                        if ann.get("type") == "url_citation":
                            citations.append(
                                {
                                    "title": ann.get("title", ""),
                                    "url": ann.get("url", ""),
                                }
                            )

    result["text"] = "\n".join(text_parts)
    if citations:
        result["citations"] = citations

    return result


@mcp.tool
async def search_x(
    query: str,
    allowed_handles: Optional[list[str]] = None,
    excluded_handles: Optional[list[str]] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    enable_image_understanding: bool = False,
    enable_video_understanding: bool = False,
    model: Optional[str] = None,
    system_prompt: Optional[str] = None,
    temperature: Optional[float] = None,
) -> dict:
    """Search X (Twitter) posts using Grok and return a summarised answer with citations.

    The xAI server autonomously searches X, analyses results, and synthesises
    an answer grounded in real posts.

    Args:
        query: Natural-language search query (e.g. "What are people saying about $TSLA?").
        allowed_handles: Whitelist of X usernames to restrict search to (max 10).
        excluded_handles: X usernames to exclude from results (max 10).
        from_date: Only include posts on or after this date (ISO 8601, e.g. "2026-02-01").
        to_date: Only include posts on or before this date (ISO 8601).
        enable_image_understanding: Let the model analyse images attached to posts.
        enable_video_understanding: Let the model analyse video clips in posts.
        model: Override the default Grok model.
        system_prompt: Optional system prompt to shape the response style.
        temperature: Sampling temperature (0-2).

    Returns:
        Dict with 'text' (answer), optional 'citations' list, 'model', and 'usage'.
    """
    tool_config: dict = {"type": "x_search"}
    if allowed_handles:
        tool_config["allowed_x_handles"] = allowed_handles[:10]
    if excluded_handles:
        tool_config["excluded_x_handles"] = excluded_handles[:10]
    if from_date:
        tool_config["from_date"] = from_date
    if to_date:
        tool_config["to_date"] = to_date
    if enable_image_understanding:
        tool_config["enable_image_understanding"] = True
    if enable_video_understanding:
        tool_config["enable_video_understanding"] = True

    return await _responses(
        query,
        tools=[tool_config],
        model=model,
        system_prompt=system_prompt,
        temperature=temperature,
    )


@mcp.tool
async def ask_grok(
    query: str,
    model: Optional[str] = None,
    system_prompt: Optional[str] = None,
    temperature: Optional[float] = None,
) -> dict:
    """Ask Grok a question without live search (uses model knowledge only).

    Args:
        query: Your question or prompt.
        model: Override the default Grok model.
        system_prompt: Optional system prompt.
        temperature: Sampling temperature (0-2).

    Returns:
        Dict with 'text' (answer), 'model', and 'usage'.
    """
    return await _responses(
        query,
        model=model,
        system_prompt=system_prompt,
        temperature=temperature,
    )


def main():
    mcp.run()


if __name__ == "__main__":
    main()

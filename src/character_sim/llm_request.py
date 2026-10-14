"""LLM Request - Perform a request to a large language model provider."""

# Programmed by CoolCat467

from __future__ import annotations

# LLM Request - Perform a request to a large language model provider
# Copyright (C) 2026  CoolCat467
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

__title__ = "LLM Request"
__author__ = "CoolCat467"
__license__ = "GNU General Public License Version 3"


from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, Any

import httpx2 as httpx
import orjson
import trio

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator


async def perform_openrouter_request(
    client: httpx.AsyncClient,
    auth_token: str,
    endpoint: str,
    payload: dict[str, Any] | None = None,
    timeout: int | None = 50,  # noqa: ASYNC109
) -> httpx.Response:
    """Return openrouter request."""
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json",
    }
    if payload is None:
        payload = {}
    response = await client.post(
        url=f"https://openrouter.ai/api/v1/{endpoint}",
        headers=headers,
        content=orjson.dumps(payload),
        timeout=timeout,
    )

    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as http_exc:
        try:
            error_data = orjson.loads(await response.aread())
        except orjson.JSONDecodeError as decode_exc:
            # raise decode error from http error
            raise decode_exc from http_exc
        # if the API returned an error, add error message as a note
        http_exc.add_note(error_data["error"]["message"])
        raise http_exc from None

    return response


@asynccontextmanager
async def perform_openrouter_stream_request(  # type: ignore[misc]
    client: httpx.AsyncClient,
    auth_token: str,
    endpoint: str,
    payload: dict[str, Any] | None = None,
    timeout: int | None = 50,  # noqa: ASYNC109
) -> AsyncGenerator[httpx.Response, None]:
    """Return openrouter request."""
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json",
    }
    if payload is None:
        payload = {}
    payload["stream"] = True

    async with client.stream(
        "POST",
        url=f"https://openrouter.ai/api/v1/{endpoint}",
        headers=headers,
        content=orjson.dumps(payload),
        timeout=timeout,
    ) as response:
        # check pre-stream errors
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as http_exc:
            try:
                error_data = orjson.loads(await response.aread())
            except orjson.JSONDecodeError as decode_exc:
                # raise decode error from http error
                raise decode_exc from http_exc
            # if the API returned an error, add error message as a note
            http_exc.add_note(error_data["error"]["message"])
            raise http_exc from None

        yield response


async def perform_chat_completion_request(
    prompt: str,
    client: httpx.AsyncClient,
    auth_token: str,
    model: str = "dots-studio/dots-3-note-preview:free",
) -> dict[str, Any]:
    """Return JSON decoded response body from LLM provider request."""
    response = await perform_openrouter_request(
        client,
        auth_token,
        endpoint="chat/completions",
        payload={
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
        },
    )

    # get response as a dictionary
    response_body = orjson.loads(await response.aread())

    print(f"[{__title__}] {response_body = }")

    assert isinstance(response_body, dict)
    return response_body


async def get_llm_response(
    prompt: str,
    client: httpx.AsyncClient,
    key: str,
    model: str = "dots-studio/dots-3-note-preview:free",
) -> str:
    """Retrieve a response from an AI model.

    This function takes in a prompt, sends it to an AI model using
    OpenRouter's API, and retrieves a response. This response is parsed
    to get just the actual message content from the model.

    Args:
        prompt: The string input sent to the model.
        model: The model used to get a response, set to a free model by
        default

    Returns:
         A string of the AI model's response to the prompt, or an error
         if the model cannot be connected to or a response cannot be
         found.

    """
    response_body = await perform_chat_completion_request(
        prompt,
        client,
        key,
        model,
    )

    # parse the model's response for the actual reply
    content = (
        response_body.get("choices", [{}])[0].get("message", {}).get("content")
    )
    if content:
        assert isinstance(content, str)
        return content

    new_exc = ValueError("could not find message content in response body")
    new_exc.add_note(f"{response_body = }")
    raise new_exc


@trio.as_safe_channel
async def yield_llm_stream(
    prompt: str,
    client: httpx.AsyncClient,
    auth_token: str,
    model: str = "dots-studio/dots-3-note-preview:free",
) -> AsyncGenerator[str, None]:
    """Yield a stream of text fragments from LLM provider request."""
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
    }

    async with perform_openrouter_stream_request(
        client,
        auth_token=auth_token,
        endpoint="chat/completions",
        payload=payload,
    ) as response:
        async for line in response.aiter_lines():
            # Skip blank lines and SSE comments (for example, keep-alive
            # messages).
            if not line or line.startswith(":"):
                continue

            if not line.startswith("data: "):
                continue

            data = line[6:]
            if data == "[DONE]":
                break

            try:
                parsed = orjson.loads(data)
            except orjson.JSONDecodeError:
                continue

            # Check for mid-stream error
            if "error" in parsed:
                raise OSError(parsed["error"]["message"])

            content = parsed["choices"][0]["delta"].get("content")
            if content:
                yield content


@trio.as_safe_channel
async def fake_stream(text: str) -> AsyncGenerator[str, None]:
    """Yield a fake stream of word fragments from given text.

    Number of characters yielded is determined by a very naive custom
    determanistic pseudo-random number generator to choose from 1 to 7
    characters. Do not use for cryptographic purposes.
    """
    head = 0
    seed = 0
    while head < len(text):
        seed = ((seed * 7) + 3) % 4096
        pseudo_random = (seed % 7) + 1

        consume = min(len(text) - head, pseudo_random)

        yield text[head : head + consume]
        head += consume

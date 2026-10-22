"""Structured decoding and narrowly scoped compatibility fallback."""

import json
from unittest.mock import Mock

import httpx
import pytest
from openai import OpenAI, APIStatusError

from src.ia_multitools.core.openai_client import OpenAIClient


def completion(content, finish_reason="stop"):
    return {
        "id": "test", "object": "chat.completion", "created": 0, "model": "test",
        "choices": [{"index": 0, "message": {"role": "assistant", "content": content},
                     "finish_reason": finish_reason}],
    }


@pytest.fixture
def make_client(monkeypatch):
    clients = []

    def create(handler):
        monkeypatch.setattr(
            OpenAIClient, "_build_client",
            staticmethod(lambda *_args: OpenAI(
                api_key="dummy", base_url="http://test.local/v1", max_retries=0,
                http_client=httpx.Client(transport=httpx.MockTransport(handler)),
            )),
        )
        client = OpenAIClient(temperature=0.3, max_tokens=100)
        clients.append(client)
        return client
    yield create
    for client in clients:
        client.close()


def test_schema_is_sent_and_json_envelope_removed(make_client):
    requests = []

    def handler(request):
        requests.append(json.loads(request.content))
        return httpx.Response(200, json=completion('{"result": "**Texte corrigé.**"}'))
    client = make_client(handler)
    assert client.constrained_completion("text", "instructions", temperature=0.0) == "**Texte corrigé.**"
    body = requests[0]
    assert body["temperature"] == 0.0
    assert body["max_tokens"] == 100
    assert body["response_format"]["type"] == "json_schema"
    schema = body["response_format"]["json_schema"]
    assert schema["strict"]
    assert schema["schema"]["required"] == ["result"]
    assert schema["schema"]["additionalProperties"] is False


def test_unsupported_schema_retries_plain_text_and_logs(make_client, caplog):
    requests = []

    def handler(request):
        body = json.loads(request.content)
        requests.append(body)
        if "response_format" in body:
            return httpx.Response(400, json={"error": {
                "message": "response_format json_schema is not supported", "type": "invalid_request_error",
            }})
        return httpx.Response(200, json=completion("Texte corrigé."))
    client = make_client(handler)
    assert client.constrained_completion("text", "instructions") == "Texte corrigé."
    assert len(requests) == 2
    assert "response_format" not in requests[1]
    assert "repli" in caplog.text


@pytest.mark.parametrize("status,message", [
    (400, "temperature must be numeric"),
    (400, "invalid json_schema"),
    (401, "Unauthorized"), (429, "Rate limit exceeded"), (500, "Internal server error"),
])
def test_other_errors_never_trigger_plain_fallback(make_client, status, message):
    handler = Mock(return_value=httpx.Response(status, json={"error": {"message": message}}))
    client = make_client(handler)
    with pytest.raises(APIStatusError):
        client.constrained_completion("text", "instructions")
    assert handler.call_count == 1


@pytest.mark.parametrize("content,reason", [
    ("plain text despite schema", "stop"), ('{"result": ["a", "b"]}', "stop"),
    ('{"result": ""}', "stop"), ('{"result": "a", "extra": "b"}', "stop"),
    ('{"result": "partial"}', "length"), (None, "stop"),
])
def test_invalid_or_truncated_result_is_rejected(make_client, content, reason):
    client = make_client(lambda request: httpx.Response(200, json=completion(content, reason)))
    with pytest.raises(ValueError):
        client.constrained_completion("text", "instructions")

"""Services must retain a usable client after configuration changes."""

from unittest.mock import Mock
import json

import httpx
import pytest
from openai import OpenAI

from src.ia_multitools.core import openai_client as clients
from src.ia_multitools.services.definition_service import DefinitionService
from src.ia_multitools.services.synonym_service import SynonymService
from src.ia_multitools.services.text_correction_service import TextCorrectionService
from src.ia_multitools.services.email_correction_service import EmailCorrectionService


def test_all_services_complete_after_repeated_reconfiguration(monkeypatch):
    requests = []

    def respond(request):
        requests.append(request)
        structured = "response_format" in json.loads(request.content)
        return httpx.Response(200, json={
            "id": "test", "object": "chat.completion", "created": 0, "model": "updated",
            "choices": [{"index": 0, "message": {"role": "assistant", "content":
                         '{"result": "OK"}' if structured else "OK"},
                         "finish_reason": "stop"}],
        })

    def build(api_key, base_url, timeout, verify_ssl):
        return OpenAI(
            api_key=api_key or "dummy", base_url=base_url, timeout=timeout,
            http_client=httpx.Client(transport=httpx.MockTransport(respond)),
        )

    monkeypatch.setattr(clients, "_openai_client", None)
    monkeypatch.setattr(clients.OpenAIClient, "_build_client", staticmethod(build))
    original = clients.init_openai_client(max_tokens=100)
    services = [
        DefinitionService(history_manager=Mock()),
        SynonymService(history_manager=Mock()),
        TextCorrectionService(history_manager=Mock()),
        EmailCorrectionService(history_manager=Mock()),
    ]
    try:
        for model in ("after-wizard", "after-settings", "after-reset"):
            old_http_client = original.client
            current = clients.init_openai_client(
                model=model, base_url="http://local.test/v1", temperature=0.7,
                timeout=95, verify_ssl=False, max_tokens=None,
            )
            assert current is original
            assert old_http_client.is_closed()
            assert not current.client.is_closed()
            assert current.max_tokens is None
            assert all(service.client is current for service in services)
            assert services[0].get_definition("test")
            assert services[1].get_synonyms_antonyms("test")
            assert services[2].correct_text("Texte de test.")
            assert services[3].correct_email("Bonjour, ceci est un test.")
        assert len(requests) == 12
        assert all(request.url.host == "local.test" for request in requests)
    finally:
        original.close()


def test_failed_reconfiguration_preserves_working_client(monkeypatch):
    monkeypatch.setattr(clients, "_openai_client", None)
    original = clients.init_openai_client()
    http_client = original.client
    try:
        monkeypatch.setattr(
            clients.OpenAIClient, "_build_client",
            Mock(side_effect=ValueError("invalid configuration")),
        )
        with pytest.raises(ValueError):
            clients.init_openai_client(model="new-model")
        assert clients.get_openai_client() is original
        assert original.client is http_client
        assert not http_client.is_closed()
        assert original.model != "new-model"
    finally:
        original.close()

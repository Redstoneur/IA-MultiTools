"""Exercise real UI-to-service calls through an in-memory OpenAI server."""

import json
from unittest.mock import Mock, patch

import httpx
import pytest
import ttkbootstrap as ttk
from openai import OpenAI

from src.ia_multitools.core.openai_client import OpenAIClient
from src.ia_multitools.services.definition_service import DefinitionService
from src.ia_multitools.services.synonym_service import SynonymService
from src.ia_multitools.services.text_correction_service import TextCorrectionService
from src.ia_multitools.services.email_correction_service import EmailCorrectionService
from src.ia_multitools.ui.tabs.definition_tab import DefinitionTab
from src.ia_multitools.ui.tabs.synonym_tab import SynonymTab
from src.ia_multitools.ui.tabs.correction_tab import CorrectionTab
from src.ia_multitools.ui.tabs.email_tab import EmailTab
from .test_first_run_wizard import config_manager


@pytest.mark.parametrize("kind,output_format,mode", [
    ("definition", "text", None), ("definition", "markdown", None),
    ("synonym", "text", "synonyms"), ("synonym", "markdown", "synonyms"),
    ("synonym", "text", "antonyms"), ("synonym", "markdown", "antonyms"),
    ("synonym", "text", "both"), ("synonym", "markdown", "both"),
    ("correction", "text", None), ("correction", "markdown", None),
    ("email", "text", None), ("email", "markdown", None),
])
def test_ui_sends_numeric_temperature_and_selected_format(root, monkeypatch, kind, output_format, mode):
    requests = []

    def handler(request):
        body = json.loads(request.content)
        requests.append(body)
        assert isinstance(body["temperature"], (int, float))
        return httpx.Response(200, json={
            "id": "test", "object": "chat.completion", "created": 0, "model": "test",
            "choices": [{"index": 0, "message": {
                "role": "assistant", "content": '{"result": "Résultat unique."}'},
                "finish_reason": "stop"}],
        })

    monkeypatch.setattr(OpenAIClient, "_build_client", staticmethod(lambda *_args: OpenAI(
        api_key="dummy", base_url="http://test.local/v1",
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )))
    client = OpenAIClient(temperature=0.2)
    service_class, tab_class, getter = {
        "definition": (DefinitionService, DefinitionTab, "get_definition_service"),
        "synonym": (SynonymService, SynonymTab, "get_synonym_service"),
        "correction": (TextCorrectionService, CorrectionTab, "get_text_correction_service"),
        "email": (EmailCorrectionService, EmailTab, "get_email_correction_service"),
    }[kind]
    history = Mock()
    service = service_class(openai_client=client, history_manager=history)
    notebook = ttk.Notebook(root)
    manager = config_manager()
    with patch(f"{tab_class.__module__}.{getter}", return_value=service):
        tab = tab_class(notebook, manager)
    monkeypatch.setattr(tab.frame, "after", lambda delay, callback: callback())
    monkeypatch.setattr(
        f"{tab_class.__module__}.threading.Thread",
        lambda target, **kwargs: Mock(start=target),
    )
    try:
        instructions = "Emploie un vocabulaire adapté à un enfant."
        tab.instructions_entry.insert(0, instructions)
        prompt_field = {"correction": "text_correction", "email": "email_correction"}.get(kind, kind)
        setattr(manager.get_config().prompts, prompt_field, "Contexte personnalisé modifié après ouverture.")
        if kind == "definition":
            tab.term_entry.insert(0, "maison")
            tab.format_var.set(output_format)
            tab._generate_definition()
        elif kind == "synonym":
            tab.word_entry.insert(0, "maison")
            tab.mode_var.set(mode)
            tab.format_var.set(output_format)
            tab._generate_synonyms()
        elif kind == "correction":
            assert tab.markdown_var.get() is False
            tab.markdown_var.set(output_format == "markdown")
            tab.input_text.insert("1.0", "ceci et un test")
            tab._correct_text()
        else:
            assert tab.markdown_var.get() is False
            assert tab.add_greeting_var.get() is False
            tab.markdown_var.set(output_format == "markdown")
            tab.input_text.insert("1.0", "Salut, tu peux me transmettre le document ?")
            tab.make_professional_var.set(False)
            tab.add_greeting_var.set(False)
            tab._correct_email()
        assert len(requests) == 1
        assert tab.result_text.get("1.0", "end").strip() == "Résultat unique."
        assert requests[0]["temperature"] == 0.2
        prompt = requests[0]["messages"][0]["content"]
        assert instructions in prompt
        assert "Contexte personnalisé modifié après ouverture." in prompt
        assert instructions not in requests[0]["messages"][1]["content"]
        if output_format == "markdown":
            assert "Markdown" in prompt
        else:
            assert "texte brut" in prompt
        assert history.add_entry.call_args.kwargs["metadata"]["output_format"] == output_format
        assert history.add_entry.call_args.kwargs["metadata"]["instructions"] == instructions
        if kind == "correction":
            assert "une seule version" in prompt
            assert "Ne propose jamais plusieurs" in prompt
            tab._reset()
            assert tab.markdown_var.get() is False
        if kind == "email":
            assert "Option professionnel DÉSACTIVÉE" in prompt
            assert "Option politesse DÉSACTIVÉE" in prompt
            assert "Conserve impérativement le tutoiement" in prompt
            assert "Conserve celles déjà présentes" in prompt
            tab.add_greeting_var.set(True)
            tab._reset()
            assert tab.add_greeting_var.get() is False
            assert tab.markdown_var.get() is False
        if kind in ("email", "correction"):
            assert tab.instructions_entry.get() == ""
    finally:
        notebook.destroy()
        client.close()

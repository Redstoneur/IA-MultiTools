"""Sequential correction and translation, without partial-success history."""

import json
from unittest.mock import Mock

import pytest

from src.ia_multitools.services.translation_service import TranslationService


@pytest.mark.parametrize("output_format", ["text", "markdown"])
def test_translation_uses_corrected_text_and_records_final_result(output_format):
    client, history = Mock(), Mock()
    client.constrained_completion.side_effect = ["Texte corrigé.", "Corrected text."]
    service = TranslationService(client, history, "Contexte personnalisé.")
    result = service.correct_text(
        "texte corigé", target_language="Anglais",
        instructions="Vocabulaire simple.", output_format=output_format,
    )
    assert result == "Corrected text."
    first, second = client.constrained_completion.call_args_list
    assert json.loads(first.kwargs["prompt"]) == {"texte": "texte corigé"}
    assert "Ne traduis pas encore" in first.kwargs["system_prompt"]
    assert json.loads(second.kwargs["prompt"]) == {
        "langue_cible": "Anglais", "texte_corrige": "Texte corrigé.",
    }
    for call in (first, second):
        assert "Contexte personnalisé." in call.kwargs["system_prompt"]
        assert "Vocabulaire simple." in call.kwargs["system_prompt"]
    assert (
        "Produis du Markdown" if output_format == "markdown" else "Produis du texte brut"
    ) in second.kwargs["system_prompt"]
    history.add_entry.assert_called_once()
    assert history.add_entry.call_args.kwargs["ai_response"] == result
    assert history.add_entry.call_args.kwargs["tool_name"] == "translation"


@pytest.mark.parametrize("responses,count", [
    ([None], 1), ([RuntimeError("unavailable")], 1),
    (["Corrigé", None], 2), (["Corrigé", RuntimeError("unavailable")], 2),
])
def test_failure_does_not_return_or_record_partial_result(responses, count):
    client, history = Mock(), Mock()
    client.constrained_completion.side_effect = responses
    service = TranslationService(client, history)
    assert service.correct_text("Texte") is None
    assert client.constrained_completion.call_count == count
    history.add_entry.assert_not_called()


@pytest.mark.parametrize("text,language,output_format", [
    ("", "Anglais", "text"), ("texte", "", "text"),
    ("texte", "x" * 101, "text"), ("texte", "Anglais", "html"),
])
def test_invalid_input_never_calls_api(text, language, output_format):
    client = Mock()
    service = TranslationService(client, Mock())
    assert service.correct_text(
        text, target_language=language, output_format=output_format
    ) is None
    client.constrained_completion.assert_not_called()

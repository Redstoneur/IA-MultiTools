"""Every email option has an explicit positive and negative instruction."""

from unittest.mock import Mock

import pytest

from src.ia_multitools.services.email_correction_service import EmailCorrectionService


@pytest.mark.parametrize("professional", [False, True])
@pytest.mark.parametrize("greeting", [False, True])
@pytest.mark.parametrize("output_format", ["text", "markdown"])
def test_email_options_override_old_prompt(professional, greeting, output_format):
    client, history = Mock(), Mock()
    client.constrained_completion.return_value = "Salut, tu peux me transmettre le document ?"
    service = EmailCorrectionService(
        openai_client=client, history_manager=history,
        system_prompt="Rends toujours les e-mails professionnels. Utilise des virgules sans Markdown.",
    )
    assert service.correct_email(
        "Salut, tu peux me transmetre le document ?",
        instructions="Garde un message court.", make_professional=professional,
        add_greeting=greeting, output_format=output_format, temperature=0,
    )
    args = client.constrained_completion.call_args.kwargs
    prompt = args["system_prompt"]
    assert f"Option professionnel {'ACTIVÉE' if professional else 'DÉSACTIVÉE'}" in prompt
    assert f"Option politesse {'ACTIVÉE' if greeting else 'DÉSACTIVÉE'}" in prompt
    assert "Conserve impérativement le tutoiement ou le vouvoiement d'origine" in prompt
    assert "Garde un message court." in prompt
    assert "Les options explicites priment" in prompt
    assert "Produis du Markdown" in prompt if output_format == "markdown" else "Produis du texte brut" in prompt
    assert args["temperature"] == 0
    assert history.add_entry.call_args.kwargs["metadata"]["temperature"] == 0


def test_invalid_email_format_never_sends_request():
    client = Mock()
    service = EmailCorrectionService(openai_client=client, history_manager=Mock())
    assert service.correct_email("Test", output_format="html") is None
    client.constrained_completion.assert_not_called()

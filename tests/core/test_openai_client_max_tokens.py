"""
Tests unitaires pour OpenAIClient.simple_completion avec support max_tokens
Validation du fix pour le bug TypeError dans first_run_wizard
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Optional

from src.ia_multitools.core.openai_client import OpenAIClient


class TestSimpleCompletionMaxTokens:
    """Tests pour valider le support de max_tokens dans simple_completion"""

    @pytest.fixture
    def mock_openai_client(self):
        """Fixture pour créer un client mocké"""
        with patch('src.ia_multitools.core.openai_client.OpenAI') as mock_openai:
            mock_instance = MagicMock()
            mock_openai.return_value = mock_instance

            client = OpenAIClient(
                api_key="test-key",
                base_url="http://localhost:9999/v1",
                model="test-model"
            )

            # Mock la réponse de l'API
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "Test response"
            mock_instance.chat.completions.create.return_value = mock_response

            yield client, mock_instance

    def test_simple_completion_accepts_max_tokens(self, mock_openai_client):
        """Vérifie que simple_completion accepte le paramètre max_tokens"""
        client, mock_api = mock_openai_client

        # Appel avec max_tokens (comme dans first_run_wizard)
        result = client.simple_completion(
            prompt="Test prompt",
            system_prompt="Test system",
            max_tokens=50
        )

        assert result == "Test response"

        # Vérifier que l'API a été appelée avec max_tokens
        mock_api.chat.completions.create.assert_called_once()
        call_kwargs = mock_api.chat.completions.create.call_args[1]
        assert 'max_tokens' in call_kwargs
        assert call_kwargs['max_tokens'] == 50

    def test_simple_completion_without_max_tokens(self, mock_openai_client):
        """Vérifie la rétrocompatibilité sans max_tokens"""
        client, mock_api = mock_openai_client

        # Appel sans max_tokens (comme dans les services existants)
        result = client.simple_completion(
            prompt="Test prompt",
            temperature=0.7
        )

        assert result == "Test response"
        mock_api.chat.completions.create.assert_called_once()

    def test_simple_completion_with_all_parameters(self, mock_openai_client):
        """Vérifie que tous les paramètres peuvent être utilisés ensemble"""
        client, mock_api = mock_openai_client

        result = client.simple_completion(
            prompt="Test prompt",
            system_prompt="System prompt",
            temperature=0.5,
            max_tokens=100
        )

        assert result == "Test response"

        # Vérifier tous les paramètres
        call_kwargs = mock_api.chat.completions.create.call_args[1]
        assert call_kwargs['temperature'] == 0.5
        assert call_kwargs['max_tokens'] == 100
        assert call_kwargs['messages'][0]['role'] == 'system'
        assert call_kwargs['messages'][0]['content'] == 'System prompt'
        assert call_kwargs['messages'][1]['role'] == 'user'
        assert call_kwargs['messages'][1]['content'] == 'Test prompt'

    def test_simple_completion_max_tokens_none(self, mock_openai_client):
        """Vérifie le comportement avec max_tokens=None explicite"""
        client, mock_api = mock_openai_client

        result = client.simple_completion(
            prompt="Test",
            max_tokens=None
        )

        assert result == "Test response"

        # Avec max_tokens=None et self.max_tokens=None,
        # le paramètre max_tokens ne devrait pas être dans la requête
        call_kwargs = mock_api.chat.completions.create.call_args[1]
        # max_tokens peut ne pas être présent ou être None
        if 'max_tokens' in call_kwargs:
            assert call_kwargs['max_tokens'] is None

    def test_simple_completion_uses_instance_max_tokens(self, mock_openai_client):
        """Vérifie que max_tokens de l'instance est utilisé si non fourni"""
        client, mock_api = mock_openai_client

        # Configurer max_tokens au niveau de l'instance
        client.max_tokens = 200

        result = client.simple_completion(prompt="Test")

        assert result == "Test response"

        # Le max_tokens de l'instance devrait être utilisé
        call_kwargs = mock_api.chat.completions.create.call_args[1]
        assert call_kwargs['max_tokens'] == 200

    def test_simple_completion_parameter_overrides_instance(self, mock_openai_client):
        """Vérifie que le paramètre max_tokens surcharge celui de l'instance"""
        client, mock_api = mock_openai_client

        # Configurer max_tokens au niveau de l'instance
        client.max_tokens = 200

        # Mais passer un max_tokens différent dans l'appel
        result = client.simple_completion(
            prompt="Test",
            max_tokens=50
        )

        assert result == "Test response"

        # Le paramètre passé devrait avoir priorité
        call_kwargs = mock_api.chat.completions.create.call_args[1]
        assert call_kwargs['max_tokens'] == 50

    def test_first_run_wizard_pattern(self, mock_openai_client):
        """Teste le pattern exact utilisé dans first_run_wizard"""
        client, mock_api = mock_openai_client

        # Pattern exact du wizard (ligne 194-198)
        response = client.simple_completion(
            prompt="Dis simplement 'connexion réussie'",
            system_prompt="Réponds brièvement.",
            max_tokens=50
        )

        # Devrait fonctionner sans TypeError
        assert response is not None
        assert response == "Test response"

        # Vérifier les paramètres
        call_kwargs = mock_api.chat.completions.create.call_args[1]
        assert call_kwargs['max_tokens'] == 50
        assert any(m['content'] == "Réponds brièvement." for m in call_kwargs['messages'])


class TestSimpleCompletionSignature:
    """Tests de validation de la signature de simple_completion"""

    def test_signature_has_required_parameters(self):
        """Vérifie que la signature contient tous les paramètres requis"""
        import inspect

        # Créer un client temporaire
        with patch('src.ia_multitools.core.openai_client.OpenAI'):
            client = OpenAIClient()
            sig = inspect.signature(client.simple_completion)
            params = list(sig.parameters.keys())

            # Vérifier les paramètres (self n'est pas dans inspect.signature)
            assert 'prompt' in params
            assert 'system_prompt' in params
            assert 'temperature' in params
            assert 'max_tokens' in params, "max_tokens doit être dans la signature"

    def test_max_tokens_is_optional(self):
        """Vérifie que max_tokens est optionnel (a une valeur par défaut)"""
        import inspect

        with patch('src.ia_multitools.core.openai_client.OpenAI'):
            client = OpenAIClient()
            sig = inspect.signature(client.simple_completion)
            max_tokens_param = sig.parameters['max_tokens']

            # Vérifier que max_tokens a une valeur par défaut
            assert max_tokens_param.default is None, \
                "max_tokens doit avoir None comme valeur par défaut"

    def test_parameter_order(self):
        """Vérifie l'ordre des paramètres"""
        import inspect

        with patch('src.ia_multitools.core.openai_client.OpenAI'):
            client = OpenAIClient()
            sig = inspect.signature(client.simple_completion)
            params = list(sig.parameters.keys())

            # Vérifier l'ordre logique
            expected_order = ['prompt', 'system_prompt', 'temperature', 'max_tokens']
            assert params == expected_order, \
                f"Ordre attendu: {expected_order}, obtenu: {params}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

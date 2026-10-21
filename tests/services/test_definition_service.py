"""
Tests pour le service de définition.
"""

import pytest
from unittest.mock import Mock, patch
from src.ia_multitools.services.definition_service import DefinitionService


def test_definition_service_initialization():
    """Test de l'initialisation du service."""
    with patch('src.ia_multitools.services.definition_service.get_openai_client'):
        with patch('src.ia_multitools.services.definition_service.get_history_manager'):
            service = DefinitionService()
            assert service is not None


def test_validate_term():
    """Test de validation de terme."""
    with patch('src.ia_multitools.services.definition_service.get_openai_client'):
        with patch('src.ia_multitools.services.definition_service.get_history_manager'):
            service = DefinitionService()

            # Terme valide
            valid, msg = service.validate_term("intelligence")
            assert valid is True
            assert msg == ""

            # Terme vide
            valid, msg = service.validate_term("")
            assert valid is False

            # Terme trop long
            valid, msg = service.validate_term("a" * 201)
            assert valid is False


def test_get_definition_with_mock():
    """Test de génération de définition avec mock."""
    with patch('src.ia_multitools.services.definition_service.get_openai_client') as mock_client:
        with patch('src.ia_multitools.services.definition_service.get_history_manager') as mock_history:
            # Configurer le mock
            mock_client_instance = Mock()
            mock_client_instance.constrained_completion.return_value = "Définition test"
            mock_client.return_value = mock_client_instance

            mock_history_instance = Mock()
            mock_history.return_value = mock_history_instance

            service = DefinitionService()
            result = service.get_definition("test")

            assert result == "Définition test"
            mock_client_instance.constrained_completion.assert_called_once()
            mock_history_instance.add_entry.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

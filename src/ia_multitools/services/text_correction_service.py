"""
Service de correction de texte.

Corrige l'orthographe, la grammaire et améliore le style de textes.
"""

import logging
from typing import Optional
from ..core.openai_client import OpenAIClient, get_openai_client
from ..core.history_manager import HistoryManager, get_history_manager

logger = logging.getLogger(__name__)


class TextCorrectionService:
    """
    Service de correction de texte.

    Utilise l'IA pour corriger l'orthographe, la grammaire et améliorer le style.
    """

    TOOL_NAME = "text_correction"

    def __init__(
        self,
        openai_client: Optional[OpenAIClient] = None,
        history_manager: Optional[HistoryManager] = None,
        system_prompt: Optional[str] = None
    ) -> None:
        """
        Initialise le service de correction de texte.

        Args:
            openai_client: Client OpenAI
            history_manager: Gestionnaire d'historique
            system_prompt: Prompt système personnalisé
        """
        self.client = openai_client or get_openai_client()
        self.history = history_manager or get_history_manager()
        self.system_prompt = system_prompt or self._get_default_system_prompt()

        logger.info("Service de correction de texte initialisé")

    def _get_default_system_prompt(self) -> str:
        """
        Retourne le prompt système par défaut.

        Returns:
            Prompt système
        """
        return (
            "Tu es un correcteur professionnel. Corrige l'orthographe, la grammaire "
            "et améliore le style du texte fourni. Respecte les instructions embarquées "
            "entre <instruction> et </instruction>. Retourne uniquement le texte corrigé, "
            "sans commentaires ni explications. Ne modifie pas le sens du texte original."
        )

    def set_system_prompt(self, prompt: str) -> None:
        """
        Définit un prompt système personnalisé.

        Args:
            prompt: Nouveau prompt système
        """
        self.system_prompt = prompt
        logger.debug("Prompt système mis à jour pour le service de correction de texte")

    def correct_text(
        self,
        text: str,
        instructions: Optional[str] = None,
        temperature: Optional[float] = None
    ) -> Optional[str]:
        """
        Corrige un texte.

        Args:
            text: Texte à corriger
            instructions: Instructions complémentaires optionnelles
            temperature: Température pour la génération

        Returns:
            Texte corrigé ou None en cas d'erreur
        """
        if not text or not text.strip():
            logger.warning("Texte vide fourni")
            return None

        try:
            # Construire le prompt utilisateur
            user_prompt = f"Texte à corriger:\n\n{text}"

            if instructions and instructions.strip():
                user_prompt += f"\n\n<instruction>{instructions}</instruction>"

            logger.info(f"Demande de correction de texte ({len(text)} caractères)")

            # Appel à l'IA
            response = self.client.simple_completion(
                prompt=user_prompt,
                system_prompt=self.system_prompt,
                temperature=temperature
            )

            if response:
                # Sauvegarder dans l'historique
                self.history.add_entry(
                    tool_name=self.TOOL_NAME,
                    user_request=text,
                    ai_response=response,
                    metadata={
                        "instructions": instructions,
                        "text_length": len(text),
                        "output_format": output_format,
                        "temperature": temperature or self.client.temperature
                    }
                )

                logger.info("Texte corrigé avec succès")
                return response
            else:
                logger.error("Aucune réponse de l'IA")
                return None

        except Exception as e:
            logger.error(f"Erreur lors de la correction du texte: {e}")
            return None

    def validate_text(self, text: str) -> tuple[bool, str]:
        """
        Valide un texte avant correction.

        Args:
            text: Texte à valider

        Returns:
            Tuple (valide, message_erreur)
        """
        if not text or not text.strip():
            return False, "Le texte ne peut pas être vide"

        if len(text) > 50000:
            return False, "Le texte est trop long (max 50 000 caractères)"

        return True, ""


# Instance globale
_text_correction_service: Optional[TextCorrectionService] = None


def get_text_correction_service(
    openai_client: Optional[OpenAIClient] = None,
    history_manager: Optional[HistoryManager] = None,
    system_prompt: Optional[str] = None
) -> TextCorrectionService:
    """
    Récupère l'instance globale du service de correction de texte.

    Args:
        openai_client: Client OpenAI (utilisé uniquement lors de l'initialisation)
        history_manager: Gestionnaire d'historique (utilisé uniquement lors de l'initialisation)
        system_prompt: Prompt système (utilisé uniquement lors de l'initialisation)

    Returns:
        Instance du service de correction de texte
    """
    global _text_correction_service
    if _text_correction_service is None:
        _text_correction_service = TextCorrectionService(
            openai_client, history_manager, system_prompt
        )
    return _text_correction_service


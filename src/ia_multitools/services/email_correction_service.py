"""
Service de correction d'e-mails.

Améliore et professionnalise les e-mails.
"""

import logging
from typing import Optional
from ..core.openai_client import OpenAIClient, get_openai_client
from ..core.history_manager import HistoryManager, get_history_manager
from .output_rules import build_tool_prompt, source_content

logger = logging.getLogger(__name__)


class EmailCorrectionService:
    """
    Service de correction d'e-mails.

    Utilise l'IA pour améliorer et professionnaliser les e-mails.
    """

    TOOL_NAME = "email_correction"

    def __init__(
        self,
        openai_client: Optional[OpenAIClient] = None,
        history_manager: Optional[HistoryManager] = None,
        system_prompt: Optional[str] = None
    ) -> None:
        """
        Initialise le service de correction d'e-mails.

        Args:
            openai_client: Client OpenAI
            history_manager: Gestionnaire d'historique
            system_prompt: Prompt système personnalisé
        """
        self.client = openai_client or get_openai_client()
        self.history = history_manager or get_history_manager()
        self.system_prompt = system_prompt or self._get_default_system_prompt()

        logger.info("Service de correction d'e-mails initialisé")

    def _get_default_system_prompt(self) -> str:
        """
        Retourne le prompt système par défaut.

        Returns:
            Prompt système
        """
        return (
            "Tu es un assistant de correction d'e-mails. "
            "Corrige le contenu en respectant les options sélectionnées. "
            "Retourne uniquement l'e-mail final, sans commentaires ni explications. "
            "Ne modifie pas l'intention du message original."
        )

    def set_system_prompt(self, prompt: str) -> None:
        """
        Définit un prompt système personnalisé.

        Args:
            prompt: Nouveau prompt système
        """
        self.system_prompt = prompt
        logger.debug("Prompt système mis à jour pour le service de correction d'e-mails")

    def correct_email(
        self,
        content: str,
        instructions: Optional[str] = None,
        make_professional: bool = False,
        add_greeting: bool = False,
        output_format: str = "text",
        temperature: Optional[float] = None
    ) -> Optional[str]:
        """
        Corrige et améliore un e-mail.

        Args:
            content: Contenu de l'e-mail
            instructions: Instructions complémentaires optionnelles
            make_professional: Rendre le ton plus professionnel
            add_greeting: Ajouter une formule de politesse
            output_format: Format de sortie ("text" ou "markdown")
            temperature: Température pour la génération

        Returns:
            E-mail corrigé ou None en cas d'erreur
        """
        if not content or not content.strip():
            logger.warning("Contenu vide fourni")
            return None

        try:
            rules = (
                "Corrige l'orthographe, la grammaire et la ponctuation de l'e-mail. "
                "Conserve le sens et les informations. Rends une seule version finale. "
                "Conserve impérativement le tutoiement ou le vouvoiement d'origine, "
                "y compris en mode professionnel. N'invente ni destinataire, ni signature.\n"
            )
            rules += (
                "Option professionnel ACTIVÉE : rends le ton plus professionnel, "
                "sans transformer le tutoiement en vouvoiement.\n"
                if make_professional else
                "Option professionnel DÉSACTIVÉE : conserve le ton et le registre d'origine. "
                "Ne professionnalise pas le message, ne le rends pas plus formel.\n"
            )
            rules += (
                "Option politesse ACTIVÉE : ajoute une salutation et une formule de politesse "
                "adaptées au ton si elles manquent, sans doubler celles déjà présentes."
                if add_greeting else
                "Option politesse DÉSACTIVÉE : n'ajoute aucune salutation, formule de "
                "politesse, formule de clôture ou signature. Conserve celles déjà présentes "
                "dans le texte source sans en inventer."
            )

            logger.info(
                f"Demande de correction d'e-mail (professionnel: {make_professional}, greeting: {add_greeting}, format: {output_format})")

            # Appel à l'IA
            response = self.client.constrained_completion(
                prompt=source_content("email", content),
                system_prompt=build_tool_prompt(
                    self.system_prompt, output_format, rules, instructions
                ),
                temperature=temperature
            )

            if response:
                # Sauvegarder dans l'historique
                self.history.add_entry(
                    tool_name=self.TOOL_NAME,
                    user_request=content,
                    ai_response=response,
                    metadata={
                        "instructions": instructions,
                        "make_professional": make_professional,
                        "add_greeting": add_greeting,
                        "output_format": output_format,
                        "content_length": len(content),
                        "temperature": self.client.temperature if temperature is None else temperature
                    }
                )

                logger.info("E-mail corrigé avec succès")
                return response
            else:
                logger.error("Aucune réponse de l'IA")
                return None

        except Exception as e:
            logger.error(f"Erreur lors de la correction de l'e-mail: {e}")
            return None

    def validate_email(self, content: str) -> tuple[bool, str]:
        """
        Valide un contenu d'e-mail avant correction.

        Args:
            content: Contenu à valider

        Returns:
            Tuple (valide, message_erreur)
        """
        if not content or not content.strip():
            return False, "Le contenu de l'e-mail ne peut pas être vide"

        if len(content) > 50000:
            return False, "Le contenu est trop long (max 50 000 caractères)"

        return True, ""


# Instance globale
_email_correction_service: Optional[EmailCorrectionService] = None


def get_email_correction_service(
    openai_client: Optional[OpenAIClient] = None,
    history_manager: Optional[HistoryManager] = None,
    system_prompt: Optional[str] = None
) -> EmailCorrectionService:
    """
    Récupère l'instance globale du service de correction d'e-mails.

    Args:
        openai_client: Client OpenAI (utilisé uniquement lors de l'initialisation)
        history_manager: Gestionnaire d'historique (utilisé uniquement lors de l'initialisation)
        system_prompt: Prompt système (utilisé uniquement lors de l'initialisation)

    Returns:
        Instance du service de correction d'e-mails
    """
    global _email_correction_service
    if _email_correction_service is None:
        _email_correction_service = EmailCorrectionService(
            openai_client, history_manager, system_prompt
        )
    return _email_correction_service

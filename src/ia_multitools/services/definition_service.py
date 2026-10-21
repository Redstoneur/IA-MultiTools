"""
Service de définition de mots et concepts.

Fournit des définitions claires et concises via l'IA.
"""

import logging
from typing import Optional
from ..core.openai_client import OpenAIClient, get_openai_client
from ..core.history_manager import HistoryManager, get_history_manager
from .output_rules import build_tool_prompt, source_content

logger = logging.getLogger(__name__)


class DefinitionService:
    """
    Service de définition de mots et concepts.
    
    Utilise l'IA pour fournir des définitions claires et concises.
    """
    
    TOOL_NAME = "definition"
    
    def __init__(
        self,
        openai_client: Optional[OpenAIClient] = None,
        history_manager: Optional[HistoryManager] = None,
        system_prompt: Optional[str] = None
    ) -> None:
        """
        Initialise le service de définition.
        
        Args:
            openai_client: Client OpenAI
            history_manager: Gestionnaire d'historique
            system_prompt: Prompt système personnalisé
        """
        self.client = openai_client or get_openai_client()
        self.history = history_manager or get_history_manager()
        self.system_prompt = system_prompt or self._get_default_system_prompt()
        
        logger.info("Service de définition initialisé")
    
    def _get_default_system_prompt(self) -> str:
        """
        Retourne le prompt système par défaut.
        
        Returns:
            Prompt système
        """
        return (
            "Tu es un assistant spécialisé dans les définitions. "
            "Fournis une définition claire, concise et précise du terme demandé. "
            "Ne fournis aucune information supplémentaire, seulement la définition. "
            "Sois direct et professionnel."
        )
    
    def set_system_prompt(self, prompt: str) -> None:
        """
        Définit un prompt système personnalisé.
        
        Args:
            prompt: Nouveau prompt système
        """
        self.system_prompt = prompt
        logger.debug("Prompt système mis à jour pour le service de définition")
    
    def get_definition(
        self,
        term: str,
        word_limit: Optional[int] = None,
        temperature: Optional[float] = None,
        *,
        output_format: str = "text",
        instructions: Optional[str] = None,
    ) -> Optional[str]:
        """
        Obtient la définition d'un terme.
        
        Args:
            term: Mot ou concept à définir
            word_limit: Limite optionnelle du nombre de mots
            temperature: Température pour la génération
            output_format: Texte brut ou Markdown
            instructions: Précisions complémentaires sur la définition
        
        Returns:
            Définition ou None en cas d'erreur
        """
        if not term or not term.strip():
            logger.warning("Terme vide fourni")
            return None
        
        try:
            if output_format not in ("text", "markdown"):
                raise ValueError("Format de définition non pris en charge.")
            # Construire le prompt utilisateur
            rules = "Fournis une seule définition du terme demandé."
            if word_limit and word_limit > 0:
                rules += f" Limite la définition à {word_limit} mots maximum."
            
            logger.info(f"Demande de définition: {term}")
            
            # Appel à l'IA
            response = self.client.constrained_completion(
                prompt=source_content("terme", term),
                system_prompt=build_tool_prompt(
                    self.system_prompt, output_format, rules, instructions
                ),
                temperature=temperature
            )
            
            if response:
                # Sauvegarder dans l'historique
                self.history.add_entry(
                    tool_name=self.TOOL_NAME,
                    user_request=term,
                    ai_response=response,
                    metadata={
                        "word_limit": word_limit,
                        "output_format": output_format,
                        "instructions": instructions,
                        "temperature": self.client.temperature if temperature is None else temperature
                    }
                )
                
                logger.info("Définition obtenue avec succès")
                return response
            else:
                logger.error("Aucune réponse de l'IA")
                return None
                
        except Exception as e:
            logger.error(f"Erreur lors de l'obtention de la définition: {e}")
            return None
    
    def validate_term(self, term: str) -> tuple[bool, str]:
        """
        Valide un terme avant de demander une définition.
        
        Args:
            term: Terme à valider
        
        Returns:
            Tuple (valide, message_erreur)
        """
        if not term or not term.strip():
            return False, "Le terme ne peut pas être vide"
        
        if len(term) > 200:
            return False, "Le terme est trop long (max 200 caractères)"
        
        return True, ""


# Instance globale
_definition_service: Optional[DefinitionService] = None


def get_definition_service(
    openai_client: Optional[OpenAIClient] = None,
    history_manager: Optional[HistoryManager] = None,
    system_prompt: Optional[str] = None
) -> DefinitionService:
    """
    Récupère l'instance globale du service de définition.
    
    Args:
        openai_client: Client OpenAI (utilisé uniquement lors de l'initialisation)
        history_manager: Gestionnaire d'historique (utilisé uniquement lors de l'initialisation)
        system_prompt: Prompt système (utilisé uniquement lors de l'initialisation)
    
    Returns:
        Instance du service de définition
    """
    global _definition_service
    if _definition_service is None:
        _definition_service = DefinitionService(openai_client, history_manager, system_prompt)
    return _definition_service

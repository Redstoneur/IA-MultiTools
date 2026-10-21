"""
Service de synonymes et antonymes.

Fournit des listes de synonymes et antonymes via l'IA.
"""

import logging
from typing import Optional, Literal
from ..core.openai_client import OpenAIClient, get_openai_client
from ..core.history_manager import HistoryManager, get_history_manager

logger = logging.getLogger(__name__)

SynonymMode = Literal["synonyms", "antonyms", "both"]


class SynonymService:
    """
    Service de synonymes et antonymes.
    
    Utilise l'IA pour fournir des listes de synonymes et/ou antonymes.
    """
    
    TOOL_NAME = "synonym"
    
    def __init__(
        self,
        openai_client: Optional[OpenAIClient] = None,
        history_manager: Optional[HistoryManager] = None,
        system_prompt: Optional[str] = None
    ) -> None:
        """
        Initialise le service de synonymes.
        
        Args:
            openai_client: Client OpenAI
            history_manager: Gestionnaire d'historique
            system_prompt: Prompt système personnalisé
        """
        self.client = openai_client or get_openai_client()
        self.history = history_manager or get_history_manager()
        self.system_prompt = system_prompt or self._get_default_system_prompt()
        
        logger.info("Service de synonymes initialisé")
    
    def _get_default_system_prompt(self) -> str:
        """
        Retourne le prompt système par défaut.
        
        Returns:
            Prompt système
        """
        return (
            "Tu es un assistant spécialisé dans les synonymes et antonymes. "
            "Fournis uniquement une liste de mots, sans explications, sans numérotation, "
            "séparés par des virgules. Ne fournis aucune autre information. "
            "Sois concis et précis."
        )
    
    def set_system_prompt(self, prompt: str) -> None:
        """
        Définit un prompt système personnalisé.
        
        Args:
            prompt: Nouveau prompt système
        """
        self.system_prompt = prompt
        logger.debug("Prompt système mis à jour pour le service de synonymes")
    
    def get_synonyms_antonyms(
        self,
        word: str,
        mode: SynonymMode = "synonyms",
        temperature: Optional[float] = None
    ) -> Optional[str]:
        """
        Obtient des synonymes et/ou antonymes d'un mot.
        
        Args:
            word: Mot à analyser
            mode: Mode de recherche ("synonyms", "antonyms", "both")
            temperature: Température pour la génération
        
        Returns:
            Liste de synonymes/antonymes ou None en cas d'erreur
        """
        if not word or not word.strip():
            logger.warning("Mot vide fourni")
            return None
        
        try:
            # Construire le prompt utilisateur
            if mode == "synonyms":
                user_prompt = f"Liste des synonymes pour : {word}"
            elif mode == "antonyms":
                user_prompt = f"Liste des antonymes pour : {word}"
            else:  # both
                user_prompt = (
                    f"Pour le mot '{word}':\n"
                    f"- Synonymes: \n"
                    f"- Antonymes: "
                )
            
            logger.info(f"Demande de {mode} pour: {word}")
            
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
                    user_request=word,
                    ai_response=response,
                    metadata={
                        "mode": mode,
                        "temperature": temperature or self.client.temperature
                    }
                )
                
                logger.info("Synonymes/antonymes obtenus avec succès")
                return response
            else:
                logger.error("Aucune réponse de l'IA")
                return None
                
        except Exception as e:
            logger.error(f"Erreur lors de l'obtention des synonymes/antonymes: {e}")
            return None
    
    def validate_word(self, word: str) -> tuple[bool, str]:
        """
        Valide un mot avant de demander des synonymes/antonymes.
        
        Args:
            word: Mot à valider
        
        Returns:
            Tuple (valide, message_erreur)
        """
        if not word or not word.strip():
            return False, "Le mot ne peut pas être vide"
        
        if len(word) > 100:
            return False, "Le mot est trop long (max 100 caractères)"
        
        return True, ""


# Instance globale
_synonym_service: Optional[SynonymService] = None


def get_synonym_service(
    openai_client: Optional[OpenAIClient] = None,
    history_manager: Optional[HistoryManager] = None,
    system_prompt: Optional[str] = None
) -> SynonymService:
    """
    Récupère l'instance globale du service de synonymes.
    
    Args:
        openai_client: Client OpenAI (utilisé uniquement lors de l'initialisation)
        history_manager: Gestionnaire d'historique (utilisé uniquement lors de l'initialisation)
        system_prompt: Prompt système (utilisé uniquement lors de l'initialisation)
    
    Returns:
        Instance du service de synonymes
    """
    global _synonym_service
    if _synonym_service is None:
        _synonym_service = SynonymService(openai_client, history_manager, system_prompt)
    return _synonym_service


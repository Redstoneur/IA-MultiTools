"""
Client pour l'API OpenAI et services compatibles.

Ce module fournit un client pour interagir avec OpenAI et tout service compatible
(LM Studio, LocalAI, llama.cpp, etc.).
"""

import logging
from typing import Optional, Dict, Any, List
import openai
from openai import OpenAI, OpenAIError
import ssl

logger = logging.getLogger(__name__)


class OpenAIClient:
    """
    Client pour l'API OpenAI et services compatibles.

    Supporte OpenAI, LM Studio, LocalAI, llama.cpp Server, Text Generation WebUI,
    et tout serveur compatible avec l'API OpenAI.
    """

    def __init__(
        self,
        api_key: str = "sk-dummy",
        base_url: str = "http://127.0.0.1:1234/v1",
        model: str = "meta-llama-3.1-8b-instruct",
        temperature: float = 0.2,
        max_tokens: Optional[int] = None,
        timeout: int = 60,
        verify_ssl: bool = False
    ) -> None:
        """
        Initialise le client OpenAI.

        Args:
            api_key: Clé API (peut être factice pour services locaux)
            base_url: URL de base de l'API
            model: Nom du modèle à utiliser
            temperature: Température pour la génération (0.0-2.0)
            max_tokens: Nombre max de tokens à générer (optionnel)
            timeout: Timeout en secondes
            verify_ssl: Vérifier les certificats SSL
        """
        self.api_key = api_key or "sk-dummy"
        self.base_url = base_url
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout
        self.verify_ssl = verify_ssl

        # Configuration SSL
        if not verify_ssl:
            ssl._create_default_https_context = ssl._create_unverified_context

        # Initialiser le client OpenAI
        try:
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
                timeout=self.timeout
            )
            logger.info(f"Client OpenAI initialisé - URL: {base_url}, Modèle: {model}")
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation du client OpenAI: {e}")
            raise

    def update_config(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        timeout: Optional[int] = None,
        verify_ssl: Optional[bool] = None
    ) -> None:
        """
        Met à jour la configuration du client.

        Args:
            api_key: Nouvelle clé API
            base_url: Nouvelle URL de base
            model: Nouveau modèle
            temperature: Nouvelle température
            max_tokens: Nouveau max tokens
            timeout: Nouveau timeout
            verify_ssl: Nouveau paramètre SSL
        """
        if api_key is not None:
            self.api_key = api_key
        if base_url is not None:
            self.base_url = base_url
        if model is not None:
            self.model = model
        if temperature is not None:
            self.temperature = temperature
        if max_tokens is not None:
            self.max_tokens = max_tokens
        if timeout is not None:
            self.timeout = timeout
        if verify_ssl is not None:
            self.verify_ssl = verify_ssl

        # Réinitialiser le client
        try:
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
                timeout=self.timeout
            )
            logger.info("Configuration du client OpenAI mise à jour")
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour de la configuration: {e}")
            raise

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> Optional[str]:
        """
        Effectue une complétion de chat.

        Args:
            messages: Liste des messages de la conversation
            system_prompt: Prompt système optionnel
            temperature: Température pour cette requête (surcharge la config)
            max_tokens: Max tokens pour cette requête (surcharge la config)
            stream: Activer le streaming (non implémenté)

        Returns:
            Réponse de l'IA ou None en cas d'erreur
        """
        try:
            # Ajouter le prompt système si fourni
            if system_prompt:
                messages = [{"role": "system", "content": system_prompt}] + messages

            # Paramètres de la requête
            request_params = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature if temperature is not None else self.temperature,
            }

            if max_tokens or self.max_tokens:
                request_params["max_tokens"] = max_tokens or self.max_tokens

            logger.debug(f"Envoi de la requête à l'API - Modèle: {self.model}, "
                        f"Messages: {len(messages)}")

            # Appel à l'API
            response = self.client.chat.completions.create(**request_params)

            # Extraire la réponse
            content = response.choices[0].message.content
            logger.info("Réponse reçue de l'API avec succès")

            return content

        except OpenAIError as e:
            logger.error(f"Erreur OpenAI: {e}")
            return None
        except Exception as e:
            logger.error(f"Erreur lors de la complétion: {e}")
            return None

    def simple_completion(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> Optional[str]:
        """
        Effectue une complétion simple (un seul message utilisateur).

        Args:
            prompt: Prompt utilisateur
            system_prompt: Prompt système optionnel
            temperature: Température pour cette requête
            max_tokens: Nombre max de tokens à générer (optionnel)

        Returns:
            Réponse de l'IA ou None en cas d'erreur
        """
        messages = [{"role": "user", "content": prompt}]
        return self.chat_completion(
            messages=messages,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens
        )

    def test_connection(self) -> tuple[bool, str]:
        """
        Test la connexion à l'API.

        Returns:
            Tuple (succès, message)
        """
        try:
            logger.info("Test de connexion à l'API...")

            # Essayer une requête simple
            messages = [{"role": "user", "content": "Réponds juste 'OK' en un mot."}]
            response = self.chat_completion(messages, temperature=0.1)

            if response:
                logger.info("Connexion à l'API réussie")
                return True, "Connexion réussie"
            else:
                logger.warning("Connexion échouée: aucune réponse")
                return False, "Aucune réponse de l'API"

        except Exception as e:
            error_msg = f"Erreur de connexion: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

    def list_models(self) -> List[str]:
        """
        Liste les modèles disponibles.

        Returns:
            Liste des noms de modèles
        """
        try:
            models = self.client.models.list()
            model_names = [model.id for model in models.data]
            logger.info(f"Modèles disponibles: {len(model_names)}")
            return model_names
        except Exception as e:
            logger.error(f"Erreur lors du listage des modèles: {e}")
            return []

    def get_model_info(self) -> Dict[str, Any]:
        """
        Récupère les informations du modèle actuel.

        Returns:
            Dictionnaire d'informations
        """
        return {
            "model": self.model,
            "base_url": self.base_url,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "timeout": self.timeout,
            "verify_ssl": self.verify_ssl
        }


# Instance globale
_openai_client: Optional[OpenAIClient] = None


def get_openai_client(
    api_key: str = "sk-dummy",
    base_url: str = "http://127.0.0.1:1234/v1",
    model: str = "meta-llama-3.1-8b-instruct",
    temperature: float = 0.2,
    timeout: int = 60,
    verify_ssl: bool = False
) -> OpenAIClient:
    """
    Récupère l'instance globale du client OpenAI.

    Args:
        api_key: Clé API (utilisé uniquement lors de l'initialisation)
        base_url: URL de base (utilisé uniquement lors de l'initialisation)
        model: Modèle (utilisé uniquement lors de l'initialisation)
        temperature: Température (utilisé uniquement lors de l'initialisation)
        timeout: Timeout (utilisé uniquement lors de l'initialisation)
        verify_ssl: Vérifier SSL (utilisé uniquement lors de l'initialisation)

    Returns:
        Instance du client OpenAI
    """
    global _openai_client
    if _openai_client is None:
        _openai_client = OpenAIClient(
            api_key=api_key,
            base_url=base_url,
            model=model,
            temperature=temperature,
            timeout=timeout,
            verify_ssl=verify_ssl
        )
    return _openai_client


def init_openai_client(
    api_key: str = "sk-dummy",
    base_url: str = "http://127.0.0.1:1234/v1",
    model: str = "meta-llama-3.1-8b-instruct",
    temperature: float = 0.2,
    max_tokens: Optional[int] = None,
    timeout: int = 60,
    verify_ssl: bool = False
) -> OpenAIClient:
    """
    Initialise le client OpenAI global.

    Args:
        api_key: Clé API
        base_url: URL de base
        model: Modèle
        temperature: Température
        max_tokens: Max tokens
        timeout: Timeout
        verify_ssl: Vérifier SSL

    Returns:
        Instance du client OpenAI
    """
    global _openai_client
    _openai_client = OpenAIClient(
        api_key=api_key,
        base_url=base_url,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        timeout=timeout,
        verify_ssl=verify_ssl
    )
    return _openai_client


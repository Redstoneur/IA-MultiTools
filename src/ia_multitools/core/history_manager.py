"""
Gestionnaire d'historique chiffré.

Ce module gère l'historique des requêtes et réponses de l'IA de manière sécurisée.
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict

from .secure_storage import SecureStorage, get_secure_storage

logger = logging.getLogger(__name__)


@dataclass
class HistoryEntry:
    """Entrée d'historique."""
    id: str
    timestamp: str
    tool_name: str
    user_request: str
    ai_response: str
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convertit l'entrée en dictionnaire."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HistoryEntry":
        """Crée une entrée depuis un dictionnaire."""
        return cls(**data)


class HistoryManager:
    """
    Gestionnaire d'historique chiffré.

    Stocke et récupère l'historique des interactions avec l'IA de manière sécurisée.
    """

    HISTORY_FILENAME = "history"

    def __init__(
        self,
        storage: Optional[SecureStorage] = None,
        max_entries: int = 1000,
        enabled: bool = True
    ) -> None:
        """
        Initialise le gestionnaire d'historique.

        Args:
            storage: Gestionnaire de stockage sécurisé
            max_entries: Nombre maximum d'entrées à conserver
            enabled: Active ou désactive l'historique
        """
        self.storage = storage or get_secure_storage()
        self.max_entries = max_entries
        self.enabled = enabled
        self.entries: List[HistoryEntry] = []

        if self.enabled:
            self._load()

        logger.info(f"Gestionnaire d'historique initialisé - Activé: {enabled}, "
                   f"Max entrées: {max_entries}")

    def _load(self) -> None:
        """Charge l'historique depuis le stockage sécurisé."""
        try:
            data = self.storage.load_encrypted(self.HISTORY_FILENAME)

            if data and "entries" in data:
                self.entries = [
                    HistoryEntry.from_dict(entry)
                    for entry in data["entries"]
                ]
                logger.info(f"Historique chargé: {len(self.entries)} entrées")
            else:
                logger.info("Aucun historique trouvé, démarrage avec un historique vide")
                self.entries = []
        except Exception as e:
            logger.error(f"Erreur lors du chargement de l'historique: {e}")
            self.entries = []

    def _save(self) -> bool:
        """
        Sauvegarde l'historique dans le stockage sécurisé.

        Returns:
            True si la sauvegarde a réussi
        """
        try:
            data = {
                "entries": [entry.to_dict() for entry in self.entries],
                "metadata": {
                    "last_updated": datetime.now().isoformat(),
                    "count": len(self.entries)
                }
            }

            success = self.storage.save_encrypted(self.HISTORY_FILENAME, data)

            if success:
                logger.debug(f"Historique sauvegardé: {len(self.entries)} entrées")

            return success
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde de l'historique: {e}")
            return False

    def add_entry(
        self,
        tool_name: str,
        user_request: str,
        ai_response: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Ajoute une entrée à l'historique.

        Args:
            tool_name: Nom de l'outil utilisé
            user_request: Requête de l'utilisateur
            ai_response: Réponse de l'IA
            metadata: Métadonnées optionnelles

        Returns:
            ID de l'entrée créée, ou None si l'historique est désactivé
        """
        if not self.enabled:
            logger.debug("Historique désactivé, entrée non ajoutée")
            return None

        import uuid
        entry_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()

        entry = HistoryEntry(
            id=entry_id,
            timestamp=timestamp,
            tool_name=tool_name,
            user_request=user_request,
            ai_response=ai_response,
            metadata=metadata or {}
        )

        self.entries.append(entry)

        # Limiter le nombre d'entrées
        if len(self.entries) > self.max_entries:
            removed = len(self.entries) - self.max_entries
            self.entries = self.entries[-self.max_entries:]
            logger.debug(f"{removed} anciennes entrées supprimées")

        self._save()
        logger.debug(f"Entrée d'historique ajoutée: {entry_id}")

        return entry_id

    def get_entries(
        self,
        tool_name: Optional[str] = None,
        limit: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[HistoryEntry]:
        """
        Récupère des entrées de l'historique.

        Args:
            tool_name: Filtrer par nom d'outil
            limit: Nombre maximum d'entrées à retourner
            start_date: Date de début du filtre
            end_date: Date de fin du filtre

        Returns:
            Liste des entrées correspondant aux critères
        """
        if not self.enabled:
            return []

        filtered_entries = self.entries.copy()

        # Filtrer par outil
        if tool_name:
            filtered_entries = [
                entry for entry in filtered_entries
                if entry.tool_name == tool_name
            ]

        # Filtrer par date
        if start_date or end_date:
            filtered_entries = [
                entry for entry in filtered_entries
                if self._is_in_date_range(entry, start_date, end_date)
            ]

        # Trier par date décroissante (plus récent en premier)
        filtered_entries.sort(
            key=lambda e: datetime.fromisoformat(e.timestamp),
            reverse=True
        )

        # Limiter le nombre de résultats
        if limit:
            filtered_entries = filtered_entries[:limit]

        return filtered_entries

    def _is_in_date_range(
        self,
        entry: HistoryEntry,
        start_date: Optional[datetime],
        end_date: Optional[datetime]
    ) -> bool:
        """
        Vérifie si une entrée est dans l'intervalle de dates.

        Args:
            entry: Entrée à vérifier
            start_date: Date de début
            end_date: Date de fin

        Returns:
            True si l'entrée est dans l'intervalle
        """
        entry_date = datetime.fromisoformat(entry.timestamp)

        if start_date and entry_date < start_date:
            return False

        if end_date and entry_date > end_date:
            return False

        return True

    def get_entry_by_id(self, entry_id: str) -> Optional[HistoryEntry]:
        """
        Récupère une entrée par son ID.

        Args:
            entry_id: ID de l'entrée

        Returns:
            Entrée trouvée ou None
        """
        for entry in self.entries:
            if entry.id == entry_id:
                return entry
        return None

    def delete_entry(self, entry_id: str) -> bool:
        """
        Supprime une entrée de l'historique.

        Args:
            entry_id: ID de l'entrée à supprimer

        Returns:
            True si la suppression a réussi
        """
        initial_count = len(self.entries)
        self.entries = [entry for entry in self.entries if entry.id != entry_id]

        if len(self.entries) < initial_count:
            self._save()
            logger.info(f"Entrée supprimée: {entry_id}")
            return True

        logger.warning(f"Entrée non trouvée: {entry_id}")
        return False

    def clear_all(self) -> bool:
        """
        Supprime tout l'historique.

        Returns:
            True si la suppression a réussi
        """
        self.entries = []
        success = self._save()

        if success:
            logger.warning("Tout l'historique a été supprimé")

        return success

    def cleanup_old_entries(self, days: int = 90) -> int:
        """
        Supprime les entrées plus anciennes que le nombre de jours spécifié.

        Args:
            days: Nombre de jours de rétention

        Returns:
            Nombre d'entrées supprimées
        """
        if days <= 0:
            return 0

        cutoff_date = datetime.now() - timedelta(days=days)
        initial_count = len(self.entries)

        self.entries = [
            entry for entry in self.entries
            if datetime.fromisoformat(entry.timestamp) >= cutoff_date
        ]

        removed_count = initial_count - len(self.entries)

        if removed_count > 0:
            self._save()
            logger.info(f"{removed_count} anciennes entrées supprimées (> {days} jours)")

        return removed_count

    def get_statistics(self) -> Dict[str, Any]:
        """
        Calcule des statistiques sur l'historique.

        Returns:
            Dictionnaire de statistiques
        """
        if not self.entries:
            return {
                "total_entries": 0,
                "tools_usage": {},
                "oldest_entry": None,
                "newest_entry": None
            }

        tools_usage: Dict[str, int] = {}
        for entry in self.entries:
            tools_usage[entry.tool_name] = tools_usage.get(entry.tool_name, 0) + 1

        timestamps = [datetime.fromisoformat(e.timestamp) for e in self.entries]

        return {
            "total_entries": len(self.entries),
            "tools_usage": tools_usage,
            "oldest_entry": min(timestamps).isoformat(),
            "newest_entry": max(timestamps).isoformat()
        }

    def set_enabled(self, enabled: bool) -> None:
        """
        Active ou désactive l'historique.

        Args:
            enabled: True pour activer, False pour désactiver
        """
        self.enabled = enabled
        logger.info(f"Historique {'activé' if enabled else 'désactivé'}")


# Instance globale
_history_manager: Optional[HistoryManager] = None


def get_history_manager(max_entries: int = 1000, enabled: bool = True) -> HistoryManager:
    """
    Récupère l'instance globale du gestionnaire d'historique.

    Args:
        max_entries: Nombre max d'entrées (utilisé uniquement lors de l'initialisation)
        enabled: Active l'historique (utilisé uniquement lors de l'initialisation)

    Returns:
        Instance du gestionnaire d'historique
    """
    global _history_manager
    if _history_manager is None:
        _history_manager = HistoryManager(max_entries=max_entries, enabled=enabled)
    return _history_manager


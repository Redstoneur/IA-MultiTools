"""Validation shared by the initial wizard and settings."""


def validate_ai_settings(base_url, model, api_key, temperature, timeout, verify_ssl,
                         require_model=True) -> tuple[str, str, str, float, int, bool]:
    base_url, model = base_url.strip(), model.strip()
    if not base_url:
        raise ValueError("Veuillez entrer l'URL de base.")
    if require_model and not model:
        raise ValueError("Veuillez entrer ou sélectionner le nom du modèle.")
    try:
        temperature = float(temperature)
    except ValueError as exc:
        raise ValueError("La température doit être un nombre entre 0 et 2.") from exc
    if not 0 <= temperature <= 2:
        raise ValueError("La température doit être comprise entre 0 et 2.")
    try:
        timeout = int(timeout)
    except ValueError as exc:
        raise ValueError("Le timeout doit être un nombre entier positif de secondes.") from exc
    if timeout <= 0:
        raise ValueError("Le timeout doit être supérieur à zéro.")
    return base_url, model, api_key.strip(), temperature, timeout, verify_ssl

"""
Configuración de idioma para la aplicación
Archivo centralizado para gestionar el idioma de toda la app
"""

# Idioma actual de la aplicación ('es' para español, 'en' para inglés)
CURRENT_LANGUAGE = 'es'

# Idiomas disponibles
AVAILABLE_LANGUAGES = {
    'es': 'Español',
    'en': 'English'
}

def set_language(language_code: str):
    """
    Cambia el idioma actual de la aplicación.
    
    Args:
        language_code: Código de idioma ('es' o 'en')
    """
    global CURRENT_LANGUAGE
    if language_code in AVAILABLE_LANGUAGES:
        CURRENT_LANGUAGE = language_code
        return True
    return False

def get_language() -> str:
    """
    Retorna el código del idioma actual.
    
    Returns:
        str: Código de idioma ('es' o 'en')
    """
    return CURRENT_LANGUAGE

def get_available_languages() -> dict:
    """
    Retorna el diccionario de idiomas disponibles.
    
    Returns:
        dict: Diccionario con códigos y nombres de idiomas
    """
    return AVAILABLE_LANGUAGES.copy()

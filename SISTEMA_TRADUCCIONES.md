# Sistema de Traducciones - Torneo de Fútbol

## Descripción

La aplicación cuenta con un sistema de traducciones que permite cambiar entre español e inglés de forma dinámica.

## Archivos Involucrados

### 1. config_idioma.py
Archivo de configuración centralizado que gestiona el idioma actual de la ventana Gestión de Partidos.

# Cambiar idioma
set_language('en')  # Cambiar a inglés
set_language('es')  # Cambiar a español

# Obtener idioma actual
current = get_language()  # Retorna 'es' o 'en'

# Obtener idiomas disponibles
langs = get_available_languages()  # {'es': 'Español', 'en': 'English'}

## Notas Importantes

- El idioma se almacena en config_idioma.CURRENT_LANGUAGE
- La función translate() sin parámetro de idioma usa el configurado globalmente
- Para cambiar el idioma de toda la app, usar set_language(language_code)
- Los cambios de idioma requieren actualizar los widgets (llamar refresh_ui() o similar)

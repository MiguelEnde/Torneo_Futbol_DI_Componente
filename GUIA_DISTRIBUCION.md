# Gestor de Torneo de Fútbol - Guía de Distribución

## Opción 1: Usar los scripts ejecutables (RECOMENDADO)

Esta es la forma más sencilla de distribuir la aplicación:

### Para Windows:
1. Comprime toda la carpeta del proyecto
2. El usuario extrae la carpeta
3. El usuario hace doble clic en `EJECUTAR.bat`
4. La aplicación se inicia automáticamente

**Requisitos del usuario:**
- Python 3.10+ instalado (descargar desde python.org)
- PySide6 se instala automáticamente

### Para Linux/Mac:
1. Comprime toda la carpeta del proyecto
2. El usuario extrae la carpeta
3. El usuario abre terminal en la carpeta
4. El usuario ejecuta: `bash EJECUTAR.sh` o `chmod +x EJECUTAR.sh && ./EJECUTAR.sh`
5. La aplicación se inicia automáticamente

**Requisitos del usuario:**
- Python 3.10+ instalado
- PySide6 se instala automáticamente

---

## Opción 2: Crear un ejecutable standalone (Alternativa)

Si necesitas un .exe único sin dependencias externas:

```bash
# Instalar PyInstaller
pip install pyinstaller

# Compilar (desde la carpeta raíz del proyecto)
pyinstaller --onefile --windowed ^
  --add-data="RESOURCES:RESOURCES" ^
  --add-data="DATA:DATA" ^
  --add-data="COMPONENTS:COMPONENTS" ^
  --add-data="CONTROLLERS:CONTROLLERS" ^
  --add-data="MODELS:MODELS" ^
  --add-data="VIEWS:VIEWS" ^
  --add-data="WIDGET:WIDGET" ^
  --name="Torneo_Futbol" ^
  main.py
```

Esto generará: `dist/Torneo_Futbol.exe`

---

## Estructura de la Carpeta para Distribuir

```
Torneo_Futbol/
├── EJECUTAR.bat              ← Para Windows
├── EJECUTAR.sh               ← Para Linux/Mac
├── README.md
├── requirements.txt
├── main.py
├── config.py
├── COMPONENTS/
├── CONTROLLERS/
├── MODELS/
├── RESOURCES/
├── VIEWS/
├── WIDGET/
└── DATA/
```

---

## Instrucciones para el Usuario Final

### En Windows:
```
1. Extrae la carpeta Torneo_Futbol.zip
2. Abre la carpeta
3. Haz doble clic en "EJECUTAR.bat"
4. ¡Listo! La aplicación se abre
```

### En Linux/Mac:
```
1. Extrae la carpeta Torneo_Futbol.zip
2. Abre terminal en esa carpeta
3. Ejecuta: bash EJECUTAR.sh
4. ¡Listo! La aplicación se abre
```

---

## Solución de Problemas

### Error: "Python no está instalado"
→ Descargar Python desde: https://www.python.org/downloads/

### Error: "No se encontró PySide6"
→ Ejecutar manualmente: `pip install PySide6`

### La aplicación se cierra inmediatamente
→ Abrir terminal/CMD en la carpeta del proyecto
→ Ejecutar: `python main.py`
→ Ver el mensaje de error

---

## Archivos Importantes

- `main.py` - Archivo principal de la aplicación
- `config.py` - Configuración de la aplicación
- `requirements.txt` - Dependencias Python
- `RECURSOS/` - Imágenes, iconos, traducciones
- `MODELS/` - Modelos de datos y base de datos
- `VIEWS/` - Interfaces gráficas
- `CONTROLLERS/` - Lógica de la aplicación


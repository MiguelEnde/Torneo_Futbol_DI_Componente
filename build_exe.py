"""
Script para crear un ejecutable portable de la aplicación
Copia todos los archivos necesarios en una carpeta que se puede distribuir
"""

import os
import shutil
import subprocess
import sys

def crear_ejecutable():
    """Crea un ejecutable usando PyInstaller de forma robusta"""
    
    print("=" * 60)
    print("Generando ejecutable del Gestor de Torneo de Fútbol...")
    print("=" * 60)
    
    # Comando para ejecutar PyInstaller
    cmd = [
        sys.executable,
        "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--name=Torneo_Futbol",
        "--add-data=RESOURCES:RESOURCES",
        "--add-data=DATA:DATA",
        "--add-data=COMPONENTS:COMPONENTS",
        "--add-data=CONTROLLERS:CONTROLLERS",
        "--add-data=MODELS:MODELS",
        "--add-data=VIEWS:VIEWS",
        "--add-data=WIDGET:WIDGET",
        "main.py"
    ]
    
    print("\nEjecutando PyInstaller...")
    print(f"Comando: {' '.join(cmd)}\n")
    
    try:
        # Ejecutar el comando
        result = subprocess.run(cmd, check=False)
        
        if result.returncode == 0:
            exe_path = "dist/Torneo_Futbol.exe"
            if os.path.exists(exe_path):
                size_mb = os.path.getsize(exe_path) / (1024 * 1024)
                print("\n" + "=" * 60)
                print(f"✓ Ejecutable creado exitosamente!")
                print(f"  Ubicación: {os.path.abspath(exe_path)}")
                print(f"  Tamaño: {size_mb:.2f} MB")
                print("=" * 60)
                print("\nPuedes distribuir este archivo a cualquier persona.")
                print("Solo necesita ejecutarlo, sin instalar nada más.")
            else:
                print("\n✗ No se pudo encontrar el ejecutable generado")
                return False
        else:
            print(f"\n✗ Error al ejecutar PyInstaller (código: {result.returncode})")
            return False
            
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = crear_ejecutable()
    sys.exit(0 if success else 1)

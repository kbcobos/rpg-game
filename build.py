import subprocess
import sys
import os
import shutil


def check_pyinstaller():
    """Verifica que PyInstaller este instalado."""
    try:
        import PyInstaller
        print(f"  PyInstaller {PyInstaller.__version__} encontrado. OK.")
        return True
    except ImportError:
        print("  PyInstaller no esta instalado.")
        print("  Instalalalo con:  pip install pyinstaller")
        return False


def clean_previous_build():
    """Elimina carpetas de compilaciones anteriores."""
    for folder in ("build", "dist", "__pycache__"):
        if os.path.exists(folder):
            shutil.rmtree(folder)
            print(f"  Carpeta '{folder}' eliminada.")


def build():
    print()
    print("=" * 50)
    print("  DUNGEONS OF AETHORIA — Build Script")
    print("=" * 50)
    print()

    print("[ 1/3 ] Verificando PyInstaller...")
    if not check_pyinstaller():
        sys.exit(1)

    print()
    print("[ 2/3 ] Limpiando compilaciones anteriores...")
    clean_previous_build()

    print()
    print("[ 3/3 ] Compilando... (puede tardar un minuto)")
    print()

    result = subprocess.run(
        [sys.executable, "-m", "PyInstaller", "dungeons_of_aethoria.spec"],
        capture_output=False,
    )

    print()
    if result.returncode == 0:
        exe_name = "dungeons-of-aethoria.exe" if sys.platform == "win32" else "dungeons-of-aethoria"
        exe_path = os.path.join("dist", exe_name)
        print("=" * 50)
        print("  Compilacion exitosa!")
        print(f"  Ejecutable: {exe_path}")
        print()
        print("  Para jugar:")
        if sys.platform == "win32":
            print(f"    .\\dist\\{exe_name}")
        else:
            print(f"    ./dist/{exe_name}")
        print("=" * 50)
    else:
        print("=" * 50)
        print("  La compilacion fallo.")
        print("  Revisa los mensajes de error arriba.")
        print("=" * 50)
        sys.exit(1)


if __name__ == "__main__":
    build()

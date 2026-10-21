"""
Script de build PyInstaller pour IA-MultiTools.

Génère un exécutable standalone pour Windows et Linux.
"""

import os
import sys
import platform
import subprocess
from pathlib import Path

def build_executable():
    """Construit l'exécutable avec PyInstaller."""

    print("=" * 60)
    print("Build IA-MultiTools")
    print("=" * 60)

    # Vérifier que PyInstaller est installé
    try:
        import PyInstaller
    except ImportError:
        print("❌ PyInstaller n'est pas installé.")
        print("Installez-le avec: pip install pyinstaller")
        return False

    # Déterminer le système
    system = platform.system()
    print(f"\n📦 Système détecté: {system}")

    # Paramètres communs
    main_script = "src/ia_multitools/main.py"
    app_name = "IA-MultiTools"

    # Commande PyInstaller
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name", app_name,
        "--clean",

        # Imports cachés
        "--hidden-import", "ttkbootstrap",
        "--hidden-import", "openai",
        "--hidden-import", "cryptography",
        "--hidden-import", "keyring",
        "--hidden-import", "platformdirs",
        "--hidden-import", "dotenv",

        # Exclure des modules non nécessaires
        "--exclude-module", "pytest",
        "--exclude-module", "numpy",
        "--exclude-module", "pandas",

        # Script principal
        main_script
    ]

    # Icône (si disponible)
    icon_path = Path("assets/icon.ico" if system == "Windows" else "assets/icon.png")
    if icon_path.exists():
        cmd.extend(["--icon", str(icon_path)])
        print(f"✓ Icône trouvée: {icon_path}")
    else:
        print(f"⚠ Icône non trouvée: {icon_path} (optionnel)")

    # Afficher la commande
    print(f"\n🔧 Commande PyInstaller:")
    print(" ".join(cmd))
    print()

    # Exécuter
    try:
        print("⏳ Build en cours... (cela peut prendre plusieurs minutes)\n")
        result = subprocess.run(cmd, check=True)

        if result.returncode == 0:
            print("\n" + "=" * 60)
            print("✅ Build réussi!")
            print("=" * 60)

            # Localiser l'exécutable
            if system == "Windows":
                exe_path = Path("dist") / f"{app_name}.exe"
            else:
                exe_path = Path("dist") / app_name

            if exe_path.exists():
                size_mb = exe_path.stat().st_size / (1024 * 1024)
                print(f"\n📦 Exécutable créé: {exe_path}")
                print(f"📊 Taille: {size_mb:.1f} MB")

            print("\n💡 Pour tester:")
            if system == "Windows":
                print(f"   {exe_path}")
            else:
                print(f"   chmod +x {exe_path}")
                print(f"   ./{exe_path}")

            return True
        else:
            print("\n❌ Build échoué.")
            return False

    except subprocess.CalledProcessError as e:
        print(f"\n❌ Erreur lors du build: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {e}")
        return False


def clean_build_files():
    """Nettoie les fichiers de build."""
    import shutil

    print("\n🧹 Nettoyage des fichiers de build...")

    dirs_to_clean = ["build", "dist", "__pycache__"]
    files_to_clean = ["*.spec"]

    for dir_name in dirs_to_clean:
        dir_path = Path(dir_name)
        if dir_path.exists():
            shutil.rmtree(dir_path)
            print(f"  ✓ Supprimé: {dir_path}")

    # Supprimer les fichiers .spec
    for spec_file in Path(".").glob("*.spec"):
        spec_file.unlink()
        print(f"  ✓ Supprimé: {spec_file}")

    print("✓ Nettoyage terminé\n")


def main():
    """Fonction principale."""
    if len(sys.argv) > 1 and sys.argv[1] == "clean":
        clean_build_files()
        return

    # Vérifier que nous sommes à la racine du projet
    if not Path("src/ia_multitools/main.py").exists():
        print("❌ Erreur: Lancez ce script depuis la racine du projet")
        return

    # Build
    success = build_executable()

    if success:
        print("\n✅ Build terminé avec succès!")
        print("\nCommandes disponibles:")
        print("  python build.py        - Build l'exécutable")
        print("  python build.py clean  - Nettoie les fichiers de build")
    else:
        print("\n❌ Le build a échoué.")
        sys.exit(1)


if __name__ == "__main__":
    main()


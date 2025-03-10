import os

def sanitize_name(name):
    """Remplace les espaces et les virgules par des underscores"""
    return name.replace(" ", "_").replace(",", "")

def rename_files_and_folders_recursively(base_directory):
    """Renomme récursivement fichiers et dossiers pour éviter les caractères problématiques"""

    # 🔹 Étape 1 : Renommer les fichiers (pour éviter qu'un dossier renommé casse les chemins)
    for root, _, files in os.walk(base_directory, topdown=False):  # Parcours en profondeur (bottom-up)
        for filename in files:
            old_path = os.path.join(root, filename)
            new_filename = sanitize_name(filename)
            new_path = os.path.join(root, new_filename)

            if old_path != new_path:
                print(f"Renaming file: {old_path} -> {new_path}")
                os.rename(old_path, new_path)

    # 🔹 Étape 2 : Renommer les dossiers après les fichiers
    for root, dirs, _ in os.walk(base_directory, topdown=False):  # Toujours bottom-up pour éviter les conflits
        for dirname in dirs:
            old_path = os.path.join(root, dirname)
            new_dirname = sanitize_name(dirname)
            new_path = os.path.join(root, new_dirname)

            if old_path != new_path:
                print(f"Renaming directory: {old_path} -> {new_path}")
                os.rename(old_path, new_path)

# 🔹 Appliquer la fonction au répertoire principal
base_directory = "/Users/molli-p/BodyOfKnowledge"
rename_files_and_folders_recursively(base_directory)

import os
import shutil

def sort_files(folder_path: str):
    if not os.path.exists(folder_path):
        print(f"❌ Folder '{folder_path}' does not exist.")
        return

    # Create a dictionary of common file categories
    file_types = {
        "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg"],
        "Videos": [".mp4", ".mov", ".avi", ".mkv", ".flv"],
        "Documents": [".pdf", ".docx", ".doc", ".txt", ".pptx", ".xlsx", ".odt"],
        "Music": [".mp3", ".wav", ".aac", ".flac"],
        "Archives": [".zip", ".tar", ".gz", ".rar", ".7z"],
        "Code": [".py", ".js", ".html", ".css", ".java", ".cpp", ".go", ".ts"],
        "Spreadsheets": [".csv", ".xls", ".xlsx"],
        "Others": []
    }

    # Iterate over all files
    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)

        # Skip directories
        if os.path.isdir(file_path):
            continue

        # Get file extension
        _, ext = os.path.splitext(file)
        ext = ext.lower()

        # Find category
        moved = False
        for category, extensions in file_types.items():
            if ext in extensions:
                category_path = os.path.join(folder_path, category)
                os.makedirs(category_path, exist_ok=True)
                shutil.move(file_path, os.path.join(category_path, file))
                print(f"📂 Moved: {file} → {category}/")
                moved = True
                break

        # If extension not found, move to Others
        if not moved:
            other_path = os.path.join(folder_path, "Others")
            os.makedirs(other_path, exist_ok=True)
            shutil.move

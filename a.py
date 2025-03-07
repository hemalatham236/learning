import os

# Define the directory structure
structure = {
    "flask_app": {
        "static": {
            "css": ["styles.css"],
            "plot.png": ""
        },
        "templates": [
            "login.html",
            "dashboard.html",
            "overview.html",
            "visualize.html"
        ],
        "uploads": [],
        "app.py": ""
    }
}

def create_structure(base_path, structure):
    for name, content in structure.items():
        path = os.path.join(base_path, name)
        if isinstance(content, dict):
            os.makedirs(path, exist_ok=True)
            create_structure(path, content)
        elif isinstance(content, list):
            os.makedirs(path, exist_ok=True)
            for file_name in content:
                open(os.path.join(path, file_name), 'w').close()
        else:
            open(path, 'w').close()

# Create the directory structure
base_path = "."
create_structure(base_path, structure)

print("Project structure created successfully!")

import importlib.util, json, sys

REQUIRED = {
    "docx": "python-docx", "fitz": "PyMuPDF",
    "openpyxl": "openpyxl", "pptx": "python-pptx", "jinja2": "jinja2",
}

def check_setup() -> dict:
    installed, missing = [], []
    for import_name, pip_name in REQUIRED.items():
        (installed if importlib.util.find_spec(import_name) else missing).append(pip_name)
    return {
        "ok": len(missing) == 0,
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "installed": installed, "missing": missing,
    }

if __name__ == "__main__":
    result = check_setup()
    print(json.dumps(result))
    sys.exit(0 if result["ok"] else 1)

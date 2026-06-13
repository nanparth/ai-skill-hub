import importlib.util, json, sys

REQUIRED = {
    "docx": "python-docx", "fitz": "PyMuPDF",
    "openpyxl": "openpyxl", "pptx": "python-pptx", "jinja2": "jinja2",
}

# Optional packages: absence does not set ok=false; missing entry names the pip package.
OPTIONAL = {
    "pdfplumber": {"pip_name": "pdfplumber", "purpose": "PDF tables"},
}

def check_setup() -> dict:
    installed, missing = [], []
    for import_name, pip_name in REQUIRED.items():
        (installed if importlib.util.find_spec(import_name) else missing).append(pip_name)
    optional = {}
    for import_name, meta in OPTIONAL.items():
        optional[import_name] = {
            "installed": importlib.util.find_spec(import_name) is not None,
            "pip_name": meta["pip_name"],
            "purpose": meta["purpose"],
        }
    return {
        "ok": len(missing) == 0,
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "installed": installed, "missing": missing,
        "optional": optional,
    }

if __name__ == "__main__":
    result = check_setup()
    print(json.dumps(result))
    sys.exit(0 if result["ok"] else 1)

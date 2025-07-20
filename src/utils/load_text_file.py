def load_txt_file(path: str) -> str:
    try:
        with open(path, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return None

def index() -> str:
    with open("templates/index.html") as f:
        return f.read()
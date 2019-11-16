import os
from pathlib import Path

from .app import create_app


def main():
    path = Path(os.path.abspath(__file__)).parent
    config_file = path / ".." / "conf" / "pyrsched.dev.ini"
    app = create_app(config_file.resolve())
    app.run(port=8080)


if __name__ == "__main__":
    main()

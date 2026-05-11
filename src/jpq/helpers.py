import os


def env(name: str) -> str:
    return os.environ[name]

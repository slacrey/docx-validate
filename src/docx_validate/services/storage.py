from pathlib import Path
import json

class LocalStorage:
    def __init__(self, root: Path) -> None:
        self.root = root

    def write_bytes(self, object_key: str, content: bytes) -> str:
        path = self.root / object_key
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        return object_key

    def write_json(self, object_key: str, content: dict[str, object]) -> str:
        return self.write_bytes(
            object_key,
            json.dumps(content, ensure_ascii=False, indent=2).encode("utf-8"),
        )

    def resolve_path(self, object_key: str) -> Path:
        return self.root / object_key


from fastapi import Request


def build_storage(request: Request) -> LocalStorage:
    return LocalStorage(request.app.state.storage_root)

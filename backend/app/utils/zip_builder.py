"""ZIP creation and temporary artifact storage helpers."""

from __future__ import annotations

from io import BytesIO
from uuid import uuid4
from zipfile import ZIP_DEFLATED, ZipFile

from app.models.agent_config import GeneratedFile


class ZipArtifactStore:
    """In-memory ZIP store keyed by download token."""

    def __init__(self) -> None:
        """Initialise the store."""
        self._artifacts: dict[str, bytes] = {}

    def create(self, files: list[GeneratedFile]) -> str:
        """Create and store a ZIP artifact for the given files."""
        buffer = BytesIO()
        with ZipFile(buffer, mode="w", compression=ZIP_DEFLATED) as zip_file:
            for generated_file in files:
                zip_file.writestr(generated_file.filename, generated_file.content)
        token = uuid4().hex
        self._artifacts[token] = buffer.getvalue()
        return token

    def get(self, token: str) -> bytes | None:
        """Return a stored ZIP artifact by token."""
        return self._artifacts.get(token)

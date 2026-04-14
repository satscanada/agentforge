"""Routes for scaffold generation and ZIP download."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from app.generator.engine import GeneratorEngine
from app.models.agent_config import ScaffoldRequest, ScaffoldResponse
from app.utils.zip_builder import ZipArtifactStore


router = APIRouter(prefix="/api", tags=["Generate"])
artifact_store = ZipArtifactStore()


@router.post("/generate", response_model=ScaffoldResponse)
def generate_scaffold(request: ScaffoldRequest) -> ScaffoldResponse:
    """Render all scaffold files and return a download token."""
    files = GeneratorEngine(request).render_all()
    token = artifact_store.create(files)
    return ScaffoldResponse(files=files, download_token=token)


@router.get("/download/{token}")
def download_scaffold(token: str) -> Response:
    """Download a generated scaffold ZIP by token."""
    content = artifact_store.get(token)
    if content is None:
        raise HTTPException(status_code=404, detail="download token not found")
    headers = {"Content-Disposition": f'attachment; filename="agentforge-{token}.zip"'}
    return Response(content=content, media_type="application/zip", headers=headers)

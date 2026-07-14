"""Repository API routes — list and detail endpoints for the dashboard."""

import logging

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.db.models.repository import Repository
from app.schemas.repository import RepositoryListResponse, RepositoryResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/repositories", tags=["repositories"])


@router.get(
    "",
    response_model=RepositoryListResponse,
    summary="List all connected repositories",
)
def list_repositories(db: Session = Depends(get_db)) -> RepositoryListResponse:
    """Return all repositories that have been registered via webhook."""
    repos = db.query(Repository).order_by(Repository.created_at.desc()).all()
    return RepositoryListResponse(
        items=[RepositoryResponse.model_validate(r) for r in repos],
        total=len(repos),
    )


@router.get(
    "/{repository_id}",
    response_model=RepositoryResponse,
    summary="Get a single repository",
)
def get_repository(
    repository_id: int,
    db: Session = Depends(get_db),
) -> RepositoryResponse:
    """Return a single repository by its internal id."""
    repo = db.query(Repository).filter(Repository.id == repository_id).first()
    if repo is None:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=404,
            detail={
                "error": {
                    "code": "NOT_FOUND",
                    "message": f"Repository {repository_id} not found",
                    "details": None,
                }
            },
        )
    return RepositoryResponse.model_validate(repo)

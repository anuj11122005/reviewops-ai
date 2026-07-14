import logging
from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.db.models.feedback import Feedback
from app.schemas.feedback import FeedbackCreate, FeedbackResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.post("/", response_model=FeedbackResponse)
def submit_feedback(
    feedback_in: FeedbackCreate,
    db: Session = Depends(get_db),
) -> Any:
    """Submit user feedback for an AI suggestion."""
    feedback = Feedback(
        pull_request_id=feedback_in.pull_request_id,
        category=feedback_in.category,
        target_identifier=feedback_in.target_identifier,
        accepted=feedback_in.accepted,
        comment=feedback_in.comment,
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)

    logger.info(
        f"Feedback recorded: PR {feedback.pull_request_id}, "
        f"Category: {feedback.category}, Accepted: {feedback.accepted}"
    )
    return FeedbackResponse.model_validate(feedback)


@router.get("/stats", response_model=dict[str, Any])
def get_feedback_stats(db: Session = Depends(get_db)) -> Any:
    """Get overall feedback statistics."""
    total = db.query(Feedback).count()
    accepted = db.query(Feedback).filter(Feedback.accepted).count()
    rejected = total - accepted

    return {
        "total": total,
        "accepted": accepted,
        "rejected": rejected,
        "acceptance_rate": (accepted / total) if total > 0 else 0.0,
    }

from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, BigInteger, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.db.models.pull_request import PullRequest


class Review(TimestampMixin, Base):
    """Stores automated AI review results for a specific Pull Request."""

    __tablename__ = "reviews"

    pull_request_id: Mapped[int] = mapped_column(
        ForeignKey("pull_requests.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False)
    commit_sha: Mapped[str | None] = mapped_column(String(40), nullable=True)
    bug_prediction_results: Mapped[dict[str, Any] | None] = mapped_column(
        JSON, nullable=True
    )
    static_analysis_results: Mapped[dict[str, Any] | None] = mapped_column(
        JSON, nullable=True
    )
    security_results: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    explainability_results: Mapped[dict[str, Any] | None] = mapped_column(
        JSON, nullable=True
    )
    documentation_results: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    test_generation_results: Mapped[str | None] = mapped_column(String, nullable=True)
    reviewer_recommendation_results: Mapped[str | None] = mapped_column(String, nullable=True)
    deployment_status_results: Mapped[str | None] = mapped_column(String, nullable=True)
    github_comment_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)

    # Relationships
    pull_request: Mapped["PullRequest"] = relationship(
        "PullRequest",
        back_populates="reviews",
    )

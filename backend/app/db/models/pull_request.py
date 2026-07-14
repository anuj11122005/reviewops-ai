"""PullRequest ORM model — a PR received via GitHub webhook."""

import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.db.models.feedback import Feedback
    from app.db.models.repository import Repository
    from app.db.models.review import Review


class PullRequest(TimestampMixin, Base):
    """A GitHub Pull Request associated with a connected repository."""

    __tablename__ = "pull_requests"

    repository_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("repositories.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    github_pr_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    number: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    author: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="open",
    )
    head_sha: Mapped[str] = mapped_column(String(40), nullable=False)
    base_branch: Mapped[str] = mapped_column(String(255), nullable=False)
    head_branch: Mapped[str] = mapped_column(String(255), nullable=False)

    body: Mapped[str | None] = mapped_column(Text, nullable=True)
    opened_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relationships
    repository: Mapped["Repository"] = relationship(back_populates="pull_requests")
    reviews: Mapped[list["Review"]] = relationship(
        back_populates="pull_request", cascade="all, delete-orphan"
    )
    feedbacks: Mapped[list["Feedback"]] = relationship(
        back_populates="pull_request", cascade="all, delete-orphan"
    )

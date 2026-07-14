from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.db.models.pull_request import PullRequest


class Feedback(TimestampMixin, Base):
    """Stores user feedback (accept/reject) on AI suggestions."""

    __tablename__ = "feedback"

    pull_request_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("pull_requests.id", ondelete="CASCADE"), index=True
    )

    # What exactly are they giving feedback on? (e.g. "bug_prediction", "security", "overall")
    category: Mapped[str] = mapped_column(String, nullable=False)

    # Specific file or issue this feedback applies to (optional)
    target_identifier: Mapped[str | None] = mapped_column(String, nullable=True)

    # True for accept, False for reject
    accepted: Mapped[bool] = mapped_column(Boolean, nullable=False)

    # Optional comment from the user
    comment: Mapped[str | None] = mapped_column(String, nullable=True)



    pull_request: Mapped["PullRequest"] = relationship(back_populates="feedbacks")

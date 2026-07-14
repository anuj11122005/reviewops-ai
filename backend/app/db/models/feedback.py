from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Feedback(Base):
    """Stores user feedback (accept/reject) on AI suggestions."""

    __tablename__ = "feedback"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
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
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    pull_request: Mapped["PullRequest"] = relationship(back_populates="feedbacks")

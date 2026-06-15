from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(200), nullable=False)
    full_name = Column(String(100), nullable=False)
    role = Column(String(20), default="operator")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class GuideSign(Base):
    __tablename__ = "guide_signs"

    id = Column(Integer, primary_key=True, index=True)
    sign_number = Column(String(50), unique=True, index=True, nullable=False)
    batch_code = Column(String(50), index=True)
    applicable_session = Column(String(100), nullable=False)
    current_area = Column(String(100), nullable=False)
    responsible_person = Column(String(100), nullable=False)
    status = Column(String(20), default="pending_production", index=True)
    remark = Column(Text, default="")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    position_records = relationship("PositionRecord", back_populates="guide_sign", cascade="all, delete-orphan")
    issue_records = relationship("IssueRecord", back_populates="guide_sign", cascade="all, delete-orphan")
    review_records = relationship("ReviewRecord", back_populates="guide_sign", cascade="all, delete-orphan")


class PositionRecord(Base):
    __tablename__ = "position_records"

    id = Column(Integer, primary_key=True, index=True)
    sign_id = Column(Integer, ForeignKey("guide_signs.id"), nullable=False)
    from_area = Column(String(100), nullable=False)
    to_area = Column(String(100), nullable=False)
    operator = Column(String(100), nullable=False)
    reason = Column(String(200), default="")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    guide_sign = relationship("GuideSign", back_populates="position_records")


class IssueRecord(Base):
    __tablename__ = "issue_records"

    id = Column(Integer, primary_key=True, index=True)
    sign_id = Column(Integer, ForeignKey("guide_signs.id"), nullable=False)
    issue_type = Column(String(20), nullable=False)
    session = Column(String(100))
    operator = Column(String(100), nullable=False)
    receiver = Column(String(100))
    remark = Column(Text, default="")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    guide_sign = relationship("GuideSign", back_populates="issue_records")


class ReviewRecord(Base):
    __tablename__ = "review_records"

    id = Column(Integer, primary_key=True, index=True)
    sign_id = Column(Integer, ForeignKey("guide_signs.id"), nullable=False)
    reviewer = Column(String(100), nullable=False)
    conclusion = Column(String(20), nullable=False)
    reason = Column(Text, default="")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    guide_sign = relationship("GuideSign", back_populates="review_records")

from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class UserBase(BaseModel):
    username: str
    full_name: str
    role: str = "operator"


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse


class PositionRecordBase(BaseModel):
    from_area: str
    to_area: str
    operator: str
    reason: str = ""


class PositionRecordResponse(PositionRecordBase):
    id: int
    sign_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class IssueRecordBase(BaseModel):
    issue_type: str
    session: Optional[str] = None
    operator: str
    receiver: Optional[str] = None
    remark: str = ""


class IssueRecordResponse(IssueRecordBase):
    id: int
    sign_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ReviewRecordBase(BaseModel):
    reviewer: str
    conclusion: str
    reason: str = ""


class ReviewRecordResponse(ReviewRecordBase):
    id: int
    sign_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class GuideSignBase(BaseModel):
    sign_number: str
    batch_code: str = ""
    applicable_session: str
    current_area: str
    responsible_person: str
    status: str = "pending_production"
    remark: str = ""


class GuideSignCreate(GuideSignBase):
    pass


class GuideSignUpdate(BaseModel):
    applicable_session: Optional[str] = None
    current_area: Optional[str] = None
    responsible_person: Optional[str] = None
    remark: Optional[str] = None


class GuideSignResponse(GuideSignBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    position_records: List[PositionRecordResponse] = []
    issue_records: List[IssueRecordResponse] = []
    review_records: List[ReviewRecordResponse] = []

    class Config:
        from_attributes = True


class IssueSignRequest(BaseModel):
    receiver: str
    session: str
    operator: str
    remark: str = ""


class RecycleSignRequest(BaseModel):
    operator: str
    to_pending_review: bool = False
    remark: str = ""


class PositionAdjustRequest(BaseModel):
    to_area: str
    operator: str
    reason: str = ""


class ReviewRequest(BaseModel):
    reviewer: str
    conclusion: str
    reason: str = ""


class SessionUsageItem(BaseModel):
    session: str
    count: int


class AreaConflictItem(BaseModel):
    area: str
    conflict_count: int


class PersonWorkloadItem(BaseModel):
    person: str
    count: int


class OverviewStats(BaseModel):
    total_signs: int
    pending_production: int
    available: int
    issued: int
    pending_recycle: int
    pending_review: int
    restored: int
    deactivated: int
    session_usage: List[SessionUsageItem]
    area_conflicts: List[AreaConflictItem]
    person_workload: List[PersonWorkloadItem]
    pending_review_list: List[GuideSignResponse]

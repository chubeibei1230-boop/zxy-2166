from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional

from database import get_db
from models import GuideSign, PositionRecord, IssueRecord, ReviewRecord, User
from auth import get_current_user
from schemas import (
    GuideSignCreate, GuideSignUpdate, GuideSignResponse,
    IssueSignRequest, RecycleSignRequest, PositionAdjustRequest, ReviewRequest
)

router = APIRouter(prefix="/api/signs", tags=["引导牌"])

STATUS_MAP = {
    "pending_production": "待制作",
    "available": "可发放",
    "issued": "已发放",
    "pending_recycle": "待回收",
    "pending_review": "待复核",
    "restored": "恢复可用",
    "deactivated": "停用"
}


@router.get("", response_model=List[GuideSignResponse])
def list_signs(
    status: Optional[str] = None,
    batch_code: Optional[str] = None,
    applicable_session: Optional[str] = None,
    responsible_person: Optional[str] = None,
    keyword: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(GuideSign)
    
    if status:
        query = query.filter(GuideSign.status == status)
    if batch_code:
        query = query.filter(GuideSign.batch_code.contains(batch_code))
    if applicable_session:
        query = query.filter(GuideSign.applicable_session.contains(applicable_session))
    if responsible_person:
        query = query.filter(GuideSign.responsible_person.contains(responsible_person))
    if keyword:
        query = query.filter(
            GuideSign.sign_number.contains(keyword) |
            GuideSign.current_area.contains(keyword)
        )
    
    signs = query.order_by(GuideSign.id.desc()).offset(skip).limit(limit).all()
    return signs


@router.get("/{sign_id}", response_model=GuideSignResponse)
def get_sign(
    sign_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    sign = db.query(GuideSign).filter(GuideSign.id == sign_id).first()
    if not sign:
        raise HTTPException(status_code=404, detail="引导牌不存在")
    return sign


@router.post("", response_model=GuideSignResponse)
def create_sign(
    sign_data: GuideSignCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    existing = db.query(GuideSign).filter(GuideSign.sign_number == sign_data.sign_number).first()
    if existing:
        raise HTTPException(status_code=400, detail="引导牌编号已存在")
    
    sign = GuideSign(**sign_data.model_dump())
    db.add(sign)
    db.commit()
    db.refresh(sign)
    return sign


@router.put("/{sign_id}", response_model=GuideSignResponse)
def update_sign(
    sign_id: int,
    sign_data: GuideSignUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    sign = db.query(GuideSign).filter(GuideSign.id == sign_id).first()
    if not sign:
        raise HTTPException(status_code=404, detail="引导牌不存在")
    
    update_data = sign_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(sign, key, value)
    
    db.commit()
    db.refresh(sign)
    return sign


@router.delete("/{sign_id}")
def delete_sign(
    sign_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    sign = db.query(GuideSign).filter(GuideSign.id == sign_id).first()
    if not sign:
        raise HTTPException(status_code=404, detail="引导牌不存在")
    db.delete(sign)
    db.commit()
    return {"message": "删除成功"}


@router.post("/{sign_id}/status/available", response_model=GuideSignResponse)
def mark_available(
    sign_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    sign = db.query(GuideSign).filter(GuideSign.id == sign_id).first()
    if not sign:
        raise HTTPException(status_code=404, detail="引导牌不存在")
    if sign.status not in ["pending_production", "deactivated"]:
        raise HTTPException(status_code=400, detail="当前状态不可设置为可发放")
    
    sign.status = "available"
    db.commit()
    db.refresh(sign)
    return sign


@router.post("/{sign_id}/issue", response_model=GuideSignResponse)
def issue_sign(
    sign_id: int,
    request: IssueSignRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    sign = db.query(GuideSign).filter(GuideSign.id == sign_id).first()
    if not sign:
        raise HTTPException(status_code=404, detail="引导牌不存在")
    if sign.status not in ["available", "restored"]:
        raise HTTPException(status_code=400, detail="当前状态不可发放")
    
    sign.status = "issued"
    
    issue_record = IssueRecord(
        sign_id=sign.id,
        issue_type="issue",
        session=request.session,
        operator=request.operator,
        receiver=request.receiver,
        remark=request.remark
    )
    db.add(issue_record)
    db.commit()
    db.refresh(sign)
    return sign


@router.post("/{sign_id}/pending-recycle", response_model=GuideSignResponse)
def mark_pending_recycle(
    sign_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    sign = db.query(GuideSign).filter(GuideSign.id == sign_id).first()
    if not sign:
        raise HTTPException(status_code=404, detail="引导牌不存在")
    if sign.status != "issued":
        raise HTTPException(status_code=400, detail="只有已发放状态才能标记待回收")
    
    sign.status = "pending_recycle"
    db.commit()
    db.refresh(sign)
    return sign


@router.post("/{sign_id}/recycle", response_model=GuideSignResponse)
def recycle_sign(
    sign_id: int,
    request: RecycleSignRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    sign = db.query(GuideSign).filter(GuideSign.id == sign_id).first()
    if not sign:
        raise HTTPException(status_code=404, detail="引导牌不存在")
    if sign.status not in ["pending_recycle", "issued"]:
        raise HTTPException(status_code=400, detail="当前状态不可回收")
    
    if request.to_pending_review:
        sign.status = "pending_review"
    else:
        sign.status = "available"
    
    recycle_record = IssueRecord(
        sign_id=sign.id,
        issue_type="recycle",
        operator=request.operator,
        remark=request.remark
    )
    db.add(recycle_record)
    db.commit()
    db.refresh(sign)
    return sign


@router.post("/{sign_id}/adjust-position", response_model=GuideSignResponse)
def adjust_position(
    sign_id: int,
    request: PositionAdjustRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    sign = db.query(GuideSign).filter(GuideSign.id == sign_id).first()
    if not sign:
        raise HTTPException(status_code=404, detail="引导牌不存在")
    if sign.current_area == request.to_area:
        raise HTTPException(status_code=400, detail="调整前后区域相同")
    
    from_area = sign.current_area
    sign.current_area = request.to_area
    
    position_record = PositionRecord(
        sign_id=sign.id,
        from_area=from_area,
        to_area=request.to_area,
        operator=request.operator,
        reason=request.reason
    )
    db.add(position_record)
    db.commit()
    db.refresh(sign)
    return sign


@router.post("/{sign_id}/review", response_model=GuideSignResponse)
def review_sign(
    sign_id: int,
    request: ReviewRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    sign = db.query(GuideSign).filter(GuideSign.id == sign_id).first()
    if not sign:
        raise HTTPException(status_code=404, detail="引导牌不存在")
    if sign.status != "pending_review":
        raise HTTPException(status_code=400, detail="只有待复核状态才能复核")
    
    review_record = ReviewRecord(
        sign_id=sign.id,
        reviewer=request.reviewer,
        conclusion=request.conclusion,
        reason=request.reason
    )
    db.add(review_record)
    
    if request.conclusion == "restore":
        sign.status = "restored"
    elif request.conclusion == "deactivate":
        sign.status = "deactivated"
    elif request.conclusion == "reissue":
        sign.status = "available"
    else:
        raise HTTPException(status_code=400, detail="无效的复核结论")
    
    db.commit()
    db.refresh(sign)
    return sign


@router.post("/{sign_id}/restore", response_model=GuideSignResponse)
def restore_sign(
    sign_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    sign = db.query(GuideSign).filter(GuideSign.id == sign_id).first()
    if not sign:
        raise HTTPException(status_code=404, detail="引导牌不存在")
    if sign.status == "pending_review":
        raise HTTPException(status_code=400, detail="待复核期间禁止直接恢复，请先完成复核")
    if sign.status not in ["deactivated"]:
        raise HTTPException(status_code=400, detail="当前状态不可恢复")
    
    sign.status = "restored"
    db.commit()
    db.refresh(sign)
    return sign

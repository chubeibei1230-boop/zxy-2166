from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime

from database import get_db
from models import Anomaly, AnomalyFlowRecord, GuideSign, User
from auth import get_current_user
from schemas import (
    AnomalyCreate, AnomalyUpdate, AnomalyResponse,
    AnomalyProcessRequest, AnomalyFlowRecordResponse
)

router = APIRouter(prefix="/api/anomalies", tags=["异常管理"])

ANOMALY_STATUS = {
    "pending": "待处理",
    "processing": "处理中",
    "pending_confirm": "待确认",
    "closed": "已关闭"
}

ANOMALY_TYPES = {
    "lost": "丢失",
    "damaged": "损坏",
    "wrong_issue": "错发",
    "overdue": "逾期未还",
    "other": "其他"
}

ANOMALY_LEVELS = {
    "low": "低",
    "normal": "一般",
    "high": "高",
    "critical": "严重"
}


@router.get("", response_model=List[AnomalyResponse])
def list_anomalies(
    current_status: Optional[str] = None,
    anomaly_type: Optional[str] = None,
    anomaly_level: Optional[str] = None,
    session: Optional[str] = None,
    responsible_person: Optional[str] = None,
    reporter: Optional[str] = None,
    keyword: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Anomaly).join(GuideSign)
    
    if current_status:
        query = query.filter(Anomaly.current_status == current_status)
    if anomaly_type:
        query = query.filter(Anomaly.anomaly_type == anomaly_type)
    if anomaly_level:
        query = query.filter(Anomaly.anomaly_level == anomaly_level)
    if session:
        query = query.filter(Anomaly.session.contains(session))
    if responsible_person:
        query = query.filter(Anomaly.responsible_person.contains(responsible_person))
    if reporter:
        query = query.filter(Anomaly.reporter.contains(reporter))
    if keyword:
        query = query.filter(
            GuideSign.sign_number.contains(keyword) |
            Anomaly.description.contains(keyword)
        )
    
    anomalies = query.order_by(Anomaly.created_at.desc()).offset(skip).limit(limit).all()
    return anomalies


@router.get("/{anomaly_id}", response_model=AnomalyResponse)
def get_anomaly(
    anomaly_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    anomaly = db.query(Anomaly).filter(Anomaly.id == anomaly_id).first()
    if not anomaly:
        raise HTTPException(status_code=404, detail="异常记录不存在")
    return anomaly


@router.post("", response_model=AnomalyResponse)
def create_anomaly(
    anomaly_data: AnomalyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    sign = db.query(GuideSign).filter(GuideSign.id == anomaly_data.sign_id).first()
    if not sign:
        raise HTTPException(status_code=404, detail="引导牌不存在")
    
    anomaly = Anomaly(**anomaly_data.model_dump())
    anomaly.current_status = "pending"
    
    flow_record = AnomalyFlowRecord(
        action="register",
        operator=anomaly_data.reporter,
        remark="异常登记：" + (anomaly_data.description or ""),
        from_status=None,
        to_status="pending"
    )
    anomaly.flow_records.append(flow_record)
    
    db.add(anomaly)
    db.commit()
    db.refresh(anomaly)
    return anomaly


@router.put("/{anomaly_id}", response_model=AnomalyResponse)
def update_anomaly(
    anomaly_id: int,
    anomaly_data: AnomalyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    anomaly = db.query(Anomaly).filter(Anomaly.id == anomaly_id).first()
    if not anomaly:
        raise HTTPException(status_code=404, detail="异常记录不存在")
    if anomaly.current_status == "closed":
        raise HTTPException(status_code=400, detail="已关闭的异常不能修改")
    
    update_data = anomaly_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(anomaly, key, value)
    
    db.commit()
    db.refresh(anomaly)
    return anomaly


@router.post("/{anomaly_id}/process", response_model=AnomalyResponse)
def process_anomaly(
    anomaly_id: int,
    request: AnomalyProcessRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    anomaly = db.query(Anomaly).filter(Anomaly.id == anomaly_id).first()
    if not anomaly:
        raise HTTPException(status_code=404, detail="异常记录不存在")
    if anomaly.current_status == "closed":
        raise HTTPException(status_code=400, detail="已关闭的异常不能处理")
    
    action = request.action
    from_status = anomaly.current_status
    to_status = None
    
    if action == "start_process":
        if from_status not in ["pending", "pending_confirm"]:
            raise HTTPException(status_code=400, detail="当前状态不能开始处理")
        to_status = "processing"
    elif action == "submit_confirm":
        if from_status != "processing":
            raise HTTPException(status_code=400, detail="只有处理中状态才能提交确认")
        to_status = "pending_confirm"
    elif action == "confirm_close":
        if from_status != "pending_confirm":
            raise HTTPException(status_code=400, detail="只有待确认状态才能关闭")
        to_status = "closed"
        anomaly.closed_at = datetime.now()
        anomaly.final_result = request.remark
    elif action == "reject":
        if from_status != "pending_confirm":
            raise HTTPException(status_code=400, detail="只有待确认状态才能驳回")
        to_status = "processing"
    elif action == "reopen":
        if from_status != "closed":
            raise HTTPException(status_code=400, detail="只有已关闭状态才能重新打开")
        to_status = "processing"
        anomaly.closed_at = None
        anomaly.final_result = ""
    elif action == "add_remark":
        to_status = from_status
    else:
        raise HTTPException(status_code=400, detail="无效的操作类型")
    
    if to_status and to_status != from_status:
        anomaly.current_status = to_status
    
    flow_record = AnomalyFlowRecord(
        anomaly_id=anomaly.id,
        action=action,
        operator=request.operator,
        remark=request.remark,
        from_status=from_status,
        to_status=to_status
    )
    db.add(flow_record)
    
    db.commit()
    db.refresh(anomaly)
    return anomaly


@router.get("/{anomaly_id}/flows", response_model=List[AnomalyFlowRecordResponse])
def get_anomaly_flows(
    anomaly_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    anomaly = db.query(Anomaly).filter(Anomaly.id == anomaly_id).first()
    if not anomaly:
        raise HTTPException(status_code=404, detail="异常记录不存在")
    
    flows = db.query(AnomalyFlowRecord).filter(
        AnomalyFlowRecord.anomaly_id == anomaly_id
    ).order_by(AnomalyFlowRecord.created_at.asc()).all()
    return flows


@router.delete("/{anomaly_id}")
def delete_anomaly(
    anomaly_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    anomaly = db.query(Anomaly).filter(Anomaly.id == anomaly_id).first()
    if not anomaly:
        raise HTTPException(status_code=404, detail="异常记录不存在")
    
    db.delete(anomaly)
    db.commit()
    return {"message": "删除成功"}

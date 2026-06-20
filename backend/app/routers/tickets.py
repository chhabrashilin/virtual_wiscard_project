"""
Athletic & event ticketing endpoints.

Students hold tickets issued by an admin; each ticket has a unique code that is
shown as a QR at the gate. The gate scanner validates the code (single-use).
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime

from app.database import get_db
from app.auth import get_current_user
from app.models import User, Ticket

router = APIRouter(prefix="/api/tickets", tags=["tickets"])


def _serialize(t: Ticket) -> dict:
    return {
        "id": t.id,
        "code": t.code,
        "event_name": t.event_name,
        "event_date": (t.event_date.isoformat() + "Z") if t.event_date else None,
        "venue": t.venue,
        "seat": t.seat,
        "status": t.status,
        "used_at": (t.used_at.isoformat() + "Z") if t.used_at else None,
    }


@router.get("")
def my_tickets(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List the current student's tickets."""
    tickets = db.query(Ticket).filter(
        Ticket.user_id == current_user.id
    ).order_by(Ticket.created_at.desc()).all()
    return {"tickets": [_serialize(t) for t in tickets]}


class TicketValidateRequest(BaseModel):
    code: str


@router.post("/validate")
def validate_ticket(
    request: TicketValidateRequest,
    db: Session = Depends(get_db),
):
    """Validate a ticket at the gate (single-use). No auth: this is a gate scanner."""
    ticket = db.query(Ticket).filter(Ticket.code == request.code.strip()).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    if ticket.status == "void":
        raise HTTPException(status_code=403, detail="Ticket has been voided")
    if ticket.status == "used":
        raise HTTPException(
            status_code=409,
            detail=f"Ticket already used at {ticket.used_at.isoformat()}Z" if ticket.used_at
            else "Ticket already used",
        )

    ticket.status = "used"
    ticket.used_at = datetime.utcnow()
    holder = db.query(User).filter(User.id == ticket.user_id).first()
    db.commit()

    return {
        "success": True,
        "event_name": ticket.event_name,
        "venue": ticket.venue,
        "seat": ticket.seat,
        "holder": {
            "full_name": holder.full_name if holder else "Unknown",
            "student_id": holder.student_id if holder else "",
        },
    }

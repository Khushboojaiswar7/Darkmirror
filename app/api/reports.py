from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.services.report_service import ReportService
import uuid
from app.models.report import AuditReport
from app.schemas.report import ReportResponse

router = APIRouter()
report_service = ReportService()

@router.post("/{conversation_id}/generate", response_model=ReportResponse)
async def generate(conversation_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    return await report_service.generate_report(db, conversation_id)

@router.get("", response_model=list[ReportResponse])
async def list_reports(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(AuditReport).order_by(AuditReport.created_at.desc()))
    return res.scalars().all()

@router.get("/{id}/download")
async def download(id: uuid.UUID, format: str = "json", db: AsyncSession = Depends(get_db)):
    if format == "pdf":
        pdf_path = await report_service.generate_pdf(db, id)
        return FileResponse(pdf_path, media_type="application/pdf", filename=f"report_{id}.pdf")
    elif format == "csv":
        csv_content = await report_service.generate_csv(db, id)
        return Response(content=csv_content, media_type="text/csv", headers={"Content-Disposition": f"attachment; filename=report_{id}.csv"})
    return await report_service.generate_json(db, id)

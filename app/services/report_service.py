"""
Report Generation Service – summary + PDF + JSON + CSV export.

Updated to add CSV export and richer PDF content matching the
architecture diagram's "Report Gen (summary + CSV export)" box.
"""
import csv
import io
import os
import uuid
import logging
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor

from app.models.conversation import Conversation
from app.models.report import AuditReport
from app.models.prediction import Prediction
from app.config import settings

logger = logging.getLogger(__name__)

# Risk → colour mapping for PDF
_RISK_COLORS = {
    "HIGH": HexColor("#f43f5e"),
    "MEDIUM": HexColor("#fbbf24"),
    "LOW": HexColor("#34d399"),
}


class ReportService:
    """Generate downloadable audit reports in PDF, JSON, and CSV."""

    async def generate_report(
        self, db: AsyncSession, conversation_id: uuid.UUID
    ) -> AuditReport:
        """Create a new AuditReport row from a completed conversation."""
        result = await db.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        conversation = result.scalar_one_or_none()
        if not conversation:
            raise ValueError("Conversation not found")

        # Pull associated prediction(s)
        pred_result = await db.execute(
            select(Prediction)
            .where(Prediction.conversation_id == conversation_id)
            .order_by(Prediction.created_at.desc())
        )
        prediction = pred_result.scalar_one_or_none()

        patterns_detected = {}
        if prediction and prediction.agent_outputs:
            for agent_name, output in prediction.agent_outputs.items():
                results = output.get("results", []) if isinstance(output, dict) else []
                for det in results:
                    ptype = det.get("pattern_type", "Unknown")
                    patterns_detected.setdefault(ptype, []).append({
                        "message_index": det.get("message_index"),
                        "confidence": det.get("confidence"),
                        "evidence": det.get("evidence", []),
                    })

        report = AuditReport(
            conversation_id=conversation_id,
            overall_risk=conversation.overall_risk,
            confidence=conversation.confidence,
            summary={
                "title": conversation.title,
                "verdict_flag": prediction.flag if prediction else 0,
                "verdict_confidence": prediction.confidence if prediction else 0.0,
                "reasoning_intent": prediction.reasoning_intent if prediction else None,
                "deliberate_confidence": prediction.deliberate_confidence if prediction else None,
            },
            patterns_detected=patterns_detected,
            pdf_path=None,
        )
        db.add(report)
        await db.commit()
        await db.refresh(report)
        return report

    async def generate_pdf(self, db: AsyncSession, report_id: uuid.UUID) -> str:
        """Create a styled PDF report and return its file path."""
        result = await db.execute(
            select(AuditReport).where(AuditReport.id == report_id)
        )
        report = result.scalar_one_or_none()
        if not report:
            raise ValueError("Report not found")

        report_dir = settings.REPORT_STORAGE_PATH
        os.makedirs(report_dir, exist_ok=True)
        pdf_path = os.path.join(report_dir, f"{report_id}.pdf")

        c = canvas.Canvas(pdf_path, pagesize=A4)
        width, height = A4

        # Header
        c.setFillColor(HexColor("#8b5cf6"))
        c.rect(0, height - 80, width, 80, fill=True, stroke=False)
        c.setFillColor(HexColor("#ffffff"))
        c.setFont("Helvetica-Bold", 22)
        c.drawString(40, height - 50, "DarkMirror Audit Report")
        c.setFont("Helvetica", 11)
        c.drawString(40, height - 70, f"Report ID: {report_id}")

        # Body
        y = height - 120
        c.setFillColor(HexColor("#1e293b"))
        c.setFont("Helvetica-Bold", 14)
        c.drawString(40, y, "Summary")
        y -= 25

        c.setFont("Helvetica", 11)
        c.setFillColor(HexColor("#0f172a"))
        summary = report.summary or {}
        for key, val in summary.items():
            c.drawString(60, y, f"{key}: {val}")
            y -= 18

        y -= 15
        c.setFont("Helvetica-Bold", 14)
        risk_color = _RISK_COLORS.get(report.overall_risk, HexColor("#334155"))
        c.setFillColor(risk_color)
        c.drawString(40, y, f"Overall Risk: {report.overall_risk}")
        y -= 20
        c.setFillColor(HexColor("#0f172a"))
        c.setFont("Helvetica", 11)
        c.drawString(40, y, f"Confidence: {report.confidence:.2%}")
        y -= 30

        # Detected patterns
        c.setFont("Helvetica-Bold", 14)
        c.drawString(40, y, "Detected Patterns")
        y -= 20
        c.setFont("Helvetica", 10)
        patterns = report.patterns_detected or {}
        for ptype, detections in patterns.items():
            c.setFont("Helvetica-Bold", 11)
            c.drawString(60, y, f"• {ptype} ({len(detections)} occurrence(s))")
            y -= 16
            c.setFont("Helvetica", 10)
            for det in detections[:5]:
                evidence_text = ", ".join(det.get("evidence", [])[:3])
                c.drawString(80, y, f"  msg {det.get('message_index')}: {evidence_text}")
                y -= 14
                if y < 60:
                    c.showPage()
                    y = height - 60

        c.save()

        report.pdf_path = pdf_path
        await db.commit()
        return pdf_path

    async def generate_json(self, db: AsyncSession, report_id: uuid.UUID) -> dict:
        """Return the full report as a JSON-serialisable dict."""
        result = await db.execute(
            select(AuditReport).where(AuditReport.id == report_id)
        )
        report = result.scalar_one_or_none()
        if not report:
            raise ValueError("Report not found")

        return {
            "id": str(report.id),
            "conversation_id": str(report.conversation_id),
            "overall_risk": report.overall_risk,
            "confidence": report.confidence,
            "summary": report.summary,
            "patterns_detected": report.patterns_detected,
            "created_at": report.created_at.isoformat() if report.created_at else None,
        }

    async def generate_csv(self, db: AsyncSession, report_id: uuid.UUID) -> str:
        """
        Generate a CSV export of the report.

        Returns the CSV content as a string (callers can stream or save).
        """
        result = await db.execute(
            select(AuditReport).where(AuditReport.id == report_id)
        )
        report = result.scalar_one_or_none()
        if not report:
            raise ValueError("Report not found")

        output = io.StringIO()
        writer = csv.writer(output)

        # Header row
        writer.writerow([
            "report_id", "conversation_id", "overall_risk", "confidence",
            "pattern_type", "message_index", "detection_confidence", "evidence",
        ])

        patterns = report.patterns_detected or {}
        if patterns:
            for ptype, detections in patterns.items():
                for det in detections:
                    writer.writerow([
                        str(report.id),
                        str(report.conversation_id),
                        report.overall_risk,
                        report.confidence,
                        ptype,
                        det.get("message_index", ""),
                        det.get("confidence", ""),
                        "; ".join(det.get("evidence", [])),
                    ])
        else:
            writer.writerow([
                str(report.id), str(report.conversation_id),
                report.overall_risk, report.confidence,
                "", "", "", "",
            ])

        return output.getvalue()

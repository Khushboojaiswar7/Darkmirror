from fastapi import APIRouter
from app.api.auth import router as auth_router
from app.api.conversations import router as conv_router
from app.api.reports import router as reports_router
from app.api.analytics import router as analytics_router
from app.api.datasets import router as datasets_router
from app.api.evaluation import router as eval_router
from app.api.explain import router as explain_router
from app.api.audit import router as audit_router

api_router = APIRouter()
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(conv_router, prefix="/conversations", tags=["conversations"])
api_router.include_router(reports_router, prefix="/reports", tags=["reports"])
api_router.include_router(analytics_router, prefix="/analytics", tags=["analytics"])
api_router.include_router(datasets_router, prefix="/datasets", tags=["datasets"])
api_router.include_router(eval_router, prefix="/evaluation", tags=["evaluation"])
api_router.include_router(explain_router, prefix="/explain", tags=["explainability"])
api_router.include_router(audit_router, prefix="/audits", tags=["audits"])

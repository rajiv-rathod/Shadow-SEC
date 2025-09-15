"""
Reports router for AI-generated correlation reports
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
import logging
from datetime import datetime

from backend.app.core.database import get_db
from backend.app.models.schemas import (
    Report, ReportCreate, ReportRequest, ReportJob, 
    ReportJobStatus, TimelineEvent
)
from backend.app.schemas.models import Report as ReportModel, Stock as StockModel
from backend.app.services.ai_service import AIService
from backend.app.services.report_service import ReportService

logger = logging.getLogger(__name__)
router = APIRouter()

# In-memory job tracking for MVP (replace with Redis in production)
active_jobs = {}


@router.post("/reports/generate", response_model=ReportJob)
async def generate_report(
    request: ReportRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Generate an AI correlation report for a specific stock and event
    Returns immediately with a job ID for async processing
    """
    try:
        # Validate stock symbol
        stock = db.query(StockModel).filter(StockModel.symbol == request.stock_symbol.upper()).first()
        if not stock:
            raise HTTPException(
                status_code=404, 
                detail=f"Stock {request.stock_symbol} not found in tracked stocks"
            )
        
        # Generate unique job ID
        job_id = str(uuid.uuid4())
        
        # Initialize job status
        active_jobs[job_id] = {
            "status": "pending",
            "progress": 0,
            "created_at": datetime.now(),
            "stock_id": stock.id,
            "request": request
        }
        
        # Start background task
        background_tasks.add_task(
            process_report_generation,
            job_id=job_id,
            stock_id=stock.id,
            request=request,
            db=db
        )
        
        logger.info(f"Started report generation job {job_id} for stock {request.stock_symbol}")
        
        return ReportJob(
            job_id=job_id,
            status="pending",
            message="Report generation started",
            estimated_completion=None
        )
        
    except Exception as e:
        logger.error(f"Failed to start report generation: {e}")
        raise HTTPException(status_code=500, detail="Failed to start report generation")


@router.get("/reports/status/{job_id}", response_model=ReportJobStatus)
async def get_report_status(job_id: str, db: Session = Depends(get_db)):
    """
    Check the status of a report generation job
    """
    if job_id not in active_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = active_jobs[job_id]
    
    # If completed, fetch the actual report
    result = None
    if job["status"] == "completed" and "report_id" in job:
        result = db.query(ReportModel).filter(ReportModel.id == job["report_id"]).first()
    
    return ReportJobStatus(
        job_id=job_id,
        status=job["status"],
        progress=job.get("progress", 0),
        result=result,
        error_message=job.get("error_message")
    )


@router.get("/reports", response_model=List[Report])
async def list_reports(
    stock_symbol: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    List AI-generated reports with optional filtering
    """
    query = db.query(ReportModel)
    
    if stock_symbol:
        query = query.join(StockModel).filter(StockModel.symbol == stock_symbol.upper())
    
    if status:
        query = query.filter(ReportModel.status == status)
    
    reports = query.order_by(ReportModel.generated_at.desc()).offset(offset).limit(limit).all()
    
    return reports


@router.get("/reports/{report_id}", response_model=Report)
async def get_report(report_id: int, db: Session = Depends(get_db)):
    """
    Get a specific report by ID
    """
    report = db.query(ReportModel).filter(ReportModel.id == report_id).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    return report


@router.get("/timeline", response_model=List[TimelineEvent])
async def get_timeline(
    stock_symbol: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    event_types: Optional[List[str]] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get timeline events for analysis
    This is a placeholder - full implementation would join multiple tables
    """
    # For MVP, return a basic timeline structure
    # In full implementation, this would aggregate events from multiple sources
    
    timeline_events = []
    
    # This is a simplified version - would need to implement proper event aggregation
    logger.info(f"Timeline requested for stock: {stock_symbol}, limit: {limit}")
    
    return timeline_events


async def process_report_generation(job_id: str, stock_id: int, request: ReportRequest, db: Session):
    """
    Background task to process AI report generation
    """
    try:
        # Update job status
        active_jobs[job_id]["status"] = "in_progress"
        active_jobs[job_id]["progress"] = 10
        
        # Initialize services
        ai_service = AIService()
        report_service = ReportService(db)
        
        # Update progress
        active_jobs[job_id]["progress"] = 30
        
        # Gather data for analysis
        data = await report_service.gather_analysis_data(
            stock_id=stock_id,
            event_date=request.event_date,
            include_sources=request.include_sources
        )
        
        active_jobs[job_id]["progress"] = 60
        
        # Generate AI report
        ai_response = await ai_service.generate_correlation_report(data)
        
        active_jobs[job_id]["progress"] = 80
        
        # Save report to database
        report_data = ReportCreate(
            stock_id=stock_id,
            title=ai_response.get("title", f"Correlation Analysis for {request.stock_symbol}"),
            content=ai_response.get("content", ""),
            confidence_score=ai_response.get("confidence_score"),
            correlations_found=ai_response.get("correlations"),
            data_sources=ai_response.get("sources"),
            ai_model_version=ai_response.get("model_version", "gemini-1.0")
        )
        
        report = await report_service.create_report(report_data)
        
        # Update job completion
        active_jobs[job_id]["status"] = "completed"
        active_jobs[job_id]["progress"] = 100
        active_jobs[job_id]["report_id"] = report.id
        
        logger.info(f"Report generation job {job_id} completed successfully")
        
    except Exception as e:
        logger.error(f"Report generation job {job_id} failed: {e}")
        active_jobs[job_id]["status"] = "failed"
        active_jobs[job_id]["error_message"] = str(e)
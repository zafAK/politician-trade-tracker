from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..db import get_session
from ..ingest.sync import get_source, run_sync
from ..schemas import SyncResult

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/sync", response_model=SyncResult)
def trigger_sync(source: str | None = None, session: Session = Depends(get_session)) -> SyncResult:
    result = run_sync(session, source=get_source(source))
    return SyncResult(
        source=result["source"],
        inserted=result["inserted"],
        updated=result["updated"],
        total_in_db=result["total_in_db"],
    )

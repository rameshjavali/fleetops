import logging
import os
import time

from fleetops.infrastructure.db import JobRecord, initialize_database, session_scope

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)


def process_one(processing_delay: float | None = None) -> int | None:
    """Claim and process one queued maintenance job; return its ID, or None when idle."""
    with session_scope() as session:
        job = (
            session.query(JobRecord)
            .filter_by(status="queued")
            .order_by(JobRecord.id)
            .with_for_update(skip_locked=True)
            .first()
        )
        if job is None:
            return None
        job.status = "processing"
        session.flush()
        job_id = job.id

    try:
        delay = (
            processing_delay
            if processing_delay is not None
            else float(os.getenv("JOB_PROCESSING_SECONDS", "2"))
        )
        if delay > 0:
            time.sleep(delay)
        with session_scope() as session:
            job = session.get(JobRecord, job_id)
            if job is None:
                return job_id
            job.status = "completed"
            job.result = f"Completed: {job.description}"
        logger.info("Processed maintenance job %s", job_id)
    except Exception:
        logger.exception("Failed to process maintenance job %s", job_id)
        with session_scope() as session:
            job = session.get(JobRecord, job_id)
            if job is not None:
                job.status = "failed"
                job.result = "Processing failed; inspect worker logs."
    return job_id


def run_forever(poll_interval: float = 2.0) -> None:
    initialize_database()
    logger.info("FleetOps worker started")
    while True:
        if process_one() is None:
            time.sleep(poll_interval)


if __name__ == "__main__":
    run_forever()

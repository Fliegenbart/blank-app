import json
from typing import Optional, Dict, Any
from functools import lru_cache
import structlog

from redis import Redis
from rq import Queue
from rq.job import Job as RQJob

from app.core.config import get_settings

logger = structlog.get_logger()
settings = get_settings()


class JobQueueService:
    """Service for managing job queues with RQ."""

    def __init__(self):
        self.redis = Redis.from_url(settings.REDIS_URL)
        self.high_queue = Queue("high", connection=self.redis)
        self.default_queue = Queue("default", connection=self.redis)
        self.low_queue = Queue("low", connection=self.redis)

    def enqueue_analyze(self, job_id: str) -> str:
        """Enqueue an analysis job."""
        rq_job = self.high_queue.enqueue(
            "app.tasks.analyze.analyze_upload",
            job_id,
            job_timeout="30m",
        )
        logger.info("Enqueued analyze job", job_id=job_id, rq_job_id=rq_job.id)
        return rq_job.id

    def enqueue_generate_website(self, job_id: str) -> str:
        """Enqueue a website generation job."""
        rq_job = self.default_queue.enqueue(
            "app.tasks.generate.generate_website",
            job_id,
            job_timeout="15m",
        )
        logger.info("Enqueued generate_website job", job_id=job_id, rq_job_id=rq_job.id)
        return rq_job.id

    def enqueue_generate_newsletter(self, job_id: str) -> str:
        """Enqueue a newsletter generation job."""
        rq_job = self.default_queue.enqueue(
            "app.tasks.generate.generate_newsletter",
            job_id,
            job_timeout="10m",
        )
        logger.info("Enqueued generate_newsletter job", job_id=job_id, rq_job_id=rq_job.id)
        return rq_job.id

    def enqueue_scrape_reference(self, job_id: str) -> str:
        """Enqueue a reference scraping job."""
        rq_job = self.default_queue.enqueue(
            "app.tasks.scrape.scrape_reference",
            job_id,
            job_timeout="20m",
        )
        logger.info("Enqueued scrape_reference job", job_id=job_id, rq_job_id=rq_job.id)
        return rq_job.id

    def enqueue_generate_landing_page(self, job_id: str) -> str:
        """Enqueue a landing page generation job."""
        rq_job = self.default_queue.enqueue(
            "app.tasks.generate.generate_landing_page",
            job_id,
            job_timeout="20m",
        )
        logger.info("Enqueued generate_landing_page job", job_id=job_id, rq_job_id=rq_job.id)
        return rq_job.id

    def enqueue_generate_social_media(self, job_id: str) -> str:
        """Enqueue a social media content generation job."""
        rq_job = self.default_queue.enqueue(
            "app.tasks.generate.generate_social_media",
            job_id,
            job_timeout="15m",
        )
        logger.info("Enqueued generate_social_media job", job_id=job_id, rq_job_id=rq_job.id)
        return rq_job.id

    def enqueue_generate_email(self, job_id: str) -> str:
        """Enqueue an email template generation job."""
        rq_job = self.default_queue.enqueue(
            "app.tasks.generate.generate_email",
            job_id,
            job_timeout="15m",
        )
        logger.info("Enqueued generate_email job", job_id=job_id, rq_job_id=rq_job.id)
        return rq_job.id

    def get_job_status(self, rq_job_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of an RQ job."""
        try:
            rq_job = RQJob.fetch(rq_job_id, connection=self.redis)
            return {
                "id": rq_job.id,
                "status": rq_job.get_status(),
                "result": rq_job.result,
                "exc_info": rq_job.exc_info,
            }
        except Exception as e:
            logger.error("Failed to fetch RQ job", rq_job_id=rq_job_id, error=str(e))
            return None

    def cancel_job(self, rq_job_id: str) -> bool:
        """Cancel an RQ job."""
        try:
            rq_job = RQJob.fetch(rq_job_id, connection=self.redis)
            rq_job.cancel()
            logger.info("Cancelled RQ job", rq_job_id=rq_job_id)
            return True
        except Exception as e:
            logger.error("Failed to cancel RQ job", rq_job_id=rq_job_id, error=str(e))
            return False


@lru_cache()
def get_job_queue() -> JobQueueService:
    """Get the job queue service instance."""
    return JobQueueService()

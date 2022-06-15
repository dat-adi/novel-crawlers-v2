from redis import Redis
from rq import Queue
from rq.job import Job
from rq.registry import FailedJobRegistry

redis = Redis()
queue = Queue(connection=redis)
registry = FailedJobRegistry(queue=queue)

# Show all failed job IDs and the exceptions they caused during runtime
for job_id in registry.get_job_ids():
    job = Job.fetch(job_id, connection=redis)
    print(job_id, job.exc_info)

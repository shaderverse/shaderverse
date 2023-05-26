from celery import current_app as current_celery_app
from celery.result import AsyncResult, TimeoutError, GroupResult

from .celery_config import settings
from enum import Enum
import logging


def create_celery():
    
    celery_app = current_celery_app
    celery_app.config_from_object(settings, namespace='CELERY')
    celery_app.conf.update(task_track_started=True)
    celery_app.conf.update(task_serializer='json')
    celery_app.conf.update(result_serializer='json')
    celery_app.conf.update(accept_content=['pickle', 'json'])
    celery_app.conf.update(result_persistent=True)
    celery_app.conf.update(worker_send_task_events=False)
    celery_app.conf.update(worker_prefetch_multiplier=1)

    return celery_app


def get_task_info(task_id):
    """
    return task info for the given task_id
    """
    try:
        task_result = AsyncResult(task_id)
        
        result = {
            "task_id": task_id,
            "task_status": task_result.status,
            "task_result": task_result.result
        }
        task_result.get(timeout=0.1)
    except TimeoutError as e:
        result = {
            "task_id": task_id,
            "task_status": task_result.status,
            "task_result": e
        }
        print(f"Exception: {e}")
    except ValueError as e:
        result = {
            "task_id": task_id,
            "task_status": "VALUE_ERROR",
            "task_result": e
        }
        print(f"Exception: {e}")


    return result

class BatchStatus(Enum):
    PENDING = "PENDING"
    STARTED = "STARTED"
    SUCCESS = "SUCCESS"
    WAITING = "WAITING"
    FAILURE = "FAILURE"

def get_batch_info(task_id):
    """
    return batch info for the given task_id
    """

    status = BatchStatus.PENDING
    result = {}

    try:
        batch_result = GroupResult.restore(task_id)
        batch_size = batch_result.__len__()
        result = {
            "batch_id": task_id,
            "status": status,
            "completed_count": batch_result.completed_count(),
            "total_count": batch_size,
            "percent_complete": batch_result.completed_count() / batch_size,
        }

        batch_result.get(timeout=0.1)
        # print(f"task_result: {task_result}")
        result_id_list = [result.id for result in batch_result.results]

        if batch_result.successful():
            status = BatchStatus.SUCCESS
        elif batch_result.failed():
            status = BatchStatus.FAILURE
        elif batch_result.waiting():
            status = BatchStatus.WAITING

        result["status"] = status

        results = []
        for result_id in result_id_list:
            results.append(get_task_info(result_id))
        
        result["batch_result"] = results

    except TimeoutError as e:
        print(f"Exception: {e}")

    except ValueError as e:
        result["status"] = "VALUE_ERROR"
        print(f"Exception: {e}")

    except Exception as e:
        result["status"] = "EXCEPTION"
        print(f"Exception: {e}")

    return result


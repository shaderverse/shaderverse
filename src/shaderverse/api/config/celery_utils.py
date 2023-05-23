from celery import current_app as current_celery_app
from celery.result import AsyncResult, TimeoutError

from .celery_config import settings


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

import os
from functools import lru_cache
from kombu import Queue
from pathlib import Path
from tempfile import gettempdir
from shaderverse.api.utils import get_temporary_directory

def route_task(name, args, kwargs, options, task=None, **kw):
    print(f"Routing task: {name}")
    if ":" in name:
        queue, _ = name.split(":")
        return {"queue": queue}
    return {"queue": "celery"}


class BaseConfig:
    # CELERY_broker_url: str = os.environ.get("CELERY_broker_url", "amqp://guest:guest@localhost:5672//")
    # result_backend: str = os.environ.get("result_backend", "rpc://")
    tempdir = get_temporary_directory()
    db_path = tempdir.joinpath("celerydb.sqlite")
    db_url = f"sqla+sqlite:///{str(db_path)}"
    
    broker_url = db_url

    result_path = tempdir.joinpath("result.sqlite")
    result_backend = f"db+sqlite:///{str(result_path)}"

    cache_path = tempdir.joinpath("celery.sqlite")
    cache_backend = f"db+sqlite:///{str(cache_path)}"


    

    # CELERY_BROKER_BACKEND = broker_url
    

   
    # broker_url: str = os.environ.get("CELERY_broker_url", db_url)

    # # result_backend: str = os.environ.get("db+sqlite:///results.sqlite")
    # CELERY_BROKER_BACKEND = "db+sqlite:///celery.sqlite"
    # cache_backend = "db+sqlite:///celery.sqlite"
    # result_backend = "db+sqlite:///celery.sqlite"
    # worker_send_task_events = True

    CELERY_TASK_QUEUES: list = (
        # default queue
        Queue("celery"),
        # custom queue
        Queue("render"),
        Queue("generate"),
    )

    CELERY_TASK_ROUTES = (route_task,)


class DevelopmentConfig(BaseConfig):
    pass


@lru_cache()
def get_settings():
    config_cls_dict = {
        "development": DevelopmentConfig,
    }
    config_name = os.environ.get("CELERY_CONFIG", "development")
    config_cls = config_cls_dict[config_name]
    return config_cls()


settings = get_settings()

import bpy
from shaderverse.nft import NFT
import typing
from typing import Generator
from fastapi import BackgroundTasks
from starlette.concurrency import run_in_threadpool
from starlette.background import BackgroundTask


async def get_nft() -> Generator:
    nft = NFT()
    yield nft

def get_bpy() -> Generator:
    yield bpy


class BlockingBackgroundTasks(BackgroundTasks):
    def add_task(
        self, func: typing.Callable, *args: typing.Any, **kwargs: typing.Any
    ) -> None:
        print("adding task")
        task = BackgroundTask(func, *args, **kwargs)
        task.is_async = False
        self.tasks.append(task)


            # print(f"running task: {task.func.__name__}")
            # print()
            # await run_in_threadpool(task.func, *task.args, **task.kwargs)
            # print(f"completed task: {task.func.__name__}")
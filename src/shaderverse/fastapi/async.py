import asyncio

async def start():
    proc = await asyncio.create_subprocess_exec('python','controller.py', stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)

    # do something else while ls is working

    # if proc takes very long to complete, the CPUs are free to use cycles for 
    # other processes
    # stdout, stderr = await proc.communicate()
    print("waiting")
    # print(stdout)

asyncio.run(start())
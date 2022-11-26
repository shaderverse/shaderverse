import asyncio
import httpx
import time
import os
from start_api import BlenderInstance



number_requests = 30
timeout = 60 * number_requests
number_workers = 1
wait_time = 3 * number_workers

async def get_glb(client: httpx.AsyncClient, url, number):
    print(f'making request {number}')
    start_time = time.time()
    resp = await client.post(url, timeout=timeout)
    status = resp.status_code
    result_file = resp.read()
    with open(f"results/{number}.glb", "wb") as binary_file:
        binary_file.write(result_file)

    end_time = time.time()
    elapsed_time = end_time - start_time
    result = f'request: {number}, status:{status}, elapsed time: {elapsed_time}'
    print(result)
    return result



async def main():

    async with httpx.AsyncClient() as client:

        tasks = []

        for number in range(1, number_requests + 1):
            instance_number = number % number_workers
            selected_instance = instances[instance_number]
            port = selected_instance.port
            # url = f'http://localhost:{port}/render_glb'
            # url = f'http://localhost:8119/render_glb'
            url = f'http://192.168.86.49:3000/render_glb'
        
            

            tasks.append(asyncio.ensure_future(get_glb(client, url, number)))

        all_results = await asyncio.gather(*tasks)
        for result in all_results:
            print(result)


if __name__ == "__main__":
    print(f"Spinning up {number_workers} Blender instances")
    instances: list[BlenderInstance] = []
    for instance in range(0, number_workers):
        instances.append(BlenderInstance())
        print(f"http://localhost:{instances[instance].port}/docs")
    
    time.sleep(wait_time)
    start_time = time.time()



    asyncio.run(main())
    os.system('pause')
    print("--- %s seconds ---" % (time.time() - start_time))
import asyncio
import select
import sys


async def input_reader():
    while True:
        input = select([sys.stdin], [], [], 0.1)
        if input:
            input_value = sys.stdin.readline().rstrip()
            await print(input_value)
        

asyncio.run(input_reader())
import asyncio
from functools import wraps

def async_wrap(func):
    """
    Wraps a synchronous function to make it asynchronous.
    """
    @wraps(func)
    async def run(*args, **kwargs):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, func, *args, **kwargs)
    return run

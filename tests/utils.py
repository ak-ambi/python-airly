import asyncio


def run_coroutine_synchronously(coroutine):
    loop = asyncio.new_event_loop()
    result = loop.run_until_complete(coroutine)
    loop.close()
    return result


def wrap_to_future(result):
    import asyncio
    future = asyncio.get_event_loop().create_future()
    if isinstance(result, BaseException):
        future.set_exception(result)
    else:
        future.set_result(result)
    return future

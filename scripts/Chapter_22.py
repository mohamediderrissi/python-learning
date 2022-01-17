#########################################################################################
##############  Chapter 22: Asynchronous Programming
#########################################################################################

# asyncio is a library to write concurrent code using the async/await syntax
import asyncio
from asyncio import events
from asyncio.exceptions import CancelledError


############## Native coroutines: Definition 
# a native coroutine defined using the keyword: async def
# a native coroutine object is the result of calling a function defined with async def.
async def example_of_native_coroutine():
    print('example_of_native_coroutine')

# Inside a native cortounite we can delegate to another native coroutine using the keyword: await (cannot be used outside a native coroutine) :

async def delegate():
    await example_of_native_coroutine()

############## Example: Probing domains - search for domains for a Python blog
# In this example, we look for available domains in the following format: {pythonKeyword}.dev (like while.dev or await.dev) 
"""
import socket
from keyword import kwlist  # list of Python keywords

MAX_KEYWORD_LEN = 4     # we take keywords <= 4

async def probe(domain: str) -> tuple[str, bool]:
    loop = asyncio.get_running_loop()
    try:
        await loop.getaddrinfo(host=domain, port=None)    # Asynchronous version of socket.getaddrinfo()
    except socket.gaierror:
        return (domain,False)
    return (domain,True)


async def main() -> None:
    names = (name for name in kwlist if len(name) <= MAX_KEYWORD_LEN)
    domains = (f'{name}.dev'.lower() for name in names)
    coros = [probe(domain) for domain in domains]

    for coro in asyncio.as_completed(coros):    # generator that yields the coroutines in the order they are completed, similar to futures.as_completed
        domain, found = await coro      # At this point, we know the coroutine is done because that’s how as_completed works, 
                                        # Therefore, the await expression will not block but we need it to get the result from coro,
                                        # If coro raised an unhandled exception, it would be re-raised her. 
        mark = '+' if found else ' '
        print(f'{mark} {domain}')

if __name__ == '__main__':
    asyncio.run(main())
"""
# Output:
#  
# + as.dev
# + elif.dev
#   pass.dev
#   else.dev
# + in.dev  
#   if.dev  
# + try.dev 
#   none.dev
#   is.dev
# + def.dev 
#   with.dev
#   or.dev
# + for.dev
# + from.dev
# + not.dev
# + true.dev
# + and.dev
# + del.dev
#  
# # # # # # # # # 

############## awaitable concept :
# The await keyword applies to any awaitable objects like :
#  - native coroutine object which we get calling a native coroutine function
#  - asyncio.Task object which usually we get by passing a coroutine object to asyncio.create_task()


############## Downloading with asyncio and aiohttp:
"""
from aiohttp import *  # aiohttp not part of the standard library. (asyncio support only UDP/TCP connection - No http)
from Chapter_21 import save_flag, BASE_URL, main

async def get_flag(session: ClientSession, cc: str):    # We did not use get_flag from Chapter_21 because it uses the requests library, which performs blocking I/O, instead we use aiohttp.
    url = f'{BASE_URL}/{cc}/{cc}.gif'.lower()
    async with session.get(url) as resp:    # general note: Network I/O operations are implemented as coroutine-methods, so they are driven asynchronously by the asyncio event loop.
        return await resp.read()

async def download_one(session: ClientSession, cc: str):
    image = await get_flag(session, cc)
    save_flag(image, f'{cc}.gif')   # For better performance, the save_flag call inside get_flag should be asynchronous, 
                                    # but asyncio does not provide an asynchronous filesystem API at this time — as Node.js does.
                                    # However, we can use  can use the loop.run_in_executor function to run save_flag in a thread pool
    print(cc, end=' ', flush=True)
    return cc

async def supervisor(cc_list: list[str]) -> int:
    async with ClientSession() as session:
        to_do = [download_one(session,cc) 
                for cc in sorted(cc_list)]
        res = await asyncio.gather(*to_do)     # .gather() accepts one or more awaitable arguments and waits for all of them to complete, returning a list of results for the given awaitables in the order they were submitted.
    
    return len(res)

def download_many(cc_list: list[str]) -> int:
    return asyncio.run(supervisor(cc_list))

if __name__ == "__main__":
    main(download_many)
"""
# Output:
#  
# IN JP EG TR VN IR RU CN ID BR US PK BD FR NG MX ET CD PH DE 
# 20 downloads in 2.19s
#  
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

############## The all-or-nothing problem :
#
# We should ewrite all the code so none of it blocks or we’re just wasting our time. Because if some-parts blocks, il blocks, 
# the blocks will affectes the event loop and all the program, since we have one thread. That's way, once we want to leverage asyncio, one should use libraries 
# that are asynchronous (aiohttp for example, instead of requests). 
#   The functions that we use should also be asynchronous as possible (so we do not blocks the event loop). In a situation where we have 
# a function that blocks (and affects performance too much), we can launch this function in a sperate thread as we will see ...
#   


############## Asynchronous Context Managers: async with
# 
# async with is used for asynchronous context maanger.(For example, a database connetion as set-up and commit or rollback as a tear-down)
# To suport async with, an object should implements __aenter__ and __aexit__
# 

############## Enhancing the asyncio downloader:
# Skip this part to later ...



############## Using an Executor to Avoid Blocking the Event Loop :
# 
#   - The Probem: 
#       With asyncio, we perform the concurrency of actions using the event loop with one thread. Hence, if a blocking call is used inside a 
#  coroutine, this call will affect the global performance of all the program.
# 
#   - The solution: 
#       Use a separate thread to call the blocking code. For example, in a prevouis example, we have save_flag function to save a flag in the hard disk.
#  This Function blocks, so we create a dedicated thread that call save_flag. With asyncio, we can use :
#   
#  Instead of:
# 
#   async def download_one(session: ClientSession, cc: str):
#     image = await get_flag(session, cc)
#     save_flag(image, f'{cc}.gif')   
#     print(cc, end=' ', flush=True)
#     return cc
# 
# We can do:
# 
#   async def download_one(session: ClientSession, cc: str):
#     loop = asyncio.get_running_loop()
#     loop.run_in_executor(None, save_flag, image, f'{cc}.gif')
#     image = await get_flag(session, cc)
#     save_flag(image, )   
#     print(cc, end=' ', flush=True)
#     return cc
# 
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 




############## Make asynchronous call in a definite order :
# 
#   We can do that using  await keyword, like in JavaScript:
# 
# async def function_with_multi_asynchronous_call():
#     resp_1 = await asynchrnous_call_1()     # Call
#     rersp_2 = await asynchrnous_call_2()    # asynchrnous_call_2() will not be invoked, until asynchrnous_call_1() returns !
# 
# # # # # # # # # # # # # # # # # # # 




############## An asyncio TCP Server :
"""

import asyncio
import functools
import sys
from asyncio.trsock import TransportSocket
from typing import cast

from charindex import InvertedIndex, format_results         # This file was downloaded from fluententpython respository


CRLF = b'\r\n'
PROMPT = b'?>'

async def search(query: str,
                 index: InvertedIndex,
                 writer: asyncio.StreamWriter) -> int:
    chars = index.search(query)
    lines = (line.encode() + CRLF for line 
             in format_results(chars))
    writer.writelines(lines)    # regular function not like readline(coroutine)
    await writer.drain()
    status_line = f"{'-' * 66 } {len(chars)} found"
    writer.write(status_line.encode() + CRLF)
    await writer.drain()
    return len(chars)

async def finder(index: InvertedIndex,
                 reader: asyncio.StreamReader,
                 writer: asyncio.StreamWriter):
    client = writer.get_extra_info("peername")      # Get the remote client address to which the socket is connected
    while True:
        writer.write(PROMPT)            # The StreamWriter.write method is not a coroutine, just a plain function; this line sends the ?> prompt.
        await writer.drain()            # StreamWriter.drain flushes the writer buffer; it is a coroutine, so it must be driven with await.
        data = await reader.readline()  # StreamWriter.readline is a coroutine that returns bytes.
        try:
            query = data.decode().strip()   # decode the bytes with default encoding UTF-8. string.strip() without argument, return a copy of the string with leading and trailing whitespace removed.
        except UnicodeDecodeError:          # A UnicodeDecodeError may happen when the user hits CTRL-C
            query = '\x00'                  # This is the null character (ord('\x00') = 0)
        if query:
            if ord(query[:1]) < 32:
                break
            results = await search(query, index, writer)    # search() is a coroutine
            print(f' To {client}: {results} results.')
    writer.close()                  # Close the StreamWriter
    await writer.wait_closed()      # Wait for the StreamWriter to close. This is recommended in the .close() method documentation.
    print(f'Close {client}.')       # Log the end of this client’s session to the server console.

async def supervisor(index: InvertedIndex, host: str, port: int):
    server = await asyncio.start_server(            # start a socket server, the first parmater is a callback run when a new client connection starts.
             functools.partial(finder, index),      # The callback can be a function or a coroutine, but it must accept exactly two arguments: an asyncio.StreamReader and an asyncio.StreamWriter
             host, port)                            # the finder function here accepts 3 parms, so we use functools.partial to return a callback that accepts 2 params. (the first parm will be index)
    socket_list = cast(tuple[TransportSocket, ...], server.sockets)
    addr = socket_list[0].getsockname()
    print(f'Serving on {addr}. Hit CTRL-C to stop.')
    await server.serve_forever()

def main(host: str = "127.0.0.1", port_arg: str = "2323"):
    port = int(port_arg)
    print('Building index.')
    index = InvertedIndex()
    try:
        asyncio.run(supervisor(index, host, port))
    except KeyboardInterrupt:
        print('\n Server shut down.')

if __name__ == '__main__':
    main(*sys.argv[1:])
"""

    
############## Asynchronous iteration and asynchronous iterables
# 
# - "async for" works for asynchronous iterables. Asynchronous iteravle are objects that implements __aiter__.
# - __aiter__ must be a regular function and not a coroutine. It must return a asynchronous iterator.
# - Asynchrnous iterator is an object provides __anext__ coroutine method that returns an awaitable (often coroutine object), and implemnt __aiter__ that return self.(Like classic Iterator Pattern,  "Don't make the iterable an iterator for itself")
# 
# # # # 

# Asynchronous Generator Functions :
# 
#  As we did to implement iterators using generator functions (instead of implementing the classic iterator Pattern). In the same way, we can
# use asynchrnous generator functions to implement asynchrnous iterators. (instead of implementing __aiter__,  __anext__ ...etc)
# 
# Asynchrnous generator function: Function declared with "async for" and contains yield in its body !
# 
# # # # # # # # # # # # # # # # # # # # # # # # # 

# Use case:
# 
#       We need for example to use ansyncronous genertor, when iterating over lines comming from database, using an async DB driver.
#   In this case, the async for loop will not blocks the event loop (as a regular a for does).
# 
# # # # # # # # # 

# Example:   

import socket
from collections.abc import Iterable, AsyncIterator
from typing import NamedTuple, Optional

class Result(NamedTuple):
    domain: str
    found: bool


OptionalLoop = Optional[asyncio.AbstractEventLoop]  # To make the ligne shorter in type hint of the probe() function

async def probe(domain: str, loop: OptionalLoop) -> Result:
    if loop is None:
        loop = asyncio.get_running_loop()
    try:
        await loop.getaddrinfo(domain, None)
    except socket.gaierror:
        return Result(domain, False)
    return Result(domain, True)

async def multi_probe(domains: Iterable[str]) -> AsyncIterator[Result]:
    loop = asyncio.get_running_loop()
    coros = [probe(domain, loop) for domain in domains]
    for coro in asyncio.as_completed(coros):
        result = await coro     # Even if coro here is compeleted, we use await !
        yield result            # We can make the two lines shorter using: yield await coro !

names = 'python.org rust-lang.org golang.org n05uch1an9.org'.split()

# print(multi_probe(names))       # <async_generator object multi_probe at 0x000002A3F5DB6540>

async def for_with_async_for():
    async for r in multi_probe(names):
        print(r)
"""
if __name__ == "__main__":
    asyncio.run(for_with_async_for())
"""
# Output:
# ======
# Result(domain='golang.org', found=True)       # The results are not shown in the order they were submitted.
# Result(domain='rust-lang.org', found=True)  
# Result(domain='python.org', found=True)     
# Result(domain='n05uch1an9.org', found=False) 
# 
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 



############## Asynchronous Generators as Context Managers:
# 
# We can create asynchrnoous context managers using @asynccontextmanager decorator, combined with an asynchrnous generator function
# 
"""
from contextlib import asynccontextmanager

def download_page(url):
    # Some code that blocks, like a request using Requests
    pass

def update_stats(url):
    # Some code that blocks
    pass

@asynccontextmanager
async def web_page(url):
    loop = asyncio.get_running_loop()                           # use the lightweight get_running_loop instead of get_event_loop
    data = await loop.run_in_executor(None, download_page, url) # Here we use .run_in_executor() to run the blocking code in a seperate thread
    yield data                                                  # All lines before this yield expression will become the __aenter__ coroutine-method of the asynchronous context manager built by the decorator.
    await loop.run_in_executor(None, update_stats, url)         # Lines after the yield will become the __aexit__ coroutine-method

async def test():
    async with web_page("google.com") as data:      # data will be bound to the yielded data in web_page() function
        process(data)
"""


############## Async Comprehensions and Async Generator Expressions: 

async def test_async_gen_exp():
    gen_found = (domain async for domain, found in multi_probe(names) if found) # this is an asyncronous generator expression
    print(gen_found)
    async for r in gen_found:
        print(r)
    
    gen_found_list = [domain async for domain, found in multi_probe(names) if found]
    print(gen_found_list)

    gen_found_with_await = [await probe(name, None) for name in sorted(names)]  # similar to asyncio.gather(), results are in the same order they were submitted !
    print(gen_found_with_await)

    await_in_dict= {name: found async for name, found in multi_probe(names)}
    print(await_in_dict)

    await_in_set = { name for name in names if (await probe(name,None)).found }
    print(await_in_set)

if __name__ == "__main__":
    asyncio.run(test_async_gen_exp())

# Output:
# ======
# 
# <async_generator object test_async_gen_exp.<locals>.<genexpr> at 0x000002572CDC6640>
# python.org
# rust-lang.org
# golang.org
# 
# ['python.org', 'rust-lang.org', 'golang.org']
# 
# [Result(domain='golang.org', found=True), Result(domain='n05uch1an9.org', found=False), Result(domain='python.org', found=True), Result(domain='rust-lang.org', found=True)]
# 
# {'python.org': True, 'golang.org': True, 'n05uch1an9.org': False, 'rust-lang.org': True}
# 
# {'rust-lang.org', 'python.org', 'golang.org'}
#  
# # # # # # # # # # # # # # # # # # # # # # # # # 


############## Examples from Chapter 20 using asyncio :

############## Spinner: 
from itertools import cycle


quit = False

async def spin(msg) -> None:
    for char in cycle(r'\|/-'):
        status = f'\r{char} {msg}'
        print(status, flush=True, end='')
        try:
            await asyncio.sleep(.1)
        except asyncio.CancelledError:
            break
    blanks = ' ' * len(status)
    print(f'\r{blanks}\r', end='')


async def slow() -> int:
    await asyncio.sleep(3)
    return 42


async def supervisor() -> int:
    spinner = asyncio.create_task(spin('thinking ...'))
    print(spinner)
    result = await slow()
    spinner.cancel()
    return result

def main() -> None:
    result = asyncio.run(supervisor())
    print(f"Answer: {result}")

if __name__ == "__main__":
    main()


############## flag downloader with progress bar: 

# ... To be continued ...

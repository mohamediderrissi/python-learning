#######################################################################
##############  Chapter 21: Concurrency with Futures
#######################################################################

# Goal of the chapter: spawning a bunch of independent threads and collecting the results in a queue, using concurrent.futures library.

# # # # # # #  Script to donwload 20 images, seqentialy:
#              =========================================

from concurrent.futures.process import ProcessPoolExecutor
from concurrent.futures.thread import ThreadPoolExecutor
import time
from pathlib import Path
from typing import Callable, Counter

import requests     # This import does not belongs to the standard library (so by convention, we import it after the standard libray modules,and we insert a blank line to sperate them)


POP20_CC = ('CN IN US ID BR PK NG BD RU JP MX PH VN ET EG DE IR TR CD FR').split()  # country code by population size

DIST_DIR = Path(__file__).parent / "Chapter_21"   # The special variable __file__ contains the path to the current file.
BASE_URL = 'http://fluentpython.com/data/flags'

def save_flag(img: bytes, filename: str) -> None:
    (DIST_DIR/filename).write_bytes(img)

def get_flag(cc: str) -> bytes:
    url = f'{BASE_URL}/{cc}/{cc}.gif'.lower()
    resp = requests.get(url)
    return resp.content

"""
def download_many(cc_list: list[str]) -> int:
    for cc in sorted(cc_list):
        image = get_flag(cc)
        save_flag(image, f'{cc}.gif')
        print(cc, end= ' ', flush=True)     # flush=True : When True print the output immediatley (without waiting the buffer to reach a new line, and then printing)
    return len(cc_list)
"""


def main(downloader: Callable[[list[str]], int]) -> None:
    t0 = time.perf_counter()
    count = downloader(POP20_CC)
    elapsed = time.perf_counter() - t0
    print(f'\n{count} downloads in {elapsed:.2f}s')


"""
if __name__ == '__main__':
    main(download_many)
"""

# Output:
# 
# BD BR CD CN DE EG ET FR ID IN IR JP MX NG PH PK RU TR US VN 
# 20 downloads in 16.37
#  
# The flags are printed one by one, and not all in one time (this is due to flush=True)
# # # # # # # 

# # # # # # #  Downloading with concurrent.futures :
#              ====================================

# The main feautures of concurrent.futures are : ThreadPoolExecutor and ProcessPoolExecutor.

# donwload with ThreadPoolExecutor :
from concurrent import futures

def download_one(cc: str) -> str:  # This is what each worker will execute
    image = get_flag(cc)
    save_flag(image, f'{cc}.gif')
    print(cc, end= ' ', flush=True)
    return cc       # imporatnt to return cc, it will be used later. See download_many.
"""
def download_many(cc_list: list[str]) -> int:
    with futures.ThreadPoolExecutor() as executor:  # ThreadPoolExecutor() accepts max_workers as argument. (default value None)
        res = executor.map(download_one, sorted(cc_list))   # the map here is similar to map built-in, except that download_one() will be called concurently by multiple threads.
                                                            # it return a generator, that we can iterate over to retrieve the value return by each function call. 
    return len(list(res))

if __name__ == '__main__':
    main(download_many)
"""
# Output:
# 
# BD DE FR BR EG CN ET CD ID IN JP IR NG MX PH PK RU VN TR US   # The output is not in order (like sequential) and differs from a running session to an other.
# 20 downloads in 2.36s
# 
# That's the advantage of concurency programming in asynchronous calls (like network calls) 
# # # # # # # 


# # # # # # Where Are the Futures ?
# ================================
#   - We have two classes named Future : concurrent.futures.Future and asyncio.Future.
# For both classes, we have the following:
#   - Future object represents deferred computation (postpone computation) that may or may not have completed ! (Like Promises in JavaScripts)
#   - Client code should not create Future Object. (They are created internally by the modules)
#   

# Example To get a practical look at futures: 

def download_many(cc_list: list[str]) -> int:
    cc_list = cc_list[:5]       # limit the number to 5 for this demonstratoion
    with futures.ThreadPoolExecutor(max_workers=3) as executor:
        to_do : list[futures.Future] = []

        for cc in sorted(cc_list):
            future = executor.submit(download_one, cc)  # executor.submit schedules the callable to be executed, and returns a future representing this pending operation.
            to_do.append(future)
            print(f'Scheduled for {cc} the future: {future}')
        
        for count, future in enumerate(futures.as_completed(to_do), start=1): # futures.as_completed() returns An iterator over the given futures that yields each as it completes.
            res: str = future.result()  # Return the result of the call that the future represents.
            print(f'{future} result: {res!r}')
    return count
"""
if __name__ == '__main__':
    main(download_many)
"""
# The Output:
# ==========
# Scheduled for BR the future: <Future at 0x205c692d360 state=running>  # we have 3 workers, so 3 are running and 2 are pending
# Scheduled for CN the future: <Future at 0x205c692e800 state=running>  # The futures are scheduled in alphabetical order
# Scheduled for ID the future: <Future at 0x205c692ef80 state=running>
# Scheduled for IN the future: <Future at 0x205c692f700 state=pending>
# Scheduled for US the future: <Future at 0x205c692f7c0 state=pending>
# CN <Future at 0x1431549e890 state=finished returned str> result: 'CN'     # The first 'CN' is the output of download_one(), and the rest of the line by download_many()
# ID BR <Future at 0x1431549ebc0 state=finished returned str> result: 'ID'  # Here two threads output codes before download_many in the main thread can display the result of the first thread.
# <Future at 0x1431549d3f0 state=finished returned str> result: 'BR'
# IN <Future at 0x1431549fa00 state=finished returned str> result: 'IN'
# US <Future at 0x1431549fac0 state=finished returned str> result: 'US'
# 
# 5 downloads in 1.30s
# 
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 



############ Multi-core Prime Checker with ProcessPoolExecutor
import sys

from Chapter_20 import check, NUMBERS      # import from prevouis chapter
"""
def main() -> None:
    if len(sys.argv) < 2:
        workers = None
    else:
        workers = int(sys.argv[1])

    executor = futures.ProcessPoolExecutor(max_workers=workers)     # When max_workers = None (it will be determined by os.cpu_count())
    actual_workers = executor._max_workers      # type: ignore  # This comment for mypy  # ._max_workers is an undocumented instance attribute of ProcessPoolExecutor.

    print(f'Checking {len(NUMBERS)} numbers with {actual_workers} processes: ')
    
    t0 = time.perf_counter()
    numbers = sorted(NUMBERS, reverse=True)

    with executor:
        for n, prime, elapsed in executor.map(check, numbers):
            label = 'P' if prime else ' '
            print(f'{n:16} {label} {elapsed:9.6f}s')

    total_time = time.perf_counter() - t0
    print(f'Total time: {total_time:.2f}s')

if __name__ == '__main__':
    main()
"""
# The Output:
# ==========
# 
# Checking 20 numbers with 4 processes: 
# 9999999999999999    0.000009s     # remark that the results are in descending order (as the original numbers used inside the map function)
# 9999999999999917 P 16.335718s     # Why the order is preserved ?
# 7777777777777777    0.000010s     #   This is because ProcessPoolExecutor.map(), returns a generator object that yields results
# 7777777777777753 P 14.389204s     # in the same order of the iterable given to .map() ! (if a result is not yet available, __next()__ will blocks until the result is available)
# 7777777536340681   14.575634s
# 6666667141414921   13.418562s
# 6666666666666719 P 13.970373s
# 6666666666666666    0.000002s
# 5555555555555555    0.000006s
# 5555555555555503 P 12.842640s
# 5555553133149889   12.712022s
# 4444444488888889   11.687359s
# 4444444444444444    0.000002s
# 4444444444444423 P  9.838281s
# 3333335652092209    8.775659s
# 3333333333333333    0.000007s
# 3333333333333301 P  8.937996s
#  299593572317531 P  3.012731s
#  142702110479723 P  2.132606s
#                2 P  0.000001s
# Total time: 37.86s
# 
# # # # # # # # # # # # # # # # # # 


# Example to Show that map returns results in the same order of the second argument: 

def mutiplay_by_2(n):
    return n*2

def test():
    with ProcessPoolExecutor() as executor:
        results = executor.map(mutiplay_by_2, range(1,11))
        print(results)

        for result in results:
            print(result, end= ' ')

if __name__ == '__main__':
    test()
# The Output:
# ==========
# <generator object _chain_from_iterable_of_lists at 0x000001DFE79CC040>
# 2 4 6 8 10 12 14 16 18 20
#  
# # # #  


# 
#### ThreadPoolExecutor.map() or ProcessPoolExecutor.map()   Vs  [ThreadPoolExector or ProcessPoolExecutor]().submit() and futures.as_completed() :
# 
# -  .map() is easy to use. However, we have the results in order and not once a result is ready like future.as_complete does !
# - Also, The combination of executor.submit and futures.as_completed is more flexible than executor.map because we can submit 
#       different callables and arguments, while executor.map is designed to run the same callable on the different arguments.
# - the set of futures we pass to futures.as_completed may come from more than one executor—perhaps some were 
#   created by a ThreadPoolExecutor instance while others are from a ProcessPoolExecutor
#  

# DOS(Denial of Service) attack can be made using concurrent HTTP clients

# # # # # # # Downloads with Progress Display and Error Handling
# 
# For this part, check the folder: Chapter_21_scripts
#  
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #







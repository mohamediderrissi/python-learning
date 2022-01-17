#######################################################################
##############  Chapter 20: Concurrency Models in Python
#######################################################################

############## Spinner with threrads: 
# Concepts:
#   - GIL: Global Interpereter Lock
#   - There is only one threads that holds the GIL (Only one thread is running at a time) (Not like Java. That's way to leverage mutli-core cpu, we should use processes instead of threads)
#   - To prevent a Python thread from holding the GIL indefinitely, Python’s bytecode interpreter pauses the current Python thread
#     every 5ms by defaul.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #  #  #
# from threading import Thread, Event
# import itertools
# import multiprocessing
# from multiprocessing import queues
# import queue
import time
# def spin(msg, done: Event) -> None:
#     for char in itertools.cycle('\|/-'):
#         status = f'\r{char} {msg}'         # '\r' carriage return: move the cursor to the begining on the current line. print('My website is Latracal \rSolution') => has the output: Solutionte is Latracal
#         print(status, end='', flush=True)
#         if done.wait(.1):
#             break
#     blanks = ' ' * len(status)
#     print(f'\r{blanks}\r', end='')

# def slow():
#     time.sleep(3)       # make the calling thread release the GIL, which means suspended (so other threads can be resumed)
#     return 42

# def supervisor():
#     done = Event()
#     spinner = Thread(target=spin, args=('thinking', done))
#     print(f'spinner object: {spinner}')     # spinner object: <Thread(Thread-1 (spin), initial)>
#     spinner.start()
#     result = slow()
#     done.set()
#     spinner.join()  # make the caller thread waits the thread for which .join() was called. main thread waits spinner thread until finished
#     return result

# def main():
#     result = supervisor()
#     print(f'Answer: {result}')

# if __name__ == '__main__':
#     main()


############## Spinner with multiprocessing: 
# When you create a multiprocessing.Process instance, a whole new Python interpreter is started as a child process in the background.
# Each Process has its own GIL.
# from multiprocessing import Process, Event
# from multiprocessing import synchronize

# def spin_with_process(msg: str, done: synchronize.Event) -> None:
#     # Same body as spin
#     for char in itertools.cycle('\|/-'):
#         status = f'\r{char} {msg}'         # '\r' carriage return: move the cursor to the begining on the current line. print('My website is Latracal \rSolution') => has the output: Solutionte is Latracal
#         print(status, end='', flush=True)
#         if done.wait(.1):
#             break
#     blanks = ' ' * len(status)
#     print(f'\r{blanks}\r', end='')

# def supervisor():
#     done = Event()
#     spinner = Process(target=spin_with_process, args=('thinking', done))
#     print(f'spinner object {spinner}')      # spinner object <Process name='Process-1' parent=7052 initial>
#     spinner.start()
#     result = slow()
#     done.set()
#     spinner.join()
#     return result

# def main():
#     result = supervisor()
#     print(f'Answer: {result}')

# if __name__ == '__main__':
#     main()

# 
# In the two previous approaches, we used Event to synchronize (threads / processes)
# 


############## My remarks: 
# In Python, we have 3 ways for concurency programing, using :
# - Threads :  The problem with threads in Python is The GIL. (only one thread is running, so we can not benefit from cpu with multicores )
# - Processes : Here we can benefits from the cpu with multicores
# - Native Coroutine : This is sequential code (one thread is running), that use coroutines to handle concurency (event loop)
# In many times, using sequenctiel code is better than multi-threading in Python (due to the GIL limitation). Hence the use of coroutine may be 
# more appropriate than threads



############### A Homegrown Process Pool :
# Two approaches (sequential and process-based) to compute the primality of 20 numbers (Example of a CPU intensive work).
import math
from typing import NamedTuple

# Numbers :
PRIME_FIXTURE = [
    (2, True),
    (142702110479723, True),
    (299593572317531, True),
    (3333333333333301, True),
    (3333333333333333, False),
    (3333335652092209, False),
    (4444444444444423, True),
    (4444444444444444, False),
    (4444444488888889, False),
    (5555553133149889, False),
    (5555555555555503, True),
    (5555555555555555, False),
    (6666666666666666, False),
    (6666666666666719, True),
    (6666667141414921, False),
    (7777777536340681, False),
    (7777777777777753, True),
    (7777777777777777, False),
    (9999999999999917, True),
    (9999999999999999, False),
]

NUMBERS = [n for n, _ in PRIME_FIXTURE]

# Function to check the primality of a number: 
def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    root = math.isqrt(n)
    for i in range(3, root + 1, 2):
        if n % i == 0:
            return False
    return True

# Class to store the result: 
class Result(NamedTuple):
    prime: bool
    elapsed: float

# # # # Sequential approach :

# def check(n: int) -> Result:
#     """ Check if n is prime and return Result(bool, elapsed_time) """
#     t0 = time.perf_counter()
#     prime = is_prime(n)
#     return Result(prime, time.perf_counter()- t0)

# def main():
#     t0 = time.perf_counter()
#     for n in NUMBERS:
#         prime, elapsed = check(n)
#         label =  'P' if prime else ' '
#         print(f'{n:16}  {label}   {elapsed:9.6f}s')

#     elapsed = time.perf_counter() - t0
#     print(f"Total time: {elapsed:.2f}s")

# main()

# Output of the sequential approach :
# ==================================
# 
#                2  P    0.000001s
#  142702110479723  P    0.967090s
#  299593572317531  P    1.310283s
# 3333333333333301  P    4.337700s
# 3333333333333333      0.000011s
# 3333335652092209      4.047295s
# 4444444444444423  P    5.003431s
# 4444444444444444      0.000003s
# 4444444488888889      5.116319s
# 5555553133149889      6.580974s
# 5555555555555503  P    5.784053s
# 5555555555555555      0.000011s
# 6666666666666666      0.000003s
# 6666666666666719  P    6.159968s
# 6666667141414921      6.023145s
# 7777777536340681      6.759737s
# 7777777777777753  P    7.068352s
# 7777777777777777      0.000014s
# 9999999999999917  P    7.791780s
# 9999999999999999      0.000018s
# Total time: 67.00s
# 
#    


# # # # Process-based Solution :
# The idea :
#  - We have a set of tasks. We will create a number of processes (in this example = number of cpu cores if no argument is given on the comandline)
#  - Each process will pick a task (check if a number is prime), and once finished, put the result in some place (Here we use another queue).
#  - For Each worker, we put a value that termines him (Here, we use 0. We can any pickable object). => This techinuqe called Poison Pill
# 
import sys
from multiprocessing import Process, SimpleQueue, cpu_count
from multiprocessing import queues

class PrimeResult(NamedTuple):
    n: int
    prime: bool
    elapsed: float

# used for type hints
JobQueue = queues.SimpleQueue[int]
ResultQueue = queues.SimpleQueue[PrimeResult]

def check(n: int):
    t0 = time.perf_counter()
    res = is_prime(n)
    return PrimeResult(n, res, time.perf_counter() - t0)

def worker(jobs: JobQueue, results: ResultQueue):
    while n:= jobs.get():   # assign inside a loop with :=
        results.put(check(n))

def main() -> None:
    # Check if an argument is the command line :
    if len(sys.argv) < 2 :
        workers = cpu_count()       # number of cores on the machine
    else:
        workers = int(sys.argv[1])
    
    print(f'Checking {len(NUMBERS)} numbers with {workers} processes :')
    jobs : JobQueue = SimpleQueue()
    results : ResultQueue = SimpleQueue()

    t0 = time.perf_counter()

    # Put the numbers in the job queue :
    for n in NUMBERS:
        jobs.put(n)

    # Create and start processes :
    for _ in range(workers):
        proc = Process(target=worker, args=(jobs, results))
        proc.start()
        jobs.put(0)     # Poison Pill for each worker to stop him once finished
    
    while True:
        n, prime, elapsed = results.get()
        label = 'P' if prime else ' '
        print(f'{n:16} {label} {elapsed:9.6f}s')
        if jobs.empty():
            break
        
    elapsed = time.perf_counter() - t0
    print(f"Total time: {elapsed:.2f}s")

if __name__ == '__main__':
    main()
# Output :
# Checking 20 numbers with 4 processes :
#                2 P  0.000002s
# 3333333333333333    0.000008s
#  142702110479723 P  2.022276s
#  299593572317531 P  2.959609s
# 4444444444444444    0.000002s
# 3333335652092209    9.503461s
# 3333333333333301 P  9.643531s
# 4444444444444423 P 11.454194s
# 5555555555555555    0.000009s
# 6666666666666666    0.000002s
# 4444444488888889   11.671801s
# 5555555555555503 P 13.887182s
# 5555553133149889   14.025723s
# 6666666666666719 P 14.879737s
# 7777777777777777    0.000010s
# 6666667141414921   14.589172s
# 9999999999999999    0.000008s
# 7777777536340681   12.483228s
# 7777777777777753 P 12.789878s
# 9999999999999917 P 11.238177s
# Total time: 39.88s

# Conclusion :
# multi-process based solution is faster
# The same exercise with threads is less performant than sequential code (mentienned in the book)
# The GIL limitation of python is overtaken using some techniques (as used in Performance-oriented library )




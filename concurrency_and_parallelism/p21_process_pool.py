#!/usr/bin/env python3
""" Chopping vegetables with a ThreadPool """

import threading
from concurrent.futures import ProcessPoolExecutor
import os

def vegetable_chopper(vegetable_id):
    name = os.getpid()
    print(name, 'chopped vegetable', vegetable_id)

if __name__ == '__main__':
    # if max_workers not specified, it creates 5 times as many threads as CPUs.
    # This is based on the assumption that thread pools are used to overlap I/O
    # bound tasks rather than CPU intensive tasks. So the number of threads should
    # exceed the number of processes.
    with ProcessPoolExecutor(max_workers = 5) as pool:
        for vegetable in range(100):
        # submit the function as a callable object.
            pool.submit(vegetable_chopper, vegetable)



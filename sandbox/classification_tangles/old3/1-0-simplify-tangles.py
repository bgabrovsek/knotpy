import sys
sys.path.append('/home/bostjan/remote_code/knotpy')

import knotpy as kp
from knotpy import Bar
import multiprocessing
from itertools import  chain
from read_input import safe_delete_file
import time

input_tangles = "data/tangles-em.txt"
num_tangles = 3805162

output_tangles = "data/canonical_tangles.txt"
output_tangles1 = "data/canonical_tangles1.txt"

def make_diagrams2(k, lock,shared_int,  filename, depth):
    #print(k)

    k_diagrams = kp.all_minimal_crossings_simplifications(k, depth=depth, max_difference=0)

    with lock:
        #print("write")
        #shared_int.value += 1
        #if shared_int.value % 100 == 0:
        #    print(f"{100*shared_int.value/num_tangles:.1f}%")
        kp.append_to_collection(filename, k_diagrams, "cem")


def make_diagrams(k,  filename, depth):
    #print(k)

    k_diagrams = kp.all_minimal_crossings_simplifications(k, depth=depth, max_difference=0)

    #with lock:
        #print("write")
        #shared_int.value += 1
        #if shared_int.value % 100 == 0:
        #    print(f"{100*shared_int.value/num_tangles:.1f}%")
    kp.append_to_collection(filename, k_diagrams, "cem")



if __name__ == "__main__":

    safe_delete_file(output_tangles)
    safe_delete_file(output_tangles1)

    for k in Bar(kp.load_collection_iterator(input_tangles), total=num_tangles):
        make_diagrams(k, output_tangles, 0)


    # manager = multiprocessing.Manager()
    # lock = manager.Lock()
    # shared_int = manager.Value('i', 0)
    #
    #
    # num_workers = 16
    # pool = multiprocessing.Pool(num_workers)
    # for index in Bar(range(3716), total=3716):
    #     data = [(k, lock, shared_int, f"data/canonical_tangles/canonical_tangles_{index}.txt", 0)
    #             for k in kp.load_collection(f"data/tangles/tangles-em_{index}.txt", notation="cem")]
    #     result = pool.starmap(make_diagrams, data)
    #
    # pool.close()
    # pool.join()
    #
    # for tngls in kp.load_collection_iterator(input_tangles, chunk_size=1024):
    #     pool.starmap(make_diagrams,
    #                  ((k, lock, shared_int, output_tangles1, 1) for k in tngls))
    # pool.close()
    # pool.join()


    # for k in kp.load_collection_iterator(input_knots):
    #     pool.apply_async(make_diagrams, args=(k, lock, output_knots))
    #
    # pool.close()
    # pool.join()
        #print(k)
    # pool.starmap(make_diagrams, [[k, lock, output_knots] for k in kp.load_collection_iterator(input_knots)])
    #for k in kp.load_collection_iterator(input_knots))

    #
    # for knot in Bar(kp.load_collection_iterator(input_knots), total=num_knots):
    #     task = pool.apply_async(make_diagrams, args=(knot, lock, output_knots))
    #
    #     running_tasks.append(task)
    #
    #     # Check if we are above the max allowed tasks in flight
    #     if len(running_tasks) >= max_tasks_in_flight:
    #         # Wait for at least one task to finish before submitting more
    #         while running_tasks:
    #             for running_task in running_tasks:
    #                 if running_task.ready():  # If task is done
    #                     running_tasks.remove(running_task)  # Remove it from the list
    #                     break
    #             time.sleep(0.1)  # Short sleep to avoid busy-waiting
    #
    # # Wait for all remaining tasks to complete
    # pool.close()
    # pool.join()


    # with multiprocessing.Pool(processes=24) as pool:
    #     pool.starmap(make_diagrams, (k, lock) for k in kp.load_collection_iterator(input_knots))
        #results = set(chain(*results))



import sys
sys.path.append('/home/bostjan/remote_code/knotpy')

import knotpy as kp
from knotpy import Bar
import multiprocessing
from itertools import  chain
from read_input import safe_delete_file
import time

input_knots, input_links, input_tangles = "data/knots-em.txt", "data/links-em.txt", "data/tangles-em.txt"
num_knots, num_links, num_tangles = 59937, 4188, 3805162

output_knots, output_links, output_tangles = "data/canonical_knots.txt", "data/canonical_links.txt", "data/canonical_tangles.txt"

def make_diagrams(k, lock,shared_int,  filename):
    #print(k)

    k_diagrams = kp.all_minimal_crossings_simplifications(k, depth=1, max_difference=0)

    m = kp.mirror(k.copy())
    m.name = k.name + "m"

    m_diagrams = kp.all_minimal_crossings_simplifications(m, depth=0)
    if m_diagrams.isdisjoint(k_diagrams):
        m_diagrams = kp.all_minimal_crossings_simplifications(m, depth=1, max_difference=0)

        if not m_diagrams.isdisjoint(k_diagrams):
            m_diagrams = set()
    else:
        m_diagrams = set()

    # min_crossings_k = min(len(_) for _ in k_diagrams)
    # min_crossings_m = min(len(_) for _ in m_diagrams) if m_diagrams else 0

    # diagrams = ([f"{k.name}:{knot2str(k)}\n" for k in k_diagrams] +
    #             [f"{m.name}:{knot2str(m)}\n" for m in m_diagrams])
    # diagrams_min = ([f"{k.name}:{knot2str(k)}\n" for k in k_diagrams if len(k) == min_crossings_k] +
    #                 [f"{m.name}:{knot2str(m)}\n" for m in m_diagrams if len(m) == min_crossings_m])
    #
    with lock:
        #print("write")
        shared_int.value += 1
        if shared_int.value % 100 == 0:
            print(f"{100*shared_int.value/num_knots:.1f}%")
        kp.append_to_collection(filename, k_diagrams | m_diagrams, "cem")


if __name__ == "__main__":

    safe_delete_file(output_knots)

    manager = multiprocessing.Manager()
    lock = manager.Lock()
    shared_int = manager.Value('i', 0)

    #for knots in Bar(kp.load_collection_iterator(input_knots, chunk_size=chunk_size), total=num_knots//chunk_size):

    running_tasks = []

    num_workers = 31
    max_tasks_in_flight = 31
    pool = multiprocessing.Pool(num_workers)
    pool.starmap(make_diagrams, ((k, lock, shared_int, output_knots) for k in kp.load_collection_iterator(input_knots)))

    pool.close()
    pool.join()

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



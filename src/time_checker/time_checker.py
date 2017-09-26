import time

__all__ = ['start', 'stop', 'get_pass_time']


MIN_ID = 0
MAX_ID = 250
last_id = [0]

times_dict = {}

free_ids = []


def start():
    start_t = time.time()

    id = -1
    if free_ids:
        id = free_ids.pop(0)
    else:
        last_id[0] += 1
        id = last_id[0]

    times_dict[id] = start_t

    return id


def stop(id, no_matter=False):
    stop_t = time.time()
    if id in times_dict:
        res = stop_t - times_dict[id]

        times_dict[id] = res


def get_pass_time(id):
    if id in times_dict:
        time = "{:s}(sec)".format(str(round(times_dict[id], 4)))
        del times_dict[id]
    else:
        time = "id is not available"

    return time
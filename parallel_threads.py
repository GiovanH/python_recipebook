import threading
import queue
import traceback

class QueueWorker(threading.Thread):
    """A worker that executes a specific function on all the work
    in a given queue."""

    def __init__(self, queue, fn, *args, **kwargs):
        """Summary
        
        Args:
            queue: Queue to draw work from.
            fn: Function executed
            *args: Passthough to threading.Thread
            **kwargs: Passthough to threading.Thread
        """
        self.queue = queue
        self.fn = fn
        super().__init__(*args, **kwargs)

    def run(self):
        """Run fn on items popped from q until queue is empty."""
        while True:
            try:
                work = self.queue.get(timeout=3)  # 3s timeout
            except queue.Empty:
                return
            self.fn(*work)
            self.queue.task_done()

def do_work_helper(workfn, inputs, max_threads=8):
    """Use threads and a queue to parallelize work done by a function."""
    # Create a queue. (Everything following has q in the namespace)
    q = queue.Queue()

    results = []

    def _process(*args):
        try:
            ret = workfn(*args)
        except Exception as e:
            traceback.print_exc()
            ret = e
        results.append(ret)

    for args in inputs:
        # Replace with actual function arguments
        q.put_nowait(args)

    # Start threads
    for _ in range(max_threads):
        QueueWorker(q, _process).start()

    # Block until the queue is empty.
    q.join()  

    return results

def test_do_work():
    MAX_THREADS = 8
    # Create a queue. (Everything following has q in the namespace)
    q = queue.Queue()

    results = []

    def processWork(w):
        # This is the actual processing function
        results.append(w * 10)

    for work in range(80):
        # Replace with actual function arguments
        q.put_nowait([work])

    # Start threads
    for _ in range(MAX_THREADS):
        QueueWorker(q, processWork).start()

    # Block until the queue is empty.
    q.join()  

    # Verify
    assert len(results) == 80
    for work in range(80):
        assert (work * 10) in results


def test_do_work_helper():
    def timesTen(x):
        return x * 10

    results = do_work_helper(
        timesTen,
        [(i,) for i in range(80)]
    )

    # Verify
    assert len(results) == 80
    for work in range(80):
        assert (work * 10) in results


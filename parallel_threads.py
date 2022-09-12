import threading
import queue


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
        kwargs['daemon'] = True  # Don't block the program on exceptions
        super().__init__(*args, **kwargs)

    def run(self):
        import traceback
        """Run fn on items popped from q until queue is empty."""
        while True:
            try:
                work = self.queue.get()
            except queue.Empty:
                return

            try:
                self.fn(*work)
            except Exception:
                traceback.print_exc()
            finally:
                self.queue.task_done()


class ReschedulableQueueWorker(QueueWorker):
    """A QueueWorker that can be rescheduled from within the queue.

    Throw ReschedulableQueueWorker.NeedRescheduleError in the work function
    to abort and move the work to the end of the queue."""
    class NeedRescheduleError(Exception):
        pass

    def run(self):
        import traceback
        """Run fn on items popped from q until queue is empty."""
        while True:
            try:
                work = self.queue.get()
            except queue.Empty:
                return

            try:
                self.fn(*work)
            except self.NeedRescheduleError:
                traceback.print_exc()
                self.queue.put_nowait(work)
            except Exception:
                traceback.print_exc()
            finally:
                self.queue.task_done()

def do_work_helper(workfn, inputs, max_threads=8):
    """Use threads and a queue to parallelize work done by a function.

    >>> do_work_helper(lambda x: x * 5, [(i,) for i in range(10)])
    [0, 5, 10, 15, 20, 25, 30, 35, 40, 45]
    """
    import traceback
    
    # Create a queue. (Everything following has q in the namespace)
    q = queue.Queue()

    results = []
    result_lock = threading.Lock()

    def _process(*args):
        try:
            ret = workfn(*args)
        except Exception as e:
            traceback.print_exc()
            ret = e
        # You usually don't need to lock like this thanks to the GIL, for details see
        # https://docs.python.org/3/faq/library.html#what-kinds-of-global-value-mutation-are-thread-safe
        with result_lock:
            results.append(ret)

    for args in inputs:
        # Replace with actual function arguments
        q.put_nowait(args)

    # Start threads
    for _ in range(max_threads):
        QueueWorker(q, _process).start()

    # Block until the queue is empty.
    try:
        q.join()
    except KeyboardInterrupt:
        return

    return results


def test_do_work():
    # Do work manually, without a helper.
    # Entirely redundant, but included as a recipe.
    MAX_THREADS = 8

    # Create a queue. (Everything following has q in the namespace)
    q = queue.Queue()

    results = []

    def processWork(w):
        results.append(w * 10)

    for work in range(80):
        q.put_nowait([work])

    for _ in range(MAX_THREADS):
        QueueWorker(q, processWork).start()

    q.join()

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

def test_reschedule():
    MAX_THREADS = 3
    MAX_RANGE = 12

    # Create a queue. (Everything following has q in the namespace)
    q = queue.Queue()

    results = []

    def doConditionalWork(w):
        # Can only succeed if it's sequential, otherwise errors.
        if w == 0 or (results and results[-1] == w - 1):
            results.append(w)
        else:
            raise ReschedulableQueueWorker.NeedRescheduleError(w)

    for work in reversed(range(MAX_RANGE)):
        # Queue in reverse error so work is not executed in sequential order
        q.put_nowait([work])

    for _ in range(MAX_THREADS):
        ReschedulableQueueWorker(q, doConditionalWork).start()

    q.join()

    assert results == list(range(MAX_RANGE))

# Only dependency needed
import threading
import datetime

# Dependency for the task
import time

def interval_generator(period):
    """
    Create periodic times according to https://stackoverflow.com/a/28034554
    """
    t = time.time()
    while True:
        t += period
        yield max(t - time.time(),0)

def run_periodically(interval, function, times=-1, args=None, kwargs=None):
    """
    Returns:
        stop - <Event> call set() to stop the periodic calls
    """
    stop = threading.Event()

    # We need this, because [] and {} are not immutable. Otherwise we have a shared instance as default value.
    args = args if args is not None else []
    kwargs = kwargs if kwargs is not None else {}

    def inner_wrap():
        i = 0
        
        # Avoid time drift by using an interval generator
        intervals = interval_generator(interval)

        while i != times and not stop.isSet():
            stop.wait(next(intervals))
            function(*args, **kwargs)
            i += 1

    t = threading.Timer(0, inner_wrap)
    t.daemon = True
    t.start()

    return stop

# Function wrapper 
def periodic_task_decorator(interval, times = -1):
    """
    Source: https://gist.github.com/Depado/7925679
    """
    def outer_wrap(function):
        def wrap(*args, **kwargs):
            return run_periodically(interval=interval, function=function, times=times, args=args, kwargs=kwargs)
        return wrap
    return outer_wrap

if __name__ == "__main__":
    # Call the function once to launch the periodic system
        
    @periodic_task_decorator(1)
    def my_periodic_task():
        # This function is executed every 10 seconds
        print("I am executed at {}".format(datetime.datetime.now()))

    token = my_periodic_task()

    # This task will run while the program is alive, so for testing purpose we're just going to sleep.
    time.sleep(3)
    token.set()
    time.sleep(500)
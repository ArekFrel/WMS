import functools
from datetime import datetime
from wms_main.const import TimeConsts
import time


def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_point = time.time()
        func(*args, **kwargs)
        exec_time = time.time() - start_point
        print(f'Execution of {func.__name__}: {exec_time:.6f} s')
        return float(exec_time)
    return wrapper


def time_break(from_=1, to_=6):
    def dec(func):
        def wrapper():
            if not from_ <= datetime.now().hour < to_:
                func()
            else:
                now = str(datetime.fromtimestamp(time.time(), ))[0:-7]
                print(f'{now} - Break from {TimeConsts.FROM_OCLOCK} to {TimeConsts.TO_OCLOCK}.\n')
        return wrapper
    return dec


def main():
    pass


if __name__ == '__main__':
    main()

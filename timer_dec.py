import functools
import time


def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_point = time.time()
        func(*args, **kwargs)
        exec_time = time.time() - start_point
        print(f'Execution of {func.__name__}: {exec_time:.0f} s')
    return wrapper


def main():
    pass


if __name__ == '__main__':
    main()

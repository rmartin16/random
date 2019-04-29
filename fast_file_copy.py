import os
import sys


def copy_file(src, dst, progress_bar=True):
    return_value = 0
    file_in = None
    file_out = None

    try:
        O_BINARY = os.O_BINARY
    except AttributeError:
        O_BINARY = 0
    READ_FLAGS = os.O_RDONLY | O_BINARY
    WRITE_FLAGS = os.O_WRONLY | os.O_CREAT | os.O_TRUNC | O_BINARY
    BUFFER_SIZE = 128*1024

    # remove if progress bar isn't needed
    expected_loop_count = os.path.getsize(src) / BUFFER_SIZE
    (loop_count, progress_count) = (0, 0)

    # copy the file - TODO: implement handling for different error cases
    try:
        file_in = os.open(src, READ_FLAGS)
        stat = os.fstat(file_in)
        file_out = os.open(dst, WRITE_FLAGS, stat.st_mode)
        for x in iter(lambda: os.read(file_in, BUFFER_SIZE), b""):
            os.write(file_out, x)

            if progress_bar:
                (loop_count, progress_count) = manage_progress_bar(expected_loop_count, loop_count, progress_count)

    except OSError:
        return_value = 1
    finally:
        for fd in [file_in, file_out]:
            if fd is not None:
                try:
                    os.close(fd)
                except OSError:
                    pass
    return return_value


def manage_progress_bar(expected_loop_count, loop_count, progress_count):
    if loop_count == 0:
        sys.stdout.write("Copying...")
    if expected_loop_count < 20:
        div = 1  # if not many loops, don't over-complicate the progress bar
    else:
        div = .1
    mod = expected_loop_count * div
    loop_count = loop_count + 1
    if loop_count > (progress_count * mod):
        per = int(progress_count * (div * 100))
        sys.stdout.write(str(per) + "%")
        if per < 100:
            sys.stdout.write("...")
        else:
            print()  # try to make the progress bar end in a newline
        sys.stdout.flush()
        progress_count = progress_count + 1
    return loop_count, progress_count

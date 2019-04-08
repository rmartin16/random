import os
import sys


def copy_file(src, dst):
    retval = 0
    try:
        O_BINARY = os.O_BINARY
    except AttributeError:
        O_BINARY = 0
    READ_FLAGS = os.O_RDONLY | O_BINARY
    WRITE_FLAGS = os.O_WRONLY | os.O_CREAT | os.O_TRUNC | O_BINARY
    BUFFER_SIZE = 128*1024

    file_size = os.path.getsize(src)
    write_loops = file_size / BUFFER_SIZE
    div = .1
    mod = write_loops * div
    pcount = 1
    lcount = 1

    try:
        fin = os.open(src, READ_FLAGS)
        stat = os.fstat(fin)
        fout = os.open(dst, WRITE_FLAGS, stat.st_mode)
        sys.stdout.write("Copying...")
        sys.stdout.flush()
        for x in iter(lambda: os.read(fin, BUFFER_SIZE), b""):
            os.write(fout, x)
            lcount = lcount + 1
            if (lcount > (pcount * (mod))):
                per = int(pcount * (div * 100))
                sys.stdout.write(str(per) + "%")
                if per < 100:
                    sys.stdout.write("...")
                sys.stdout.flush()
                pcount = pcount + 1
    except Exception:
        retval = 1
    finally:
        try:
            os.close(fin)
        except Exception:
            pass
        try:
            os.close(fout)
        except Exception:
            pass

    return retval

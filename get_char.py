
class _GetChar:
    """Gets a single character from standard input.  Does not echo to the screen."""
    def __init__(self):
        from os import name as osname
        if osname == 'nt':
            self.impl = _GetCharWindows()
        else:
            self.impl = _GetCharUnix()

    # TODO: add support for a default value...it s a little trickier than
    #       it looks since the char may not be printable e.g. the up arrow key
    def __call__(self, timeout=None):
        char = self.impl(timeout)
        # catch CTRL+C (needed for non-windows)
        if char == '\x03':
            raise KeyboardInterrupt
        return char


class _GetCharUnix:
    """Fetch and character using the termios module."""
    def __init__(self):
        pass

    def __call__(self, timeout):
        from sys import stdin
        from tty import setraw
        from termios import tcgetattr, tcsetattr, TCSADRAIN
        from select import select

        fd = stdin.fileno()
        old_settings = tcgetattr(fd)

        try:
            setraw(stdin.fileno())

            # [ Wait until ready for reading,
            #   wait until ready for writing
            #   wait for an "exception condition" ]
            # The below line times out after 1 second
            # This can be changed to a floating-point value if necessary
            [i, _, _] = select([stdin.fileno()], [], [], timeout)
            if i:
                ch = stdin.read(1)
            else:
                ch = None

        finally:
            tcsetattr(fd, TCSADRAIN, old_settings)

        return ch


class _GetCharWindows:
    """Fetch a character using the Microsoft Visual C Runtime."""
    def __init__(self):
        pass

    def __call__(self, timeout):
        from msvcrt import getch, kbhit
        from time import sleep

        # just block for input if no timeout
        if timeout is None:
            return getch()

        else:  # otherwise continuously check for input until timeout
            for _ in range(0, timeout):
                if kbhit():  # is input waiting?
                    return getch()  # return that input
                sleep(1)
        return


get_char = _GetChar()

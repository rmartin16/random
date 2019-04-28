
class _GetChar:
    """
       Gets a single character from standard input. Does not echo to the screen.
       Outcomes:
         1. upon timeout -> None returned
         2. upon UTF-8 entry -> UTF-8 char returned
         3. upon non-UTF-8 entry -> best case is hex encoding...
    """
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
        ch = None

        try:
            setraw(stdin.fileno())

            [i, _, _] = select([stdin.fileno()], [], [], timeout)
            if i:
                ch = stdin.read(1)

        finally:
            tcsetattr(fd, TCSADRAIN, old_settings)

        return ch


class _GetCharWindows:
    """Fetch a character using the Microsoft Visual C Runtime.

       NOTE: this windows implementation works but is finicky. I've mostly
             peculiar behavior around entering non-ASCII characters. For
             instance, entering the up arrow key seems to leave something in
             the buffer such that the next call may find something...FYI...

    """
    def __init__(self):
        pass

    def __call__(self, timeout):
        from msvcrt import getch, kbhit
        from time import sleep
        char = None

        # just block for input if no timeout
        if timeout is None:
            char = getch()

            # otherwise continuously check for input until timeout
        else:
            for _ in range(0, int(timeout)*2):
                if kbhit():  # is any input waiting?
                    char = getch()  # get it
                    break
                sleep(.5)

        if char is None:
            return char

        # make a best effort to convert bytes to string to match unix.
        #  first just attempt a straight UTF-8 conversion.
        #  then attempt a non-UTF-8 conversion; since non-UTF-8 chars convert
        # with a 'b' on the front and has quotes, trim that stuff.
        try:
            return char.decode()
        except UnicodeDecodeError:
            return str(char)[2:-1]


get_char = _GetChar()

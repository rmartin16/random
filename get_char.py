
class _GetChar:
    """Gets a single character from standard input.  Does not echo to the screen."""
    def __init__(self):
        try:
            self.impl = _GetCharWindows()
        except ImportError:
            self.impl = _GetCharUnix()

    def __call__(self, timeout=None):
        ch = self.impl(timeout)
        # catch CTRL+C (needed for non-windows)
        if ch == '\x03':
            raise KeyboardInterrupt
        return ch


class _GetCharUnix:
    """Fetch and character using the termios module."""
    def __init__(self):
        import tty, sys
        from select import select

    def __call__(self, timeout):
        import sys, tty, termios
        from select import select

        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)

        try:
            tty.setraw(sys.stdin.fileno())

            # [ Wait until ready for reading,
            #   wait until ready for writing
            #   wait for an "exception condition" ]
            # The below line times out after 1 second
            # This can be changed to a floating-point value if necessary
            [i, _, _] = select([sys.stdin.fileno()], [], [], timeout)
            if i:
                ch = sys.stdin.read(1)
            else:
                ch = None

        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

        return ch


class _GetCharWindows:
    """Fetch a character using the Microsoft Visual C Runtime."""
    def __init__(self):
        import msvcrt

    def __call__(self, timeout):
        import msvcrt
        import time

        # just block for input if no timeout
        if timeout is None:
            return msvcrt.getch()

        else:  # otherwise continuously check for input until timeout
            try:
                timeout = int(timeout)
                for _ in range(0, timeout):
                    if msvcrt.kbhit():  # is input waiting?
                        return msvcrt.getch()  # return that input
                    time.sleep(1)
            except ValueError:
                pass  # ensure timeout is an integer...
        return


get_char = _GetChar()

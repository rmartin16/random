#!/usr/bin/python3

import subprocess
import psutil
import sys
import os
import time
from get_char import get_char

timeout = 5 * 60  # X minutes


class Timeout(Exception):
    pass


def run_with_input():
    proc = None
    commands = ['l', 'n', 'g', 't']
    while True:
        try:
            start_time = time.time()
            proc = subprocess.Popen(['nmon', '-g', '/home/user/.nmon_disk_group'], stdin=subprocess.PIPE) #, stdout=subprocess.PIPE)

            # commands may be populated if we're just restarting nmon
            # so, send the commands to restore state
            for command in commands:
                os.write(proc.stdin.fileno(), str(command).encode())

            while True:
                # get next command if any
                user_char = get_char(1)

                # treat q as ctrl+c to force us all the way out
                if user_char == 'q':
                    raise Exception

                # logs user input and send the char to nmon
                if user_char is not None:
                    #proc.stdin.write(user_char.encode())
                    os.write(proc.stdin.fileno(), user_char.encode())

                    # keep track of state so it can be restored when nmon is restarted
                    if user_char in commands:
                        commands.remove(user_char)
                    else:
                        commands.append(user_char)

                # check if nmon needs to be restarted
                if (time.time() - start_time) > timeout:
                    raise Timeout

        # and start back over
        except Timeout:
            kill(proc)

        # clean up and exit on *any* exception (otherwise, screen is hosed...)
        except BaseException as e:
            exit_prog(proc)


def run_naked():
    while True:
        proc = subprocess.Popen(['nmon', '-g', '/home/user/.nmon_disk_group'], stdin=subprocess.PIPE)
        try:
            proc.communicate(input=b'lngt', timeout=timeout)
        except subprocess.TimeoutExpired:
            kill(proc)
        except KeyboardInterrupt:
            exit_prog(proc)


def kill(proc=None):
    if proc is not None:
        process = psutil.Process(proc.pid)
        for proc in process.children(recursive=True):
            proc.terminate()
        process.terminate()


def exit_prog(proc=None):
    kill(proc)
    subprocess.call('reset')
    print()
    sys.exit(0)


run_with_input()

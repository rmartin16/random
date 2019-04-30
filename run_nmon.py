#!/usr/bin/env python3

import subprocess
import psutil
import sys
import os
import time
from get_char import get_char

timeout = 15 * 60  # X minutes


class Timeout(Exception):
    pass


class GetOutOfHere(Exception):
    pass


def run_with_input():
    proc = None
    all_commands = 'cmdrkhljnNtVvb0u.1345'
    top_process_commands = '1345'
    user_commands = ['l', 'n', 'g', 't']
    while True:
        try:
            start_time = time.time()
            proc = subprocess.Popen(['nmon', '-g', '/home/user/.nmon_disk_group'], stdin=subprocess.PIPE)  # , stdout=subprocess.PIPE)

            # commands may be populated if we're just restarting nmon
            # so, send the commands to restore state
            for command in user_commands:
                os.write(proc.stdin.fileno(), str(command).encode())

            while True:
                # get next command if any
                user_char = get_char(1)

                # treat q as special to force us all the way out "properly"
                if user_char == 'q':
                    raise GetOutOfHere

                # send command to nmon and log the command
                if user_char is not None:
                    # proc.stdin.write(user_char.encode())
                    os.write(proc.stdin.fileno(), user_char.encode())

                    # keep track of state so it can be restored when nmon is restarted
                    if user_char in all_commands:
                        if user_char in user_commands:
                            if user_char not in top_process_commands:
                                user_commands.remove(user_char)
                        else:
                            if user_char in top_process_commands and 't' in user_commands:
                                user_commands.append(user_char)
                            else:
                                user_commands.append(user_char)

                # check if nmon needs to be restarted
                if (time.time() - start_time) > timeout:
                    raise Timeout

        # and start back over
        except Timeout:
            kill(proc)
        # exit out of everything
        except GetOutOfHere:
            break

        # clean up on the way out (otherwise, screen is hosed...)
        finally:
            exit_program(proc)


def run_naked():
    while True:
        proc = subprocess.Popen(['nmon', '-g', '/home/user/.nmon_disk_group'], stdin=subprocess.PIPE)
        try:
            proc.communicate(input=b'lngt', timeout=timeout)
        except subprocess.TimeoutExpired:
            kill(proc)
        finally:
            exit_program()


def kill(input_process=None):
    if input_process is not None:
        process = psutil.Process(input_process.pid)
        for proc in process.children(recursive=True):
            proc.terminate()
        process.terminate()


def exit_program(proc=None):
    kill(proc)
    subprocess.call('reset')  # reset terminal since it always seems to be messed up after...
    print()
    # sys.exit(0)


run_with_input()
# run_naked()

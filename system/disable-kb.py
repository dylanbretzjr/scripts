#!/usr/bin/env python3
"""Temporarily disable the keyboard to allow for physical cleaning.

Uses pynput to suppress all keystrokes for a specified duration.

Requirements:
- pynput
"""

import sys
import time
from pynput import keyboard

def main():
    sleep_time = 10

    if len(sys.argv) > 1:
        try:
            sleep_time = int(sys.argv[1])
            if sleep_time <= 0:
                print('Error: Time must be greater than 0.')
                sys.exit(1)
        except ValueError:
            print('Error: Please provide a valid whole number for seconds.')
            print(f'Usage: {sys.argv[0]} [seconds]')
            sys.exit(1)

    print(f'Keyboard disabled for {sleep_time} seconds...')

    listener = keyboard.Listener(suppress=True)
    listener.start()

    try:
        for i in range(sleep_time, 0, -1):
            print(f'Seconds remaining: {i}')
            time.sleep(1)

    finally:
        listener.stop()
        listener.join()
        print('Keyboard enabled.')

if __name__ == '__main__':
    main()

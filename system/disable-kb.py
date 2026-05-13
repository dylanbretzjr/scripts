#!/usr/bin/env python3
"""Temporarily disable the keyboard to allow for physical cleaning.

This script uses pynput to suppress all keystrokes for a specified 
duration. The remaining time is printed to the terminal.

Requirements:
- pynput
"""

import time
from pynput import keyboard

SLEEP_TIME = 10

def main():
    print(f'Keyboard disabled for {SLEEP_TIME} seconds...')

    listener = keyboard.Listener(suppress=True)
    listener.start()

    try:
        for i in range(SLEEP_TIME, 0, -1):
            print(f'Seconds remaining: {i}')
            time.sleep(1)

    finally:
        listener.stop()
        listener.join()
        print('Keyboard enabled.')

if __name__ == "__main__":
    main()

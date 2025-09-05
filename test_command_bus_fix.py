#!/usr/bin/env python3
"""
Test script for CommandBus threading fix
"""

from cli.command_bus import get_command_bus
import time

def test_command_bus():
    bus = get_command_bus()
    result_received = False

    def callback(result):
        nonlocal result_received
        result_received = True
        print(f'Command result: success={result.success}, output={result.output[:50]}...')

    # Test with a simple command
    bus.execute_command('python', ['-c', 'print("Hello from CommandBus")'], callback=callback)

    # Wait for result
    timeout = 10
    start_time = time.time()
    while not result_received and (time.time() - start_time) < timeout:
        time.sleep(0.1)

    if result_received:
        print('CommandBus threading fix successful!')
        return True
    else:
        print('Command timed out')
        return False

if __name__ == '__main__':
    test_command_bus()

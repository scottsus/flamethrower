"""
The main test, automating some basic keystrokes.
TODO: Somehow the tests don't really render well, even if it works on manual ☹️
TODO: Add more robust testing
"""

import pyautogui
import subprocess
import time

cli_process = subprocess.Popen(["python3", "main.py"])

time.sleep(1)
pyautogui.write('ls -lah')
pyautogui.press('enter')

time.sleep(1)
pyautogui.write('What is the capital of Brazil?')
pyautogui.press('enter')

time.sleep(1.5)
pyautogui.write('Write Java code for the LeetCode TwoSum problem')
pyautogui.press('enter')

time.sleep(20)
pyautogui.write('Write Python code for the LeetCode TwoSum problem')
pyautogui.press('enter')

time.sleep(17)
pyautogui.write('exit')
pyautogui.press('enter')

cli_process.wait()
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

time.sleep(5)
pyautogui.write('Write Java code for the LeetCode TwoSum problem')
pyautogui.press('enter')

time.sleep(10)
pyautogui.write('Write Python code for the LeetCode TwoSum problem')
pyautogui.press('enter')

time.sleep(10)
pyautogui.write('exit')
pyautogui.press('enter')

cli_process.wait()

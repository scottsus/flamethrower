import time
import subprocess
import pyautogui as ag

def e2e() -> None:
    cli_process = subprocess.Popen(['poetry', 'run', 'flamethrower'])

    time.sleep(30)
    ag.write('ls -lah')
    ag.press('enter')

    time.sleep(2)
    ag.write('What is the capital of Brazil?')
    ag.press('enter')

    time.sleep(10)
    ag.write('exit')
    ag.press('enter')

    cli_process.wait()

if __name__ == "__main__":
    e2e()

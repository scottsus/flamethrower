import os
import sys

def ask(query: str):
    os.write(sys.stdout.fileno(), b'\033[G')
    os.write(sys.stdout.fileno(), b'\nAsking LLM...')
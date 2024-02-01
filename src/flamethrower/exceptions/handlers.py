from flamethrower.utils.colors import *

def get_quota_exceeded_message() -> str:
    return (
        f'You might have {STDIN_RED.decode("utf-8")}exceeded your current quota for OpenAI{STDIN_DEFAULT.decode("utf-8")}.\n\n'
        f'We are working hard to provide a {STDIN_ORANGE.decode("utf-8")}free, open source 🔥 flamethrower server{STDIN_DEFAULT.decode("utf-8")} for your usage.\n\n'
        f'Please check {STDIN_UNDERLINE.decode("utf-8")}https://github.com/scottsus/flamethrower{STDIN_DEFAULT.decode("utf-8")} for updates!'
    )

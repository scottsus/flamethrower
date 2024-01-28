import pexpect

def test_flamethrower():
    child = pexpect.spawn('flamethrower')
    child.timeout = 5

    # Send a command
    child.sendline("echo 'Hello World'")

    child.expect('Hello World')

    print('Success!')
    child.close()

test_flamethrower()

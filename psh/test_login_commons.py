from builtins import TimeoutError
import pexpect
import string

# Login actions functions
def assert_first_prompt(p):
	prompt = '\r\x1b[0J' + '(psh)% '
	got = p.read(len(prompt))
	if got == prompt:
		return 0
	else:
		return 1

def assert_psh(p):
	try:
		p.expect_exact('(psh)%')
	except pexpect.TIMEOUT:
		return 1
	else:
		return 0


def assert_login_prompt(p):
	try:
		p.expect_exact('Login:')
	except pexpect.TIMEOUT:
		return 1
	else:
		return 0
	


def assert_enter_login(p, login):
	p.sendline(login)
	try:
		p.expect_exact('Login: ')
		p.expect_exact(login)
		p.expect_exact('\n')
	except pexpect.TIMEOUT:
		return 1
	else:
		return 0




def assert_enter_password(p, password):
	p.sendline(password)
	try:
		p.expect('Password: ')
	except pexpect.TIMEOUT:
		return 1
	else:
		return 0


def assert_login_failed(p):
	global pexpect
	p.sendline('\n')
	try: 
		p.expect_exact('Login: ')
	except pexpect.TIMEOUT:
		return 1
	else:
		return 0



def assert_login_success(p, login_failed_msg):
	try: 
		p.expect_exact(login_failed_msg)
	except pexpect.TIMEOUT:
		return 1
	else:
		return 0


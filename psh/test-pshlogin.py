# Phoenix-RTOS test
#
# - Phoenix SHell tests
# - pshlogin aplet tests
#
# - only for ia32 as long as runfile does not work on other targets

import random
import string
import pexpect

from collections import namedtuple

User = namedtuple('User', ['login','password'])
root = User('root','1234')
defuser = User('defuser','1234')
users = (root, defuser)
notuser = User('NotValidUsername', 'NotValidPassword')

access_login_cmd = 'pshlogin'
psh_interactive_succes_msg = 'psh: already in interactive session!'

# Data manip functions
def get_random_string(length):
	 return ''.join(random.choice(string.ascii_lowercase) for i in range(length))

def assert_command(p, command):
	p.sendline(command)
	try:
		p.expect_exact(command)
		p.expect_exact('\n')
	except pexpect.TIMEOUT:
		return 1
	else:
		return 0


#Harness function
def harness(p):
	from test_login_commons import assert_first_prompt, assert_psh, assert_enter_login, assert_enter_password, assert_login_failed

	assert_first_prompt(p) #Ensure we are in psh

	#Access login prompt
	assert 0 == assert_command(p, access_login_cmd), f'Failed to access "{access_login_cmd}"'

	scenarios = [ \
		# Failed login scenarios:
		'0) no login passed', \
		'1) wrong login, existing password', \
		'2) login extended with random, matching password', \
		'3) good login, no password,', \
		'4) good login, wrong password,', \
		'5) existing login, matching password extended with random', \
		'6) exiting login prompt', \
		# Success login:
		'7) success login using `pshlogin` command from active psh', \
		'8) success login using `pshlogin` command with no active psh', \
		# Exiting active pshlogin session:
		'9) unable to exit pshlogin with ctrl+d', \
		'10) unable to exit pshlogin with exit' ]

	# 0)
	err = assert_enter_login(p, '')
	err += assert_login_failed(p)
	assert err == 0, f'For user: {u.login} failed scenario: {scenarios[0]}'

	# 1)
	for u in users:
		err += assert_enter_login(p, notuser.login)
		err += assert_enter_password(p, u.password)
		err += assert_login_failed(p)
		assert err == 0, f'For user: "{u.login}" failed scenario: "{scenarios[1]}"'


	# 2)
	for u in users:
		err = assert_enter_login(p, u.login + get_random_string(100))
		err += assert_enter_password(p, u.password)
		err += assert_login_failed(p)
		assert err == 0, f'For user: "{u.login}" failed scenario: {scenarios[2]}'

	# 3)
	for u in users:
		err = assert_enter_login(p, u.login)
		err += assert_enter_password(p, '')
		err += assert_login_failed(p)
		assert err == 0, f'For user: "{u.login}" failed scenario: {scenarios[3]}'

	# 4)
	for u in users:
		err = assert_enter_login(p, u.login)
		err += assert_enter_password(p, notuser.password)
		err += assert_login_failed(p)
		assert err == 0, f'For user: "{u.login}" failed scenario: {scenarios[4]}'

	# 5)
	for u in users:
		err = assert_enter_login(p, u.login)
		err += assert_enter_password(p, u.password + get_random_string(100))
		err += assert_login_failed(p)
		assert err == 0, f'For user: "{u.login}" failed scenario: {scenarios[5]}'

	# 6) 
	p.sendline('\004')
	err = assert_psh(p)
	assert err == 0,  f'Failed scenario: {scenarios[6]}'
	
	#Passed login scenarios:
	# 7)
	for u in users:
		err = assert_command(p, access_login_cmd)
		err += assert_enter_login(p,u.login)
		err += assert_enter_password(p, u.password)
		try:
			p.expect_exact(psh_interactive_succes_msg)
		except pexpect.TIMEOUT:
			err += 1

		assert err == 0, f'For user: {u.login} failed scenario: {scenarios[7]}'

	# 8)
	for u in users:
		err = assert_command(p, '/bin/pshlogin')
		err += assert_enter_login(p,u.login)
		err += assert_enter_password(p, u.password)
		err += assert_psh(p)
		assert err == 0, f'For user: {u.login} failed scenario: {scenarios[8]}'

	# 9)
	p.send('\004')
	err = assert_enter_login(p, root.login)
	err += assert_enter_password(p, root.password)
	err += assert_psh(p)
	assert err == 0,  f'failed scenario: {scenarios[9]}'

	# 10)
	err += assert_command(p,'exit')
	err = assert_enter_login(p, root.login)
	err += assert_enter_password(p, root.password)
	err += assert_psh(p)
	assert err == 0,  f'failed scenario: {scenarios[10]}'

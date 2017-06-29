#!/usr/bin/python

import time
import socket
import sys
import getopt
import threading
import thread
from TCPClient import TCPClient
from time import gmtime, strftime, localtime



class MyThread(threading.Thread):
	def __init__(self, serverip, serverport):
		threading.Thread.__init__(self)
		self.serverip = serverip
		self.serverport = serverport
		self.f = 0
		self.timer1 = None
		self.istimeout = 0
		self.totaltrycount = 0
		self.successcount = 0
		self.failcount = 0
		
	def stop(self):
		sys.stdout.write('thread for %r ' % self.serverip )
		sys.stdout.write('is shutdowning\r\n')
		if not self.f.closed:	
			self.f.write("======================================\r\n")
			self.f.write('[%r] stopped at %r\r\n' % (self.serverip, strftime("%d %b %Y %H:%M:%S", localtime())))
			self.f.write("Total try: %r\r\n" % self.totaltrycount)
			self.f.write("Success count: %r\r\n" % self.successcount)
			self.f.write("Fail count: %r\r\n" % self.failcount)
			self.f.write("======================================\r\n")
			self.f.close()
		self._Thread__stop()

	def myTimer(self):
		sys.stdout.write('timer1 timeout\r\n')
		self.istimeout = 1

		
	def run(self):
		SOCK_CLOSE_STATE = 1
		SOCK_OPENTRY_STATE = 2
		SOCK_OPEN_STATE = 3
		SOCK_CONNECTTRY_STATE = 4
		SOCK_CONNECT_STATE = 5

		idle_state = 1
		datasent_state = 2
		
		sys.stdout.write('thread for %r ' % self.serverip )
		sys.stdout.write('is starting\r\n')

		# TCPClient instance creation

		client = TCPClient(2, self.serverip, self.serverport)
		filename = self.serverip + '_log.txt'

		#print(filename)
		IsTimeout = 0

		self.f = open(filename, 'w+')


		while True:
			if client.state is SOCK_CLOSE_STATE:
				cur_state = client.state
				client.state = client.open()
				if client.state != cur_state:
					sys.stdout.write('client.state is %r\r\n' % client.state) 
				time.sleep(1)
			
			elif client.state is SOCK_OPEN_STATE:
				cur_state = client.state
				client.state = client.connect()
				if client.state != cur_state:
					sys.stdout.write('client.state is %r\r\n' % client.state) 
				time.sleep(1)
		
			
			elif client.state is SOCK_CONNECT_STATE:
				if client.working_state == idle_state:
					try:
						client.write(msg)
						client.working_state = datasent_state
						self.istimeout = 0
						self.totaltrycount += 1
				
						self.timer1 = threading.Timer(5.0, self.myTimer)				
						self.timer1.start()
					except Exception as e:
						sys.stdout.write('%r\r\n' % e)
				elif client.working_state == datasent_state:
					response = client.readline()
					if(response != ""):
						sys.stdout.write(response)
						sys.stdout.write('\n')
						sys.stdout.flush()
						self.timer1.cancel()
						self.istimeout = 0
				
						if (msg in response) :
							logstr = '[' + self.serverip + ']' + strftime("%d %b %Y %H:%M:%S", localtime()) + ': success\r\n'
							sys.stdout.write(logstr)
							self.successcount += 1
							time.sleep(10)
							client.working_state = idle_state
						else :
							logstr = '[' + self.serverip + ']' + strftime("%d %b %Y %H:%M:%S", localtime()) + ': fail by broken data\r\n'
							sys.stdout.write(logstr)
							self.failcount += 1
							self.f.write(logstr)
							self.f.write("\r\n")
							time.sleep(10)
							client.working_state = idle_state

					if self.istimeout is 1:
						self.timer1.cancel()
						self.istimeout = 0
						logstr = '[' + self.serverip + ']' + strftime("%d %b %Y %H:%M:%S", localtime()) + ': fail by timeout\r\n'
						sys.stdout.write(logstr)
						self.failcount += 1
						self.f.write(logstr)
						self.f.write("\r\n")
						time.sleep(5)
						client.working_state = idle_state
					
					response = ""



if __name__=='__main__':
		
	dst_ip = ''
	dst_port = 5000
	dst_num = 0

	msg = "Hello WIZ750SR\r"

	if len(sys.argv) <= 4:
		sys.stdout.write('Invalid syntax. Refer to below\r\n')
		sys.stdout.write('TempTest.py -s <WIZ107SR ip address> -c <server count>\r\n)')
		sys.exit(0)
	
	try:
		opts, args = getopt.getopt(sys.argv[1:], "h:s:c:")
	except getopt.GetoptError:
		sys.stdout.write('Invalid syntax. Refer to below\r\n')
		sys.stdout.write('TempTest.py -s <WIZ107SR ip address>  -c <server count>\r\n)')
		sys.exit(0)

	sys.stdout.write('%r\r\n' % opts)

	for opt, arg in opts:
		if opt == '-h':
			sys.stdout.write('Valid syntax\r\n')
			sys.stdout.write('TempTest.py -s <WIZ107SR ip address>  -c <server count>\r\n')
			sys.exit(0)
		elif opt in ("-s", "--sip") :
			dst_ip = arg
			sys.stdout.write('%r\r\n' % dst_ip)
		elif opt in ("-c", "--count") :
			dst_num = int(arg)
			sys.stdout.write('%r\r\n' % dst_num)


	lastnumindex = dst_ip.rfind('.')
	lastnum = int(dst_ip[lastnumindex+1:len(dst_ip)])

	threads = []

	try:	
		for i in range(dst_num):
			t = MyThread(dst_ip[:lastnumindex+1] + str(lastnum + i), dst_port)
			threads.append(t)
			
		for i in range(dst_num):
			threads[i].start()
	
		while True:
			pass
			
	except (KeyboardInterrupt, SystemExit):	
		for i in range(dst_num):
			threads[i].stop()


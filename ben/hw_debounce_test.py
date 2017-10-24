import os
import select
import time

def configure_ack_buttons( io_numbers=[20, 26]):
	BASEDIR = '/sys/class/gpio/'
	io={"ack_button":{"io_nb":io_numbers[0]},"nack_button":{"io_nb":io_numbers[1]}}
	for i in io :
		if os.path.isdir(BASEDIR + 'gpio' + str(io[i]["io_nb"])):
			print("gpio{} exists".format(io[i]["io_nb"]))
			io[i]["path"] = (BASEDIR + 'gpio' + str(io[i]["io_nb"]))
		else:
			retVal = open(BASEDIR + 'export', 'w')
			retVal.write(str(io[i]["io_nb"]))
			io[i]["path"] = (BASEDIR + 'gpio' + str(io[i]["io_nb"]))
			retVal.close()
		#ios are exported now they have to be configured
		ack_button_configure_gpio(io[i]["path"])
	return io

# define GPIO configuration functions
def set_gpio_direction( gpio, state):
	retVal = open(gpio + "/direction", 'w')
	retVal.write(state)
	retVal.close()

def set_gpio_trigger( gpio, edge):
	retVal = open(gpio + "/edge", 'w')
	retVal.write(edge)
	retVal.close

def set_gpio_active_low( gpio, string_flag):
	retVal = open(gpio + "/active_low", 'w')
	retVal.write(string_flag)
	retVal.close()

def set_gpio_value( gpio, value):
	retVal = open(gpio + "/value", 'w')
	retVal.write(str(value))
	retVal.close()

def get_gpio_value( gpio, value):
	retVal = open(gpio + "/value", 'r')
	result = retVal.read()
	retVal.close()
	return result

def check_gpio( gpio):
	path = PigState.BASEDIR + 'gpio' + str(gpio)
	if os.path.isdir(path):
		print("gpio{} exists".format(gpio))
	else:
		retVal = open(PigState.BASEDIR + 'export', 'w')
		retVal.write(str(gpio))
		retVal.close()
	return path
	
def ack_button_configure_gpio( gpio):
		#self.check_gpio(gpio)#demons to modify for uniformity
		set_gpio_direction(gpio, "in")
		set_gpio_active_low(gpio,"1") #if pulled up an active low comportment is more logic : button pressed = 1
		set_gpio_trigger(gpio,"both")

		
ack_buttons = configure_ack_buttons()


epoll = select.epoll()
registered_buttons = dict() 
registered_sock = dict()
fd = list()
fd.append((open(ack_buttons["ack_button"]["path"]+"/value",'r'),0))
fd.append((open(ack_buttons["nack_button"]["path"]+"/value",'r'),1))
for i in range(len(fd)):
	epoll.register(fd[i][0].fileno(),select.EPOLLET)  #EPOLLET seem to be better than EPOLLPRI
	fd[i][0].read()
	registered_buttons[fd[i][0].fileno()] = {'button':i, 'file_desc' : fd[i][0]}

	count=0
while True:
	events = epoll.poll(-1)

	for fileno, event in events:
		print("evts : {}".format(len(events)))
		if fileno in registered_buttons:
			registered_buttons[fileno]['file_desc'].read()
			registered_buttons[fileno]['file_desc'].seek(0,0)
			active_file = registered_buttons[fileno]
			count +=1
			t=time.time()
			print("event detected count = {} time = {} active_file{}".format(count, t, active_file))
			time.sleep(0.1) #may we avoid this using a 100nF cap with scmitt trigger ?

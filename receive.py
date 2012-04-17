import sys
import socket
import time
from Tkinter import *
from threading import Thread
import tooltip

SQUARESIZE = 3

def read_packet(guis,files,input_packet):
    if input_packet['name'] not in files:
        file_data = [None for x in range(input_packet['total'])]
        file_data[input_packet['block']] = input_packet['data']
        file_info = {\
            'total':input_packet['total'],
            'data':file_data,
            'block_size':input_packet['block_size'],
            }
            
        files[input_packet['name']] = file_info
        guis[input_packet['name']] = GuiReceiver(file_details=input_packet)
        display = Display(guis[input_packet['name']])
        display.start()
    else:
        files[input_packet['name']]['data'][input_packet['block']] = input_packet['data']
        guis[input_packet['name']].update(input_packet)

def construct(input_files):
    complete_list = []
    for name,info in input_files.iteritems():
        if None in info['data']:
                return None
        output = ''
        for fragment in info['data']:
            output+=fragment
        open('new'+name,'wb').write(output)
        print 'Creating: %s' % ('new'+name)
        complete_list.append(name)
    for filename in complete_list:
        del input_files[filename]



class Receiver(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.files = {}
        self.guis = {}
        self.init_comms()

    def init_comms(self):
        self.sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,True)
        self.sock.bind(('',44000))

    def run(self):
        while(1):
            data = eval(self.sock.recv(65536))
            print data
            read_packet(self.guis,self.files,data)            
            construct(self.files)

class Display(Thread):
    def __init__(self,gui_receiver):
        Thread.__init__(self)
        self._gui_receiver = gui_receiver

    def run(self):
        self._gui_receiver.mainloop()


class GuiReceiver(Frame):
    def __init__(self,master=None,file_details=None):
        Frame.__init__(self,master)
        self._file_details = file_details
        self.master.title(self._file_details['name'])
        self.received = [None for x in range(self._file_details['total'])]
        self.grid()
        self.buttons = []
        button_count = 0
        for row in xrange(SQUARESIZE):
            for col in xrange(SQUARESIZE):
                button = Button(self,text='%03d' % (button_count),anchor=W)
                button.grid(row=row,column=col)
                tooltip.createToolTip(button, '%d to %d' %(self.get_block_range(button_count)[0],self.get_block_range(button_count)[1]))
                self.buttons.append(button)
                button_count+=1
                if button_count > self._file_details['total']:
                    break
            if button_count > self._file_details['total']:
                    break

    def get_block_range(self,input_value):
        block_count = self._file_details['total']
        if block_count < SQUARESIZE**2:
            block_range_size = 1
        else:
            block_range_size = block_count/(SQUARESIZE**2)
            
        block_range_lower = input_value * block_range_size
        block_range_upper = block_range_lower + block_range_size
        return (block_range_lower,block_range_upper)

    def check_range_received(self,start,end):
        for i in xrange(start,end):
            if not self.received[i]:
                return False
        return True

    def update(self,input_packet):
        self.received[input_packet['block']] = True
        for i in xrange(len(self.buttons)):
            start,end = self.get_block_range(i)
            if self.check_range_received(start,end):
                self.buttons[i].configure(bg = "green")
            

if __name__ == "__main__":
    receiver = Receiver()
    receiver.start()



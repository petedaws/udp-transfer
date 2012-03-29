import sys
import socket
import time
from Tkinter import *
from threading import Thread
import tooltip

SQUARESIZE = 10

def read_packet(files,input_packet):
    if input_packet['name'] not in files:
        file_data = [None for x in range(input_packet['total'])]
        file_data[input_packet['block']] = input_packet['data']
        file_info = {\
            'total':input_packet['total'],
            'data':file_data,
            'block_size':input_packet['block_size'],
            }
            
        files[input_packet['name']] = file_info
    else:
        files[input_packet['name']]['data'][input_packet['block']] = input_packet['data']

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
        self.init_comms()

    def init_comms(self):
        self.sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,True)
        self.sock.bind(('',44000))

    def run(self):
        while(1):
            data = eval(self.sock.recv(65536))
            print data
            read_packet(self.files,data)            
            construct(self.files)

class GuiReceiver(Frame):
    def __init__(self,master=None):
        Frame.__init__(self,master)
        receiver = Receiver()
        receiver.start()
        self.master.title(".")	  
        self.grid()
        self.buttons = []
        self.handlers = []
        button_count = 0
        for row in xrange(SQUARESIZE):
            for col in xrange(SQUARESIZE):
                button = Button(self,text='%03d' % (button_count),anchor=W)
                button.grid(row=row,column=col)
                tooltip.createToolTip(button, '%d to %d' %(self.get_block_range(button_count)[0],self.get_block_range(button_count)[1]))
                def handler(event, self=self,button_number=button_count,blockrange=self.get_block_range(button_count)):
                        return None
                button.bind("<Button-1>", handler)
                self.buttons.append(button)
                self.handlers.append(handler)
                button_count+=1
                #if button_count > self.processed_file['total']:
                    #break
            #if button_count > self.processed_file['total']:
                    #break

    def get_block_range(self,input_value):
        block_count = self.processed_file['total']
        if block_count < SQUARESIZE**2:
            block_range_size = 1
        else:
            block_range_size = block_count/(SQUARESIZE**2)
            
        block_range_lower = input_value * block_range_size
        block_range_upper = block_range_lower + block_range_size - 1
        return (block_range_lower,block_range_upper)

    def update(self,processed_file):
        None
            

if __name__ == "__main__":
    guiReceiver = GuiReceiver()
    fileSender.mainloop()


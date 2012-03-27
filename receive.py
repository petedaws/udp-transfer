import sys
import socket
import time
from Tkinter import *
import asyncore

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
  
class DisplayBlocks(Frame,asyncore.dispatcher):
    def __init__(self,master=None):
        Frame.__init__(self,master)
        self.master.title("Receiver")
        self.grid()
        self.files = {}
        self.init_comms()

    def init_comms(self):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,True)
        self.bind(('',44000))
        self.socket_poll()

    def socket_poll(self):
        asyncore.poll(timeout=0.0)
        self.after(1, self.socket_poll) 

    def handle_read(self):
        print 'here'
        data = eval(self.recv(65536))
        read_packet(self.files,data)            
        construct(self.files)
        self.display(self.files)

    def handle_connect(self):
        pass

    def display(self,files):
        for name,info in files.iteritems():
            display_width = 100
            block_count = info['total']
            display_height = (block_count / display_width) + 1
            labels = []
            row_count = 0
            col_count = 0
            for i in xrange(block_count):
                if info['data'][i]:
                    label = Label(self,text='+',anchor=W)
                else:
                    label = Label(self,text='-',anchor=W)
                label.grid(row=row_count,column=col_count)
                labels.append(label)
                if col_count+1 > display_width:
                    col_count = 0
                    row_count+=1
                else:
                    col_count+=1
                 
            

if __name__ == "__main__":
    displayBlocks = DisplayBlocks()
    displayBlocks.mainloop()


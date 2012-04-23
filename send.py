import sys
import socket
import time
from Tkinter import *
from threading import Thread
import tooltip

PORT = 44000
BLOCKSIZE = 100
PAUSETIME = 0.05
SQUARESIZE = 3

def next_packet(processed_file):
    for i in xrange(len(processed_file['data'])):
        yield {\
                'block':i,
                'total_blocks':processed_file['total_blocks'],
                'name':processed_file['name'],
                'data':processed_file['data'][i],
                'block_size':processed_file['block_size'],
                }

def read_file(input_filename,block_size):
    input_file = open(input_filename,'rb').read()
    block_count = len(input_file) / block_size
    if len(input_file) % block_size != 0:
        block_count += 1
    file_data = [None for x in range(block_count)]
    send_status = [False for x in range(block_count)]
    for i in xrange(block_count):
        if i*block_size > len(input_file):
            file_data[i] = input_file[i*block_size:]
        else:
            file_data[i] = input_file[i*block_size:(i+1)*block_size]
    processed_file = {\
                    'name':input_filename,
                    'block_size':block_size,
                    'total_blocks':block_count,
                    'data':file_data,
                    'send_status':send_status
                    }
    return processed_file

class Observable(object):
    def __init__(self,observer,callback):
        self._observers = {}
        self._observers[observer] = callback
 
    def emit(self,args):
        for observer,callback in self._observers.iteritems():
            call = getattr(observer, callback)
            call(*args)

class Sender(Thread,Observable):
    def __init__(self,processed_file,sender_id,start,end,observer,callback):
        Observable.__init__(self,observer,callback)
        self._processed_file = processed_file
        self._start = start
        self._end = end
        self._sender_id = sender_id
        Thread.__init__(self)

    def run(self):
        sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        for i in xrange(self._start,self._end):
            packet = {\
                    'block':i,
                    'total_blocks':self._processed_file['total_blocks'],
                    'name':self._processed_file['name'],
                    'data':self._processed_file['data'][i],
                    'block_size':self._processed_file['block_size'],
                    }
            print 'Sending block %i of %i' % (packet['block'],packet['total_blocks'])
            sock.sendto(repr(packet),('localhost',44000))
            self._processed_file['send_status'][i] = True
            time.sleep(PAUSETIME)
        self.emit((self._sender_id,self._start,self._end))

def check_range_sent(processed_file,start,end):
    for i in xrange(start,end):
        if not processed_file['send_status'][i]:
            return False
    return True


class FileSender(Frame):
    def __init__(self,filename,master=None):
        Frame.__init__(self,master)
        self.master.title(".")	  
        self.grid()
        self.processed_file = read_file(filename,BLOCKSIZE)
        self.buttons = []
        self.handlers = []
        button_count = 0
        for row in xrange(SQUARESIZE):
            for col in xrange(SQUARESIZE):
                button = Button(self,text='%04d' % (button_count),anchor=W)
                button.grid(row=row,column=col)
                tooltip.createToolTip(button, '%d to %d' %(self.get_block_range(button_count)[0],self.get_block_range(button_count)[1]))
                def handler(event, self=self,button_number=button_count,blockrange=self.get_block_range(button_count)):
                        return self.send_blocks(button_number,blockrange[0],blockrange[1])
                button.bind("<Button-1>", handler)
                self.buttons.append(button)
                self.handlers.append(handler)
                button_count+=1
                if button_count > self.processed_file['total_blocks']:
                    break
            if button_count > self.processed_file['total_blocks']:
                    break
        #self.send_all()

    def send_all(self):
        for handler in self.handlers:
            handler(None)

    def send_blocks(self,button_number,start,end):
        Sender(self.processed_file,button_number,start,end,self,"update_button").start()
 
    def update_button(self,button_number,start,end):
        if check_range_sent(self.processed_file,start,end):
            self.buttons[button_number].configure(bg = "green")

    def get_block_range(self,input_value):
        block_count = self.processed_file['total_blocks']
        if block_count < SQUARESIZE**2:
            block_range_size = 1
        else:
            block_range_size = block_count/(SQUARESIZE**2)
            
        block_range_lower = input_value * block_range_size
        block_range_upper = block_range_lower + block_range_size
        if block_range_upper + (block_range_size*2) >= block_count:
            block_range_upper = block_count
        return (block_range_lower,block_range_upper)


if __name__ == "__main__":
    file_name = 'sample.jpg'#sys.argv[1]
    fileSender = FileSender(filename=file_name)
    fileSender.mainloop()

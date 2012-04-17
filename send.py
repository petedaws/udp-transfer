import sys
import socket
import time
from Tkinter import *
import tooltip

BLOCKSIZE = 50
PAUSETIME = 0.05
SQUARESIZE = 3

def next_packet(processed_file):
    for i in xrange(len(processed_file['data'])):
        yield {\
                'block':i,
                'total':processed_file['total'],
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
                    'total':block_count,
                    'data':file_data,
                    'send_status':send_status
                    }
    return processed_file

def send(processed_file):
    sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    for packet in next_packet(processed_file):
        print 'Sending block %i of %i' % (packet['block'],packet['total'])
        sock.sendto(repr(packet),('localhost',44000))
        processed_file['send_status'][packet['block']] = True
        time.sleep(PAUSETIME)

def send_block_range(processed_file,start,end):
    sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    for i in xrange(start,end):
        packet = {\
                'block':i,
                'total':processed_file['total'],
                'name':processed_file['name'],
                'data':processed_file['data'][i],
                'block_size':processed_file['block_size'],
                }
        print 'Sending block %i of %i' % (packet['block'],packet['total'])
        sock.sendto(repr(packet),('localhost',44000))
        processed_file['send_status'][i] = True
        time.sleep(PAUSETIME)

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
                button = Button(self,text='%03d' % (button_count),anchor=W)
                button.grid(row=row,column=col)
                tooltip.createToolTip(button, '%d to %d' %(self.get_block_range(button_count)[0],self.get_block_range(button_count)[1]))
                def handler(event, self=self,button_number=button_count,blockrange=self.get_block_range(button_count)):
                        return self.send_blocks(button_number,blockrange[0],blockrange[1])
                button.bind("<Button-1>", handler)
                self.buttons.append(button)
                self.handlers.append(handler)
                button_count+=1
                if button_count > self.processed_file['total']:
                    break
            if button_count > self.processed_file['total']:
                    break
        #self.send_all()

    def send_all(self):
        for handler in self.handlers:
            handler(None)

    def send_blocks(self,button_number,start,end):
        send_block_range(self.processed_file,start,end)
        if check_range_sent(self.processed_file,start,end):
            self.buttons[button_number].configure(bg = "green")
        

    def get_block_range(self,input_value):
        block_count = self.processed_file['total']
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

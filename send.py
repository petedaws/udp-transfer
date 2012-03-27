import sys
import socket
import time
from Tkinter import *
import tooltip

BLOCKSIZE = 10
PAUSETIME = 0.5
SQUARESIZE = 10

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
                    }
    return processed_file

def send(processed_file):
    sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    for packet in next_packet(processed_file):
        print 'Sending block %i of %i' % (packet['block'],packet['total'])
        sock.sendto(repr(packet),('localhost',44000))
        time.sleep(PAUSETIME)


class FileSender(Frame):
    def __init__(self,filename,master=None):
        Frame.__init__(self,master)
        self.master.title(".")	  
        self.grid()
        self.processed_file = read_file(filename,BLOCKSIZE)
        buttons = []
        button_count = 0
        for row in xrange(SQUARESIZE):
            for col in xrange(SQUARESIZE):
                button = Button(self,text='%03d' % (button_count),anchor=W)
                button.grid(row=row,column=col)
                tooltip.createToolTip(button, '%d to %d' %(self.get_block_range(button_count)[0],self.get_block_range(button_count)[1]))
                def handler(event, self=self,blockrange=self.get_block_range(button_count)):
                        return self.send_blocks(blockrange[0],blockrange[1])
                button.bind("<Button-1>", handler)
                
                buttons.append(button)
                button_count+=1
                if button_count > self.processed_file['total']:
                    break
            if button_count > self.processed_file['total']:
                    break

    def send_blocks(self,start,end):
        print '%d to %d' % (start,end)

    def get_block_range(self,input_value):
        block_count = self.processed_file['total']
        if block_count < SQUARESIZE**2:
            block_range_size = 1
        else:
            block_range_size = block_count/(SQUARESIZE**2)
            
        block_range_lower = input_value * block_range_size
        block_range_upper = block_range_lower + block_range_size - 1
        return (block_range_lower,block_range_upper)


if __name__ == "__main__":
    file_name = 'sample.jpg'#sys.argv[1]
    fileSender = FileSender(filename=file_name)
    fileSender.mainloop()
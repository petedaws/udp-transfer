import sys
import socket
import time

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
        open(name,'wb').write(output)
        print 'Creating: %s' % (name)
        complete_list.append(name)
    for filename in complete_list:
        del input_files[filename]

def receive():
    sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    sock.bind(('',44000))
    files = {}
    while True:
        try:
            data = eval(sock.recv(65536))
            read_packet(files,data)            
            construct(files)
        except Exception as inst:
            print inst
            

def send():
    sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    block_size = 1000
    pause_time = 0.02
    filename = 'Fig126_12000_Inun_west_2000.pdf'
    input_file = read_file(filename,block_size)
    for packet in next_packet(input_file):
        print 'Sending block %i of %i' % (packet['block'],packet['total'])
        sock.sendto(repr(packet),('localhost',44000))
        time.sleep(pause_time)

send()

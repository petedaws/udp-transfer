import sys
import socket

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

def construct(input_files,output_filename):
    for input_file in input_files:
        if None in input_file['data']:
                print 'file incomplete'
                return None
        output = ''
        for fragment in input_file['data']:
            output+=fragment
        open(input_file['name'],'wb').write(output)
        print 'Creating: %s' % (input_file['name'])

def receive():
    sock = socket.socet(socket.AF_INET,socket.DGRAM)
    sock.bind(('',44000))
    try:
        files = {}
        while True:
            data = eval(sock.recv(65536))
            read_packet(files,data)            
            construct(files)
    except:
        print 'error'

def send():
    sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    block_size = 1000
    input_file = read_file('sample.jpg',block_size)
    for packet in next_packet(input_file):
        sock.sendto(repr(packet),('localhost',44000))

    

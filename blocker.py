import sys

BLOCK_SIZE = 1000


def blockerize(input_filename):
    input_file = open(input_filename,'rb').read()
    blocks = []
    block_count = len(input_file) / BLOCK_SIZE
    if len(input_file) % BLOCK_SIZE != 0:
        block_count += 1
    for i in xrange(block_count):
        if i*BLOCK_SIZE > len(input_file):
            block = input_file[i*BLOCK_SIZE:]
            i+=1
        else:
            block = input_file[i*BLOCK_SIZE:(i+1)*BLOCK_SIZE]
        blocks.append({\
                    'block':i,
                    'total':block_count,
                    'name':input_filename,
                    'data':block,
                    'block_size':BLOCK_SIZE,
                    })
    return blocks


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
                                            

def construct(input_list,output_filename):
    if None in input_list['data']:
            print 'file incomplete'
            return None
    output = ''
    for fragment in input_list['data']:
        output+=fragment
    open(output_filename,'wb').write(output)

if __name__ == "__main__":
    files = {}
    blocked = blockerize('sample.jpg')
    for block in blocked:
        read_packet(files,block)

    construct(files['sample.jpg'],'sample_reconstructed.jpg')
    

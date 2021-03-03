import requests


host = input('NIO INSTANCE (http://localhost:8181): ')
username = input('USERNAME (Admin): ')
password = input('PASSWORD (Admin): ')

if not host:
    host = 'http://localhost:8181'
if not username:
    username = 'Admin'
if not password:
    password = 'Admin'
auth = (username, password)

def GET(endpoint):
    response = requests.get('{}/{}'.format(host, endpoint), auth=auth)
    return response.json()

def DEL_BLOCK(id):
    response = requests.delete('{}/blocks/{}'.format(host, id), auth=auth)
    response.raise_for_status()

# get blocks used in all service configs
blocks = []
for id, config in GET('services').items():
    if id == '__instance_metadata__':
        continue
    for map in config['mappings']:
        blocks.append(map['mapping'])
    for block in config['execution']:
        blocks.append(block['id'])

# get all block configs, and check against blocks used in service configs
unused_blocks = []
for id, config in GET('blocks').items():
    if id not in blocks:
        if not unused_blocks:
            # first block found, only detected for printing
            print('FOUND BLOCKS:')
        unused_blocks.append(id)
        print('\t{} ({})'.format(config['name'], config['type']))

if not unused_blocks:
    print('No unused blocks found.')
    exit()

try:
    input('[ENTER] to remove {} unused blocks.\n[CTRL]+[C] to exit'.format(
        len(unused_blocks)))
except KeyboardInterrupt:
    print()
    exit()

print('Removing {} unused blocks...'.format(len(unused_blocks)))
for block in unused_blocks:
    DEL_BLOCK(block)

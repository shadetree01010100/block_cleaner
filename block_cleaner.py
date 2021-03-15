import getpass
import requests


# get user input
try:
    host = input('NIO INSTANCE (http://localhost:8181): ')
    username = input('USERNAME (Admin): ')
    password = getpass.getpass('PASSWORD (Admin): ')
except KeyboardInterrupt:
    # catch and feed a newline for tidy exit
    print()
    exit()

# default values
if not host:
    host = 'http://localhost:8181'
if not username:
    username = 'Admin'
if not password:
    password = 'Admin'
# basic auth for http requests
auth = (username, password)

def _make_request(method, endpoint):
    try:
        response = method('{}/{}'.format(host, endpoint), auth=auth)
        response.raise_for_status()
    except requests.exceptions.ConnectionError:
        print('Failed to connect to \"{}\"'.format(host))
        exit()
    except requests.exceptions.HTTPError as e:
        print(e.args[-1])
        exit()
    return response

def GET_BLOCKS():
    return _make_request(requests.get, 'blocks').json()

def GET_SERVICES():
    return _make_request(requests.get, 'services').json()

def DELETE_BLOCK(id):
    _make_request(requests.delete, 'blocks/{}'.format(id))

print('working...', end='\r')

# get blocks used in all service configs
blocks = []
for id, config in GET_SERVICES().items():
    if id == '__instance_metadata__':
        # not a service, ignore it
        continue
    for map in config['mappings']:
        blocks.append(map['mapping'])
    for block in config['execution']:
        blocks.append(block['id'])

# get all block configs, and check against blocks used in service configs
unused_blocks = []
for id, config in GET_BLOCKS().items():
    if id not in blocks:
        # this block instance is not referenced in any service,
        if not unused_blocks:
            # this is the first discovered block, so print a table header
            print('Found unused blocks:')
        unused_blocks.append(id)
        print('\t{} ({})'.format(config['name'], config['type']))

# exit if there's nothing to do
if not unused_blocks:
    print('No unused blocks found.')
    exit()

# prompt for user input
try:
    # use getpasss simply to hide keyboard input while waiting at prompt
    getpass.getpass(
        '[ENTER] to remove {} unused block{},\n'
        '[CTRL]+[C] to exit'.format(
            len(unused_blocks),
            's' if len(unused_blocks) > 1 else ''))
except KeyboardInterrupt:
    # catch and feed a newline for tidy exit
    print()
    exit()

print('working...', end='\r')
for id in unused_blocks:
    DELETE_BLOCK(id)
print('Removed {} unused block{}.'.format(
    len(unused_blocks),
    's' if len(unused_blocks) > 1 else ''))

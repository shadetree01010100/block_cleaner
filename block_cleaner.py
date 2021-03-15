import getpass
import requests


# get user input
host = input('NIO INSTANCE (http://localhost:8181): ')
username = input('USERNAME (Admin): ')
password = getpass.getpass('PASSWORD (Admin): ')

# default values
if not host:
    host = 'http://localhost:8181'
if not username:
    username = 'Admin'
if not password:
    password = 'Admin'
# basic auth for http requests
auth = (username, password)

def GET(endpoint):
    try:
        response = requests.get('{}/{}'.format(host, endpoint), auth=auth)
        response.raise_for_status()
    except requests.exceptions.ConnectionError:
        print('Failed to connect to \"{}\"'.format(host))
        exit()
    except requests.exceptions.HTTPError as e:
        print(e.args[-1])
        exit()
    return response.json()

def DEL_BLOCK(id):
    try:
        response = requests.delete('{}/blocks/{}'.format(host, id), auth=auth)
        response.raise_for_status()
    except requests.exceptions.ConnectionError:
        print('Failed to connect to \"{}\"'.format(host))
        exit()
    except requests.exceptions.HTTPError as e:
        print(e.args[-1])
        exit()

print('working...', end='\r')

# get blocks used in all service configs
blocks = []
for id, config in GET('services').items():
    if id == '__instance_metadata__':
        # not a service, ignore it
        continue
    for map in config['mappings']:
        blocks.append(map['mapping'])
    for block in config['execution']:
        blocks.append(block['id'])

# get all block configs, and check against blocks used in service configs
unused_blocks = []
for id, config in GET('blocks').items():
    if id not in blocks:
        # this block instance is not referenced in any service,
        if not unused_blocks:
            # this is the first discovered block, so print a table header
            print('FOUND BLOCKS:')
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
        '[ENTER] to remove {} unused blocks,\n'
        '[CTRL]+[C] to exit'.format(len(unused_blocks)))
except KeyboardInterrupt:
    # catch and feed a newline for tidy exit
    print()
    exit()

print('working...', end='\r')
for block in unused_blocks:
    DEL_BLOCK(block)
print('Removed {} unused blocks...'.format(len(unused_blocks)))

import asyncio
import re
import subprocess
import os
loop = asyncio.get_event_loop()
import argparse

async def main(command):
    reader, writer = await asyncio.open_connection('192.168.0.199', 56013)
    with open(os.path.join('.git', 'config'), 'r') as f:
        origin = re.findall('url = [^\n]+', f.read())[0].split(' ')[-1]
    project = origin.split('/')[-1][:-4]
    user = subprocess.check_output('git config --global user.name', shell=True).decode().split('\n')[0]
    # if command == 'checkout':
    b = [_str.strip(' *') for _str in subprocess.check_output("git branch", shell=True).decode().split('\n')
         if _str.startswith('*')]
    data = b[0]
    print('::'.join([user, project, command, data, origin]).encode())
    writer.write('::'.join([user, project, command, data, origin]).encode())
    await writer.drain()
    writer.close()


parser = argparse.ArgumentParser(description='DevOps')
parser.add_argument('--command', dest='command', type=str)
# parser.add_argument('--data', dest='data', type=str)
args = parser.parse_args()
loop.run_until_complete(asyncio.ensure_future(main(args.command)))
print('complete', args.command)

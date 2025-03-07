from panda3d.core import *
from direct.showbase import PythonUtil
import traceback
import builtins
import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--base-channel', help='The base channel that the server may use.')
parser.add_argument('--max-channels', help='The number of channels the server may use.')
parser.add_argument('--stateserver', help="The control channel of this UD's designated State Server.")
parser.add_argument('--astron-ip', help="The IP address of the Astron Message Director to connect to.")
parser.add_argument('--eventlogger-ip', help="The IP address of the Astron Event Logger to log to.")
parser.add_argument('config', nargs='*', default=['config/general.prc', 'config/server.prc'], help="PRC file(s) to load.")
args = parser.parse_args()

for prc in args.config:
    if not os.path.exists(prc):
        print(':ServiceStart(warning): Failed to locate prc %s!' % prc)
        continue
    loadPrcFile(prc)
    print("loaded: " + prc)

if os.path.exists('config/general.prc'):
    loadPrcFile('config/general.prc')

localconfig = ''
if args.base_channel: localconfig += 'air-base-channel %s\n' % args.base_channel
if args.max_channels: localconfig += 'air-channel-allocation %s\n' % args.max_channels
if args.stateserver: localconfig += 'air-stateserver %s\n' % args.stateserver
if args.astron_ip: localconfig += 'air-connect %s\n' % args.astron_ip
if args.eventlogger_ip: localconfig += 'eventlog-host %s\n' % args.eventlogger_ip
loadPrcFileData('Command-line', localconfig)

class game:
    name = 'uberDog'
    process = 'server'

builtins.game = game

from otp.ai.AIBaseGlobal import *

from pirates.uberdog.PiratesUberRepository import PiratesUberRepository
simbase.air = PiratesUberRepository(config.GetInt('air-base-channel', 400000000),
    config.GetInt('air-stateserver', 10000))

host = config.GetString('air-connect', '127.0.0.1')
port = 7199
if ':' in host:
    host, port = host.split(':', 1)
    port = int(port)

simbase.air.connect(host, port)

try:
    simbase.run()
except SystemExit:
    raise
except Exception:
    info = traceback.format_exc()
    simbase.air.writeServerEvent('uberdog-exception', avId=simbase.air.getAvatarIdFromSender(), accId=simbase.air.getAccountIdFromSender(), info=info)
    raise

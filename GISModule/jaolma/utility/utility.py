_utility_verbose_options_status=True
_utility_verbose_options_error=True
_utility_verbose_options_timestamp=True
_utility_verbose_options_tag_whitelist=[]
_utility_verbose_options_tag_blacklist=[]

import datetime
import pynmea2
import os
import jaolma.gis.wfs as wfs
from colorsys import hsv_to_rgb

from colormap import hex2rgb, rgb2hls, hls2rgb, rgb2hex

def load_route(filename):
    if not os.path.exists(filename):
        return None
    with open(filename, 'r') as f:
        nmea_file = f.readlines()

    fts = []
    fixes = []
    for line in nmea_file[1:]:
        line = ','.join(line.strip().split(',')[2:])
        nmea_msg = pynmea2.parse(line)
        if nmea_msg.sentence_type != 'GGA':
            continue
        ft = wfs.Feature((nmea_msg.latitude, nmea_msg.longitude), 'EPSG:4326')
        fts.append(ft)
        fixes.append(nmea_msg.gps_qual)

    collection = wfs.Collection('','',fts,'EPSG:4326')
    collection.to_srs('EPSG:25832')
    route = [[ft.x(), ft.y(), fix] for ft, fix in zip(collection.features, fixes)]
    return route

# status, error, tag_whitelist, tag_blacklist, timestamp
def set_verbose(**args):
    global _utility_verbose_options_status, _utility_verbose_options_error, _utility_verbose_options_timestamp, _utility_verbose_options_tag_whitelist, _utility_verbose_options_tag_blacklist
    for key, val in zip(args.keys(), args.values()):
        if key == 'status': _utility_verbose_options_status = val
        if key == 'error': _utility_verbose_options_error = val
        if key == 'tag_whitelist': _utility_verbose_options_tag_whitelist = val
        if key == 'tag_blacklist': _utility_verbose_options_tag_blacklist = val
        if key == 'timestamp': _utility_verbose_options_timestamp = val

def _get_timestamp(b):
    if b:
        return datetime.datetime.now().strftime('%H:%M:%S')
    return ''

def _print(message_type, message_content, message_tag):
    if (len(_utility_verbose_options_tag_whitelist) > 0 and not message_tag in _utility_verbose_options_tag_whitelist) or message_tag in _utility_verbose_options_tag_blacklist:
        return

    message_tag = str(message_tag)

    timestamp = datetime.datetime.now().strftime('%H:%M:%S')

    to_print = f'[{message_type.upper()}] ({message_tag}): {message_content}'
    if _utility_verbose_options_timestamp:
        to_print = f'{timestamp} [{message_type.upper()}] ({message_tag}): {message_content}'
    print(to_print)

    with open('log.txt', 'a+') as f:
        f.write(';'.join([timestamp, message_type, message_tag, message_content]) + '\n')

def prints(s, tag=None):
    if not _utility_verbose_options_status:
        return

    _print('status', s, tag)

def printe(s, tag=None):
    if not _utility_verbose_options_error:
        return

    _print('error', s, tag)

def shortstring(s, maxlen):
    if len(s) > maxlen:
        return s[:maxlen] + '...'
    return s

def uniform_colors(n):
    return ['#' + "".join("%02X" % round(i*255) for i in hsv_to_rgb(j/n, 1, 1)) for j in range(n)]

def transpose(l):
    return [list(row) for row in zip(*l)]

with open('log.txt', 'a+') as f:
    f.write('\n---\n\n')

def linspace(min, max, N):
    return [n/(N - 1) * (max - min) + min for n in range(N)]

class Color:
    def __init__(self, color):
        r, g, b = hex2rgb(color)
        h, l, s = rgb2hls(r/255, g/255, b/255)

        self.rgb = (r, g, b)
        self.hls = (h, l, s)

    def get_l(self):
        h, l, s = self.hls
        return l

    def with_l(self, l):
        h, _, s = self.hls
        r, g, b = hls2rgb(h, l, s)
        return rgb2hex(int(r*255), int(g*255), int(b*255))

    def __mul__(self, val):
        return self.with_l(max(min(self.get_l() * val, 1), 0))

def flatten(dictionary):
    return [b for a in dictionary for b in dictionary[a]]

def find_in_string(s, before, after, dtype=None):
    if before != '' and before != None:
        if not before in s:
            raise Exception(f'Argument before "{before}" could not be found in string "{s}".')
        
        s = s.split(before)[1]

    if after != '' and after != None:
        if not after in s:
            raise Exception(f'Argument after ("{after}") could not be found in string "{s}".')

        s = s.split(after)[0]

    if dtype != None:
        s = dtype(s)

    return s

s = "32.471 visninger•Streamede live for 7 timer siden"
before = 'live for '
after = ' timer siden'
dtype = None

val = find_in_string(s, before, after=None, dtype=dtype)

print(val)
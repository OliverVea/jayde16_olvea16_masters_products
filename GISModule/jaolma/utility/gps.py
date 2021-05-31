from jaolma.utility.utility import prints, printe
from jaolma.gis.wfs import Feature

import socket
import json
import time

class GPSConnection:
    def __init__(self, address: str, port: int, encoding: str='utf-8'):
        self.address = address
        self.port = port
        self.encoding = encoding

        self.socket = socket.socket()

    def get_coords(self, n_tries: int = 10, n_bytes: int = 4096, timeout: float = None) -> Feature:
        if timeout != None:
            self.socket.settimeout(timeout)
        
        try:
            self.socket.connect((self.address, self.port))
        except:
            printe(f'Unable to establish connection to \'{self.address}:{self.port}\'.')
            return None

        i = 0
        received_data = False
        while (not received_data) and (i < n_tries):
            try:
                bts = self.socket.recv(n_bytes)
                bts = bts.decode(self.encoding)
                bts = bts[2:]
                obj = json.loads(bts)
                received_data = True
            except:
                printe(f'Unable to aquire GPS coordinates from \'{self.address}:{self.port}\'.')
                if i < n_tries - 1:
                    prints('Retrying in 1 second.')
                time.sleep(1)
            i += 1

        self.socket.close()

        try:
            lat = obj['lat']
            lon = obj['lon']

            del obj['lat']
            del obj['lon']

            return Feature('GPS', geometry=(lat, lon), srs='EPSG:4326', attributes=obj)
            
        except:
            printe('Response JSON not understood.')

        return None 

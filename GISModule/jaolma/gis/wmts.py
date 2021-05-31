print(__name__)

from jaolma.gis.wfs import WebService, WFS, Feature
from jaolma.utility.utility import prints


from PIL import Image
from math import ceil

class WMTS(WebService):
    def __init__(self, use_login, url: str, username: str, password: str, layer: str, tile_matrix_set: str, format: str='image/jpeg', version: str='1.0.0'):
        super(WMTS, self).__init__(url, username, password, version)
        self.pixel_size = 0.00028
        self.layer = layer
        self.format = format
        self.tile_matrix_set = tile_matrix_set

        self.cache = {}

        self._get_capabilities(use_login)


    def _to_px(self, scale_denominator, rw=None, m=None):
        if rw != None:
            return rw / (self.pixel_size * scale_denominator)
        return m / self.pixel_size

    def _to_rw(self, scale_denominator, px=None, m=None):
        if px != None:
            return px * self.pixel_size * scale_denominator
        return m * scale_denominator

    def _to_map(self, scale_denominator, px=None, rw=None):
        if px != None:
            return px * self.pixel_size
        return rw / scale_denominator

    def _get_capabilities(self, use_login):
        url = self._make_url(service='wmts', use_login=use_login, request='GetCapabilities')
        response = self._query_url(url)

        tms = response.Contents.TileMatrixSet

        t = './/{http://www.opengis.net/ows/1.1}SupportedCRS'
        self.srs = str(tms.find(t).text)

        def to_obj(tile_matrix):
            tlc = tile_matrix.TopLeftCorner.text.split(' ')

            tm = {
                'matrix_height':        int(tile_matrix.MatrixHeight),
                'matrix_width':         int(tile_matrix.MatrixWidth),
                'scale_denominator':    float(tile_matrix.ScaleDenominator),
                'tile_height':          int(tile_matrix.TileHeight),
                'tile_width':           int(tile_matrix.TileWidth),
                'top_left_x':           float(tlc[0]),
                'top_left_y':           float(tlc[1]),
            }

            
            tm['map_width'] = self._to_rw(tm['scale_denominator'], px=tm['tile_width'] * tm['matrix_width'])
            tm['map_height'] = self._to_rw(tm['scale_denominator'], px=tm['tile_height'] * tm['matrix_height'])

            return tm

        self.tile_matrices = [to_obj(c) for c in tms.iterchildren() if self._simplify_tag(c.tag) == 'TileMatrix']

    def _get_tile(self, style, tile_matrix, row, col):
        key = (style, tile_matrix, row, col)

        if key in self.cache:
            return self.cache[key]

        url = self._make_url(service='wmts', request='GetTile', layer=self.layer, style=style, format=self.format, tilematrixset=self.tile_matrix_set, tilematrix=tile_matrix, tileRow=row, tileCol=col)
        response = self._query_url(url, response_type='jpeg')

        self.cache[key] = response

        return response

    def _stitch_images(self, images, rows, cols, image_width, image_height):
        width = len(images) * image_width
        height = len(images[0]) * image_height
        parent_img = Image.new('RGB', (width, height))

        for col, imgs in enumerate(images):
            for row, im in enumerate(imgs):
                parent_img.paste(im, (col * image_width, row * image_height))

        return parent_img

    def dpm(self, tile_matrix):
        return 1 / (0.00028 * self.tile_matrices[tile_matrix]['scale_denominator'])

    def get_map(self, style: str, tile_matrix: int, center: Feature, screen_width: int = 1920, screen_height: int = 1080):
        tm = self.tile_matrices[tile_matrix]

        cols = ceil((screen_width/2) / tm['tile_width'])
        rows = ceil((screen_height/2) / tm['tile_height'])

        x = center.x(srs=self.srs)
        center_x = tm['matrix_width'] * (x - tm['top_left_x']) / tm['map_width']
        center_col = int(center_x)

        y = center.y(srs=self.srs)
        center_y = tm['matrix_height'] * (tm['top_left_y'] - y) / tm['map_height']
        center_row = int(center_y)
        
        prints(f'Gathering map of size ({cols}, {rows}) with resolution ({screen_width}, {screen_height}). Please wait.')

        tiles = []
        for col in range(center_col - cols, cols + center_col + 1):
            if col >= 0:
                tile_col = []        
                for row in range(center_row - rows, rows + center_row + 1):
                    if row >= 0:
                        tile = self._get_tile(style, tile_matrix, row=row, col=col)
                        tile_col.append(tile)
                tiles.append(tile_col)

        m = self._stitch_images(tiles, rows*2+1, cols*2+1, tm['tile_width'], tm['tile_height'])

        tx = (cols + center_x - center_col) * tm['tile_width']
        ty = (rows + center_y - center_row) * tm['tile_height']

        crop = (
            int(tx-screen_width/2), 
            int(ty-screen_height/2), 
            int(tx+screen_width/2), 
            int(ty+screen_height/2))

        m = m.crop(crop)

        return m
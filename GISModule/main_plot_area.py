from jaolma.properties import Properties
from jaolma.utility.utility import transpose, Color, printe, prints
from jaolma.gis.wfs import Feature
from jaolma.gis.wmts import WMTS
from jaolma.gui.properties_box import PropertiesBox
from jaolma.gui import simple_dropdown

from PIL import Image, ImageDraw

import PySimpleGUI as sg
import pandas as pd

import os

class PlotImage:
    class Layer:
        def __init__(self, features: list, typename: str, size: tuple, cache: bool = True, r: float = 3, fill = None, outline = None, text_color = None):
            self.cache = cache
            self.typename = typename

            self.layer = Image.new('RGBA', size)
            draw = ImageDraw.Draw(self.layer)

            self.is_gnss = typename in [typename for typename in Properties.feature_properties if Properties.feature_properties[typename]['origin'] == 'gnss']

            if fill == None: 
                fill = Properties.feature_properties[typename]['color']

            if outline == None:
                outline = Color(fill) * 0.75

            if text_color == None:
                text_color = '#FFFFFF'
                

            for ft in features:
                x, y = ft['plot_x'], ft['plot_y']
                xy = [(x - r, y - r), (x + r, y + r)]

                draw.ellipse(xy=xy, fill=fill, outline=outline)

                if self.is_gnss:
                    draw.text(xy=[x + r, y + r], text=f'{ft["id"]}', fill=text_color)
                    
                else:
                    draw.text(xy=[x + r, y + r], text=f'{ft["id"]}', fill=text_color)

            if not cache:
                self.layer.save(f'files/gui/layers/{typename}.png')
                self.layer.close()

        def __enter__(self):
            if not self.cache:
                self.layer = Image.open(f'files/gui/layers/{self.typename}.png')
            return self.layer

        def __exit__(self, type, value, traceback):
            if not self.cache:
                self.layer.close()

    def __init__(self, size: tuple, area: str, data: dict, tile_matrix: int = 13, background_path: str = 'files/gui/background.png', image_path: str = 'files/gui/image.png', r: float = 3, cache: bool = True):
        self.wmts = WMTS(
            use_login=True,
            url='https://services.datafordeler.dk/GeoDanmarkOrto/orto_foraar_wmts/1.0.0/WMTS?',
            username='VCSWRCSUKZ',
            password='hrN9aTirUg5c!np',
            layer='orto_foraar_wmts',
            tile_matrix_set='KortforsyningTilingDK')

        self.size = (size[0] * self.wmts.dpm(tile_matrix) + 1, size[1] * self.wmts.dpm(tile_matrix) + 1)
        self.size = tuple(int(s) for s in self.size)
        self.area = area

        self.c = Properties.areas[area]
        self.c.to_srs(Properties.default_srs)

        self.tile_matrix = tile_matrix

        self.backgound_path = background_path
        self.image_path = image_path

        self.background = self.wmts.get_map(style='default', tile_matrix=tile_matrix, center=self.c, screen_width=self.size[0], screen_height=self.size[1])
        self.background.save(self.backgound_path)

        self.dpm = self.wmts.dpm(self.tile_matrix)

        self.r = r
        self.cache = cache

        self.data = {}
        self.layers = {}

        for source in data:
            types = data[source]
            self.data[source] = {}
            for typename in types:
                features = types[typename]

                for feature in features:
                    feature.to_srs(Properties.default_srs)

                features = [feature - self.c for feature in features]

                for feature in features:
                    temp_x = feature.x()
                    feature['plot_x'] = feature.x() * self.dpm + self.size[0] / 2
                    feature['plot_y'] = -feature.y() * self.dpm + self.size[1] / 2
                    pass

                if any([abs(feature.x()) > 110 or abs(feature.y()) > 110 for feature in features]):
                    printe(f'Features from source \'{source}\' with label \'{Properties.feature_properties[typename]["label"]}\' not loaded correctly. Omitting them.', tag='Warning')
                    self.data[source][typename] = [feature for feature in features if (abs(feature.x()) <= 110 or abs(feature.y()) <= 110)]

                else:
                    self.data[source][typename] = features

                self.layers[typename] = self.Layer(features, typename, self.background.size, self.cache)

    def get_image(self, types: list, show_circle: bool = True, selected: str = None, show_annotations: bool = True, r: float = 3, route=None):
        with Image.open(self.backgound_path) as im:
            draw = ImageDraw.Draw(im)

            for typename in Properties.feature_properties:
                if typename in types:
                    with self.layers[typename] as layer:
                        im.paste(layer, (0,0), layer)

            if selected != None:
                for source in self.data:
                    types = self.data[source]
                    for typename in types:
                        for ft in self.data[source][typename]:
                            if ft['id'] == selected:
                                fill = Properties.feature_properties[typename]['color']

                                x, y = ft['plot_x'], ft['plot_y']
                                xy = [(x - r, y - r), (x + r, y + r)]
                                
                                draw.ellipse(xy=xy, fill=fill, outline='red')
                                draw.text(xy=[x + r, y + r], text=f'{ft["id"]}', fill='red')

            if show_circle:
                x0 = (self.size[0] / 2 - Properties.radius * self.dpm, self.size[1] / 2 - Properties.radius * self.dpm)
                x1 = (self.size[0] / 2 + Properties.radius * self.dpm, self.size[1] / 2 + Properties.radius * self.dpm)

                draw.ellipse([x0, x1], outline='#ff0000')


            if route is not None:
                colors = {2: '#FF0000', 4: '#00FF00', 5: '#FFFF00'}
                route = [(point[0] - self.c.points['EPSG:25832'][0], point[1] - self.c.points['EPSG:25832'][1], point[2]) for point in route]
                for i, point in enumerate(route):
                    x = point[0] * self.dpm + self.size[0] / 2
                    y = -point[1] * self.dpm + self.size[1] / 2
                    radius =  r - 2
                    xy = [(x - radius, y - radius), (x + radius, y + radius)]
                    draw.ellipse(xy=xy, fill=colors[point[2]])
                    #draw.text(xy=[x + r, y + r], text=f'{i}', fill='red')


            im.save(self.image_path)

        return self.image_path

def get_area_data(area: str):    
    path = 'files/areas'
    files = [file for file in os.listdir(path) if os.path.split(file)[-1][:-4].split('_')[1] == area and os.path.split(file)[-1][:-4].split('_')[2] != '0']
    files = {file.split('_')[0]: pd.read_csv(f'{path}/{file}') for file in files}
    
    result = {}
    for source, data in zip(files.keys(), files.values()):
        features = {}
        for n, row in data.iterrows():
            row = dict(row)

            row['n'] = n

            geometry = row['geometry'].split(';')[1].split(',')
            geometry = [g[1:-1] for g in geometry]
            geometry = transpose([[float(v) for v in g.split(',')] for g in geometry])

            if len(geometry) == 1:
                geometry = geometry[0]
            else:
                geometry = [[pos[0] for pos in geometry], [pos[1] for pos in geometry]] 

            tag = row['geometry'].split(';')[0]

            del row['geometry']

            feature = Feature(geometry, srs=Properties.default_srs, tag=tag, attributes=row)
            features.setdefault(row['typename'], []).append(feature)
        result[source] = features

    return result

def plot(area, route=None):
    tile_matrix = simple_dropdown('Select tile_matrix', [14, 13, 12, 11, 10])

    inputs = {}

    pretty_area = list(Properties.areas).index(area)
    pretty_area = Properties.areas_pretty[pretty_area]

    title = f'{pretty_area}'
    export = sg.Button('Export')
    back = sg.Button('Back')

    data = get_area_data(area)
    sources = [source for source in data]

    col = [[export, back]]

    fp = Properties.feature_properties
    for source in sources:
        col.append([sg.Text(source.capitalize(), enable_events=True)])

        for feature in list(data[source]):
            if fp[feature]['origin'] != source:
                continue

            color = fp[feature]['color']
            label = fp[feature]['label']

            col.append([sg.Checkbox(label, text_color = color, key=feature, enable_events=True)])
            inputs[len(inputs)] = {'type': 'checkbox', 'source': source, 'typename': feature}

    checkboxes = sg.Column(col, vertical_alignment='top')

    size = (Properties.outer_radius*2,Properties.outer_radius*2)

    image_object = PlotImage(size=size, area=area, data=data, tile_matrix=tile_matrix)

    size = image_object.size

    graph = sg.Graph(canvas_size=size, graph_bottom_left=(0,0), graph_top_right=size, key='Click', enable_events=True)

    #Add textbox to gui

    properties = PropertiesBox(width=300, height=size[1], initial_text='Click a feature.')

    layout = [
        [checkboxes, graph, properties.get_properties()],
    ]

    window = sg.Window(title, layout)
    window.finalize()

    graph.DrawImage(image_object.get_image([], route=route), location=(0, size[1]))

    selected = None

    while True:
        event, values = window.read()

        if event == sg.WIN_CLOSED or event == 'Back':
            break

        types = set([inputs[i]['typename'] for i in inputs if values[inputs[i]['typename']]])

        if type(event) == str and event.lower() in sources:
            source = event.lower()

            source_types = list(data[source])

            if all(typename in types for typename in source_types):
                for typename in source_types:
                    cb = window.Find(typename)
                    cb.update(value=False)
                    types.remove(typename)
            else:
                for typename in source_types:
                    cb = window.Find(typename)
                    cb.update(value=True)
                    types.add(typename)

        if event.split('_')[0] == str(properties.id):
            i = event.split('_')[-1]
            i = int(i)
            property_values = list(properties.attributes.values())
            value = property_values[i]
            
            pd.DataFrame([str(value)]).to_clipboard(index=False, header=False)

        if event == 'Click':
            features = []
            for source in sources:
                for typename in image_object.data[source]:
                    if typename in types:
                        features.extend(image_object.data[source][typename])

            x, y = values['Click']
            y = size[1] - y

            features = [{'d': ((ft['plot_x'] - x)**2 + (ft['plot_y'] - y)**2), 'feature': ft} for ft in features]

            selected = None
            if len(features) > 0:
                ft = min(features, key=lambda ft: ft['d'])
                feature = ft['feature']
                
                attributes = {}
                if ft['d'] < 7**2:
                    selected = feature['id']
                    for key, val in zip(feature.attributes.keys(), feature.attributes.values()):
                        t = type(val)

                        if not t in (int, str, float) or key == 'Unnamed: 0' or str(val) in ('nan', 'None'):
                            continue
                        
                        attributes[key] = val

                properties.set_attributes(window, attributes)

        graph.DrawImage(image_object.get_image(types=types, selected=selected, route=route), location=(0, size[1]))

        if event == 'Run':
            if eval(values['textbox']): print('yay!')
    window.close()

    return event

if __name__ == '__main__':
    sg.theme('DarkGrey2')
    plot('park')
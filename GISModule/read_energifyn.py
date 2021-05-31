from jaolma.gis.wfs import WFS, Filter
from jaolma.properties import Properties
from jaolma.utility.utility import prints, set_verbose

import pandas as pd
import os

set_verbose(tag_blacklist=['WFS'])

servicename = 'energifyn'
service = Properties.services['wfs'][servicename]

files = os.listdir('files/areas/')
for file in files:
    if servicename in file:
        os.remove('files/areas/' + file)

wfs = WFS(service['url'], version=service['version'])

typenames = [typename for typename in Properties.feature_properties if 'origin' in Properties.feature_properties[typename] and Properties.feature_properties[typename]['origin'] == servicename]

prints(f'Retrieving features: {", ".join([Properties.feature_properties[typename]["label"] + " (" + typename + ")" for typename in typenames])}', tag='Main')
prints(f'In areas: {", ".join(Properties.areas.keys())}', tag='Main')

all_features = {}
for typename in typenames:
    features = wfs.get_features(
        srs='EPSG:4326', 
        typename=typename,
        reverse_x_y=True)

    features.to_srs(Properties.default_srs)

    all_features[typename] = features

for area, center in zip(Properties.areas.keys(), Properties.areas.values()):
    center.to_srs(Properties.default_srs)

    frames = []

    for typename in typenames:
        features = all_features[typename].filter(lambda feature: feature.dist(center) <= Properties.outer_radius)
        
        rows = {}    
        for feature in features:
            data = {}
            data['typename'] = typename
            data['id'] = feature['fid'].split(';')[-1]
            data['label'] = Properties.feature_properties[typename]['label']
            data['geometry'] = f'{feature.tag};{list(feature.x(enforce_list=True))},{list(feature.y(enforce_list=True))}'
            data['service'] = servicename

            optionals = {
                'description': 'mastetype',
                'height': 'lyspunktshoejde',
                'date': 'lastedited'}

            for key, val in zip(optionals.keys(), optionals.values()):
                if val in feature.attributes:
                    data[key] = feature[val]

            for key, value in zip(data.keys(), data.values()):
                rows.setdefault(key, []).append(value)

        frames.append(pd.DataFrame(rows))

    dataframe = pd.concat(frames, ignore_index=True)
    dataframe.to_csv(f'files/areas/{servicename}_{area}_{len(dataframe)}.csv')
    prints(f'Found {len(dataframe)} features for area {area}.', tag='Main')
from jaolma.gis.wfs import WFS, Filter, Feature
from jaolma.properties import Properties
from jaolma.utility.utility import prints, set_verbose

import pandas as pd
import os

def extract_points(current_position: tuple, srs: str='EPSG:4326', bbox_width: float=10, bbox_height: float=10):
    current_position = Feature(current_position, srs)
    current_position.to_srs(Properties.default_srs)

    set_verbose(tag_blacklist=['WFS'])

    servicenames = ['geodanmark', 'energifyn', 'kortopslag']

    gis_features = []

    for servicename in servicenames:
        service = Properties.services['wfs'][servicename]

        wfs = WFS(service['url'], version=service['version'], username=service['username'], password=service['password'])

        typenames = [typename for typename in Properties.feature_properties 
                    if 'origin' in Properties.feature_properties[typename] 
                    and Properties.feature_properties[typename]['origin'] == servicename
                    and not Properties.feature_properties[typename]['exclude']]
        
        prints(f'Retrieving features: {", ".join([Properties.feature_properties[typename]["label"] for typename in typenames])}', tag='Main')

        for typename in typenames:
            bbox = Filter.bbox(center=current_position, width=bbox_width, height=bbox_height)

            features = wfs.get_features(
                srs=Properties.default_srs, 
                typename=typename, 
                bbox=bbox)
            
            for feature in features:
                data = {}
                data['service'] = servicename
                data['typename'] = typename
                data['geometry'] = feature.points[Properties.default_srs]
                if servicename == 'geodanmark':
                    data['id'] = feature['id.lokalId']
                    data['date'] = feature['registreringFra']
                    data['horizontal_precision'] = feature['planNoejagtighed']
                    data['vertical_precision'] = feature['vertikalNoejagtighed']

                elif servicename == 'energifyn':
                    data['id'] = feature['fid']
                    if typename == 'TL740798':
                        data['date'] = feature['lastedited']
                        data['subtype'] = feature['mastetype']

                elif servicename == 'kortopslag':
                    data['id'] = feature['fid']
                    if typename == 'L418883_421469':
                        data['date'] = feature['tr_kontroldato']
                        data['subtype'] = feature['tr_slaegt']
                    elif typename == 'L167365_421559':
                        if feature['underelement_tekst'] not in ['Bænk', 'Affaldsspand', 'Monument', 'Bord/bænk']:
                            continue
                        data['subtype'] = feature['underelement_tekst']

                gis_features.append(data)
    return gis_features

if __name__ == '__main__':
    current_position = (55.3947509, 10.3833619)

    points = extract_points(current_position)

    pass
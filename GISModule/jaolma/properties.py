from jaolma.gis.wfs import Feature

class Properties:
    areas = {
        'downtown': (55.3947509, 10.3833619), 
        'harbor': (55.4083756, 10.3787729), 
        'park': (55.3916561, 10.3828329),
        'suburb': (55.3761308, 10.3860752), 
        'sdu': (55.3685818, 10.4317584)
    }

    # Has to only differ from areas in capitalization of letters.
    areas_pretty = ['Downtown', 'Harbor', 'Park', 'Suburb', 'SDU']

    areas = {key: Feature(geometry, 'EPSG:4326', key) for key, geometry in zip(areas.keys(), areas.values())}

    default_srs = 'EPSG:25832'

    outer_radius = 120
    radius = 100

    bbox_width = 100
    bbox_height = 100

    feature_properties = {
        'TL695099': {'origin': 'kortopslag', 'label': 'Building (ko)', 'color': '#700000', 'exclude': True},
        'TL965167': {'origin': 'kortopslag', 'label': 'Road Well (ko)', 'color': '#ff00ff', 'exclude': False},
        'L418883_421469': {'origin': 'kortopslag', 'label': 'Park Tree (ko)', 'color': '#00851b', 'exclude': False},
        'L167365_421559': {'origin': 'kortopslag', 'label': 'Park Point (ko)', 'color': '#6e452f', 'exclude': False},
        'Bænk': {'origin': 'kortopslag', 'label': 'Bench (ko)', 'color': '#613a3a', 'exclude': True},
        'Affaldsspand': {'origin': 'kortopslag', 'label': 'Trash Can (ko)', 'color': '#454343', 'exclude': True},
        'Monument': {'origin': 'kortopslag', 'label': 'Statue (ko)', 'color': '#b5b1b1', 'exclude': True},
        'Slyng- og klatreplanter': {'origin': 'kortopslag', 'label': 'Greenery (ko)', 'color': '#277d41', 'exclude': True},

        'Bygning': {'origin': 'geodanmark', 'label': 'Building (gd)', 'color': '#ff0000', 'exclude': True},
        'Broenddaeksel': {'origin': 'geodanmark', 'label': 'Manhole Cover (gd)', 'color': '#ac0fdb', 'exclude': False},
        'Mast': {'origin': 'geodanmark', 'label': 'Light Fixture (gd)', 'color': '#e0de38', 'exclude': False},
        'Hegn': {'origin': 'geodanmark', 'label': 'Fence (gd)', 'color': '#cf8b5b', 'exclude': True},
        'Soe': {'origin': 'geodanmark', 'label': 'Lake (gd)', 'color': '#3051c7', 'exclude': True},
        'KratBevoksning': {'origin': 'geodanmark', 'label': 'Bush (gd)', 'color': '#3b6e2f', 'exclude': True},
        'Trae': {'origin': 'geodanmark', 'label': 'Tree (gd)', 'color': '#30c74e', 'exclude': False},
        'Nedloebsrist': {'origin': 'geodanmark', 'label': 'Downspout Grille (gd)', 'color': '#db0f64', 'exclude': False},
        'Chikane': {'origin': 'geodanmark', 'label': 'Chicane (gd)', 'color': '#8db09b', 'exclude': True},
        'Vandloebskant': {'origin': 'geodanmark', 'label': 'Stream (gd)', 'color': '#6e86db', 'exclude': True},
        'Helle': {'origin': 'geodanmark', 'label': 'Refuge Island (gd)', 'color': '#3f4f46', 'exclude': True},
        'Skorsten': {'origin': 'geodanmark', 'label': 'Chimney (gd)', 'color': '#292927', 'exclude': False},
        'Jernbane': {'origin': 'geodanmark', 'label': 'Railroad (gd)', 'color': '#75756a', 'exclude': True},
        'Bassin': {'origin': 'geodanmark', 'label': 'Pool (gd)', 'color': '#00a2ff', 'exclude': True},

        'water_node': {'origin': 'samaqua', 'label': 'Water Node (sa)', 'color': '#5b45a3', 'exclude': False},

        'TL740798': {'origin': 'energifyn', 'label': 'Base Data (ef)', 'color': '#751e1a', 'exclude': False},
        'TL740800': {'origin': 'energifyn', 'label': 'Fuse Box (ef)', 'color': '#5e4a49', 'exclude': False},

        'heating_cover': {'origin': 'fjernvarme', 'label': 'Heating Cover (fv)', 'color': '#47657d', 'exclude': False},

        'Tree': {'origin': 'groundtruth', 'label': 'Tree (gt)', 'color': '#118a0c', 'exclude': False},
        'Light Fixture': {'origin': 'groundtruth', 'label': 'Light Fixture (gt)', 'color': '#f2f55f', 'exclude': False},
        'Downspout Grille': {'origin': 'groundtruth', 'label': 'Downspout Grille (gt)', 'color': '#711f80', 'exclude': False},
        'Manhole Cover': {'origin': 'groundtruth', 'label': 'Manhole Cover (gt)', 'color': '#080d8a', 'exclude': False},
        'Fuse Box': {'origin': 'groundtruth', 'label': 'Fuse Box (gt)', 'color': '#5c4e1c', 'exclude': False},
        'Building Corner': {'origin': 'groundtruth', 'label': 'Building Corner (gt)', 'color': '#cc3618', 'exclude': False},
        'Bench': {'origin': 'groundtruth', 'label': 'Bench (gt)', 'color': '#6e5942', 'exclude': False},
        'Trash Can': {'origin': 'groundtruth', 'label': 'Trash Can (gt)', 'color': '#5c5b5b', 'exclude': False},
        'Tree Stump': {'origin': 'groundtruth', 'label': 'Tree Stump (gt)', 'color': '#6e491b', 'exclude': False},
        'Chimney': {'origin': 'groundtruth', 'label': 'Chimney (gt)', 'color': '#291937', 'exclude': False},
        'Rock': {'origin': 'groundtruth', 'label': 'Rock (gt)', 'color': '#636363', 'exclude': False},
        'Statue': {'origin': 'groundtruth', 'label': 'Statue (gt)', 'color': '#b3b3b3', 'exclude': False},
        'Misc': {'origin': 'groundtruth', 'label': 'Misc (gt)', 'color': '#72fcfa', 'exclude': False},
        'Greenery': {'origin': 'groundtruth', 'label': 'Greenery (gt)', 'color': '#118b0b', 'exclude': False},
        'unknown': {'origin': 'groundtruth', 'label': 'unknown', 'color': '#000000', 'exclude': False},

        #'': {'origin': '', 'label': '', 'color': '#'},
    }

    '''
        'Tree': {'origin': 'gnss', 'label': 'Tree (gt)', 'color': '#118a0c'},
        'Light Fixture': {'origin': 'gnss', 'label': 'Light Fixture (gt)', 'color': '#f2f55f'},
        'Downspout Grille': {'origin': 'gnss', 'label': 'Downspout Grille (gt)', 'color': '#711f80'},
        'Manhole Cover': {'origin': 'gnss', 'label': 'Manhole Cover (gt)', 'color': '#080d8a'},
        'Fuse Box': {'origin': 'gnss', 'label': 'Fuse Box (gt)', 'color': '#5c4e1c'},
        'Building Corner': {'origin': 'gnss', 'label': 'Building Corner (gt)', 'color': '#cc3618'},
        'Bench': {'origin': 'gnss', 'label': 'Bench (gt)', 'color': '#6e5942'},
        'Trash Can': {'origin': 'gnss', 'label': 'Trash Can (gt)', 'color': '#5c5b5b'},
        'Tree Stump': {'origin': 'gnss', 'label': 'Tree Stump (gt)', 'color': '#6e491b'},
        'Chimney': {'origin': 'gnss', 'label': 'Chimney (gt)', 'color': '#291937'},
        'Rock': {'origin': 'gnss', 'label': 'Rock (gt)', 'color': '#636363'},
        'Statue': {'origin': 'gnss', 'label': 'Statue (gt)', 'color': '#b3b3b3'},
        'Misc': {'origin': 'gnss', 'label': 'Misc (gt)', 'color': '#72fcfa'}
    '''
    services = {
        'wfs': {
            'geodanmark': {
                'url': 'https://services.datafordeler.dk/GeoDanmarkVektor/GeoDanmark60_NOHIST_GML3/1.0.0/WFS?', 
                'version': '1.1.0', 
                'username': 'VCSWRCSUKZ', 
                'password': 'hrN9aTirUg5c!np'},

            'energifyn': {
                'url': 'https://services.drift.kortinfo.net/kortinfo/services/Wfs.ashx?Site=Odense&Page=Lyssignalanlaeg', 
                'version': '1.0.0',
                'username': None, 
                'password': None},

            'kortopslag': {
                'url': 'https://services.drift.kortinfo.net/kortinfo/services/Wfs.ashx?Site=Odense&Page=Kortopslag', 
                'version': '1.0.0',
                'username': None, 
                'password': None},
        }
    }

    source_colors = {'geodanmark': '#FF0000', 'kortopslag': '#00CC00', 'energifyn': '#FFA500', 'samaqua': '#1122CC', 'fjernvarme': '#A000A0', 'groundtruth': '#222222'}
    source_labels = {'geodanmark': 'GeoDanmark', 'kortopslag': 'Municipal', 'energifyn': 'Energi Fyn', 'samaqua': 'Vancenter Syd', 'fjernvarme': 'Fjernvarme Fyn', 'groundtruth': 'Ground Truth'}

    area_colors = {'suburb': '#FFA500', 'harbor': '#0000FF', 'downtown': '#FF0000', 'sdu': '#CC00CC', 'park': '#00FF00'}
    area_labels = {'suburb': 'Suburb', 'harbor': 'Harbor', 'downtown': 'Downtown', 'sdu': 'SDU', 'park': 'Park'}

    @staticmethod
    def get_feature_label(feature_name):
        if feature_name in Properties.feature_properties:
            if Properties.feature_properties[feature_name]['label'] != '':
                return Properties.feature_properties[feature_name]['label']
        return None

    @staticmethod
    def get_feature_color(feature_name):
        if feature_name in Properties.feature_properties:
            if Properties.feature_properties[feature_name]['color'] != '':
                return Properties.feature_properties[feature_name]['color']
        return None

    @staticmethod
    def get_feature_source(feature_name):
        if feature_name in Properties.feature_properties:
            if Properties.feature_properties[feature_name]['source'] != '':
                return Properties.feature_properties[feature_name]['source']
        return None
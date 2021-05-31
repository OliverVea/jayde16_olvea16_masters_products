import os
import pandas as pd

from jaolma.properties import Properties
from jaolma.utility.utility import transpose, flatten
from jaolma.gis.wfs import Feature
from jaolma.data_treatment.matches import Matches
from jaolma.data_treatment.stats import Stats

from numpy import mean as avg
from numpy import sqrt
import numpy as np


class GISData:
    all_sources = list(set(Properties.feature_properties[typename]['origin'] for typename in Properties.feature_properties if Properties.feature_properties[typename]['origin'] != 'groundtruth'))
    all_typenames = {source: {typename for typename in Properties.feature_properties if Properties.feature_properties[typename]['origin'] == source} for source in all_sources}

    def _get_data(self, features_to_exclude: list = [], use_exclude_property: bool = False):
        # TODO: Exclude features
        path = 'files/areas'
        files = [file for file in os.listdir(path) if os.path.split(file)[-1][:-4].split('_')[1] == self.area and os.path.split(file)[-1][:-4].split('_')[2] != '0']
        files = {file.split('_')[0]: pd.read_csv(f'{path}/{file}', dtype=str) for file in files}
        
        result = {}
        for source, data in zip(files.keys(), files.values()):
            features = {}
            for n, row in data.iterrows():
                row = dict(row)

                typename = row['typename']
                if use_exclude_property and Properties.feature_properties[typename]['exclude']:
                    continue

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

                if row['typename'] == 'L167365_421559':
                    if row['category'] == 'Slyng- og klatreplanter':
                        features.setdefault(row['category'], []).append(feature)
                    elif row['sub_category'] in ['Affaldsspand','Monument','Bænk','Bord/bænk']:
                        if row['sub_category'] == 'Bord/bænk':
                            features.setdefault('Bænk', []).append(feature)
                        else:
                            features.setdefault(row['sub_category'], []).append(feature)
                else:
                    features.setdefault(row['typename'], []).append(feature)
            result[source] = features
            
        return result

    def _get_validation_results(self, source, typename):
        path = f'files/validation/new_{self.area}.csv'
        data = pd.read_csv(path)

        ids = list(self.matches.matches[source].keys())
        fts = [self._get_feature(gt_id=id) for id in ids]
        fts = [ft for ft in fts if self._should_qualify(ft, typename)]
        ids = [ft['id'] for ft in fts]

        acc = [row['Accessibility'] for n, row in data.iterrows() if str(row['Feature ID']) in ids]
        ovis = [row['Obstructed Visibility'] for n, row in data.iterrows() if str(row['Feature ID']) in ids]
        vis = [100 * (a/100 + (1 - a/100) * v/100) for a, v in zip(acc, ovis)]

        return acc, vis

    # This function returns whether or not a ground truth feature should qualify as some service feature type.
    def _should_qualify(self, feature, typename):
        translation = {'heating_cover': ['Manhole Cover'], 'TL740800': ['Fuse Box'], 'TL740798': ['Light Fixture'], 
            'L418883_421469': ['Tree'], 'TL965167': ['Downspout Grille', 'Manhole Cover'], 'L167365_421559': ['Bench', 'Trash Can', 'Statue', 'Misc', 'Rock', 'Greenery'], 
            'Bænk': ['Bench'], 'Affaldsspand': ['Trash Can'], 'Monument': ['Statue'], 'Slyng- og klatreplanter': ['Greenery'],
            'water_node': ['Manhole Cover'], 'Broenddaeksel': ['Manhole Cover'],  'Mast': ['Light Fixture'],  
            'Trae': ['Tree'], 'Nedloebsrist': ['Downspout Grille'], 'Skorsten': ['Chimney']}

        for _typename in Properties.feature_properties:
            if Properties.feature_properties[_typename]['origin'] != 'groundtruth' and not _typename in translation:
                translation[_typename] = []

        if not feature['typename'] in translation[typename]:
            return False

        source = Properties.feature_properties[typename]['origin']

        # Manhole covers: 
        # Kun brug Large (geodanmark, samaqua, kortopslag, fjernvarme) og Large Square (samaqua, geodanmark)
        if feature['typename'] == 'Manhole Cover':
            sc = feature['subcategory']
            if sc == 'Large': 
                if not source in ['geodanmark', 'samaqua', 'kortopslag', 'fjernvarme']:
                    return False

            elif sc == 'Large Square':
                if not source in ['geodanmark', 'samaqua']:
                    return False

            elif sc == 'Stone':
                if not source in ['geodanmark']:
                    return False
            
            else:
                return False
                
        # Light fixture:
        # Standing (geodanmark, energifyn) og Hanging + Ground (energifyn)
        if feature['typename'] == 'Light Fixture':
            sc = feature['subcategory']
            if sc == 'Standing': 
                if not source in ['geodanmark', 'energifyn']:
                    return False

            elif sc in ['Hanging', 'Ground']:
                if source != 'energifyn':
                    return False
            
            else:
                return False

        return True
                

    def _get_feature(self, gt_id: str = None, service_id: str = None, source: str = None):
        if gt_id == None and service_id == None:
            raise Exception('Please specify an of either type.')
    
        if gt_id != None and service_id != None:
            raise Exception('Please only specify one id.')

        data, gt = self.get_data(separated_gt=True)

        if gt_id != None:
            for ft in flatten(gt):
                if ft['id'] == gt_id:
                    return ft
            return None
                    
        for ft in flatten(data[source]):
            if ft['id'] == service_id:
                return ft
        return None

    def _get_stats(self):
        stats = {source: {typename: None for typename in self.all_typenames[source]} for source in self.all_sources} 
    
        for source in self.data:
            for typename in self.data[source]:
                features = self.data[source][typename]

                # Count features
                N = len(features)

                # Count true positives
                tp = [ft for ft in features if self.matches.is_matched_service(source, ft['id'])]
                tp_gt = [ft for ft in flatten(self.ground_truth) if self._should_qualify(ft, typename) and len(self.matches.get_matches_gt(ft['id'])[source]) != 0]

                for ft in tp_gt:
                    matches = self.matches.get_matches_gt(ft['id'])[source]
                    matches = [self._get_feature(service_id=id, source=source) for id in matches]
                    matches = [ft for ft in matches if ft != None]

                    ft['matches'] = matches

                # Count false positives
                fp = [ft for ft in features if not self.matches.is_matched_service(source, ft['id'])]

                # Count false negatives
                fn = [ft for ft in flatten(self.ground_truth) if self._should_qualify(ft, typename) and len(self.matches.get_matches_gt(ft['id'])[source]) == 0]

                # Get accessibility and visibility
                acc, vis = self._get_validation_results(source, typename)

                # Get accuracy
                err = []
                for gt_id, service_ids in zip(self.matches.matches[source].keys(), self.matches.matches[source].values()):
                    ft = self._get_feature(gt_id=gt_id)

                    if ft['Measurement'] != 'Totalstation' and ft['fix'] != '4':
                        continue 

                    service_fts = [self._get_feature(service_id=id, source=source) for id in service_ids]
                    service_fts = [ft for ft in service_fts if ft != None]

                    if len(service_fts) == 0:
                        continue

                    x = avg([ft.x() for ft in service_fts])
                    y = avg([ft.y() for ft in service_fts])

                    err.append(sqrt((ft.x() - x)**2 + (ft.y() - y)**2))

                stats[source][typename] = Stats(source, typename, amount=N, true_positives=tp, true_positives_gt = tp_gt, false_positives=fp, false_negatives=fn, accessibilities=acc, visibilities=vis, accuracies=err)

        return stats

    def _filter_outliers(self):
        center = Properties.areas[self.area]
        center.to_srs(Properties.default_srs)

        # First round of filtering - removing ground truth features outside the circle.
        ground_truth = {}
        for typename, fts in zip(self.ground_truth.keys(), self.ground_truth.values()):
            ground_truth[typename] = []
            for ft in fts:
                # Checks if a ground truth feature that is outside the circle.
                if center.dist(ft) > Properties.radius:

                    # Firstly, find matches of the feature.
                    matches = self.matches.get_matches_gt(ft['id'])

                    # Remove the feature from matches.
                    self.matches.remove_gt(ft['id'])

                    # There might be service features that looks like they are inside the circle but now look like False Positives.
                    for source in matches:
                        for service_id in matches[source]:
                            gt_ids = self.matches.get_matches_service(source, service_id)

                            # Checks if the feature is now unmatched completely.
                            if len(gt_ids) == 0:
                                
                                # Removes the feature from the data.
                                self.data[source] = {typename: [f for f in self.data[source][typename] if f['id'] != service_id] for typename in self.data[source]}
                else:
                    ground_truth[typename].append(ft)
        
        self.ground_truth = ground_truth

        # Second round of filtering - removing unmatched service features outside the circle.
        data = {}
        for source in self.data:
            data[source] = {}
            for typename in self.data[source]:
                data[source][typename] = []
                for ft in self.data[source][typename]:
                    if (center.dist(ft) <= Properties.radius) or (len(self.matches.get_matches_service(source, ft['id'])) != 0):
                        data[source][typename].append(ft)
        self.data = data

    def _filter_from_file(self):
        if not f'exclude_{self.area}.csv' in os.listdir('files/ground_truth/'):
            return

        path = f'files/ground_truth/exclude_{self.area}.csv'
        data = pd.read_csv(path, dtype=str)

        for i, row in data.iterrows():
            row = dict(row)

            row = {key: val for key, val in zip(row.keys(), row.values()) if isinstance(val, str)}

            for source in row:
                data = {}
                for typename in self.data[source]:
                    data[typename] = []
                    for ft in self.data[source][typename]:
                        if ft['id'] != row[source]:
                            data[typename].append(ft)
                
                self.data[source] = data

    def __init__(self, area: str, use_exclude_property: bool = False):
        self.area = area
        self.data = self._get_data(use_exclude_property=use_exclude_property)
        self.ground_truth = self.data['groundtruth']
        del self.data['groundtruth']

        self._filter_from_file()

        self.matches = Matches(self.ground_truth, self.all_sources)

        self._filter_outliers()

        self.stats = self._get_stats()

    def get_stats(self):
        return self.stats

    def get_data(self, separated_gt: bool = False):
        if separated_gt:
            return self.data, self.ground_truth
        data = self.data
        data.update({'groundtruth': self.ground_truth})
        return data
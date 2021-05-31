import pandas as pd

from jaolma.utility.utility import flatten

class Matches:
    def __init__(self, ground_truth, sources):
        self.matches = {}
        for source in sources:
            self.matches[source] = {}
            for ft in flatten(ground_truth):
                if not pd.isna(ft[source]):
                    service_ids = [t.strip() for t in ft[source].split(',')]
                    self.matches[source][ft['id']] = service_ids

    def get_matches_gt(self, id):
        matches = {}
        for source in self.matches:
            matches[source] = []
            for gt_id in self.matches[source]:
                if gt_id == id:
                    matches[source].extend(self.matches[source][id])

        return matches

    def remove_gt(self, id):
        self.matches = {source: {gt_id: service_ids for gt_id, service_ids in zip(self.matches[source].keys(), self.matches[source].values()) if gt_id != id} for source in self.matches}

    def get_matches_service(self, source, id):
        return [gt_id for gt_id in self.matches[source] if id in self.matches[source][gt_id]]

    def remove_service(self, id):
        matches = {}
        for source in self.matches:
            matches[source] = {}
            for gt_id, service_ids in zip(self.matches[source].keys(), self.matches[source].values()):
                matches[source][gt_id] = []
                for service_id in service_ids:
                    if service_id != id:
                        matches[source][gt_id].append(service_id)
                
                if len(matches[source][gt_id]) == 0:
                    del matches[source][gt_id]

        self.matches = matches

    def is_matched_service(self, source, id):
        return len(self.get_matches_service(source, id)) != 0

    def is_matched_gt(self, id):
        return len(self.get_matches_gt(id)) != 0
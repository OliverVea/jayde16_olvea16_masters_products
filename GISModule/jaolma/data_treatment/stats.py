from numpy import mean as avg

class Stats:
    # Same equation used to calculate precision and recall.
    def _calc(self, a: float, b: float):
        if (a + b) == 0:
            return None
        return a / (a + b)

    def __init__(self, source, typename,
            amount: int = None, 
            true_positives_gt: list = None,
            true_positives: list = None, 
            false_positives: list = None, 
            false_negatives: list = None, 
            accuracies: list = [],
            accessibilities: list = [], 
            visibilities: list = [],
            matches: list = []):

        self.source = source 
        self.typename = typename
        self.amount = amount

        self.true_positives = true_positives
        self.true_positives_gt = true_positives_gt
        self.false_positives =false_positives
        self.false_negatives = false_negatives

        self.accuracies = accuracies

        self.accessibilities = accessibilities
        self.visibilities = visibilities

    def get_accessibility(self):
        return avg(self.accessibilities)

    def get_visibility(self):
        return avg(self.visibilities)

    def get_precision(self):
        return self._calc(len(self.true_positives), len(self.false_positives))

    def get_recall(self):
        return self._calc(len(self.true_positives), len(self.false_negatives))

    def get_f1(self):
        return 2 / (1 / self.get_recall() + 1 / self.get_precision())

    def get_accuracy(self):
        return avg(self.accuracies)
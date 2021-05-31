from jaolma.gis.wfs import Feature, Collection

class CSV:
    def __init__(self, filename: str, delimiter: str = ','):
        self.filename = filename
        self.delimiter = delimiter
        pass

    def _split_without_parentheses(self, text, delimiter):
        openers = {'[': 0, '{': 0, '(': 0, '"': False, "'": False}

        is_inside = lambda openers: (openers['['] > 0) or (openers['{']) > 0 or (openers['(']) > 0 or openers['"'] or openers["'"]

        result = []
        current_string = ''

        for ch in text:
            if ch == self.delimiter and not is_inside(openers):
                result.append(current_string)
                current_string = ''

            else:
                if ch == '[':
                    openers['['] += 1
                elif ch == ']':
                    openers['['] -= 1

                elif ch == '{':
                    openers['{'] += 1
                elif ch == '}':
                    openers['{'] -= 1

                elif ch == '(':
                    openers['('] += 1
                elif ch == ')':
                    openers['('] -= 1

                elif ch == '"':
                    openers['"'] = not openers['"']

                elif ch == "'":
                    openers["'"] = not openers["'"]

                if ch.isascii() and not ch in ['\n']:
                    current_string += ch
        
        result.append(current_string)

        return result

    def _row_to_feature(self, row):
        geometry = [row['Latitude'], row['Longtitude']]
        for i in range(2):
            for ch in ['"', '(', ')']:
                geometry[i] = geometry[i].replace(ch, '')
            geometry[i] = geometry[i].split(', ')

            try:
                if len(geometry[i]) > 1:
                    geometry[i] = [float(v) for v in geometry[i]]
                else:
                    geometry[i] = float(geometry[i][0])
            except:
                return

        del row['Latitude']
        del row['Longtitude']

        return Feature(geometry, 'EPSG:4326', attributes=row)

    def read(self):
        with open(self.filename, 'r') as f:
            rows = [self._split_without_parentheses(row, self.delimiter) for row in f]

        header = rows[0]
        rows = rows[1:]

        data = [{key: value for key, value in zip(header, row)} for row in rows if not all(cell == '' for cell in row)]

        features = [feature for row in data if (feature := self._row_to_feature(row)) != None]

        features = Collection(tag=self.filename.split('/')[-1].split('.')[0], type='Various', features=features, srs='EPSG:4326')

        return features

if __name__ == '__main__':
    csv_file = CSV('input/park.csv')
    features = csv_file.read()


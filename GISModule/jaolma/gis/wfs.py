from jaolma.utility.utility import printe, prints, shortstring

import io

from requests import get
from lxml import objectify, etree
from pyproj import Transformer
from PIL import Image

from math import sqrt
    
class Feature(object):
    def __init__(self, geometry, srs: str, tag: str = '', attributes: dict = {}):
        self.tag = tag
        self.attributes = attributes
        self.default_srs = srs
        self.points = {srs: geometry}

        self.is_list = type(geometry[0]) in [list, tuple]

    def __getitem__(self, key):
        return self.attributes[key]

    def __setitem__(self, key, value):
        self.attributes[key] = value

    def __iter__(self):
        return self.points[self.default_srs].__iter__()

    def __add__(self, pt):
        x, y = pt.pos(self.default_srs)

        if self.is_list:
            geometry =  [(sx + x, sy + y) for sx in self.x() for sy in self.y()]
        else:
            geometry = (self.x() + x, self.y() + y)

        return Feature(tag=self.tag, geometry=geometry, srs=self.default_srs, attributes={})

    def __sub__(self, pt):
        x, y, *_ = pt.pos(self.default_srs)

        if self.is_list:
            geometry =  [[sx - x for sx in self.x()], [sy - y for sy in self.y()]]
        else:
            geometry = (self.x() - x, self.y() - y)

        attributes = {}
        attributes.update(self.attributes)
        attributes.update(pt.attributes)

        return Feature(tag=self.tag, geometry=geometry, srs=self.default_srs, attributes=attributes)

    def dist(self, pt):
        if self.is_list:
            dists = self - pt.as_srs(self.default_srs)
            dists = [sqrt(sum(dist[i] * dist[i] for i in range(2))) for dist in dists]
            return min(dists)
        else:
            dist = self - pt.as_srs(self.default_srs)
            return sqrt(dist.x() * dist.x() + dist.y() * dist.y())

    def pos(self, srs=None, transform: callable = None):
        if srs == None:
            srs = self.default_srs

        if not srs in self.points:
            if transform == None:
                transformer = Transformer.from_crs(self.default_srs, srs)
                self.points[srs] = transformer.transform(self.x(), self.y())

            else:
                self.points[srs] = transform(self.x(), self.y())

        return self.points[srs]

    def x(self, srs=None, enforce_list: bool = False):
        x = self.pos(srs)[0]

        if enforce_list and not isinstance(x, (list, tuple)):
            x = [x]

        return x

    def y(self, srs=None, enforce_list: bool = False):
        y = self.pos(srs)[1]

        if enforce_list and not isinstance(y, (list, tuple)):
            y = [y]
            
        return y

    def z(self, srs=None, enforce_list: bool = False):
        z = self.pos(srs)[2]

        if enforce_list and not isinstance(z, (list, tuple)):
            z = [z]
            
        return z

    def to_srs(self, srs, transform: callable = None):
        self.points[srs] = self.pos(srs, transform)
        self.default_srs = srs

    def as_srs(self, srs, transform: callable = None):
        return Feature(geometry=self.pos(srs, transform), srs=srs, tag=self.tag, attributes=self.attributes)

class Filter:
    @staticmethod
    def radius(center: Feature, radius: float, property: str = 'geometri', srs: str = None):
        with open('filter_templates/Radius.xml', 'r') as f:
            filt = f.read()

        for ch in ['\t', '\n']:
            filt = filt.replace(ch, '')

        filt = filt.replace('rrr', str(radius))
        filt = filt.replace('ppp', property)

        if srs != None:
            filt = filt.replace('xxx', str(center.x(srs=srs)))
            filt = filt.replace('yyy', str(center.y(srs=srs)))
            filt = filt.replace('ccc', srs)

        else:
            filt = filt.replace('xxx', str(center.x()))
            filt = filt.replace('yyy', str(center.y()))
            filt = filt.replace('ccc', center.default_srs)

        return filt
        
    @staticmethod
    def polygon(vertices: list, property: str = 'geometri', srs: str = None):
        with open('filter_templates/Polygon.xml', 'r') as f:
            filt = f.read()

        points = []
        if srs != None:
            for vertex in vertices:
                points += [str(vertex.x(srs=srs)), str(vertex.y(srs=srs))]
        else:
            for vertex in vertices:
                points += [str(vertex.x()), str(vertex.y())]
            srs = vertices[0].default_srs
        polyvertices = ' '.join(points)
        
        filt = filt.replace('propertyname', property)
        filt = filt.replace('srsname', srs)
        filt = filt.replace('polyvertexcount', str(len(vertices)))
        filt = filt.replace('polyvertices', polyvertices)

        print(filt)
        for ch in ['\t', '\n', '  ']:
            filt = filt.replace(ch, '')
        print(filt)

        return filt
    
    @staticmethod
    def bbox(center: Feature, width: float, height: float, srs: str=None):
        bottom_left_corner = Feature((center.x('EPSG:25832') - width / 2, center.y('EPSG:25832') - height / 2), srs='EPSG:25832')
        top_right_corner = Feature((center.x('EPSG:25832') + width / 2, center.y('EPSG:25832') + height / 2), srs='EPSG:25832')

        if srs == None:
            srs = center.default_srs

        return f'{bottom_left_corner.x(srs)},{bottom_left_corner.y(srs)},{top_right_corner.x(srs)},{top_right_corner.y(srs)}'


class Collection:
    def __getitem__(self, key):
        return self.features[key]

    def __init__(self, tag: str, type: str, features: list, srs: str):
        self.tag = tag
        self.type = type
        self.features = features
        self.cached_srs = [srs]

    def __iter__(self):
        return self.features.__iter__()

    def __len__(self):
        return len(self.features)

    def __add__(self, collection):
        srs = self.cached_srs[0]
        return Collection(self.tag, self.type, self.features + collection.as_srs(srs).features, srs)

    def to_srs(self, srs):
        if len(self.features) > 0 and srs not in self.cached_srs:
            transformer = Transformer.from_crs(self.cached_srs[0], srs)

            for ft in self.features:
                ft.to_srs(srs, transformer.transform)

            self.cached_srs.append(srs)

        else:
            for ft in self.features:
                ft.to_srs(srs)
    
    def as_srs(self, srs):
        transformer = None
        if len(self.features) > 0 and srs not in self.cached_srs:
            transformer = Transformer.from_crs(self.cached_srs[0], srs)
            self.cached_srs.append(srs)

        features = [ft.as_srs(srs, transformer) for ft in self.features]
        
        return Collection(self.tag, self.type, features, srs)

    def filter(self, filter):
        return Collection(self.tag, self.type, [feature for feature in self.features if filter(feature)], self.cached_srs[0])


class WebService(object):
    def __init__(self, url, username=None, password=None, version=None):
        self.url = url
        self.use_login = False
        if username != None and password != None:
            self.username = username
            self.password = password
            self.use_login = True

        self.version = version

    def _make_url(self, service, **args):
        if self.version != None:
            arguments = {'service': service.upper(), 'version': self.version}
        else:
            arguments = {'service': service}
        arguments.update(args)

        if self.use_login:
            arguments['username'] = self.username
            arguments['password'] = self.password

        arguments = [f'{str(key)}={str(value)}' for key, value in zip(arguments.keys(), arguments.values()) if value != None]
        arguments = '&' + '&'.join(arguments)

        return self.url + arguments

    def _simplify_tag(self, tag):
        return tag.split('}')[-1]

    def _query_url(self, url, response_type='xml'):
        response = get(url)
        content = response.content

        if response_type == 'jpeg':
            return Image.open(io.BytesIO(content))
        else:
            try:
                content = objectify.fromstring(content)

                children = {self._simplify_tag(c.tag): c for c in content.iterchildren()}

                if 'Exception' in children:
                    printe(str(children['Exception'].ExceptionText), tag='WebService')
                    return None

                if response_type == 'xml':
                    with open('last_response.xml', 'wb') as f:
                        f.write(etree.tostring(content, pretty_print=True))
                    
            except Exception as e:
                printe(str(e))
        
        return content

class WFS(WebService):
    def __init__(self, url: str, username: str=None, password: str=None, version: str=None, getCapabilitiesFilename: str = None):
        WebService.__init__(self, url, username, password, version)

        if getCapabilitiesFilename != None:
            url = self._make_url('WFS', request='GetCapabilities')
            wfsCapabilities = self._query_url(url)
            with open(getCapabilitiesFilename, 'wb') as f:
                f.write(etree.tostring(wfsCapabilities, pretty_print=True))

    def _get_geometry(self, element, reverse_x_y: bool = False):

        element = element.getchildren()[0]
        tag = self._simplify_tag(element.tag)

        if tag == 'MultiPoint':
            element = element.find('.//{http://www.opengis.net/gml}Point')
            tag = self._simplify_tag(element.tag)

        if tag == 'Point':
            if (geometry := element.find('.//{http://www.opengis.net/gml/3.2}pos')) != None:
                geometry = tuple(float(val) for val in geometry.text.split(' '))
            elif (geometry := element.find('.//{http://www.opengis.net/gml}coordinates')) != None:
                geometry = tuple(float(val) for val in geometry.text.split(','))
            else:
                printe(f'Point subtype {tag} not supported.', tag='WFS._get_geometry')
                geometry = []

        elif tag == 'Polygon' or tag == 'LineString':
            if (geometry := element.find('.//{http://www.opengis.net/gml/3.2}posList')) != None:
                geometry = [float(val) for val in geometry.text.split(' ')]
                geometry = [tuple(geometry[i*3+j] for i in range(len(geometry)//3)) for j in range(3)]
            elif (geometry := element.find('.//{http://www.opengis.net/gml}coordinates')) != None:
                points = [point for point in geometry.text.split(' ')]
                geometry = [tuple(float(val) for val in point.split(',')) for point in points]
                geometry = list(zip(*geometry)) #Transpose list for later
            else:
                printe(f'Polygon subtype {tag} not supported.', tag='WFS._get_geometry')
                geometry = []
        else:
            printe(f'Geometry type {tag} not supported.', tag='WFS._get_geometry')
            geometry = []
        
        if reverse_x_y:
            geometry = list(reversed(geometry))

        return geometry, tag

    def get_capabilities(self):
        # Only works for kortinfo.
        url = self._make_url('WFS', request='GetCapabilities')
        wfsCapabilities = self._query_url(url)

        service = wfsCapabilities.find('.//Service')
        serviceName = service.find('.//Name').text

        return serviceName


    def get_features(self, srs, typename=None, bbox=None, filter=None, max_features=None, as_list=False, reverse_x_y: bool = False):
        url = self._make_url('WFS', request='GetFeature', typename=typename, bbox=bbox, filter=filter, maxFeatures=max_features, srsName=srs)
        featureCollection = self._query_url(url)

        if featureCollection == None or self._simplify_tag(featureCollection.tag) != 'FeatureCollection':
            printe(f'Error in retrieving features. Returning empty dictionary. url: \'{url}\'', tag='WFS')
            return {}

        featurelist = [member.getchildren()[0] for member in featureCollection.iterchildren()][1:]
        features = []

        type = "None"
        for ft in featurelist:
            attributes = dict(ft.attrib)
            for attribute in ft.iterchildren():
                tag = self._simplify_tag(attribute.tag)

                if tag == 'geometri' or tag == 'obj':
                    geometry, type = self._get_geometry(attribute, reverse_x_y=reverse_x_y)

                else:
                    attributes[tag] = attribute.text

            feature = Feature(tag=type, geometry=geometry, srs=srs, attributes=attributes)
            features.append(feature)

        features = Collection(type=type, tag=str(typename), features=features, srs=srs)

        prints(f'Received {len(featurelist)} features from \'{shortstring(url, maxlen=90)}\'.', tag='WFS')
        
        return features
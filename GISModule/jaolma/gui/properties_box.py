import PySimpleGUI as sg

from random import randint

class PropertiesBox:
    def __init__(self, width: int, height: int, id: str = None, title: str = 'Properties', initial_text: str = '', capacity: int = 50):
        self.prop_text = sg.Text(title, font=('Any', 11, 'bold'), pad=(0,0))
        self.init_text = sg.Text(initial_text)

        self.width = width
        self.height = height
        self.capacity = capacity

        if id == None:
            id = str(randint(0, 1e10))
        self.id = id

        self.attributes = [[sg.Text('', visible=False, key=f'{self.id}_att_{i}', font=('Any', 10), size=(width, None), auto_size_text=False, enable_events=True, pad=(0,0))] for i in range(capacity)]

        self.properties = sg.Column([[self.prop_text]] + self.attributes + [[self.init_text]], size=(width, height), vertical_alignment='top')
        
        self.visible = True

        self.attributes = []


    def get_properties(self):
        return self.properties

    def set_attributes(self, window, attributes):
        self.init_text.update(visible=False)

        for i, attribute_name in enumerate(attributes):
            attribute_entry = window.find(f'{self.id}_att_{i}')
            attribute_entry.update(value=f'{attribute_name}: {attributes[attribute_name]}', visible=True)

        for i in range(self.capacity - len(attributes)):
            i += len(attributes)
            attribute_entry = window.find(f'{self.id}_att_{i}')
            attribute_entry.update(visible=False)

        self.attributes = attributes
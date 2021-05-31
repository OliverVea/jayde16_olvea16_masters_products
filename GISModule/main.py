import main_plot_area
import main_plot_spiderplot_area
import main_plot_connections

from jaolma.properties import Properties
from jaolma.utility.utility import printe, prints, load_route

from jaolma.gui import simple_dropdown

import PySimpleGUI as sg

sg.theme('DarkGrey2')

def pick_area() -> str:
    return simple_dropdown('Select Area', list(Properties.areas))

actions = {}
def pick_action() -> str:
    return simple_dropdown('Select Action', list(actions))

actions['Plot Area'] = main_plot_area.plot
actions['Plot Area Connections'] = main_plot_connections.plot
actions['Plot Radar Charts for Area'] = main_plot_spiderplot_area.plot

route = load_route(filename='files/data.csv')


while True:
    area = pick_area()

    if area == None:
        break

    action = pick_action()

    if action in (None, ''):
        break

    if action == 'Plot Area':
        event = actions[action](area, route=route)
    else:
        event = actions[action](area)

    if event != 'Back':
        break
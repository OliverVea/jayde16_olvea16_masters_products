from jaolma.properties import Properties
from jaolma.plotting.spider_plot import spider_plot
from jaolma.gui import simple_dropdown
from jaolma.data_treatment.data_treatment import GISData
from jaolma.utility.utility import uniform_colors

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import use
import matplotlib.pyplot as plt

import PySimpleGUI as sg
import numpy as np

def pick_plottype(plottypes) -> str:
    return simple_dropdown('Select Plot', list(plottypes))

def _get_stats(area):
    
    title = 'Feature Stats'
    axis_labels=['True Positives', 'Precision', 'Recall', 'Visibility', 'Accessibility', 'Error']

    silhouettes = {}
    sources = {}

    data = GISData(area)

    stats = data.get_stats()

    for source, features in zip(stats.keys(), stats.values()):
        sources[source] = []
        for ft_name, ft in zip(features.keys(), features.values()):
            if ft == None or ft.get_recall() == None:
                continue
            label = ft_name#Properties.feature_properties[ft_name]['label']
            sources[source].append(label)
            silhouettes[label] = []
            silhouettes[label].append(len(ft.true_positives))
            silhouettes[label].append(round(ft.get_precision()*100,1))
            silhouettes[label].append(round(ft.get_recall()*100,1))
            silhouettes[label].append(round(ft.get_visibility(),1))
            silhouettes[label].append(round(ft.get_accessibility(),1))
            silhouettes[label].append(round(ft.get_accuracy(),2))
        
    return silhouettes, axis_labels, sources, title


def plot(area):
    print(f'Plotting Radar Charts for Area: {area}.')

    use("TkAgg")

    
    plottypes = {'Plot Precision, Recall, Accuracy, Visibility, Accessibility and amount for all features.': 'plot_stats'}

    plottype = pick_plottype(plottypes.keys())

    if plottype in [None, '']:
        return plottype

    if plottypes[plottype] == 'plot_stats':
        silhouettes, labels, sources, title = _get_stats(area)
    else:
        silhouettes, labels, sources, title = _get_stats(area)

    #colors = uniform_colors(len(silhouettes))

    colors = [Properties.feature_properties[silhouette]['color'] for silhouette in silhouettes]

    inputs = {}

    pretty_area = list(Properties.areas).index(area)
    pretty_area = Properties.areas_pretty[pretty_area]

    title = f'{pretty_area}'
    export = sg.Button('Export')
    back = sg.Button('Back')

    col = [[export, back]]

    i = 0
    for source in sources.keys():
        col.append([sg.Text(source.capitalize(), enable_events=True)])

        for feature in list(sources[source]):
            color = colors[i]
            label = Properties.feature_properties[list(silhouettes.keys())[i]]['label']

            col.append([sg.Checkbox(label, text_color = color, key=feature, enable_events=True)])
            inputs[len(inputs)] = {'type': 'checkbox', 'source': source, 'typename': feature}
            i += 1
    
    checkboxes = sg.Column(col, vertical_alignment='top')

    size = (1000,1000)

    graph = sg.Graph(canvas_size=size, graph_bottom_left=(0,0), graph_top_right=size, key='Radar', enable_events=True)

    layout = [
        [checkboxes, graph]
    ]
    
    window = sg.Window(title, layout, finalize=True)

    #Instantiate figure_canvas_agg to allow for destruction in infinite loop.
    fig = spider_plot('', labels=labels, silhouettes=silhouettes)
    figure_canvas_agg = FigureCanvasTkAgg(fig, window["Radar"].TKCanvas)

    while True:
        event, values = window.read()
        
        #Check for close or back event
        if event == sg.WIN_CLOSED or event == 'Back':
            break

        #Set types to all types that are checked on
        types = set([inputs[i]['typename'] for i in inputs if values[inputs[i]['typename']]])

        #Check for click on a source
        if type(event) == str and event.lower() in sources:
            source = event.lower()

            source_types = list(sources[source])

            if all(typename in types for typename in source_types):
                for typename in source_types:
                    cb = window.find(typename)
                    cb.update(value=False)
                    types.remove(typename)
            else:
                for typename in source_types:
                    cb = window.find(typename)
                    cb.update(value=True)
                    types.add(typename)

        #Destroy current canvas to allow for a new plot
        figure_canvas_agg.get_tk_widget().destroy()

        #Filter which silhouettes to plot depending on the current checkboxes
        plot_silhouettes = dict((k, v) for k, v in zip(silhouettes.keys(), silhouettes.values()) if k in types)
        
        if len(plot_silhouettes) > 0:

            #Filter colors to fit the checkboxes
            plot_colors = [colors[list(silhouettes.keys()).index(key)] for key in plot_silhouettes.keys()]

            plot_silhouettes = dict((Properties.feature_properties[k]['label'], v) for k, v in zip(plot_silhouettes.keys(), plot_silhouettes.values()))

            #Set minimum and maximum of all axes
            axis_min = [0,0,0,0,0,0]
            axis_max = [max(0.1, max(v[0] for v in plot_silhouettes.values())), 100, 100, 100, 100, max(0.1, max(v[5] for v in plot_silhouettes.values()))]

            fig = spider_plot(
            title,
            labels=labels,
            silhouettes=plot_silhouettes,
            scale_type='set',
            axis_ticks=5,
            axis_value_labels=False,
            axis_min=axis_min,
            axis_max=axis_max,
            reversed_axes=[False, False, False, False, False, True],
            silhouette_line_color=plot_colors,
            silhouette_line_size=1.5,
            silhouette_line_style='-.',
            silhouette_fill_alpha=0.25,
            axis_value_decimals=2,
            axis_value_dec_list=[0,0,0,0,0,3],
            )

            figure_canvas_agg = FigureCanvasTkAgg(fig, window["Radar"].TKCanvas)
            figure_canvas_agg.draw()
            figure_canvas_agg.get_tk_widget().pack(side="top", fill="both", expand=1)

    window.close()

    return event

if __name__ == '__main__':
    sg.theme('DarkGrey2')
    plot('park')
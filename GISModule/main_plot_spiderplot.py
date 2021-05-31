from numpy.lib.function_base import average
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

def get_gt_count(data):
    features = []
    for fts in data.ground_truth.values():
        features.extend(fts)

    return len(features)

def get_count(stats, source, area, false_positives: bool = False):
    stats = stats[source]
    stats = [stat for stat in stats.values() if stat != None]

    if len(stats) == 0:
        print(f'Could not find precision for source {source} in area {area}, as there were no features. Returning 0.')
        return 0

    tps = [len(stat.true_positives) for stat in stats]
    s = sum(tp for tp in tps if not np.isnan(tp))

    if false_positives:
        fps = [len(stat.false_positives) for stat in stats]
        s += sum(fp for fp in fps if not np.isnan(fp))

    return s

def _get_stats():
    
    title = 'Feature Stats'
    axes_labels = ['True Positives', 'Precision', 'Recall', 'Visibility', 'Accessibility', 'Error']

    gis_data = [GISData(area, use_exclude_property=True) for area in Properties.areas]
    data = [g.get_stats() for g in gis_data]
                    
    labels = set([key for area in data for source in area for key in area[source] if area[source][key] is not None])

    silhouettes = {}
    data = [{key: val for source in area for key, val in zip(area[source].keys(), area[source].values()) if area[source][key] is not None}for area in data]

    for label in labels:
        silhouettes[label] = [0 for _ in axes_labels]

        stats = [d[label] for d in data if label in d]

        # Amount
        silhouettes[label][0] = sum([len(d.true_positives) for d in stats])

        # Precision
        s = [len(d.true_positives) for d in stats]
        n = [len(d.true_positives) + len(d.false_positives) for d in stats]
        silhouettes[label][1] = sum(s) / sum(n) * 100

        # Recall
        s = [len(d.true_positives) for d in stats]
        n = [len(d.true_positives) + len(d.false_negatives) for d in stats]
        silhouettes[label][2] = sum(s) / sum(n) * 100

        # Visibility
        s = [d.get_visibility() * len(d.true_positives) for d in stats if not np.isnan(d.get_visibility())]
        n = [len(d.true_positives) for d in stats if not np.isnan(d.get_visibility())]
        silhouettes[label][3] = sum(s) / sum(n)

        # Accessibility
        s = [d.get_accessibility() * len(d.true_positives) for d in stats if not np.isnan(d.get_accessibility())]
        n = [len(d.true_positives) for d in stats if not np.isnan(d.get_accessibility())]
        silhouettes[label][4] = sum(s) / sum(n)

        # Accuracy
        s = [d.get_accuracy() * len(d.true_positives) for d in stats if not np.isnan(d.get_accuracy())]
        n = [len(d.true_positives) for d in stats if not np.isnan(d.get_accuracy())]
        silhouettes[label][5] = sum(s) / sum(n)
        
    return silhouettes, axes_labels, title

def _get_amount_gt():
    
    title = 'Feature count across areas'
    #labels=['Precision', 'Recall', 'Error', 'Visibility', 'Accessibility', 'True Positives']
    labels = ['Tree', 'Light Fixture', 'Downspout Grille', 'Manhole Cover', 'Bench', 'Trash Can', 'Statue', 'Fuse Box', 'Greenery', 'Chimney']

    silhouettes = {}
    source = 'groundtruth'

    for area in Properties.areas:
        silhouettes[area] = [0] * len(labels)
        gisdata = GISData(area)
        data = gisdata.get_data()

        for i, _ in enumerate(silhouettes[area]):
            if labels[i] in data[source]:        
                silhouettes[area][i] = len(data[source][labels[i]])
        
    return silhouettes, labels, title


def plot(plottype):
    if plottype in [None, '']:
        return plottype

    if plottype == 'plot_stats':
        print('Plotting Radar Chart with stats for each source across areas.')
        silhouettes, labels, title = _get_stats()
    elif plottype == 'plot_amount_gt':
        silhouettes, labels, title = _get_amount_gt()
    else:
        silhouettes, labels, title = _get_stats()

    use("TkAgg")
    
    #plottypes = {'Plot Precision, Recall, Accuracy, Visibility, Accessibility and amount for all features.': 'plot_stats'}

    #plottype = pick_plottype(plottypes.keys())

    #amount_features_average = np.sum([sil for sil in silhouettes.values()], axis=0)

    #print([labels, amount_features_average])

    inputs = {}

    #title = f'{title}'
    export = sg.Button('Export')
    back = sg.Button('Back')

    col = [[export, back]]

    sources = {}

    if plottype == 'plot_stats':
        for silhouette in silhouettes:
            source = Properties.feature_properties[silhouette]['origin']
            if silhouette in Properties.feature_properties and source not in sources:
                sources[source] = []
            sources[source].append(silhouette)

        for source in sources.keys():
            col.append([sg.Text(source.capitalize(), enable_events=True)])

            for i, feature in enumerate(list(sources[source])):
                color = Properties.feature_properties[feature]['color']
                label = Properties.feature_properties[list(sources[source])[i]]['label']

                #label = list(Properties.feature_properties[key]['label'] for key in silhouettes.keys())[i]

                col.append([sg.Checkbox(label, text_color = color, key=feature, enable_events=True)])
                inputs[len(inputs)] = {'type': 'checkbox', 'source': source, 'typename': feature}
    else:
        i = 0
        for silhouette in silhouettes:

            if plottype == 'plot_amount_gt':
                color = Properties.area_colors[silhouette]
            else:
                color = '#FFFFFF'

            label = list(key for key in silhouettes.keys())[i]

            col.append([sg.Checkbox(label, text_color = color, key=silhouette, enable_events=True)])
            inputs[len(inputs)] = {'type': 'checkbox', 'typename': silhouette}
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

            #Set minimum and maximum of all axes
            #axis_min = [0,0,0,0,0,0]
            #axis_max = [100, 100, max(0.1, max(v[2] for v in plot_silhouettes.values())), 100, 100, max(0.1, max(v[5] for v in plot_silhouettes.values()))]
            if plottype == 'plot_amount_gt':
                #plot_colors = [colors[list(silhouettes.keys()).index(key)] for key in plot_silhouettes.keys()]
                colors = [Properties.area_colors[area] for area in plot_silhouettes]
                fig = spider_plot(
                    title,
                    labels=labels,
                    silhouettes=plot_silhouettes,
                    #scale_type='total_max',
                    axis_ticks=5,
                    axis_value_labels=False,
                    #axis_min=axis_min,
                    #axis_max=axis_max,
                    #reversed_axes=[False, False, True, False, False, False],
                    silhouette_line_color=colors,
                    silhouette_line_size=1.5,
                    silhouette_line_style='-.',
                    silhouette_fill_alpha=0.25,
                    axis_value_decimals=0
                    )

            elif plottype == 'plot_stats':
                line_colors = [Properties.feature_properties[ft]['color'] for ft in plot_silhouettes]
                fill_colors = [Properties.source_colors[Properties.feature_properties[ft]['origin']] for ft in plot_silhouettes]

                axis_min = [0,0,0,0,0,0]
                axis_max = [max(0.1, max(v[0] for v in plot_silhouettes.values())), 100, 100, 100, 100, max(0.1, max(v[5] for v in plot_silhouettes.values()))]

                plot_silhouettes = {Properties.feature_properties[key]['label']: plot_silhouettes[key] for key in plot_silhouettes}

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
                    silhouette_line_color=line_colors,
                    silhouette_fill_color=fill_colors,
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
    plot('plot_stats')
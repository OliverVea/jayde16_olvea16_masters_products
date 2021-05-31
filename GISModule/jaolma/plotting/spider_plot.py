import matplotlib.pyplot as plt

import numpy as np

from math import pi, ceil

import PySimpleGUI as sg
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from jaolma.utility.utility import prints

class Axis:
    def __init__(self, values, label: str = '', axis_min: float = None, axis_max: float = None, reversed: bool = False):
        if axis_min == None:
            if len(values) == 0:
                self.min = 0
            else:
                self.min = min(values)
        else:
            self.min = axis_min

        if axis_max == None:
            if len(values) == 0:
                self.max = 1
            else:
                self.max = max(values)
        else:
            self.max = axis_max

        self.label = label
        self.reversed = reversed
        self.scaled = (min != 0 or max != 1)
        self.values = values
        self.norm = [self.normalize(v) for v in values]

    def normalize(self, value):
        if self.reversed:
            return 1 - (value - self.min) / (self.max - self.min)
        return (value - self.min) / (self.max - self.min)
    
    def denormalize(self, normval):
        if self.reversed:
            return (1 - normval) * (self.max - self.min) + self.min
        return normval * (self.max - self.min) + self.min

# title
# labels: list of labels for each axis. e.g. ['strength', 'dexterity', 'intelligence']
# silhouettes: dictionary containing list of values with silhouette label as key. e.g. {'warrior': [15, 13, 9], 'thief': [9, 17, 13], 'mage': [3, 8, 18]}
# scale_type: 
#   'total_max': scales all axes to the total max value. 
#   'total_both': scales both min and max to the total min and max values.
#   'axis_max': scales axes to the max value of that axis. 
#   'axis_both': scales axes to the min and max values of that one axis.
#   'set': uses the axis_max and axis_min values (or lists) to set max and min.

class PolarAxes:
    def __init__(self, fig, titles, labels, rect=None):
        if rect is None:
            rect = [0.05, 0.05, 0.95, 0.95]

        self.n = len(titles)
        self.angles = [a if a <=360. else a - 360. for a in np.arange(90, 90+360, 360.0/self.n)]
        self.axes = [fig.add_axes(rect, projection="polar", label="axes%d" % i) 
                        for i in range(self.n)]

        self.ax = self.axes[0]
        self.ax.set_thetagrids(self.angles, labels=titles, fontsize=12, weight="bold", color="black")

        for ax in self.axes[1:]:
            ax.patch.set_visible(False)
            ax.grid("off")
            ax.xaxis.set_visible(False)
            self.ax.yaxis.grid(False)

        for ax, angle, label in zip(self.axes, self.angles, labels):
            ax.set_rgrids([0.5], labels=['fisk'], angle=angle, fontsize=12)
            ax.spines["polar"].set_visible(False)
            ax.set_ylim(0, 6)  
            ax.xaxis.grid(True,color='black',linestyle='-')

def spider_plot(title: str, labels: list, silhouettes: dict, 
        size: tuple = (5, 5),
        dpi: int = 100,
        axis_min: float = None, 
        axis_max: float = None, 
        axis_value_decimals: int = 3, 
        axis_value_dec_list: list = None,
        axis_value_labels: bool = True, 
        scale_type: str = 'total_max', 
        label_origin: bool = True, 
        silhouette_line_color: str = None, 
        silhouette_line_style: str = 'solid', 
        silhouette_line_size: float = 1, 
        silhouette_fill_color: str = None, 
        silhouette_fill_alpha: float = 0.1, 
        silhouette_value_labels: list = None, 
        reversed_axes: list = None, 
        axis_ticks: int = 5, 
        marker: str = 'o', 
        marker_size: int = 3,
        fill_nan: bool = True,
        legend_loc: str = 'lower left',
        legend_bbox: tuple = (0,0)):

    fig = plt.figure(figsize=size, dpi=dpi)

    #axes = PolarAxes(fig, labels, labels)
    ax = plt.axes(projection='polar')
    ax.set_ylim(0, 1)
    fig.suptitle(title)

    if len(silhouettes) == 0:
        raise Exception('Length of silhouettes should be one or above.')

    n_silhouettes = len(silhouettes)
    n_values = len(list(silhouettes.values())[0])

    if n_values < 1:
        raise Exception('There should be at least one axis.')

    for silhouette in silhouettes.values():
        if len(silhouette) != n_values:
            raise Exception('All silhouettes must have the same amount of axes.')

    # Making axes - primarily code for scaling data along them.
    axes = []
    angles = []
    for i in range(n_values):
        values = [list(silhouettes.values())[j][i] for j in range(n_silhouettes)]

        current_axis_min = None
        current_axis_max = None

        if scale_type == 'axis_max':
            current_axis_min = 0
            pass

        elif scale_type == 'total_max':
            current_axis_min = 0
            current_axis_max = max([max(vals) for vals in silhouettes.values()])
            pass

        elif scale_type == 'axis_both':
            # Default in Axis __init__.
            prints('WARNING: Different minimum values - be careful.', tag='spider_plot')
            pass

        elif scale_type == 'total_both':
            current_axis_min = min([min(vals) for vals in silhouettes.values()])
            current_axis_max = max([max(vals) for vals in silhouettes.values()])
            pass

        elif scale_type == 'set':
            if isinstance(axis_min, list):
                if len(axis_min) != n_values:
                    raise Exception('axis_min should be value or have one value for each axis.')
                current_axis_min = axis_min[i]

                if current_axis_min == None:
                    current_axis_min = min(values)

            if isinstance(axis_max, list):
                if len(axis_max) != n_values:
                    raise Exception('axis_max should be value or have one value for each axis.')
                current_axis_max = axis_max[i]

                if current_axis_max == None:
                    current_axis_max = max(values)

        else:
            raise Exception('scale_type not understood.')

        if (current_axis_min != None and current_axis_max != None) and (current_axis_min >= current_axis_max):
            raise Exception('Axis max-min is 0 or negative.')
        
        reversed = False
        if reversed_axes != None:
            reversed = reversed_axes[i] 

        axis = Axis(values=values, label=labels[i], axis_min=current_axis_min, axis_max=current_axis_max, reversed=reversed)
        angle = 2 * pi * i / float(n_values)

        axes.append(axis)
        angles.append(angle)

    def labelize(val, max_decimals: int):
        if int(val) == val or max_decimals == 0:
            s = (int(val))
        else:
            s = str(round(val, max_decimals))

        return s

    if axis_ticks != None:
        tick_values = [(i + 1) / axis_ticks for i in range(axis_ticks)]

        if axis_value_dec_list != None:
            tick_labels = [[labelize(axes[i].denormalize(v), ax_val_dec) for v in tick_values] for i, ax_val_dec in zip(range(n_values), axis_value_dec_list)]
        else:
            tick_labels = [[labelize(axes[i].denormalize(v), axis_value_decimals) for v in tick_values] for i in range(n_values)]

        ax.set_yticks(tick_values)
        ax.set_yticklabels([])

        for i in range(axis_ticks):
            for j in range(n_values):
                plt.text(angles[j], tick_values[i], tick_labels[j][i], color="black", size=8)

                # skriver kun tekst på 1 akse.
                if False and scale_type in ['total_max', 'total_both']:
                    break
    else:
        ax.set_yticks([])

    _, tick_labels = plt.xticks(angles, ['' for _ in angles])
    
    for label, angle, text in zip(tick_labels, angles, labels):
        rotation = angle*180/pi-90

        # Rotates text so it can be read when its supposed to be upside down.
        if rotation < -90 or rotation > 90:
            rotation += 180

        plt.text(angle, 0, text, 
            transform=label.get_transform(), 
            ha=label.get_ha(), 
            va=label.get_va(),
            rotation=rotation, 
            size=12, 
            color='black')

    curved_angles = []

    for angle in angles:
        curved_angles.extend(np.arange(angle, angle + 2 * pi / n_values, 0.01))

    angles += angles[:1]
    curved_angles += angles[:1]
 
    for i in range(n_silhouettes):
        values = [ax.norm[i] for ax in axes]
        values += values[:1]
        
        if axis_value_labels != False:
            for j in range(n_values):
                if axis_value_labels == True:
                    label = str(axes[j].values[i])
                else:
                    label = axis_value_labels[i][j]

                if label != None:
                    plt.text(angles[j], values[j], label, color="black", size=8)
   
        curved_values = []
        for a, b in zip(values[:-1], values[1:]):
            curved_values.extend(np.linspace(a, b, ceil(2*np.pi/n_values/0.01+1))[:-2])
            curved_values.append(b)
        curved_values += values[:1]

        if silhouette_line_color == None:
            line_color = None
        elif isinstance(silhouette_line_color, list):
            line_color = silhouette_line_color[i]
        else:
            line_color = silhouette_line_color
            
        line = ax.plot(curved_angles, curved_values, color=line_color, linewidth=silhouette_line_size, linestyle=silhouette_line_style, label=list(silhouettes.keys())[i])[0]

        if (not marker in ['', False, None]) and marker_size > 0:
            for angle, value in zip(angles, values):
                ax.plot(angle, value, marker, color=line.get_color(), markersize=marker_size)

        if silhouette_fill_color == None:
            fill_color = line.get_color()
        elif isinstance(silhouette_fill_color, list):
            fill_color = silhouette_fill_color[i]
        else:
            fill_color = silhouette_fill_color

        if fill_nan:
            xy = [(a, v) for a, v in zip(curved_angles, curved_values) if not np.isnan(v)] 

        ax.fill([v[0] for v in xy], [v[1] for v in xy], color=fill_color, alpha=silhouette_fill_alpha)

    plt.legend(loc=legend_loc, bbox_to_anchor=legend_bbox)
    return fig

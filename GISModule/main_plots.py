'''
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import PySimpleGUI as sg
import matplotlib

fig = matplotlib.figure.Figure(figsize=(5, 4), dpi=100)
t = np.arange(0, 3, .01)
fig.add_subplot(111).plot(t, 2 * np.sin(2 * np.pi * t))

matplotlib.use("TkAgg")

def draw_figure(canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side="top", fill="both", expand=1)
    return figure_canvas_agg

# Define the window layout
layout = [
    [sg.Text("Plot test")],
    [sg.Canvas(key="-CANVAS-")],
    [sg.Button("Ok")],
]

# Create the form and show it without the plot
window = sg.Window(
    "Matplotlib Single Graph",
    layout,
    location=(0, 0),
    finalize=True,
    element_justification="center",
    font="Helvetica 18",
)

# Add the plot to the window
draw_figure(window["-CANVAS-"].TKCanvas, fig)

event, values = window.read()

window.close()
'''


import  matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import interpolate


df = pd.DataFrame({'measure':[10, 0, 10,0,20, 20,15,5,10], 'angle':[0,45,90,135,180, 225, 270, 315,360]})

angles = [y/180*np.pi for x in [np.arange(x, x+45,0.1) for x in df.angle[:-1]] for y in x]
values = [y for x in [np.linspace(x, df.measure[i+1], 451)[:-1] for i, x in enumerate(df.measure[:-1])] for y in x]
angles.append(360/180*np.pi)
values.append(values[0])


# Initialise the spider plot
#plt.figure(figsize=(12,8))
fig, axs = plt.subplots(2,2, figsize=(10,10), dpi=100)
ax = plt.subplot(221, projection='polar')
#axs[0,0] = plt.subplot(polar=True)

# Plot data
ax.plot(angles, values, linewidth=1, linestyle='solid', label='Interval linearisation')

ax.legend()

# Fill area
ax.fill(angles, values, 'b', alpha=0.1)

plt.show()

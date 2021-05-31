import PySimpleGUI as sg

def simple_dropdown(title: str, values: list):
    dd = sg.DropDown(values, default_value=values[0])
    bo = sg.Button('OK')
    bc = sg.Button('Cancel')

    layout = [[dd, bo, bc]]

    window = sg.Window(title, layout)

    while True:
        event, values = window.read()

        if event == 'Cancel' or event == sg.WIN_CLOSED:
            value = None
            break

        if event == 'OK':
            value = values[0]
            break

    window.close()
    return value
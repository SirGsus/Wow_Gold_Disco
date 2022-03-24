import win32gui
from contextlib import redirect_stdout
import os


class WindowFrame:
    '''Describes a window-frame object'''
    def __init__(self, hwnd, window_name):
        self.hwnd = hwnd
        self.window_name = window_name


def win_enum_handler(hwnd, ctx):
    '''Helper function for win32gui.EnumWindows'''
    if win32gui.IsWindowVisible(hwnd):
        print(hex(hwnd), win32gui.GetWindowText(hwnd))
        return hwnd


def get_all_hwnds(debugging=False):
    '''Returns a list of all active windows as WindowFrame objects'''
    with open('temp.txt', 'w') as f:
        with redirect_stdout(f):
            win32gui.EnumWindows(win_enum_handler, None)

    hwnds = []

    with open('temp.txt', 'r', encoding='windows-1252') as file:
        for line in file:
            temp_line = line.split(' ')
            # Remove the '\n'-characters within the window name string
            for elem_num in range(len(temp_line)):
                if temp_line[elem_num] == '\n':
                    temp_line[elem_num] = ''
                if '\n' in temp_line[elem_num]:
                    temp_line[elem_num] = temp_line[elem_num][:-1]
            #ToDo: Check the generation of the string name again, because Fortnite still has got some blanc spaces left, behind its name
            hwnd_obj = WindowFrame(str(temp_line[0]), str(' '.join(temp_line[1:])))
            hwnds.append(hwnd_obj)

    if debugging:
        for handler in hwnds:
            print("Hwnd: " + str(handler.hwnd) + ", Window name: " + str(handler.window_name))

    os.remove("temp.txt")

    return hwnds

# Debugging
get_all_hwnds(debugging=True)
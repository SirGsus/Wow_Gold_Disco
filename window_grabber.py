import win32gui, win32ui, win32con, win32api
import cv2
import numpy as np
import mss
from hwnd_scan import get_all_hwnds
import time

## Settings
window_name = 'World of Warcraft'  # ToDo: Check why the window name contains two space chars at the end
## End of settings


def match_template(img, template, debug=False):
    """ToDo: Template matching has to be for a color image!"""
    '''methods = [cv2.TM_CCOEFF, cv2.TM_CCOEFF_NORMED, cv2.TM_CCORR,
               cv2.TM_CCORR_NORMED, cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]'''

    method = cv2.TM_SQDIFF
    img2 = img.copy()

    result = cv2.matchTemplate(img2, template, method)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
        location = min_loc
    else:
        location = max_loc

    if debug:
        temp_h, temp_w = template.shape
        bottom_right = (location[0] + temp_w, location[1] + temp_h)
        cv2.rectangle(img2, location, bottom_right, 255, 1)
        cv2.imshow('Match', img2)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    return location


def get_screenshot(region=None):
    hwin = win32gui.GetDesktopWindow()

    if region:
        left, top, x2, y2 = region
        width = x2 - left + 1
        height = y2 - top + 1

    else:
        width = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
        height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)
        left = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
        top = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)

    hwindc = win32gui.GetWindowDC(hwin)
    srcdc = win32ui.CreateDCFromHandle(hwindc)
    memdc = srcdc.CreateCompatibleDC()
    bmp = win32ui.CreateBitmap()
    bmp.CreateCompatibleBitmap(srcdc, width, height)
    memdc.SelectObject(bmp)
    memdc.BitBlt((0, 0), (width, height), srcdc, (left, top), win32con.SRCCOPY)

    signedIntsArray = bmp.GetBitmapBits(True)
    img = np.frombuffer(signedIntsArray, dtype='uint8')
    img.shape = (height, width, 4)

    srcdc.DeleteDC()
    memdc.DeleteDC()
    win32gui.ReleaseDC(hwin, hwindc)
    win32gui.DeleteObject(bmp.GetHandle())

    return cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)


class GameCapture():
    """Handles the whole process of game window capturing"""

    def __init__(self, name):
        """
        :param name:
        :param activation_range: 300 for Fortnite
        """
        self.name = name
        self.w = None
        self.h = None
        self.x = None
        self.y = None
        self.hwnd = None

        hwnds = get_all_hwnds()

        # Get the respective hwnd
        for element in hwnds:
            # Check if the given string is in the window name,
            # No self.name == element. window_name because some window names contain ' '-characters at the end
            if self.name in element.window_name:
                self.hwnd = int(element.hwnd, 16)
                break

        if self.hwnd == None:
            raise Exception('Window not found: {}'.format(window_name))

        # Get the window size and coordinates
        window_rect = win32gui.GetWindowRect(self.hwnd)
        self.x = window_rect[0]
        self.y = window_rect[1]
        self.w = window_rect[2] - window_rect[0]
        self.h = window_rect[3] - window_rect[1]

    def grab_screen(self, shift_x, shift_y, activation_range_x, activation_range_y, monitor_center=False, debug=False,
                    return_array=True):
        """
        shift_x: shifts the origbox to the left for positive values
        shift_y: shifts the origbox up for positive values
        """

        if monitor_center:
            sct = mss.mss()
            window_width, window_height = sct.monitors[1]["width"], sct.monitors[1]["height"]

        else:
            window_width = self.w
            window_height = self.h

        W, H = None, None
        origbox = (int(self.x + (window_width / 2) - activation_range_x / 2 - shift_x),
                   int(self.y + (window_height / 2) - activation_range_y / 2 - shift_y),
                   int(self.x + (window_width / 2) + activation_range_x / 2 - shift_x),
                   int(self.y + (window_height / 2) + activation_range_y / 2 - shift_y))

        frame = np.array(get_screenshot(region=origbox))
        frame = cv2.cvtColor(frame, cv2.COLOR_RGBA2BGR)

        # if the frame dimensions are empty, grab them
        if W is None or H is None:
            (H, W) = frame.shape[: 2]

        frame = cv2.UMat(frame)

        if debug:
            cv2.imshow('Bot view', frame)

            if cv2.waitKey(1) == ord('q'):
                cv2.destroyAllWindows()

        if return_array:
            #frame_gray = cv2.cvtColor(frame.get(), cv2.COLOR_BGR2GRAY)
            #return frame_gray
            frame_color = frame.get()
            return frame_color

        else:
            return frame




game_window = GameCapture(window_name)

print(game_window.hwnd)
print(game_window.name)

frame = game_window.grab_screen(shift_x=336.5, shift_y=226.5, activation_range_x=10, activation_range_y=6)

print(frame.shape)
print(cv2.imread('templates/non_combat.png', 1).shape)

test = match_template(frame, cv2.imread('templates/non_combat.png', 1))
print(test)
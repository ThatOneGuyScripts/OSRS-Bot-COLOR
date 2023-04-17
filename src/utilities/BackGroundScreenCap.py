import win32gui
import win32ui
import numpy as np
from ctypes import windll
window_title = None
def get_image():
    Window_Name = window_title
    # Get the window handle
    hwnd = win32gui.FindWindow(None, Window_Name)

    # Change the line below depending on whether you want the whole window
    # or just the client area.
    left, top, right, bot = win32gui.GetWindowRect(hwnd)
    w = right - left
    h = bot - top

    hwndDC = win32gui.GetWindowDC(hwnd)
    mfcDC = win32ui.CreateDCFromHandle(hwndDC)
    saveDC = mfcDC.CreateCompatibleDC()

    saveBitMap = win32ui.CreateBitmap()
    saveBitMap.CreateCompatibleBitmap(mfcDC, w, h)

    saveDC.SelectObject(saveBitMap)

    # Change the line below depending on whether you want the whole window
    # or just the client area.
    # result = windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 1)
    result = windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 2)

    bmpinfo = saveBitMap.GetInfo()
    bmpstr = saveBitMap.GetBitmapBits(True)

    # Create a numpy array from the bitmap bits
    img = np.frombuffer(bmpstr, dtype=np.uint8)
    img.shape = (bmpinfo['bmHeight'], bmpinfo['bmWidth'], 4)

    # Remove the alpha channel from the image
    img = img[:, :, :3]

    win32gui.DeleteObject(saveBitMap.GetHandle())
    saveDC.DeleteDC()
    mfcDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwndDC)

    return img
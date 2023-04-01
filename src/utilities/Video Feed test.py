import win32gui
import win32ui
import numpy as np
import cv2
from ctypes import windll
import pyautogui

Window_Name = "RuneLite"
# Get the window handle
hwnd = win32gui.FindWindow(None, Window_Name)

# Change the line below depending on whether you want the whole window
# or just the client area.
# left, top, right, bot = win32gui.GetClientRect(hwnd)
left, top, right, bot = win32gui.GetWindowRect(hwnd)
w = right - left
h = bot - top

hwndDC = win32gui.GetWindowDC(hwnd)
mfcDC = win32ui.CreateDCFromHandle(hwndDC)
saveDC = mfcDC.CreateCompatibleDC()

saveBitMap = win32ui.CreateBitmap()
saveBitMap.CreateCompatibleBitmap(mfcDC, w, h)

saveDC.SelectObject(saveBitMap)

# Create an OpenCV window to display the video feed
cv2.namedWindow(Window_Name, cv2.WINDOW_NORMAL)

while True:
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

    # Resize the windows to match the captured image size
    cv2.resizeWindow(Window_Name, img.shape[1], img.shape[0])

    # Display the image in the OpenCV window
    cv2.imshow(Window_Name, img)


    # Exit the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

win32gui.DeleteObject(saveBitMap.GetHandle())
saveDC.DeleteDC()
mfcDC.DeleteDC()
win32gui.ReleaseDC(hwnd, hwndDC)


cv2.destroyAllWindows()

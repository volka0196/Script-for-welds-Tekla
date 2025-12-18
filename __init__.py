import pytesseract      # type: ignore
import pyautogui        # type: ignore
import re               # type: ignore
import time             # type: ignore
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

pyautogui.click(1500, 40)
def weld_prefix():
    region = (1520, 505, 400, 15)
    region1 = (1520, 505, 200, 15)
    pyautogui.screenshot(region=region).save('my_screen.png')
    pyautogui.screenshot(region=region1).save('my_screen1.png')
    screen = pyautogui.screenshot(region=region)
    text = pytesseract.image_to_string(screen)
    mark = re.search(r"(.+)", text, re.IGNORECASE)
    screen1 = pyautogui.screenshot(region=region1)
    text1 = pytesseract.image_to_string(screen1)
    mark1 = re.search(r"(.+)", text1, re.IGNORECASE)
    if mark or mark1:
        print(mark)
        print(mark1)


weld_prefix()
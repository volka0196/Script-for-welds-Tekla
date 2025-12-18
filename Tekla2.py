import re
import time
import keyboard         # type: ignore
import pyautogui        # type: ignore
import threading
import pytesseract      # type: ignore
from Tekla_lib import load_config   # type: ignore
from Tekla_lib import to_integer    # type: ignore
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


config = load_config()    #imported

class ScriptController:
    def __init__(self):
        self.running = True
        self.n = None
        self.ready = False


    def start(self):
        shortcut = config["script_hotkeys"]
        print("Hi, hotkeys for controlling the script")
        print(f"Start: {shortcut['start']}")
        print(f"Stop: {shortcut['stop']}")
        keyboard.add_hotkey(shortcut["start"], self.thread1)
        keyboard.add_hotkey(shortcut["stop"], self.stop_program)


    def setup(self):
        print("how many drawings?")
        self.n = to_integer()   #imported


    def loop(self):
        while self.running:
            self.setup()
            self.ready = True
            print("Waiting for start")
            while self.ready and self.running:
                time.sleep(0.1)


    def stop_program(self):
        self.running = False


    def thread1(self):
        thread = threading.Thread(target=self.main)
        thread.start()


    def main(self):
        current_time = self.time_for_files()
        for i in range(self.n):
            print(f"Drawing {i+1}/{self.n}")
            mark = self.mark_lists(current_time)
            self.weld_loop()
            if not self.waiting_time(mark, config["timeout"]):
                break


        print("Endpoint")
        self.ready = False


    def time_for_files(self):
        current_time = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())
        return current_time


    def waiting_time(self, mark, timeout):
        print(f"Waiting for next drawing (timeout: {timeout}s)...")
        start_time = time.time()
        while time.time() - start_time < timeout:
            if mark != self.text_for_mark():
                return True
            time.sleep(config["time_between_attempts"])
        print("Timeout")
        return False


    def text_for_mark(self):
        region = config["text_region"]

        print("Searching for drawing name...")
        region = (region["x"], region["y"], region["width"], region["height"])
        screen = pyautogui.screenshot(region=region)
        text = pytesseract.image_to_string(screen)
        mark = re.search(r"\[(.+)[_ ]\[(.+)..", text, re.IGNORECASE)
        if mark:
            return mark.group(2)
        return None


    def mark_lists(self, current_time):
        mark = self.text_for_mark()
        print("Writing mark to files...")
        if mark:
            with open(f"{current_time}_mark_list-for_model.txt", "a") as file:
                file.write(f"{mark.replace('.', '-')}\n")
            with open(f"{current_time}_mark_list.for_drawing.txt", "a") as file:
                file.write(f"{mark}\n")
            print("Writing complete")
        else:
            with open(f"{current_time}_mark_list-for_model.txt", "a") as file:
                file.write("No mark found\n")
            with open(f"{current_time}_mark_list.for_drawing.txt", "a") as file:
                file.write("No mark found\n")
            print("Not written")
        return mark


    def weld_loop(self):
        locate = self.locate_png("weld.png")
        self.locate_center(locate)
        print("all welds fixed")
        pyautogui.click(1500, 40)
        self.next_drawing()


    def locate_png(self, name_png):
        try:
            return pyautogui.locateAllOnScreen(name_png, confidence=config["confidence"])
        except pyautogui.ImageNotFoundException:
            return None


    def locate_center(self, locate):
        if locate:
            for l in locate:
                center_png = pyautogui.center(l)
                self.fix_weld(center_png)
        else:
            print("not found")


    def fix_weld(self, center_png):
        pyautogui.moveTo(center_png)
        pyautogui.doubleClick()
        if self.weld_prefix():
            pyautogui.click(1650, 510)
            pyautogui.press("z")
            pyautogui.click(1900, 510)
            pyautogui.press("z")
            pyautogui.click(1730,1025)


    def weld_prefix(self):
        region = (1520, 505, 400, 15)
        screen = pyautogui.screenshot(region=region)
        text = pytesseract.image_to_string(screen)
        mark = re.search(r"(z)", text, re.IGNORECASE)
        if mark:
            print(mark.group(1))
            return False
        return True


    def next_drawing(self):
        hotkey_tekla = config["tekla_hotkeys"]

        pyautogui.click()
        pyautogui.hotkey(hotkey_tekla["next_drawing"])
        pyautogui.press("space")


if __name__ == "__main__":
    script = ScriptController()
    script.start()
    script.loop()

from PIL import ImageGrab, Image
import pyautogui as pgui
import time
import threading
from settings import *
import keyboard
import pytesseract
from pytesseract import TesseractNotFoundError
import re

# -----------------------------------------
# author: 6Osama9 + OCR integration fix
# -----------------------------------------

attacking = False
area = (0, 0, 300, 300)  # 300x300 top-left (area of resources)
width, height = pgui.size()
threads = []
rem = 0
pytesseract.pytesseract.tesseract_cmd = r"X:\tesseract\tesseract.exe"

# takes a screenshot of given area
def create_screenshot(area: tuple[int, int, int, int]) -> None:
    ImageGrab.grab(area).save('resources.png')

# simple OCR extraction from the last screenshot
# returns zeros if Tesseract is missing
def extract_resources() -> dict:
    try:
        img = Image.open('resources.png')
        raw = pytesseract.image_to_string(img, config='--psm 6 digits')
        nums = re.findall(r"\d+", raw)
        gold, elixier, dark = (int(n) for n in nums[:3])
        return {'gold': gold, 'elixier': elixier, 'dark': dark}
    except (TesseractNotFoundError, KeyboardInterrupt):
        return {'gold': 1, 'elixier': 0, 'dark': 0}

# countdown timer
def counter(duration: int = 30) -> None:
    global rem
    duration *= 60
    for rem in range(duration, -1, -1):
        m, s = divmod(rem, 60)
        print(f"\r{m:02d}:{s:02d}", end="")
        time.sleep(1)
    return "time over!"

# unit spamming logic
def spam_units(attack_type: str) -> None:
    if attack_type == 'all':
        keybinds = "123456789asdfghjy"
        pgui.moveTo(x=int(width * (1755 / width)), y=int(height * (525 / height)))
        for key in keybinds:
            pgui.press(key, interval=0.1)
            time.sleep(0.2)
            pgui.leftClick()
            time.sleep(0.1)
            
    else:
        return

# attack logic with OCR readings
def search_attack():
    keyboard.wait(start_button)  # start attacking button

    pgui.leftClick(x=100, y=height - 100)
    time.sleep(0.5)
    pgui.leftClick(x=int(width * (1375 / width)), y=int(height * (600 / height)))

    while rem > 0:
        time.sleep(7)
        create_screenshot(area)
        res = extract_resources()
        print(f" Gold={res['gold']}  Elixier={res['elixier']}  Dark={res['dark']}")

        if res['gold'] < minimum_gold or res['elixier'] < minimum_elixer or res['dark'] < minimum_dark_elixer:
            pgui.leftClick(x=int(width * (1780 / width)), y=int(height * (800 / height)))
        else:
            spam_units('all')
            

if __name__ == "__main__":
    t = input("Enter runtime (minutes): ")

    # define threads
    timer_thread = threading.Thread(
        target=counter,
        args=(int(t),),
        daemon=True
    )
    threads.append(timer_thread)

    attack_thread = threading.Thread(
        target=search_attack,
        daemon=True
    )
    threads.append(attack_thread)

    # start threads
    for thr in threads:
        thr.start()

    # wait for finish
    for thr in threads:
        thr.join()

    print("*--done--*")

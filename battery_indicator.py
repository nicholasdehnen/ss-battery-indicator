import sys
import time
import threading
import pystray
import rivalcfg
import PySimpleGUI as sg
import winsound

from os.path import join, dirname, realpath
from PIL import Image, ImageDraw, ImageFont

# set assets path
assets_path = join(dirname(realpath(__file__)), 'assets')

def create_icon(width, height, battery_level):
    if type(battery_level) is int:
        pct = battery_level / 100
        red = min(255, (1.0-pct)*2 * 255)
        green = min(255, (pct)*2 * 255)
        color = (int(red), int(green), 0)
    else:
        color = (255, 255, 0) # yellow
    font = ImageFont.truetype("arial.ttf", 18)
    image = Image.new('RGB', (width, height), color)
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, width, height), fill=color)
    _, _, w, h = draw.textbbox((0, 0), f'{battery_level}', font=font)
    draw.text(((width-w)/2, (height-h)/2), f'{battery_level}', fill=(0, 0, 0), font=font)
    return image


def get_battery_level(device: rivalcfg.mouse.Mouse):
    return device.battery['level'] if device.battery['level'] else '?'


def get_valid_battery_level(device: rivalcfg.mouse.Mouse):
    battery_level = -1
    while type(battery_level) is int and (battery_level < 0 or battery_level > 100):
        battery_level = get_battery_level(device)
    return battery_level


def _notify_user_thread(message, timeout=3000, sound=True):
    header = [sg.Text('Battery Indicator', font=('Arial', 24), text_color='black', background_color='lightgrey', justification='center')]
    text = [sg.Text(message, font=('Arial', 18), text_color='black', background_color='lightgrey')]
    window = sg.Window('Battery Indicator', [[header, text]], background_color='lightgrey',
                       no_titlebar=True, keep_on_top=True, finalize=True)
    
    # play sound
    if sound:
        winsound.PlaySound(realpath(join(assets_path,'72127__kizilsungur__sweetalertsound3.wav')), winsound.SND_FILENAME | winsound.SND_ASYNC)

    # show window and disappear after 3 seconds
    w, _ = window.get_screen_size()
    wx, hx = window.size
    window.move(w-int(1.25*wx), int(0.5*hx))
    window(timeout=timeout)
    window.close()
    
    # prevent pysimplegui from crashing
    sg.Window.hidden_master_root.destroy()
    sg.Window.hidden_master_root = None
    del window


def notify_user(message):
    t = threading.Thread(target=_notify_user_thread, args=[message])
    t.start()


def main():
    device = rivalcfg.get_first_mouse()
    if device is None:
        sg.popup('No SteelSeries mouse detected. Please connect one and try again.')
        sys.exit(1)
    
    warn_once = False
    run_event = threading.Event()
    
    def stop_running():
        icon.stop()
        run_event.set()
        
    menu = pystray.Menu(pystray.MenuItem('Exit', lambda: stop_running()))
    icon = pystray.Icon('Battery Indicator',
                        icon=create_icon(32, 32, '?'),
                        menu=menu)
    print('Launching thread..')
    threading.Thread(target=lambda: icon.run()).start()
    print('Thread launched.')
    
    # wait for icon to launch
    while not icon._running:
        time.sleep(0.05)
    
    notify_user('Mouse battery indicator started.')
    
    while not run_event.is_set():
        battery_level = get_valid_battery_level(device)
        print(f'Battery level: {battery_level}')
        
        # sanity check, rivalcfg returns weird stuff sometimes
        if battery_level > 0 and battery_level < 100:
            icon.icon = create_icon(32, 32, battery_level)
        
        # warn once on low battery
        if not warn_once and battery_level < 15:
            message = f'Mouse battery low!!({battery_level}%)'
            notify_user(message)
            warn_once = True
        elif warn_once and battery_level > 15:
            warn_once = False
            
        run_event.wait(60) # check every minute

if __name__ == '__main__':
    main()
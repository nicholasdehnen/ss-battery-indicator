import sys
import time
import threading
import pystray
import rivalcfg
import PySimpleGUI as sg

from os.path import join, dirname, realpath
from plyer import notification
from PIL import Image, ImageDraw, ImageFont


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

def notify_user(message):
    notification.notify(**{'title': 'Battery Indicator',
                             'message': message,
                             'app_icon': join(dirname(realpath(__file__)),
                                          'assets/mouse_icon_selman_design.ico'),
                             'toast': False})

def main():
    device = rivalcfg.get_first_mouse()
    if device is None:
        sg.popup('No SteelSeries mouse detected. Please connect one and try again.')
        sys.exit(1)
        
    menu = pystray.Menu(pystray.MenuItem('Exit', lambda: icon.stop()))
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
    
    warn_once = False
    while icon._running:
        battery_level = get_valid_battery_level(device)
        print(f'Battery level: {battery_level}')
        
        # sanity check, rivalcfg returns weird stuff sometimes
        if battery_level > 0 and battery_level < 100:
            icon.icon = create_icon(32, 32, battery_level)
        
        # warn once on low battery
        if not warn_once and battery_level < 15:
            message = f'Mouse battery low!!({get_battery_level(device)}%)'
            notify_user(message)
            warn_once = True
        elif warn_once and battery_level > 15:
            warn_once = False
            
        time.sleep(60.0)

if __name__ == '__main__':
    main()
from pynput import mouse
from pynput import keyboard
import time
import json
import sys

n = len(sys.argv)

if n < 2:
    exit("Takes a compulsory argument - name of recording, and optional argument - record-all")

if n > 3:
    exit("Only takes two arguments - name of recording and (optional) record-all")

if n == 2:
    name_of_recording = str(sys.argv[1])
    record_all = False
if n == 3:
    if str(sys.argv[2]) != "record-all":
        exit("The second argument given must be 'record-all', otherwise only pass the name of recording as a parameter")
    name_of_recording = str(sys.argv[1])
    record_all = True

print("Press 'esc' to end recording.")

storage = []
count = 0

def on_press(key):
    try:
        json_object = {'action':'pressed_key', 'key':key.char, '_time': time.time()}
    except AttributeError:
        if key == keyboard.Key.esc:
            return False
        json_object = {'action':'pressed_key', 'key':str(key), '_time': time.time()}
    storage.append(json_object)

def on_release(key):
    try:
        json_object = {'action':'released_key', 'key':key.char, '_time': time.time()}
    except AttributeError:
        json_object = {'action':'released_key', 'key':str(key), '_time': time.time()}
    storage.append(json_object)
        

def on_move(x, y):
    if (record_all) == True:
        if len(storage) >= 1:
            if storage[-1]['action'] != "moved":
                json_object = {'action':'moved', 'x':x, 'y':y, '_time':time.time()}
                storage.append(json_object)
            elif storage[-1]['action'] == "moved" and time.time() - storage[-1]['_time'] > 0.02:
                json_object = {'action':'moved', 'x':x, 'y':y, '_time':time.time()}
                storage.append(json_object)
        else:
            json_object = {'action':'moved', 'x':x, 'y':y, '_time':time.time()}
            storage.append(json_object)
    else:
        if len(storage) >= 1:
            if (storage[-1]['action'] == "pressed" and storage[-1]['button'] == 'Button.left') or (storage[-1]['action'] == "moved" and time.time() - storage[-1]['_time'] > 0.02):
                json_object = {'action':'moved', 'x':x, 'y':y, '_time':time.time()}
                storage.append(json_object)

def on_click(x, y, button, pressed):
    json_object = {'action':'pressed' if pressed else 'released', 'button':str(button), 'x':x, 'y':y, '_time':time.time()}
    storage.append(json_object)

def on_scroll(x, y, dx, dy):
    json_object = {'action': 'scroll', 'vertical_direction': int(dy), 'horizontal_direction': int(dx), 'x':x, 'y':y, '_time': time.time()}
    storage.append(json_object)

# Collect events until exit key is pressed (handled in on_press)
with keyboard.Listener(on_press=on_press, on_release=on_release) as keyboard_listener:
    with mouse.Listener(on_click=on_click, on_scroll=on_scroll, on_move=on_move) as mouse_listener:
        keyboard_listener.join()  # pause script until keyboard listener exits

# Dump storage into outfile
with open('data/{}.txt'.format(name_of_recording), 'w') as outfile:
    json.dump(storage, outfile)
print('Input recording stopped and saved.')
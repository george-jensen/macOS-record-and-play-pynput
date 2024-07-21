from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Key, Controller as KeyboardController
import time, json, sys

# parse args

n = len(sys.argv)

if n != 4 and n != 5:
	exit("Usage: python play.py {name of recording} {number of plays} {delay before playing (in seconds)} [delta time in between two action (in ms, will use recoding's delta times otherwise)]")

name_of_recording = "data/" + str(sys.argv[1]) +'.txt'
number_of_plays = int(sys.argv[2])
delay = int(sys.argv[3])
dt = int(sys.argv[4]) if n == 5 else None

if number_of_plays <= 0:
	exit("number of plays must be a positive number")

if delay < 0:
	exit("delay must be 0 or a positive number (in seconds)")

if dt < 0:
	exit("delta time must be 0 or a positive number (in ms)")

dt /= 1000

try:
	with open(name_of_recording) as json_file:
		data = json.load(json_file) 
except FileNotFoundError:
	exit(f'recording "{name_of_recording}" not found')

special_keys = {"Key.shift": Key.shift, "Key.tab": Key.tab, "Key.caps_lock": Key.caps_lock, "Key.ctrl": Key.ctrl, "Key.alt": Key.alt, "Key.cmd": Key.cmd, "Key.cmd_r": Key.cmd_r, "Key.alt_l": Key.alt_l, "Key.alt_r": Key.alt_r, "Key.ctrl_l": Key.ctrl_l, "Key.ctrl_r": Key.ctrl_r, "Key.shift_r": Key.shift_r, "Key.enter": Key.enter, "Key.backspace": Key.backspace, "Key.f19": Key.f19, "Key.f18": Key.f18, "Key.f17": Key.f17, "Key.f16": Key.f16, "Key.f15": Key.f15, "Key.f14": Key.f14, "Key.f13": Key.f13, "Key.media_volume_up": Key.media_volume_up, "Key.media_volume_down": Key.media_volume_down, "Key.media_volume_mute": Key.media_volume_mute, "Key.media_play_pause": Key.media_play_pause, "Key.f6": Key.f6, "Key.f5": Key.f5, "Key.right": Key.right, "Key.down": Key.down, "Key.left": Key.left, "Key.up": Key.up, "Key.page_up": Key.page_up, "Key.page_down": Key.page_down, "Key.home": Key.home, "Key.end": Key.end, "Key.delete": Key.delete, "Key.space": Key.space}

mouse = MouseController()
keyboard = KeyboardController()

time.sleep(delay)

if dt == None:
	for loop in range(number_of_plays):
		for index, obj in enumerate(data):
			action, _time = obj['action'], obj['time']
			try:
				next_movement = data[index+1]['time']
				pause_time = next_movement - _time
			except IndexError as e:
				pause_time = 1
			
			if action == "pressed_key" or action == "released_key":
				key = obj['key'] if 'Key.' not in obj['key'] else special_keys[obj['key']]
				print("action: {}, time: {}, key: {}".format(action, _time, str(key)))
				if action == "pressed_key":
					keyboard.press(key)
				else:
					keyboard.release(key)
				time.sleep(pause_time)

			else:
				move_for_scroll = True
				x, y = obj['x'], obj['y']
				if action == "scroll" and index > 0 and (data[index - 1]['action'] == "pressed" or data[index - 1]['action'] == "released"):
					if x == data[index - 1]['x'] and y == data[index - 1]['y']:
						move_for_scroll = False
				print("x: {}, y: {}, action: {}, time: {}".format(x, y, action, _time))
				mouse.position = (x, y)
				if action == "pressed" or action == "released" or action == "scroll" and move_for_scroll == True:
					time.sleep(0.1)
				if action == "pressed":
					mouse.press(Button.left if obj['button'] == "Button.left" else Button.right)
				elif action == "released":
					mouse.release(Button.left if obj['button'] == "Button.left" else Button.right)
				elif action == "scroll":
					horizontal_direction, vertical_direction = obj['horizontal_direction'], obj['vertical_direction']
					mouse.scroll(horizontal_direction, vertical_direction)
				time.sleep(pause_time)
else:
	for loop in range(number_of_plays):
		for index, obj in enumerate(data):
			action = obj['action']
			
			if action == "pressed_key" or action == "released_key":
				key = obj['key'] if 'Key.' not in obj['key'] else special_keys[obj['key']]
				print("action: {}, key: {}".format(action, str(key)))
				if action == "pressed_key":
					keyboard.press(key)
				else:
					keyboard.release(key)

			else:
				move_for_scroll = True
				x, y = obj['x'], obj['y']
				if action == "scroll" and index > 0 and (data[index - 1]['action'] == "pressed" or data[index - 1]['action'] == "released"):
					if x == data[index - 1]['x'] and y == data[index - 1]['y']:
						move_for_scroll = False
				print("x: {}, y: {}, action: {}".format(x, y, action))
				mouse.position = (x, y)
				if action == "pressed" or action == "released" or action == "scroll" and move_for_scroll == True:
					time.sleep(0.1)
				if action == "pressed":
					mouse.press(Button.left if obj['button'] == "Button.left" else Button.right)
				elif action == "released":
					mouse.release(Button.left if obj['button'] == "Button.left" else Button.right)
				elif action == "scroll":
					horizontal_direction, vertical_direction = obj['horizontal_direction'], obj['vertical_direction']
					mouse.scroll(horizontal_direction, vertical_direction)
			
			time.sleep(dt)
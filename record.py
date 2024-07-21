from pynput import mouse, keyboard
from pynput.keyboard import Key
import time, json, sys

# parse args

n = len(sys.argv)

if n != 4 and n != 5:
	exit('Usage: python record.py {"keyboard", "mouse" or "both"} {name of recording} {delay before recording (in seconds)} [record-mouse-movement]')

what_to_record = str(sys.argv[1])
if what_to_record not in ["keyboard", "mouse", "both"]:
	exit('what to record must be either "keyboard", "mouse" or "both"')
record_keyboard = what_to_record == "both" or what_to_record == "keyboard"
record_mouse = what_to_record == "both" or what_to_record == "mouse"
name_of_recording = str(sys.argv[2])
delay = int(sys.argv[3])
record_mouse_movement = str(sys.argv[4]) == "record-mouse-movement" if n == 5 else False

if delay < 0:
	exit("delay must be 0 or a positive number (in seconds)")

storage = []

# keyboard related callbacks

ctrl_keys = {
	"'\\x01'": 'a',
	"'\\x1a'": 'z',
	"'\\x05'": 'e',
	"'\\x12'": 'r',
	"'\\x14'": 't',
	"'\\x19'": 'y',
	"'\\x15'": 'u',
	"'\\t'": 'i',
	"'\\x0f'": 'o',
	"'\\x10'": 'p',
	"'\\x11'": 'q',
	"'\\x13'": 's',
	"'\\x04'": 'd',
	"'\\x06'": 'f',
	"'\\x07'": 'g',
	"'\\x08'": 'h',
	"'\\n'": 'j',
	"'\\x0b'": 'k',
	"'\\x0c'": 'l',
	"'\\r'": 'm',
	"'\\x17'": 'w',
	"'\\x18'": 'x',
	"'\\x03'": 'c',
	"'\\x16'": 'v',
	"'\\x02'": 'b',
	"'\\x0e'": 'n'
}

ctrl_pressed = False
shift_pressed = False

def on_press(key):
	global ctrl_pressed, shift_pressed
	
	key_str = str(key)
	done = False
	
	if key_str == 'Key.ctrl_l' or key_str == 'Key.ctrl_r':
		if not ctrl_pressed:
			json_object = {'action': 'pressed_key', 'key': 'Key.ctrl_l', 'time': time.time()}
			storage.append(json_object)
		ctrl_pressed = True
		print("> CTRL ON <")
		done = True
	
	if key_str == 'Key.shift':
		if not shift_pressed:
			json_object = {'action': 'pressed_key', 'key': 'Key.shift', 'time': time.time()}
			storage.append(json_object)
		shift_pressed = True
		print("> SHIFT ON <")
		done = True

	if done: return

	if ctrl_pressed:
		# if key_str not in ctrl_keys:
		# 	print("unsupported ctrl key ({})".format(key_str))
		# 	return

		# risky, for debugging I would recommend uncommenting the code above and see
		# this is good enough for now (we might end up hardcoding every key in ctrl_keys)
		ctrl_key = ctrl_keys[key_str] if key_str in ctrl_keys else key_str
		
		json_object = {'action': 'pressed_key', 'key': ctrl_key, 'time': time.time()}
	else:
		try:
			json_object = {'action': 'pressed_key', 'key': key.char, 'time': time.time()}
		except AttributeError:
			json_object = {'action': 'pressed_key', 'key': str(key), 'time': time.time()}
	
	to_print = json_object['key']
	if shift_pressed: to_print = "shift+" + to_print
	if ctrl_pressed: to_print = "ctrl+" + to_print
	print(to_print)
	
	storage.append(json_object)

def on_release(key):
	global ctrl_pressed, shift_pressed
	
	key_str = str(key)
	done = False

	if key_str == 'Key.ctrl_l' or key_str == 'Key.ctrl_r':
		if ctrl_pressed:
			json_object = {'action': 'released_key', 'key': 'Key.ctrl_l', 'time': time.time()}
			storage.append(json_object)
		ctrl_pressed = False
		print("> CTRL OFF <")
		done = True
	
	if key_str == 'Key.shift':
		if shift_pressed:
			json_object = {'action': 'released_key', 'key': 'Key.shift', 'time': time.time()}
			storage.append(json_object)
		shift_pressed = False
		print("> SHIFT OFF <")
		done = True

	if done: return

	if ctrl_pressed:
		if key_str not in ctrl_keys: return
		json_object = {'action': 'released_key', 'key': ctrl_keys[key_str], 'time': time.time()}
	else:
		try:
			json_object = {'action': 'released_key', 'key': key.char, 'time': time.time()}
		except AttributeError:
			json_object = {'action': 'released_key', 'key': str(key), 'time': time.time()}
	
	# detect 2s long 'esc' press
	if len(storage) > 0 and json_object['key'] == 'Key.esc':
		i = len(storage) - 1
		while storage[i - 1]['action'] == 'pressed_key' and storage[i - 1]['key'] == 'Key.esc':
			if i == 0: break
			i -= 1
		last_esc_pressed_time = storage[i]['time']
		print(len(storage), i, json_object['time'], last_esc_pressed_time)
		if json_object['time'] - last_esc_pressed_time > 2:
			for _ in range(len(storage) - i):
				storage.pop()
			return False

	storage.append(json_object)

# mouse related callbacks

def on_move(x, y):
	if record_mouse_movement == True:
		if len(storage) >= 1:
			if storage[-1]['action'] != "moved":
				json_object = {'action': 'moved', 'x': x, 'y': y, 'time': time.time()}
				storage.append(json_object)
			elif storage[-1]['action'] == "moved" and time.time() - storage[-1]['time'] > 0.02:
				json_object = {'action': 'moved', 'x': x, 'y': y, 'time': time.time()}
				storage.append(json_object)
		else:
			json_object = {'action': 'moved', 'x': x, 'y': y, 'time': time.time()}
			storage.append(json_object)
	else:
		if len(storage) >= 1:
			if (storage[-1]['action'] == "pressed" and storage[-1]['button'] == 'Button.left') or (storage[-1]['action'] == "moved" and time.time() - storage[-1]['time'] > 0.02):
				json_object = {'action': 'moved', 'x': x, 'y': y, 'time': time.time()}
				storage.append(json_object)

def on_click(x, y, button, pressed):
	json_object = {'action': 'pressed' if pressed else 'released', 'button': str(button), 'x': x, 'y': y, 'time': time.time()}
	
	# detect 2s right click hold
	if len(storage) > 1:
		if json_object['action'] == 'released' and json_object['button'] == 'Button.right' and json_object['time'] - storage[-1]['time'] > 2:
			storage.pop()
			return False
	
	json_object = {'action': 'pressed' if pressed else 'released', 'button': str(button), 'x': x, 'y': y, 'time': time.time()}
	storage.append(json_object)

def on_scroll(x, y, dx, dy):
	json_object = {'action': 'scroll', 'vertical_direction': int(dy), 'horizontal_direction': int(dx), 'x': x, 'y': y, 'time': time.time()}
	storage.append(json_object)

# start recordings

time.sleep(delay)

if record_keyboard:
	print("release a 2s 'esc' hold to end the recording for keyboard")

	# Collect events from keyboard until esc is pressed
	keyboard_listener = keyboard.Listener(
		on_press=on_press,
		on_release=on_release)

	keyboard_listener.start()
	keyboard_listener.join()

if record_mouse:
	print("release a 2s right click hold to end the recording for mouse")

	# Collect events from mouse until a 2s right click is released
	mouse_listener = mouse.Listener(
			on_click=on_click,
			on_scroll=on_scroll,
			on_move=on_move)

	mouse_listener.start()
	mouse_listener.join()

# write back recording

with open('data/{}.txt'.format(name_of_recording), 'w+') as outfile:
	json.dump(storage, outfile, indent=4)
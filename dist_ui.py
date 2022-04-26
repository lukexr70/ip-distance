"""
Very simple UI to show a couple of things for purposes of development, testing,
and demos. Mostly just intended for before we get a real UI.
"""

from operator import is_
import tkinter as tk

# standard imports
import time
import random
import uuid
import json
import sys
import socket
import subprocess
import os
import validators
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError


# 3rd party imports
import utm

# table view
from tkinter import ttk

# map views
from tkintermapview import TkinterMapView


#INIT_LOC = {"lat": 39.9311644818977, "lon": -75.05127419038763}
INIT_LOC = {"lat": 35.71689, "lon": -120.76468} # Stalker "home" airstrip (airstrip near default HIL sim location)

plan_state = "PLANNING"

num_tasks = 0

def addTask(set, platform, task):
	print("Adding a task to the task table for " + platform)
	global num_tasks

	if platform in task_list:
		print("Updating platform with new task")
		task_list[platform]["ID"] = task["ID"]
		task_list[platform]["Task"] = task["Task"]
		selected_item = set.tag_has(platform)
		set.item(selected_item, values=(task["ID"], platform, task["Task"]))
		
	else:
		print("Adding new platform to task list")
		task_list[platform] = {"ID":task["ID"], "Task":task["Task"]}
		set.insert(parent='', index='end', iid=num_tasks, text='',
				values=(task["ID"], platform, task["Task"]), tags=platform)
		num_tasks += 1	


def createTablePane(panel):
	print("Creating Task table")
	set = ttk.Treeview(panel)
	set.pack()

	set['columns'] = ('ID', 'Full_Name', 'Task')
	set.column("#0", width=0,  stretch=tk.NO)
	set.column("ID", anchor=tk.CENTER, width=80)
	set.column("Full_Name", anchor=tk.CENTER, width=80)
	set.column("Task", anchor=tk.CENTER, width=80)

	set.heading("#0", text="", anchor=tk.CENTER)
	set.heading("ID", text="ID", anchor=tk.CENTER)
	set.heading("Full_Name", text="Full_Name", anchor=tk.CENTER)
	set.heading("Task", text="Task", anchor=tk.CENTER)

	return set


def addPlatform(map_widget, platform, is_blueforce = True):
	if platform["name"] in platform_list:
		print("Updating platform with new information")
		platform_list[platform["name"]]["lat"] = platform["lat"]
		platform_list[platform["name"]]["lon"] = platform["lon"]

		handle = platform_list[platform["name"]]["handle"]
		handle.set_position(platform["lat"], platform["lon"])
		return handle
	else:
		print("Adding a platform to the map")
		platform_list[platform["name"]] = {
			"lat": platform["lat"], "lon": platform["lon"], "name": platform["name"]}

		handle = map_widget.set_marker(
			platform["lat"], platform["lon"], text=platform["name"])

		platform_list[platform["name"]]["handle"] = handle
		
		return handle


def addRoute(map_widget, locations):
	print("Adding a route to the map")
	path = map_widget.set_path(locations)
	return path


def addLocationMarker(map_widget, name, lat, lon):
	location_marker = map_widget.set_position(
		lat, lon, marker=True)  # Cherry Hill, NJ
	location_marker.set_text(name)  # set new text
	# location_marker.set_position(48.860381, 2.338594)  # change position
	# location_marker.delete()
	return location_marker


def createMapPane(panel):
	print("Creating Map panel")
	map_widget = TkinterMapView(panel, width=800, height=600, corner_radius=0)

	# configure the map
	map_widget.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
	map_widget.set_zoom(19)
	map_widget.set_position(INIT_LOC["lat"], INIT_LOC["lon"])
	# map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)  # google normal
	map_widget.set_tile_server(
		"https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)  # google satellite

	return map_widget


def return_to_home(stalker_id = 0):
	print('Sending Stalker #' + str(stalker_id) + ' home')
	mi.inject_launch_stalker(mi.beddown_loc[0], mi.beddown_loc[1], alt=300, stalker_id = stalker_id)
	#subprocess_name = "./injectCommand.bash %s"
	#subprocess.check_call(subprocess_name % str(stalker_id), shell=True)

def add_platform_abort_button(panel, stalker_id):
	print('Adding new mission abort button to the UI')
	panel.add(tk.Button(root_window, text="Stalker " + str(stalker_id) + " Abort", command=lambda: return_to_home(stalker_id)))

def inject_random_redforce():
	print(1)

def add_random_redforce_button(panel):
	print('Adding new button to inject random redforce entities to the UI')
	panel.add(tk.Button(root_window, text="Inject Random Redforce", command=inject_random_redforce, bg='red'))


def add_spacers_to_panel(panel, num_spacers):
	for i in range(num_spacers):
		spacer = tk.Label(root_window,text=' ')
		panel.add(spacer)


def add_text_box(panel):
	print('Adding new mission abort button to the UI')
	text = tk.StringVar().set("IP Address")
	input_txt = tk.Entry(root_window, textvariable=text)
	panel.add(input_txt)
	return(input_txt)

def is_string_url(url_string: str) -> bool:
    validate_url = URLValidator(verify_exists=True)

    try:
        validate_url(url_string)
    except ValidationError:
        return False

    return True

def is_string_ip(ip_string: str) -> bool:
	try:
		socket.inet_aton(ip_string)
	except socket.error:
		return False
	return True

def check(i_t):
	in_str = i_t.get()
	if is_string_ip(in_str) or is_string_url(in_str):
		response = os.system("ping " + in_str)
		print(response)
		# and then check the response...
		# if response == 0:
		# 	pingstatus = "Network Active"
		# else:
		# 	pingstatus = "Network Error"
	# if validators.url(i_t.get()) == True:
	# 	print("ok")
	# else:
	# 	print("not ok")
	

def add_check_button(panel, i_t):
	print('Adding new button to inject random redforce entities to the UI')
	panel.add(tk.Button(root_window, text="Check", command=lambda: check(i_t), bg='red'))

# Tkinter Window
root_window = tk.Tk()

# Window Settings
root_window.title('Testing')
#root_window.geometry('1040x615')
#root_window.configure(background = '#353535')

#add a table
frame = tk.PanedWindow()
frame.pack(fill=tk.BOTH, expand=1)

leftPanel = tk.PanedWindow(frame, orient = tk.VERTICAL)
leftPanel.pack(expand=0)
frame.add(leftPanel)

table = createTablePane(leftPanel)
leftPanel.add(table)


# Build controls panel
planStatusButton = tk.Label(root_window, text=plan_state, fg='White', bg='#353535')
leftPanel.add(planStatusButton)


#add_platform_abort_button(leftPanel,1)
#add_platform_abort_button(leftPanel,2)
#add_platform_abort_button(leftPanel,3)

add_spacers_to_panel(leftPanel,1)
i_t = add_text_box(leftPanel)
add_check_button(leftPanel, i_t)

add_spacers_to_panel(leftPanel,8)

# Exit Button
exitButton = tk.Button(root_window, text='Exit', width=10, command=root_window.destroy)
leftPanel.add(exitButton)

add_spacers_to_panel(leftPanel,1)

# create map widget
mapPanel = tk.PanedWindow(frame)
frame.add(mapPanel)

map = createMapPane(mapPanel)
mapPanel.add(map)

#END UI LAYOUT CODE

# add some sample platforms
#addTask(table, "Stalker_1", {"ID":"101", "Task":"ISR"})
#addTask(table, "Stalker_2", {"ID":"102", "Task":"RECON"})
#addTask(table, "Stalker_3", {"ID":"103", "Task":"RELAY"})
#stalker_1 = addPlatform(map,{"lat":35.3998, "lon":-120.61605, "name":"Stalker 1"})
#stalker_2 = addPlatform(map,{"lat":35.3997, "lon":-120.61609, "name":"Stalker 2"})

#test update of table
#addTask(table, "Stalker_1", {"ID":"101", "Task":"ISR_2"})

#test update of map
#stalker_1 = addPlatform(map,{"lat":35.399, "lon":-120.616, "name":"Stalker 1"})

print("Entering main UI loop...")
root_window.mainloop()


# if __name__=='__main__':
# 	print("__main__")
# 	configure()

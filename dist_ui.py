"""
Very simple UI to show a couple of things for purposes of development, testing,
and demos. Mostly just intended for before we get a real UI.
"""

from operator import is_
import tkinter as tk

# standard imports
import time
import random
from turtle import color
import uuid
import json
import sys
import socket
import subprocess
import os
import validators
import requests
import re
import geocoder
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from bs4 import BeautifulSoup
from math import radians, cos, sin, asin, sqrt, pi

# 3rd party imports
import utm

# table view
from tkinter import ttk

# map views
from tkintermapview import TkinterMapView


INIT_LOC = {"lat": 41.4855, "lon": -71.4365}
path = None
circle = None
marker = None
num_tasks = 0
task_list = {}

def addTask(set, platform, task):
	global num_tasks

	if platform in task_list:
		task_list[platform]["IP"] = task["IP"]
		task_list[platform]["Delay"] = task["Delay"]
		task_list[platform]["TTL"] = task["TTL"]
		selected_item = set.tag_has(platform)
		set.item(selected_item, values=(task["IP"], task["Delay"], task["TTL"]))
		
	else:
		task_list[platform] = {"IP":task["IP"], "Delay": task["Delay"],"TTL":task["TTL"]}
		set.insert(parent='', index='end', iid=num_tasks, text='',
				values=(task["IP"], task["Delay"], task["TTL"]), tags=platform)
		num_tasks += 1	


def createTablePane(panel):
	print("Creating Ping table")
	set = ttk.Treeview(panel)
	set.pack()

	set['columns'] = ('IP', 'Delay', 'TTL')
	set.column("#0", width=0,  stretch=tk.NO)
	set.column("IP", anchor=tk.CENTER, width=80)
	set.column("Delay", anchor=tk.CENTER, width=80)
	set.column("TTL", anchor=tk.CENTER, width=80)

	set.heading("#0", text="", anchor=tk.CENTER)
	set.heading("IP", text="IP", anchor=tk.CENTER)
	set.heading("Delay", text="Delay", anchor=tk.CENTER)
	set.heading("TTL", text="TTL", anchor=tk.CENTER)

	return set


def addPlatform(map_widget, platform):
	if platform["name"] in platform_list:
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
	location_marker.set_text(name)
	return location_marker


def createMapPane(panel):
	print("Creating Map panel")
	map_widget = TkinterMapView(panel, width=800, height=600, corner_radius=0)

	# configure the map
	map_widget.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
	map_widget.set_zoom(15)
	map_widget.set_position(INIT_LOC["lat"], INIT_LOC["lon"])
	# map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)  # google normal
	map_widget.set_tile_server(
		"https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)  # google satellite

	return map_widget


def add_spacers_to_panel(panel, num_spacers):
	for i in range(num_spacers):
		spacer = tk.Label(root_window,text=' ')
		panel.add(spacer)


def add_text_box(panel):
	print('Adding IP input element to the UI')
	text = tk.StringVar().set("IP Address")
	input_txt = tk.Entry(root_window, textvariable=text)
	panel.add(input_txt)
	return(input_txt)

def is_string_url(url_string: str) -> bool:
    return validators.url(url_string)

def is_string_ip(ip_string: str) -> bool:
	try:
		socket.inet_aton(ip_string)
	except socket.error:
		return False
	return True

def make_path(lat, lon):
	global path, marker
	print(f'{lat}, {lon}')
	dist_calc(lat, lon, INIT_LOC["lat"], INIT_LOC["lon"])
	if marker: marker.set_position(lat, lon)
	else: marker = addLocationMarker(map1, "IP", lat, lon)
	if path: 
		map1.delete(path)
		path = map1.set_path([(lat, lon), (INIT_LOC["lat"], INIT_LOC["lon"])])
		#path.position_list = [(lat, lon), (INIT_LOC["lat"], INIT_LOC["lon"])]
	else: path = map1.set_path([(lat, lon), (INIT_LOC["lat"], INIT_LOC["lon"])])

def check(i_t):
	in_str = i_t.get()
	proc = subprocess.run(["ping", in_str], capture_output=True)
	print(proc)
	ip = ""
	if is_string_ip(in_str): ip = in_str
	else:
		reg = re.search("Reply from ([0-9a-f\.:]*): ", str(proc))
		print(reg[1])
		ip = reg[1]
	URL = f'https://db-ip.com/{ip}'
	print(URL)
	page = requests.get(URL)
	soup = BeautifulSoup(page.content, "html.parser")
	result = soup.find(id = "osm_embed")
	re_result = re.search("marker=(-?[0-9]*\.[0-9]*),(-?[0-9]*\.[0-9]*)", str(result))
	print(re_result)
	lat, lon = float(re_result[1]), float(re_result[2])
	make_path(lat, lon)

def predict(i_t):
	in_str = i_t.get()
	proc = subprocess.run(["ping", in_str], capture_output=True)
	proc2 = subprocess.run(["tracert", in_str], capture_output=True)
	print(proc)
	print(proc2)
	ping = re.search("Average = ([0-9\.]*)ms", str(proc))
	ping_resp = re.findall("Reply from ([0-9a-f\.:]*): bytes=([0-9]*) time=([0-9]*ms) TTL=([0-9]*)", str(proc))
	print(ping_resp)
	for i in range(len(ping_resp)):
		addTask(table, str(i+1), {"IP":ping_resp[i][0], "Delay":ping_resp[i][2], "TTL":ping_resp[i][3]})
	print(ping)	
	#elif is_string_url(in_str):
	d = predict_dist(float(ping[1])/1000.0)
	print(f'd = {abs(d)}')
	gen_circle((INIT_LOC["lat"], INIT_LOC["lon"]), abs(d))

def predict_dist(ping):
	a = 105267.857
	b = 15191.964 
	c = -72.5915
	return a*(ping**2) + b*ping + c


def gen_circle(center, radius):
	global circle
	radiusKm = radius / 0.621371
	radiusLon = 1 / (111.319 * cos(center[0])) * radiusKm
	radiusLat = 1 / 110.574 * radiusKm
            
    #Calculate amount to increment angle for number of points.
	dTheta = 2 * pi / 120;
	theta = 0.0

	#Produce points.
	points = []
	for i in range(120):
		points.append( (center[0] + radiusLat *sin(theta),
			center[1] + radiusLon * cos(theta)))
		theta += dTheta;
	points.append(points[0])
	#print(points)
	if circle: 
		map1.delete(circle)
	circle = map1.set_path(points, color="#c2deab")
	

def dist_calc(lat_ip, lon_ip, lat_ad, lon_ad):
	lon_ad, lat_ad, lon_ip, lat_ip = map(radians, [lon_ad, lat_ad, lon_ip, lat_ip])

	# haversine formula 
	dlon = lon_ip - lon_ad 
	dlat = lat_ip - lat_ad 
	a = sin(dlat/2)**2 + cos(lat_ad) * cos(lat_ip) * sin(dlon/2)**2
	c = 2 * asin(sqrt(a)) 
	km = 6367 * c
	miles = 3958.8 * c
	#end of calculation

	#limit decimals
	km = ('%.0f'%km)
	miles = ('%.0f'%miles)

	print('ip is about '+str(miles)+' miles away from you')	

def set_loc():
	g = geocoder.ip('me')
	INIT_LOC["lat"] = g.latlng[0]
	INIT_LOC["lon"] = g.latlng[1]

def add_check_button(panel, i_t):
	print('Adding new button to get location and distance of ip address')
	panel.add(tk.Button(root_window, text="Check", command=lambda: check(i_t), bg='red'))

def add_predict_button(panel, i_t):
	print('Adding new button to predict distance from inputted ip address')
	panel.add(tk.Button(root_window, text="Predict", command=lambda: predict(i_t), bg='red'))

# Tkinter Window
root_window = tk.Tk()

# Window Settings
root_window.title('IP Distance Prediction')
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
planStatusButton = tk.Label(root_window, text="Enter Network Address", fg='White', bg='#353535')
leftPanel.add(planStatusButton)


add_spacers_to_panel(leftPanel,1)
i_t = add_text_box(leftPanel)
add_check_button(leftPanel, i_t)
add_predict_button(leftPanel, i_t)

add_spacers_to_panel(leftPanel,8)

# Exit Button
exitButton = tk.Button(root_window, text='Exit', width=10, command=root_window.destroy)
leftPanel.add(exitButton)

add_spacers_to_panel(leftPanel,1)

# create map widget
mapPanel = tk.PanedWindow(frame)
frame.add(mapPanel)

map1 = createMapPane(mapPanel)
mapPanel.add(map1)

addLocationMarker(map1, "Start", INIT_LOC["lat"], INIT_LOC["lon"])



print("Entering main UI loop...")
root_window.mainloop()


# if __name__=='__main__':
# 	print("__main__")
# 	configure()


#proc = subprocess.run(["ping", "google.com"], capture_output=True)
#print(proc)
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import print_function

import sys

ATTRIBUTES = dict(list(zip(["bold", "dark", "", "underline", "blink", "", "reverse", "concealed"], list(range(1, 9)))))
HIGHLIGHTS = dict(list(zip(["grey", "red", "green", "yellow", "blue", "magenta", "cyan", "white"], list(range(40, 48)))))
COLORS = dict(list(zip(["grey", "red", "green", "yellow", "blue", "magenta", "cyan", "white"], list(range(30, 38)))))
RESET = "\033[0m"

color_out = None

def set(when):
	global color_out
	if when == "auto":
		color_out = sys.stdout.isatty()
	else:
		color_out = when == "always"

def gray(text):
	if color_out:
		return "\033["+str(COLORS["gray"])+"m"+text+str(RESET)
	else:
		return text

def red(text):
	if color_out:
		return "\033["+str(COLORS["red"])+"m"+text+str(RESET)
	else:
		return text

def green(text):
	if color_out:
		return "\033["+str(COLORS["green"])+"m"+text+str(RESET)
	else:
		return text

def yellow(text):
	if color_out:
		return "\033["+str(COLORS["yellow"])+"m"+text+str(RESET)
	else:
		return text

def blue(text):
	if color_out:
		return "\033["+str(COLORS["blue"])+"m"+text+str(RESET)
	else:
		return text

def magenta(text):
	if color_out:
		return "\033["+str(COLORS["magenta"])+"m"+text+str(RESET)
	else:
		return text

def cyan(text):
	if color_out:
		return "\033["+str(COLORS["cyan"])+"m"+text+str(RESET)
	else:
		return text

def white(text):
	if color_out:
		return "\033["+str(COLORS["white"])+"m"+text+str(RESET)
	else:
		return text


#!/usr/bin/python

import os
import subprocess
import random
import sys
import curses

# globals
COLS = 80
LINES = 23
MAXROOMS = 9


flags = {'ISDARK':0000001,'ISCURSED':0000001,'ISBLIND':0000001,
	'ISGONE':0000002,'ISKNOW':0000002,'ISRUN':0000004,'ISFOUND':0000010,
	'ISINVIS':0000020,'ISMEAN':0000040,'ISGREED':0000100,'ISBLOCK':0000200,
	'ISHELD':0000400,'ISHUH':0001000,'ISREGEN':0002000,'CANHUH':0004000,
	'CANSEE':0010000,'ISMISL':0020000,'ISCANC':0020000,'ISMANY':0040000,
	'ISSLOW':0040000,'ISHASTE':0100000}

tiles = {'PASSAGE':'#','DOOR':'+','FLOOR':'.','PLAYER':'@','TRAP':'^','TRAPDOOR':'>',
	'ARROWTRAP':'{','SLEEPTRAP':'$','BEARTRAP':'}','TELTRAP':'~','DARTTRAP':'`',
	'SECRETDOOR':'&','STAIRS':'%','GOLD':'*','POTION':'!','SCROLL':'?','MAGIC':'$',
	'FOOD':':','WEAPON':')','ARMOR':']','AMULET':',','RING':'=','STICK':'/'}

# vars
amulet = 0
max_level = 1
level = 1

# GOLDCALC = (random.randint(50 + 10 * level) + 2)



# classes
class coord:
	def __init__(self, x, y):
		self.x = x
		self.y = y

class room:
	def __init__(self, r_pos, r_max, r_gold, r_goldval, r_flags, r_nexits, r_exit):
		self.r_pos = coord(r_pos.x,r_pos.y)
		self.r_max = coord(r_max.x,r_max.y)
		self.r_gold = coord(r_gold.x,r_gold.y)
		self.r_goldval = r_goldval
		self.r_flags = r_flags
		self.r_nexits = r_nexits

# functions

def vert(cnt):
	y, x = stdscr.getyx()
	x -= 1
	while cnt > 0:
		y += 1
		stdscr.move(y,x)
		stdscr.addch('|')
		cnt -= 1

def horiz(cnt):
	while cnt > 0:
		stdscr.addch('-')
		cnt -= 1

def rnd_pos(room):
	newcoord = coord(0,0)
	newcoord.x = room.r_pos.x + random.randint(0,room.r_max.x - 3) + 1
	newcoord.y = room.r_pos.y + random.randint(0,room.r_max.y - 3) + 1
	return newcoord
	

def draw_room(room):
	stdscr.move(room.r_pos.y, room.r_pos.x+1)
	vert(room.r_max.y-2)
	stdscr.move(room.r_pos.y+room.r_max.y-1, room.r_pos.x)
	horiz(room.r_max.x)
	stdscr.move(room.r_pos.y,room.r_pos.x)
	horiz(room.r_max.x)
	vert(room.r_max.y-2)
	for j in range(1,room.r_max.y-1):
		stdscr.move(room.r_pos.y + j, room.r_pos.x+1)
		for k in range(1,room.r_max.x-1):
			stdscr.addch(tiles['FLOOR'])
	if room.r_goldval != 0:
		stdscr.addch(room.r_gold.y, room.r_gold.x, tiles['GOLD'])

def do_rooms():
	global rooms
	bsze = coord(COLS/3, LINES/3)
	for i in rooms:
		i.r_goldval = i.r_nexits = i.r_flags = 0
	left_out = random.randint(0,3)
	for i in range(left_out):
		rooms[random.randint(0,MAXROOMS-1)].r_flags |= flags['ISGONE']
	for i in range(MAXROOMS):
		top = coord((i%3)*bsze.x + 1,i/3*bsze.y)
		if rooms[i].r_flags & flags['ISGONE']:
			while rooms[i].r_pos.y <= 0 and rooms[i].r_pos.y >= LINES-1:
				rooms[i].r_pos.x = top.x + random.randint(0,bsze.x-3)+1
				rooms[i].r_pos.y = top.y + random.randint(0,bsze.y-3)+1
				rooms[i].r_max.x = -COLS
				rooms[i].r_max.y = -LINES
			continue
		if random.randint(0,9) < level - 1:
			rooms[i].r_flags |= flags['ISDARK']
			
		while rooms[i].r_pos.y == 0:
			rooms[i].r_max.x = random.randint(0,bsze.x-4)+4
			rooms[i].r_max.y = random.randint(0,bsze.y-4)+4
			rooms[i].r_pos.x = top.x + random.randint(0, bsze.x - rooms[i].r_max.x)
			rooms[i].r_pos.y = top.y + random.randint(0, bsze.y - rooms[i].r_max.y)

		#Gold
		if random.randint(0,99) < 50 and (amulet == 0 or level >= max_level):
			rooms[i].r_goldval = random.randint(0, (50 + 10 * level) - 1) + 2
			goldpos = rnd_pos(rooms[i])
			rooms[i].r_gold = goldpos

		draw_room(rooms[i])
		
def new_level():
	global level, max_level
	if level > max_level:
		max_level = level
	do_rooms()

def init():
	global MAXROOMS, rooms, level
	empty=coord(0,0)
	rooms = [room(empty,empty,empty,0,0,0,0) for i in range(MAXROOMS)]
	level = 1
	random.seed()
	new_level()
	

def main(stdscr):
	# start
	init()
	stdscr.getch()


greeting = "Hello, " + os.environ['USER'] + ", just a moment while I dig the dungeon..."
print greeting
stdscr=curses.initscr()
curses.curs_set(0)
curses.wrapper(main)

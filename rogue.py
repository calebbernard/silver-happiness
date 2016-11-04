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
MAXTHINGS = 9
MAXOBJ = 9
MAXPACK = 23
MAXTRAPS = 10
NUMTHINGS = 7


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
seed = random.randint(0,10000)

# GOLDCALC = (random.randint(50 + 10 * level) + 2)
# winat(y, x) (mvwinch(mw,y,x)==' '?mvwinch(stdscr,y,x):winch(mw))
# RN (((seed = seed*11109+13849) & 0x7fff) >> 1)
# cmov(xy) move((xy).y, (xy).x)
# inroom(rp, cp) (&& (cp)->y <= (rp)->r_pos.y + ((rp)->r_max.y - 1)
#	&& (rp)->r_pos.y <= (cp)->y)
# unc(cp) (cp).y, (cp).x
# DISTANCE(y1, x1, y2, x2) ((x2 - x1)*(x2 - x1) + (y2 - y1)*(y2 - y1))
# ce(a, b) ((a).x == (b).x && (a).y == (b).y)
# ISRING(h,r) (cur_ring[h] != NULL && cur_ring[h]->o_which == r)
# ISWEARING(r) (ISRING(LEFT, r) || ISRING(RIGHT, r))
# ISMULT(type) (type == POTION || type == SCROLL || type == FOOD)


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
		self.r_exit = [coord(r_exit[0].x,r_exit[0].y),coord(r_exit[1].x,r_exit[1].y),
						coord(r_exit[2].x,r_exit[2].y),coord(r_exit[3].x,r_exit[3].y)]

class rdes:
	def __init__(self, conn, isconn, ingraph):
		self.conn = conn
		self.isconn = isconn
		self.ingraph = ingraph

class trap:
	def __init__(self, tr_pos, tr_type, tr_flags):
		self.tr_pos = coord(tr_pos.x, tr_pos.y)
		self.tr_type = tr_type
		self.tr_flags = tr_flags

# functions

def rnd(range):
	global seed
	if range == 0:
		return 0
	else:
		seed = ((seed * 11109 + 13848) & 0x7ffff) >> 1
		return abs(seed) % range


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
	newcoord.x = room.r_pos.x + rnd(room.r_max.x - 2) + 1
	newcoord.y = room.r_pos.y + rnd(room.r_max.y - 2) + 1
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

def rnd_room():
	global rooms
	rm = rnd(MAXROOMS)
	while rooms[rm].r_flags & flags['ISGONE']:
		rm = rnd(MAXROOMS)
	return rm

def do_rooms():
	global rooms
	bsze = coord(COLS/3, LINES/3)
	for i in rooms:
		i.r_goldval = i.r_nexits = i.r_flags = 0
	left_out = rnd(4)
	for i in range(left_out):
		rooms[rnd_room()].r_flags |= flags['ISGONE']
	for i in range(MAXROOMS):
		top = coord((i%3)*bsze.x + 1,i/3*bsze.y)
		if rooms[i].r_flags & flags['ISGONE']:
			rooms[i].r_pos.x = top.x + rnd(bsze.x-2)+1
			rooms[i].r_pos.y = top.y + rnd(bsze.y-2)+1
			rooms[i].r_max.x = -COLS
			rooms[i].r_max.y = -LINES
			while rooms[i].r_pos.y <= 0 and rooms[i].r_pos.y >= LINES-1:
				rooms[i].r_pos.x = top.x + rnd(bsze.x-2)+1
				rooms[i].r_pos.y = top.y + rnd(bsze.y-2)+1
				rooms[i].r_max.x = -COLS
				rooms[i].r_max.y = -LINES
			continue
		if rnd(10) < level - 1:
			rooms[i].r_flags |= flags['ISDARK']
		rooms[i].r_max.x = rnd(bsze.x-4)+4
		rooms[i].r_max.y = rnd(bsze.y-4)+4
		rooms[i].r_pos.x = top.x + rnd(bsze.x - rooms[i].r_max.x)
		rooms[i].r_pos.y = top.y + rnd(bsze.y - rooms[i].r_max.y)
		while rooms[i].r_pos.y == 0:
			rooms[i].r_max.x = rnd(bsze.x-4)+4
			rooms[i].r_max.y = rnd(bsze.y-4)+4
			rooms[i].r_pos.x = top.x + rnd(bsze.x - rooms[i].r_max.x)
			rooms[i].r_pos.y = top.y + rnd(bsze.y - rooms[i].r_max.y)

		#Gold
		if rnd(100) < 50 and (amulet == 0 or level >= max_level):
			rooms[i].r_goldval = rnd(50 + 10 * level) + 2
			rooms[i].r_gold = rnd_pos(rooms[i])

		draw_room(rooms[i])

def door(room, coord):
	stdscr.move(coord.y, coord.x)
	if rnd(10) < level - 1 and rnd(100) < 20:
		stdscr.addch(tiles['SECRETDOOR'])
	else:
		stdscr.addch(tiles['DOOR'])
	room.r_exit[room.r_nexits].x = coord.x
	room.r_exit[room.r_nexits].y = coord.y
	room.r_nexits += 1

def conn(r1, r2):
	global rooms
	if r1 < r2:
		rm = r1
		if r1 + 1 == r2:
			direc = 'r'
		else:
			direc = 'd'
	else:
		rm = r2
		if r2 + 1 == r1:
			direc = 'r'
		else:
			direc = 'd'
	rpf = rooms[rm]
	# Set up the movement variables, in two cases:
	# first drawing one down.
	if direc == 'd':
		rmt = rm + 3	# room # of dest
		rpt = rooms[rmt]	# room pointer of dest
		pdelta = coord(0,1) # direction of move
		spos = coord(rpf.r_pos.x, rpf.r_pos.y) # start of move
		epos = coord(rpt.r_pos.x, rpt.r_pos.y) # end of move
		if rpf.r_flags & flags['ISGONE'] == 0:	# if not gone pick door pos
			spos.x += rnd(rpf.r_max.x-2)+1 # picks a random non-corner on top
			spos.y += rpf.r_max.y-1 # moves from top to bottom
		if rpt.r_flags & flags['ISGONE'] == 0:
			epos.x += rnd(rpt.r_max.x-2)+1 # in the dest. room, we stay on the top
		distance = abs(spos.y-epos.y) - 1	# distance to move
		turn_delta = coord(0,0)	# direction to turn
		if spos.x < epos.x:
			turn_delta.x = 1
		else:
			turn_delta.x = -1
		turn_distance = abs(spos.x - epos.x)	# how far to turn
		turn_spot = rnd(distance-1) + 1	# where turn starts
	elif direc == 'r':	# setup for moving right
		rmt=rm+1
		rpt = rooms[rmt]
		pdelta=coord(1,0)
		spos = coord(rpf.r_pos.x, rpf.r_pos.y)
		epos = coord(rpt.r_pos.x, rpt.r_pos.y)
		if rpf.r_flags & flags['ISGONE'] == 0:
			spos.x += rpf.r_max.x-1 # Move to right side
			spos.y += rnd(rpf.r_max.y-2)+1 # pick a random non-corner on right side
		if rpt.r_flags & flags['ISGONE'] == 0:
			epos.y += rnd(rpt.r_max.y-2)+1 # stay on the left for dest
		distance = abs(spos.x-epos.x) - 1
		turn_delta = coord(0,0)
		if spos.y < epos.y:
			turn_delta.y = 1
		else:
			turn_delta.y = -1
		turn_distance = abs(spos.y - epos.y)
		turn_spot = rnd(distance-1) + 1
	else:
		print "Fatal error in passages"
	# Draw in the doors on either side of the passage or just put #'s
	# if the rooms are gone.
	if rpf.r_flags & flags['ISGONE'] == 0:
		door(rpf, spos)
	else:
		stdscr.move(spos.y,spos.x)
		stdscr.addch(tiles['PASSAGE'])
	if rpt.r_flags & flags['ISGONE'] == 0:
		door(rpt, epos)
	else:
		stdscr.move(epos.y,epos.x)
		stdscr.addch('#')
	# Get ready to move...
	curr = coord(spos.x, spos.y)
	while distance != 0:
		# Move to new position
		curr.x += pdelta.x
		curr.y += pdelta.y
		# Check if we are at the turn place, if so do the turn
		if distance == turn_spot and turn_distance > 0:
			while turn_distance != 0:
				turn_distance -= 1
				stdscr.move(curr.y,curr.x)
				stdscr.addch(tiles['PASSAGE'])
				stdscr.refresh()
				curr.x += turn_delta.x
				curr.y += turn_delta.y
		# Continue digging along
		stdscr.move(curr.y,curr.x)
		stdscr.addch(tiles['PASSAGE'])
		stdscr.refresh()
		distance -= 1
	curr.x += pdelta.x
	curr.y += pdelta.y
	#if curr.x != epos.x or curr.y != epos.y:
		#print "error 1"


def do_passages():
	newrdes = [
		rdes([ 0, 1, 0, 1, 0, 0, 0, 0, 0 ], [ 0, 0, 0, 0, 0, 0, 0, 0, 0 ], 0),
		rdes([ 1, 0, 1, 0, 1, 0, 0, 0, 0 ], [ 0, 0, 0, 0, 0, 0, 0, 0, 0 ], 0),
		rdes([ 0, 1, 0, 0, 0, 1, 0, 0, 0 ], [ 0, 0, 0, 0, 0, 0, 0, 0, 0 ], 0),
		rdes([ 1, 0, 0, 0, 1, 0, 1, 0, 0 ], [ 0, 0, 0, 0, 0, 0, 0, 0, 0 ], 0),
		rdes([ 0, 1, 0, 1, 0, 1, 0, 1, 0 ], [ 0, 0, 0, 0, 0, 0, 0, 0, 0 ], 0),
		rdes([ 0, 0, 1, 0, 1, 0, 0, 0, 1 ], [ 0, 0, 0, 0, 0, 0, 0, 0, 0 ], 0),
		rdes([ 0, 0, 0, 1, 0, 0, 0, 1, 0 ], [ 0, 0, 0, 0, 0, 0, 0, 0, 0 ], 0),
		rdes([ 0, 0, 0, 0, 1, 0, 1, 0, 1 ], [ 0, 0, 0, 0, 0, 0, 0, 0, 0 ], 0),
		rdes([ 0, 0, 0, 0, 0, 1, 0, 1, 0 ], [ 0, 0, 0, 0, 0, 0, 0, 0, 0 ], 0)]
    # reinitialize room graph description
	for i in range(MAXROOMS):
		r1 = newrdes[i]
		for j in range(MAXROOMS):
			r1.isconn[j] = 0
		r1.ingraph = 0
	# starting with one room, connect it to a random adjacent room and
   	# then pick a new room to start with.
	roomcount = 1
	r1 = newrdes[rnd(MAXROOMS)]
	r1.ingraph = 1
	while roomcount < MAXROOMS:
		#for x in newrdes:
		# find a room to connect with
		j = 0
		for i in range(MAXROOMS):
			if r1.conn[i] == 1 and newrdes[i].ingraph == 0:
				j += 1
				if rnd(j) == 0:
					r2 = newrdes[i]
		# if no adjacent rooms are outside the graph, pick a new room
		# to look from
		if j == 0:
			r1 = newrdes[rnd(MAXROOMS)]
			while r1.ingraph == 0:
				r1 = newrdes[rnd(MAXROOMS)]
		# otherwise, connect new room to the graph, and draw a tunnel
		# to it
		else:
			r2.ingraph = 1
			i = newrdes.index(r1)
			j = newrdes.index(r2)
			conn(i,j)
			r1.isconn[j] = 1
			r2.isconn[i] = 1
			roomcount += 1
	# attempt to add passages to the graph a random number of times so
    # that there isn't just one unique passage through it.
	for i in range(rnd(5)):
		r1 = newrdes[rnd(MAXROOMS)] # a random room to look from
		# find an adjacent room not already connected
		j = 0
		for i in range(MAXROOMS):
			if r1.conn[i] == 1 and r1.isconn[i] == 0:
				j += 1
				if rnd(j) == 0:
					r2=newrdes[i]
		if j != 0:
			i = newrdes.index(r1)
			j = newrdes.index(r2)
			conn(i,j)
			r1.isconn[j] = 1
			r2.isconn[i] = 1



def new_level():
	global level, max_level, no_food
	if level > max_level:
		max_level = level
	do_rooms()
	do_passages()
	no_food += 1
	# Put_things()
	# Add stairs
	rm = rnd_room()
	stairs = rnd_pos(rooms[rm])
	stdscr.addch(stairs.y, stairs.x, tiles['STAIRS'])
	# Add traps
	if (rnd(10) < level):
		ntraps = rnd(level/4) + 1
		if (ntraps > MAXTRAPS):
			ntraps = MAXTRAPS
		i = ntraps
		while i != 0:
			i -= 1
			rm = rnd_room()
			trappos = rnd_pos(rooms[rm])
			x = rnd(6)
			if x == 0:
				ch = tiles['TRAPDOOR']
			elif x == 1:
				ch = tiles['BEARTRAP']
			elif x == 2:
				ch = tiles['SLEEPTRAP']
			elif x == 3:
				ch = tiles['ARROWTRAP']
			elif x == 4:
				ch = tiles['TELTRAP']
			else:
				ch = tiles['DARTTRAP']
			stdscr.addch(trappos.y, trappos.x, tiles['TRAP'])
			traps[i].tr_type = ch
			traps[i].tr_flags = 0
			traps[i].tr_pos = trappos
	# Add light
	rm = rnd_room()
	playerpos = rnd_pos(rooms[rm])
	stdscr.addch(playerpos.y, playerpos.x, tiles['PLAYER'])

def init():
	global MAXROOMS, rooms, level, no_food, traps
	empty=coord(0,0)
	rooms = [room(empty,empty,empty,0,0,0,[empty,empty,empty,empty]) for i in range(MAXROOMS)]
	traps = [trap(empty,0,0) for i in range(MAXTRAPS)]
	level = 1
	random.seed()
	no_food = 0
	new_level()


def main(stdscr):
	# start
	init()
	stdscr.getch()


greeting = "Hello, " + os.environ['USER'] + ", just a moment while I dig the dungeon...\n"
print greeting
stdscr=curses.initscr()
curses.curs_set(0)
curses.wrapper(main)

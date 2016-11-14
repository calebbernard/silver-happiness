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

BEARTIME = 3
SLEEPTIME = 5
HEALTIME = 30
HOLDTIME = 2
STPOS = 0
WANDERTIME = 70
BEFORE = 1
AFTER = 2
HUHDURATION = 20
SEEDURATION = 850
HUNGERTIME = 1300
MORETIME = 150
STOMACHSIZE = 2000
BOLT_LENGTH = 6


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

saves = {'VS_POISON':00,'VS_PARALYZATION':00,'VS_DEATH':00,'VS_PETRIFICATION':01,
	'VS_BREATH':02,'VS_MAGIC':03}

w_dam = ["2d4", "1d10", "1d1", "1d1", "1d6", "1d2", "3d6", "0d0", "1d1", "1d2", "1d8"]

w_hrl = ["1d3", "1d2", "1d1", "1d6", "1d4", "1d4", "1d2", "0d0", "1d3", "1d1", "1d10", "1d6"]

w_launch = ["NONE", "NONE", "NONE", "BOW", "NONE", "SLING", "NONE", "NONE", "NONE", "NONE", "CROSSBOW", "NONE"]

w_flags = [0,0,0,flags['ISMANY']|flags['ISMISL'],flags['ISMISL'],flags['ISMANY']|flags['ISMISL'],0,0,flags['ISMANY']|flags['ISMISL'],0,flags['ISMANY']|flags['ISMISL'],flags['ISMISL']]

# Not needed?
item_types = {'POTION':0,'SCROLL':1,'FOOD':2,'WEAPON':3,'ARMOR':4,'RING':5,'STICK':6}

potion_types = {'P_CONFUSE':0,'P_PARALYZE':1,'P_POISON':2,'P_STRENGTH':3,'P_SEEINVIS':4,
	'P_HEALING':5,'P_MFIND':6,'P_TFIND':7,'P_RAISE':8,'P_XHEAL':9,'P_HASTE':10,
	'P_RESTORE':11,'P_BLIND':12,'P_NOP':13}

scroll_types = {'S_CONFUSE':0,'S_MAP':1,'S_LIGHT':2,'S_HOLD':3,'S_SLEEP':4,'S_ARMOR':5,
	'S_IDENT':6,'S_SCARE':7,'S_GFIND':8,'S_TELEP':9,'S_ENCH':10,'S_CREATE':11,
	'S_REMOVE':12,'S_AGGR':13,'S_NOP':14,'S_GENOCIDE':15}

weapon_types = {'MACE':0,'SWORD':1,'BOW':2,'ARROW':3,'DAGGER':4,'ROCK':5,'TWOSWORD':6,
	'SLING':7,'DART':8,'CROSSBOW':9,'BOLT':10,'SPEAR':11}

armor_types = {'LEATHER':0,'RING_MAIL':1,'STUDDED_LEATHER':2,'SCALE_MAIL':3,'CHAIN_MAIL':4,
	'SPLINT_MAIL':5,'BANDED_MAIL':6,'PLATE_MAIL':7}

ring_types = {'R_PROTECT':0,'R_ADDSTR':1,'R_SUSTSTR':2,'R_SEARCH':3,'R_SEEINVIS':4,
	'R_NOP':5,'R_AGGR':6,'R_ADDHIT':7,'R_ADDDAM':8,'R_REGEN':9,'R_DIGEST':10,
	'R_TELEPORT':11,'R_STEALTH':12}

stick_types = {'WS_LIGHT':0,'WS_HIT':1,'WS_ELECT':2,'WS_FIRE':3,'WS_COLD':4,
	'WS_POLYMORPH':5,'WS_MISSILE':6,'WS_HASTE_M':7,'WS_SLOW_M':8,'WS_DRAIN':0,
	'WS_NOP':10,'WS_TELAWAY':11,'WS_TELTO':12,'WS_CANCEL':13}

s_magic = [["monster confusion",8,170],["magic mapping",5,180],["light",5,180],
	["hold monster",2,200],["sleep",5,50],["enchant armor",8,130],["identify",21,100],
	["scare monster",4,180],["gold detection",4,110],["teleportation",7,175],
	["enchant weapon",10,150],["create monster",5,75],["remove curse",8,105],
	["aggravate monsters",1,60],["blank paper",1,50],["genocide",1,200]]

p_magic = [["confusion",8,50],["paralysis",10,50],["poison",8,50],["gain strength",15,150],
	["see invisible",2,170],["healing",15,130],["monster detection",6,120],
	["magic detection",6,105],["raise level",2,220],["extra healing",5,180],
	["haste self",4,200],["restore strength",14,120],["blindness",4,50],
	["thirst quenching",1,50]]

r_magic = [["protection",9,200],["add strength",9,200],["sustain strength",5,180],
	["searching",10,200],["see invisible",10,175],["adornment",1,100],
	["aggravate monster",11,100],["dexterity",8,220],["increase damage",8,220],
	["regeneration",4,260],["slow digestion",9,240],["teleportation",9,100],
	["stealth",7,100]]

ws_magic = [["light",12,120],["striking",9,115],["lightning",3,200],["fire",3,200],
	["cold",3,200],["polymorph",15,210],["magic missile",10,170],["haste monster",9,50],
	["slow monster",11,220],["drain life",9,210],["nothing",1,70],["teleport away",5,140],
	["teleport to",5,60],["cancellation",5,130]]

a_class = [8,7,7,6,5,4,4,3]

a_names = ["leather armor", "ring mail", "studded leather armor", "scale mail",
	"chain mail", "splint mail", "banded mail", "plate mail"]

a_chances = [20,35,50,63,75,85,95,100]


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

class str_t:
	def __init__(self,st_str,st_add):
		self.st_str = st_str
		self.st_add = st_add

class magic_item:
	def __init__(self, mi_name, mi_prob, mi_worth):
		self.mi_name = mi_name
		self.mi_prob = mi_prob
		self.mi_worth = mi_worth

class stats:
	def __init__(self, s_str, s_exp, s_lvl, s_arm, s_hpt, s_dmg):
		self.s_str = str_t(s_str.st_str, s_str.st_add)
		self.s_exp = s_exp
		self.s_lvl = s_lvl
		self.s_arm = s_arm
		self.s_hpt = s_hpt
		self.s_dmg = s_dmg

class thing:
	def __init__(self,t_pos,t_turn,t_type,t_disguise,t_oldch,t_dest,t_flags,t_stats,t_pack):
		self.t_pos = coord(t_pos.x,t_pos.y)
		self.t_turn = t_turn
		self.t_type = t_type
		self.t_disguise = t_disguise
		self.t_oldch = t_oldch
		self.t_dest = coord(t_dest.x, t_dest.y)
		self.t_flags = t_flags
		self.t_stats = stats(t_stats.s_str, t_stats.s_exp, t_stats.s_lvl, t_stats.s_arm, t_stats.s_hpt, t_stats.s_dmg)
		self.t_pack = t_pack

class monster:
	def __init__(self, m_name, m_carry, m_flags, m_stats):
		self.m_name = m_name
		self.m_carry = m_carry
		self.m_flags = m_flags
		self.m_stats = stats(m_stats.s_str, m_stats.s_exp, m_stats.s_lvl, m_stats.s_arm, m_stats.s_hpt, m_stats.s_dmg)

class object:
	def __init__(self, o_type, o_pos, o_launch, o_damage,o_hurldmg, o_count, o_which, o_hplus, o_dplus, o_ac, o_flags, o_group):
		self.o_type = o_type
		self.o_pos = coord(o_pos.x, o_pos.y)
		self.o_launch = o_launch
		self.o_damage = o_damage
		self.o_hurldmg = o_hurldmg
		self.o_count = o_count
		self.o_which = o_which
		self.o_hplus = o_hplus
		self.o_dplus = o_dplus
		self.o_ac = o_ac
		self.o_flags = o_flags
		self.o_group = o_group

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

def pick_one(magic_list):
	for x in magic_list:
		i = rnd(100)
		if i < x[2]:
			return x[0]
	return magic_list[0][0]

def new_thing():
	global group, no_food
	empty = coord(0,0)
	item = object(0,empty,0,0,0,0,0,0,0,0,0,0)
	item.o_hplus = item.o_dplus = 0
	item.o_damage = item.o_hurldmg = "0d0"
	item.o_ac = 11
	item.o_count = 1
	item.o_group = 0
	item.o_flags = 0
	if no_food > 3:
		thing = 2
	else:
		thing = rnd(NUMTHINGS)
	if thing == 0:
		item.o_type = 'POTION'
		item.o_which = pick_one(p_magic)
	elif thing == 1:
		item.o_type = 'SCROLL'
		item.o_which = pick_one(s_magic)
	elif thing == 2:
		no_food = 0
		item.o_type = 'FOOD'
		if rnd(100) > 10:
			item.o_which = 0
		else:
			item.o_which = 1
	elif thing == 3:
		item.o_type = 'WEAPON'
		item.o_which = rnd(len(weapon_types))
		item.o_damage = w_dam[item.o_which]
		item.o_hurldmg = w_hrl[item.o_which]
		item.o_launch = w_launch[item.o_which]
		item.o_flags = w_flags[item.o_which]
		if item.o_flags & flags['ISMANY']:
			item.o_count = rnd(8) + 8
			item.o_group = group
			group += 1
		else:
			item.o_count = 1
			k = rnd(100)
			if k < 10:
				item.o_flags |= flags['ISCURSED']
				item.o_hplus -= rnd(3)+1
	elif thing == 4:
		item.o_type = 'ARMOR'
		for j in range(len(armor_types)):
			k = rnd(100)
			if k < a_chances[j]:
				break
			if j == len(armor_types):
				j == 0
			item.o_which = j
			item.o_ac = a_class[j]
			k = rnd(100)
			if k < 20:
				item.o_flags |= flags['ISCURSED']
				item.o_ac += rnd(3) + 1
			elif k < 28:
				item.o_ac -= rnd(3) + 1
	elif thing == 5:
		item.o_type = 'RING'
		item.o_which = pick_one(r_magic)
		if item.o_which == ring_types['R_ADDSTR'] or item.o_which == ring_types['R_PROTECT'] or	item.o_which == ring_types['R_ADDHIT'] or item.o_which == ring_types['R_ADDDAM']:
				item.o_ac = rnd(3)
				if item.o_ac == 0:
					item.o_ac = -1
					item.o_ac |= flags['ISCURSED']
		if item.o_which == ring_types['R_AGGR'] or item.o_which == ring_types['R_TELEPORT']:
				item.o_flags |= flags['ISCURSED']
	elif thing == 6:
		item.o_type = 'STICK'
		item.o_which = pick_one(ws_magic)
		#No extra staff damage, for simplicity's sake
		item.o_damage = "1d1"
		item.o_hurldmg = "1d1"
		item.o_charges =rnd(5) + 3
		if item.o_which == stick_types['WS_HIT']:
			item.o_hplus = 3
			item.o_dplus = 3
			item.o_damage = "1d8"
		elif item.o_which == stick_types['WS_LIGHT']:
			item.o_charges = rnd(10) + 10
	return item

def new_level():
	stdscr.erase()
	global level, max_level, no_food, player, items, lvl_obj, msg_list
	if level > max_level:
		max_level = level
	do_rooms()
	do_passages()
	no_food += 1

	# Add items
	if amulet == 1 or level >= max_level:
		for x in range(MAXOBJ):
			if rnd(100) < 35:
				item = new_thing()
				lvl_obj.append(item)
				rm = rnd_room()
				done = 0
				while done == 0:
					item.o_pos = rnd_pos(rooms[rm])
					tile = chr(stdscr.inch(item.o_pos.y, item.o_pos.x) & 0x00FF)
					if tile == tiles['FLOOR']:
						stdscr.addch(tiles[item.o_type])
						done = 1
	#put amulet generation here


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

	# Add stairs
	rm = rnd_room()
	stairs = rooms[rm].r_gold
	while stairs == rooms[rm].r_gold:
		stairs = rnd_pos(rooms[rm])
	stdscr.addch(stairs.y, stairs.x, tiles['STAIRS'])

	# Add light

	# Add player
	rm = rnd_room()
	playerpos = rnd_pos(rooms[rm])
	oldch = chr(stdscr.inch(playerpos.y, playerpos.x) & 0x00FF)
	player.t_oldch = oldch
	stdscr.addch(playerpos.y, playerpos.x, tiles['PLAYER'])
	player.t_pos = playerpos

	if level > 1:
		msg_list.append("You delve downwards...")
	else:
		msg_list.append("Welcome to the dungeon!")

def init():
	global MAXROOMS, group, msg_list, rooms, level, no_food, traps, player, max_hp, max_stats, purse, pack, lvl_obj
	empty=coord(0,0)
	empty_str_t = str_t(0,0)
	emptystats=stats(empty_str_t,0,0,0,0,"")
	pack = []
	rooms = [room(empty,empty,empty,0,0,0,[empty,empty,empty,empty]) for i in range(MAXROOMS)]
	traps = [trap(empty,0,0) for i in range(MAXTRAPS)]
	player = thing(empty,0,0,0,'.',empty,0,emptystats,pack)
	player.t_stats.s_lvl = 1
	player.t_stats.s_exp = 0L
	max_hp = player.t_stats.s_hpt = 12
	if rnd(100) == 7:
		player.t_stats.s_str.st_str = 16
		player.t_stats.s_str.st_add = 0
	else:
		player.t_stats.s_str.st_str = 16
		player.t_stats.s_str.st_add = 0
	player.t_stats.s_dmg = "1d4"
	player.t_stats.s_arm = 10
	max_stats = player.t_stats
	item = object(0,empty,0,"","",0,0,0,0,0,0,0)
	purse = 0
	lvl_obj = []
	msg_list = []
	group = 0
	level = 1
	random.seed()
	no_food = 0
	new_level()

def status():
	global level, purse, max_hp
	hp = player.t_stats.s_hpt
	strength = player.t_stats.s_str.st_str
	status = "Level: " + str(level) + " Gold: " + str(purse) + " Hp: "
	status +=  str(hp) + "(" + str(max_hp) + ") Str: " + str(strength)
	stdscr.addstr(LINES - 1, 0, status)

def do_move(dy,dx):
	global player, take
	nh = coord(player.t_pos.x + dx, player.t_pos.y + dy)
	if nh.x < 0 or nh.x > COLS-1 or nh.y < 0 or nh.y > LINES-1:
		return
	ch = chr(stdscr.inch(nh.y, nh.x) & 0x00FF)
	if ch == ' ' or ch == '|' or ch == '-':
		return
	if ch == tiles['GOLD']:
		take = "money"
	stdscr.addch(player.t_pos.y, player.t_pos.x, player.t_oldch)
	player.t_oldch = chr(stdscr.inch(nh.y, nh.x) & 0x00FF)
	stdscr.addch(nh.y, nh.x, tiles['PLAYER'])
	player.t_pos = nh

def command():
	global player, level, take, rooms, purse, msg_list
	# First deal with messages
	stdscr.move(0,0)
	stdscr.clrtoeol()
	while len(msg_list) > 0:
		stdscr.move(0,0)
		stdscr.clrtoeol()
		msg = msg_list.pop()
		stdscr.addstr(0,0,msg)
		if len(msg_list) > 0:
			stdscr.addstr("--More--")
			ch = stdscr.getch()
			while ch != ord(' '):
				ch = stdscr.getch()


	take = ""
	status()
	ch = stdscr.getch()

	# Move character

	if ch == ord('h'):
		do_move(0,-1)
	if ch == ord('j'):
		do_move(1,0)
	if ch == ord('k'):
		do_move(-1,0)
	if ch == ord('l'):
		do_move(0,1)
	if ch == ord('y'):
		do_move(-1,-1)
	if ch == ord('u'):
		do_move(-1,1)
	if ch == ord('b'):
		do_move(1,-1)
	if ch == ord('n'):
		do_move(1,1)

	# Pick up stuff
	for x in rooms:
		if x.r_gold.x == player.t_pos.x and x.r_gold.y == player.t_pos.y:
			purse += x.r_goldval
			x.r_gold.x = x.r_gold.y = 0
			player.t_oldch = tiles['FLOOR']



	if ch == ord('q'):
		sys.exit()
	if ch == ord('>'):
		if player.t_oldch == tiles['STAIRS']:
			level += 1
			new_level()

def main(stdscr):
	# start
	init()
	while True:
		command()


greeting = "Hello, " + os.environ['USER'] + ", just a moment while I dig the dungeon...\n"
print greeting
stdscr=curses.initscr()
curses.curs_set(0)
curses.wrapper(main)

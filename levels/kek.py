from game import *

spawn_pos = [40, 40]
background = 'game\\content/bg2.png'
guns = [
	'rifle',
	'shootgun'
]
ais = [
	
]
actors = [
	objects.Portal(x1=238, y1=52, x2=40, y2=0, w=40, h=40)
]
blocks = [
	level.Block(0,-40,'-'),
	level.Block(0,0,'-'),
	level.Block(0,40,'-'),
	level.Block(0,80,'-'),
	level.Block(0,120,'-'),
	level.Block(40,160,'-'),
	level.Block(40,200,'-'),
	level.Block(40,240,'-'),
	level.Block(80,240,'-'),
	level.Block(80,280,'-'),
	level.Block(120,280,'-'),
	level.Block(160,280,'-'),
	level.Block(200,280,'-'),
	level.Block(240,280,'-'),
	level.Block(240,240,'-')
]

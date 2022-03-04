from game import *

spawn_pos = [40, 40]
background = 'game\\content/bg2.png'
guns = [
	'rifle',
	'shootgun'
]
sun_level = 0

#### Dont delete this comment, edit only script inside ####

# called once on level loading
def load(game):
	pass

# called every frame update
def update(game):
	pass

###########################################################

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
	level.Block(280,280,'-'),
	level.Block(320,280,'-'),
	level.Block(360,280,'-'),
	level.Block(400,280,'-'),
	level.Block(440,280,'-'),
	level.Block(480,280,'-'),
	level.Block(520,280,'-'),
	level.Block(560,280,'-'),
	level.Block(600,280,'-'),
	level.Block(640,280,'-'),
	level.Block(680,280,'-'),
	level.Block(720,280,'-'),
	level.Block(760,280,'-'),
	level.Block(800,280,'-'),
	level.Block(840,280,'-'),
	level.Block(880,280,'-'),
	level.Block(920,280,'-'),
	level.Block(960,280,'-'),
	level.Block(1000,280,'-'),
	level.Block(1080,280,'-'),
	level.Block(1120,280,'-'),
	level.Block(1040,280,'-')
]

from game import *

spawn_pos = (40, 40)
background = 'game\\content/bg2.png'
guns = [
	
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
	enemies.ShoterAI(x=800, y=-120, gun='sniper')
]
actors = [
	objects.Aid(x=140, y=86, hp=150),
	objects.ZoomTriger(x=-4, y=-116, w=400, h=250, zoom=0.6),
	objects.Text(x=1153, y=10, text='To be continued...', size=40, color='white')
]
blocks = [
	level.Block(0,-80,'!'),
	level.Block(0,-40,'!'),
	level.Block(0,0,'!'),
	level.Block(0,40,'!'),
	level.Block(0,80,'!'),
	level.Block(0,120,'%'),
	level.Block(40,120,'%'),
	level.Block(80,120,'%'),
	level.Block(120,120,'%'),
	level.Block(160,120,'%'),
	level.Block(200,120,'%'),
	level.Block(240,120,'%'),
	level.Block(280,120,'%'),
	level.Block(320,120,'%'),
	level.Block(360,120,'%'),
	level.Block(0,-120,'*'),
	level.Block(40,-160,'*'),
	level.Block(80,-160,'*'),
	level.Block(120,-160,'*'),
	level.Block(240,-160,'*'),
	level.Block(280,-160,'*'),
	level.Block(360,-120,'*'),
	level.Block(320,-160,'*'),
	level.Block(40,-120,'*'),
	level.Block(320,-120,'*'),
	level.Block(280,-200,'*'),
	level.Block(240,-200,'*'),
	level.Block(200,-200,'*'),
	level.Block(160,-200,'*'),
	level.Block(120,-200,'*'),
	level.Block(80,-200,'*'),
	level.Block(400,120,'%'),
	level.Block(440,120,'%'),
	level.Block(480,120,'%'),
	level.Block(520,120,'%'),
	level.Block(560,120,'%'),
	level.Block(600,120,'%'),
	level.Block(640,120,'%'),
	level.Block(680,120,'%'),
	level.Block(720,120,'%'),
	level.Block(760,120,'%'),
	level.Block(360,-80,'!'),
	level.Block(360,-40,'!'),
	level.Block(360,0,'!'),
	level.Block(800,120,'%'),
	level.Block(840,120,'%'),
	level.Block(880,120,'%'),
	level.Block(800,80,'|'),
	level.Block(800,40,'|'),
	level.Block(800,0,'|'),
	level.Block(800,-40,'|'),
	level.Block(760,-40,'+'),
	level.Block(760,-80,'+'),
	level.Block(720,-80,'+'),
	level.Block(720,-120,'+'),
	level.Block(720,-160,'+'),
	level.Block(760,-160,'+'),
	level.Block(760,-200,'+'),
	level.Block(800,-200,'+'),
	level.Block(840,-200,'+'),
	level.Block(840,-160,'+'),
	level.Block(880,-160,'+'),
	level.Block(880,-120,'+'),
	level.Block(880,-80,'+'),
	level.Block(840,-80,'+'),
	level.Block(840,-40,'+'),
	level.Block(800,-160,'+'),
	level.Block(800,-80,'+'),
	level.Block(840,-120,'+'),
	level.Block(920,120,'%'),
	level.Block(960,120,'%'),
	level.Block(1000,120,'%'),
	level.Block(1040,120,'%'),
	level.Block(1080,120,'%'),
	level.Block(1120,120,'%'),
	level.Block(1160,120,'%'),
	level.Block(1200,120,'%'),
	level.Block(1240,120,'%'),
	level.Block(1280,120,'%'),
	level.Block(1320,120,'%'),
	level.Block(1360,120,'%'),
	level.Block(1400,120,'%'),
	level.Block(1440,120,'%'),
	level.Block(1480,120,'%')
]

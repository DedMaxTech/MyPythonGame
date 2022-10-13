from game import *

spawn_pos = (40, 40)
background = 'game\\content/bg2.png'
guns = [
	
]
sun_level = 240

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
	objects.LightZone(x=203, y=882, w=300, h=100, opacity=253),
	objects.PointLight(x=814, y=752, rotation=20),
	objects.Light(x=835, y=933, scale=5.0),
	objects.PointLight(x=105, y=726, rotation=0),
	objects.PointLight(x=585, y=735, rotation=-15)
]
blocks = [
	level.Block(0,280,'!'),
	level.Block(0,320,'!'),
	level.Block(0,360,'!'),
	level.Block(0,400,'!'),
	level.Block(0,440,'!'),
	level.Block(0,480,'!'),
	level.Block(0,520,'!'),
	level.Block(0,560,'!'),
	level.Block(0,600,'!'),
	level.Block(0,640,'!'),
	level.Block(0,680,'!'),
	level.Block(0,720,'!'),
	level.Block(0,760,'!'),
	level.Block(0,800,'!'),
	level.Block(0,840,'!'),
	level.Block(0,880,'!'),
	level.Block(0,920,'!'),
	level.Block(0,960,'!'),
	level.Block(0,1000,'!'),
	level.Block(40,1000,'!'),
	level.Block(80,1000,'!'),
	level.Block(120,1000,'!'),
	level.Block(160,1040,'!'),
	level.Block(200,1040,'!'),
	level.Block(240,1040,'!'),
	level.Block(280,1040,'!'),
	level.Block(320,1040,'!'),
	level.Block(360,1000,'!'),
	level.Block(400,1000,'!'),
	level.Block(440,1000,'!'),
	level.Block(320,1000,'!'),
	level.Block(280,1000,'!'),
	level.Block(240,1000,'!'),
	level.Block(200,1000,'!'),
	level.Block(160,1000,'!'),
	level.Block(520,1000,'!'),
	level.Block(560,1000,'!'),
	level.Block(600,1000,'!'),
	level.Block(640,1000,'!'),
	level.Block(680,1000,'!'),
	level.Block(720,1000,'!'),
	level.Block(760,1000,'!'),
	level.Block(800,1000,'!'),
	level.Block(840,1000,'!'),
	level.Block(480,1000,'!')
]

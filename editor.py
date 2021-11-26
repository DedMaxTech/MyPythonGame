import pygame as pg
from glob import glob
import os
import database
import cfg
pg.init()
from game import  *
from game.UI import Interface, Button, TextField
d  = database.DB()

class Editor:
    def __init__(self):
        self.res, self.fps = (1920,1080), cfg.fps
        os.environ['SDL_VIDEO_WINDOW_POS'] = '0,0'
        

        self.frame: pg.Surface = pg.Surface(self.res)
        self.screen=pg.display.set_mode((self.res[0], self.res[1] + 40))
        self.clock = pg.time.Clock()
        self.ui = Interface(anims=False)
        self.info_ui = Interface(anims=False)
        self.info_ui.set_ui([Button((1400+30,50),'white','Press MMB to select obj',50),])
        self.world = level.World()
        self.levelname = ''
        self.camera = pg.Rect(0,40,self.res[0], self.res[1])

        self.editing = False
        self.drawing = False
        self.brush = '='
        self.last_brush = None
        self.zoom=1

        pg.display.set_caption('Editor')

        self.main_menu()

        self.run()

    def main_menu(self):
        self.editing=False
        bs = [
            Button((100,100), 'white', 'Levels:', 80, ),
            Button((1000,600), 'white', 'Create Level', 50,self.create_menu,'darkgrey')]
        a = 0
        for i in glob('levels/*.py'):
            bs.append(Button((150, 200 + a * 45), 'white', i, 30, self.open_level, 'red', args=(i[i.index('\\')+1:-3])))
            a += 1
        a = 0
        bs.append(Button((1000,100), 'white', 'Blocks:', 80, ),)
        for i in glob('levels/blocks/*.txt'):
            bs.append(Button((1050, 200 + a * 45), 'white', i, 30, self.open_level, 'red', args=(i)));
            a += 1
        bs.append(Button((150,600), 'white', 'Exit', 50,exit,'darkgrey'))
        self.ui.set_ui(bs)

    def create_menu(self, add=[]):
        self.ui.set_ui([
            Button((100,100), 'white', 'Create Level', 80, ),
            Button((100,200), 'white', 'Level name:', 40, ), TextField((300,200),'black','click to write', 40,'white', size=(400,40)),
            Button((100,300), 'white', 'Path to bg:', 40, ), TextField((300,300),'black','click to write', 40,'white', size=(400,40)),Button((700,300), 'white', ' .png', 40, ),
            Button((100,400), 'white', 'Back', 50, self.main_menu, 'darkgrey'),Button((1000,400), 'white', 'Create', 50, self.create_level, 'darkgrey'),
        ]+add)
    def create_level(self):
        path, bg = f'levels/{self.ui.buttons[2].text}.py', f'game\content/{self.ui.buttons[4].text}.png'
        print(path,bg)
        if os.path.isfile(path):
            self.create_menu([Button((1000,450), 'red', 'Already exists', 50)])
        elif not os.path.isfile(bg):
            self.create_menu([Button((1000,450), 'red', 'No such bg', 50)])
        else:
            with open(path,'w') as file:
                file.write(level.conf.format(bg=bg))
            self.open_level(self.ui.buttons[2].text)


    def open_level(self, lvl):
        self.ui.clear()
        self.world.open_world(lvl, self)
        self.levelname = lvl
        bs = [];
        a = 0
        bs.append(Button((0, 0), 'white', 'SAVE', 35, self.save_level, bg='darkgrey', ))
        bs.append(Button((100, 0), 'white', 'EXIT', 35, self.main_menu, bg='darkgrey', ))
        for i in level.block_s:
            bs.append(Button((200 + a * 45, 0), 'white', '', 40, callback_f=self.set_brush, size=(40, 40),
                             img=level.block_s[i]['img'], args=(i)))
            a += 1
        objs = [objects.Aid,objects.Ammo,objects.GunsCase,objects.Portal, enemies.MeleeAI,enemies.ShoterAI,
            objects.ScreenTriger,objects.ScreenConditionTriger, objects.Trigger, objects.LevelTravelTriger,]
        bs+=vertical(3, [Button((1430, 500), 'white', str(i).split('.')[2][:-2], 25, self.create_obj, bg='darkgrey', args=(i)) for i in objs])
        self.ui.set_ui(bs)
        # self.camera
        self.editing = True

    def save_level(self):
        self.editing = False
        print(self.levelname)
        self.world.save_world(self.levelname)
        self.ui.clear()
        self.main_menu()

    def set_brush(self, t):
        self.last_brush = self.brush
        self.brush = t


    def camera_update(self, keys):
        if keys[pg.K_a]:
            self.camera.x -= 10
        if keys[pg.K_d]:
            self.camera.x += 10
        if keys[pg.K_w]:
            self.camera.y -= 10
        if keys[pg.K_s]:
            self.camera.y += 10


    def draw(self):
        self.frame.fill('black', [0,0,self.res[0], self.res[1]+40])
        if self.editing:
            self.world.draw(self.frame, self.camera)
            for a in self.world.actors:
                a.debug_draw(self.frame, self.camera)
            pg.draw.rect(self.frame, 'red', (-self.camera.x,-self.camera.y-40,self.camera.w,self.camera.h),1)
            pg.draw.line(self.frame, 'red', (0,-self.camera.y-40),(self.camera.w,-self.camera.y-40),1)
            pg.draw.line(self.frame, 'red', (0,-self.camera.y+self.camera.h-40),(self.camera.w,-self.camera.y+self.camera.h-40),1)
        x,y= pg.mouse.get_pos()
        x,y=utils.real((-x,-y-40), self.camera)
        

        self.screen.blit(pg.transform.scale(self.frame, (int(self.res[0]/self.zoom),int(self.res[1]/self.zoom),)),(0,0))
        self.ui.draw(self.screen)
        if self.editing: self.info_ui.draw(self.screen)
        utils.debug(f'x: {-x} y: {-y}', self.screen, y=50)
        utils.debug(self.zoom, self.screen, y=100)

    def event_loop(self):
        w=1400
        for event in pg.event.get():
            if event.type == pg.QUIT: exit()
            self.ui.update_buttons(event)
            self.info_ui.update_buttons(event)
            if self.editing:
                # if hasattr(event, 'pos'):
                #     setattr(event, 'pos', (remap(event.pos[0], (0, self.res[0]), (0,self.res[0]/self.zoom)), remap(event.pos[1], (0, self.res[1]), (0,self.res[1]/self.zoom))))
                if event.type == pg.MOUSEBUTTONDOWN:
                    if event.pos[0]>w or event.pos[1]<40: continue
                    if event.button == pg.BUTTON_RIGHT:
                        self.drawing = True
                    if event.button == pg.BUTTON_LEFT:
                        self.world.set_block((event.pos[0] + self.camera.x, event.pos[1]+self.camera.y), self.brush)
                    if event.button == pg.BUTTON_MIDDLE:
                        x,y = event.pos
                        obj = self.world.get_nearest(core.Saving, real(event.pos,self.camera, True))
                        self.obj_info(obj)
                    if event.button==pg.BUTTON_WHEELDOWN:
                        self.zoom/=1.2
                        if self.zoom<0.3:self.zoom=0.3
                    if event.button==pg.BUTTON_WHEELUP:
                        self.zoom*=1.2
                        if self.zoom>1:self.zoom=1
                if event.type == pg.MOUSEBUTTONUP:
                    if event.button == pg.BUTTON_RIGHT: self.drawing = False
                if event.type == pg.MOUSEMOTION and self.drawing: self.world.set_block(
                    (event.pos[0] + self.camera.x, event.pos[1] +self.camera.y),
                    self.brush)
                if event.type == pg.KEYDOWN and event.key == pg.K_LSHIFT:
                    self.last_brush = self.brush
                    self.brush = '0'
                if event.type == pg.KEYUP and event.key == pg.K_LSHIFT: self.brush = self.last_brush
                if event.type == pg.KEYDOWN and event.key == pg.K_SPACE: self.set_brush(self.last_brush)
    def create_obj(self, obj):
        a = obj()
        a.rect.x,a.rect.y=real((1920/2,1080/2), self.camera, invert=True)
        if isinstance(a, enemies.BaseAI): self.world.ais.append(a)
        self.world.actors.append(a)

    def obj_info(self, obj):
        w=1400
        self.info_ui.set_ui([
            Button((w+30,50),'white','Object info:',50),
            Button((w+30,110),'white',f'{obj.module}.{obj.__class__.__name__}',40),
            *vertical(3,[Button((w+30,160),'white',str(i).title(),30) for i in obj.slots]+[Button((0,0), 'white', 'Delete', 30, self.del_obj, bg='darkgrey', args=(obj))]),
            *vertical(3, [TextField((w+150, 160),'black', str(obj._get_att_val(i[0])), 30,'white',callback_f=obj.edit, args=(key,), add_text=True) for key,i in obj.slots.items()]),
            
        ])
    def del_obj(self, obj):
        self.info_ui.set_ui([Button((1400+30,50),'white','Press MMB to select obj',50),])
        del self.world.actors[self.world.actors.index(obj)]

    def loop(self):

        self.event_loop()

        self.camera_update(pg.key.get_pressed())

        self.draw()
        pg.display.update()

    def run(self):
        while True:
            self.loop()
            self.clock.tick(self.fps)


if __name__ == '__main__':
    ed = Editor()
    ed.run()

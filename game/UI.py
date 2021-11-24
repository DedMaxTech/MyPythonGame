from typing import Union, List
import pygame as pg
from .utils import *
import cfg


class Button:
    def __init__(self, pos, color, text, font: Union[int, pg.font.Font], callback_f=None, bg=None,bg_hover=None, img=None, size=None,
                 args: tuple = None, textfield=None):
        self.pos = self.x, self.y = pos
        self.color = pg.Color(color)
        self.font: pg.font.Font = font if type(font) == pg.font.Font else pg.font.Font('game/content/pixel_font.ttf', font)
        self.size = self.font.size(text) if size is None else size
        self.bg = bg if bg is None else pg.Color(bg)
        self.img = pg.image.load(img).convert_alpha() if img is not None else None
        self.text = text
        self.func = callback_f if callback_f is not None else self.nothing
        self.args = args
        self.rect = pg.Rect(self.x, self.y, self.size[0]+10, self.size[1])
        self.hover = False
        self.texfield=textfield
        
    def nothing(self): pass

    def render(self, screen:pg.Surface):
        if self.bg:
            if not self.hover:
                screen.fill(self.bg, self.rect)
            else:
                off = 50
                screen.blit(self.font.render('~ ', False, self.color), (self.rect.x+5-self.font.size('~ ')[0], self.rect.y))
                screen.fill((abs(self.bg.r-off), abs(self.bg.g-off),abs(self.bg.b-off)), (self.rect.x, self.rect.y,self.rect.w+20, self.rect.h))
        if self.img: screen.blit(self.img, self.rect.topleft)
        screen.blit(self.font.render(self.text, False, self.color), (self.rect.x+5, self.rect.y))

def vertical(margin, buttons:List[Button]):
    x,y = buttons[0].rect.topleft
    for b in buttons:
        b.rect.topleft = (x,y)
        y+=b.size[1]+margin
    return buttons
def horizontal(margin, buttons:List[Button]):
    x,y = buttons[0].rect.topleft
    for b in buttons:
        b.rect.topleft = (x,y)
        x+=b.size[0]+margin
    return buttons

class TextField:
    def __init__(self, pos, color, text, font: Union[int, pg.font.Font], bg=None, size=None, callback_f=None, args: tuple = None, add_text=False):
        self.pos = self.x, self.y = pos
        self.color = pg.Color(color)
        self.font: pg.font.Font = font if type(font) == pg.font.Font else pg.font.Font('game/content/pixel_font.ttf', font)
        self.size = self.font.size(text) if size is None else size
        self.bg = bg if bg is pg.Color('white') else pg.Color(bg)
        self.text = text
        self.func = callback_f
        self.args = args
        self.rect = pg.Rect(self.x-5, self.y, self.size[0]+5, self.size[1])
        self.hover = False
        self.active = False
        self.add = add_text
    
    def update(self, event):
        if self.active and event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE: self.active = False
            elif event.key == pg.K_RETURN:
                self.active = False
                add = (self.text,) if self.add else ()
                if self.func: self.func(*((*self.args,) + add))
            elif event.key == pg.K_BACKSPACE:
                    if len(self.text) >= 1: self.text = self.text[:-1]
            else:
                self.text += event.unicode

    def render(self, screen:pg.Surface):
        if self.bg:
            if not self.hover:
                screen.fill(self.bg, self.rect)
            else:
                off = 50
                screen.fill((abs(self.bg.r-off), abs(self.bg.g-off),abs(self.bg.b-off)), (self.rect.x, self.rect.y,self.rect.w+20, self.rect.h))
        # if self.img: screen.blit(pg.image.load(self.img), self.pos)
        screen.blit(self.font.render(self.text + "|" if self.active else self.text, False, self.color), self.rect.topleft)
    
class ProgressBar:
    def __init__(self, pos, img_full, img_empty=None, value=1, colorkey='black'):
        self.img = img_full
        self.empty_img = img_empty
        self.value = value
        self.cur_val = value
        self.rect = img_full.get_rect()
        self.rect.topleft = pos
        self.key = colorkey
    
    def update(self):
        self.cur_val += (self.value - self.cur_val) / 20
        # self.cur_val += 1 if self.cur_val>self.value else
    
    def render(self, screen):
        if self.empty_img: screen.blit(self.empty_img, self.rect.topleft)
        sf = pg.Surface((self.rect.w, self.rect.h))
        sf.fill(self.key)
        sf.set_colorkey(self.key)
        sf.blit(self.img, (0,0))
        sf.fill(self.key, (self.rect.w*self.cur_val, 0, self.rect.w, self.rect.h))
        screen.blit(sf,self.rect.topleft)

class Interface:
    def __init__(self, sounds:bool=False, anims=True):
        self.buttons:List[Button] = []
        self.pos = 0,0
        self.w=0
        self.sounds, self.anims = sounds, anims
        self.last_frame = pg.Surface(cfg.res)
        if self.sounds:
            self.sound = pg.mixer.Sound('game/content/sounds/menu2.wav')
            self.sound.set_volume(0.2)

    def clear(self):
        self.buttons = []

    def set_ui(self, buttons: list, anim=True):
        self.draw(self.last_frame)
        self.buttons = buttons
        if anim: self.w = 0

    def draw(self, screen: pg.Surface, offset=(0,0)):
        if self.w<cfg.screen_h: self.w+=10
        for b in self.buttons:
            b.render(screen)
        if self.anims and self.w<cfg.screen_h:
            sf=pg.Surface(cfg.res)
            sf.blit(self.last_frame,(0,0))
            sf.fill('green',(0,0,self.w,cfg.screen_v))
            sf.set_colorkey('green')    
            screen.blit(sf,(0,0))
            

    def update_buttons(self, event=None):
        if event and event.type == pg.MOUSEBUTTONDOWN and event.button == pg.BUTTON_LEFT:
            for b in self.buttons:
                if type(b)==TextField: b.active = False
                collide = pg.Rect.collidepoint(b.rect, event.pos)
                if collide:
                    if self.sounds:
                        self.sound.play()
                    if type(b) == Button:
                        add = () if not b.texfield else (b.texfield.text)
                        if b.args: b.func(*((b.args,) + add))
                        else: b.func(*add)
                    elif type(b)==TextField:
                        b.active = True 
                        b.text = ''
        if event and event.type == pg.MOUSEMOTION:
            for b in self.buttons:
                collide = pg.Rect.collidepoint(b.rect, event.pos)
                if collide and self.sounds and not b.hover:
                    self.sound.play()
                b.hover = collide
                    
        elif event and event.type == pg.MOUSEMOTION: self.pos = event.pos
        [b.update(event) for b in self.buttons if event and type(b)==TextField and b.active]
        [i.update() for i in self.buttons if type(i)==ProgressBar]


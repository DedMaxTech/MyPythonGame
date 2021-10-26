from typing import Union, List
import pygame as pg



class Button:
    def __init__(self, pos, color, text, font: Union[int, pg.font.Font], callback_f=None, bg=None,bg_hover=None, img=None, size=None,
                 args: tuple = None):
        self.pos = self.x, self.y = pos
        self.color = pg.Color(color)
        self.font: pg.font.Font = font if type(font) == pg.font.Font else pg.font.Font('game/content/pixel_font.ttf', font)
        self.size = self.font.size(text) if size is None else size
        self.bg = bg if bg is None else pg.Color(bg)
        self.img = img
        self.text = text
        self.func = callback_f if callback_f is not None else self.nothing
        self.args = args
        self.rect = pg.Rect(self.x, self.y, self.size[0]+10, self.size[1])
        self.hover = False
        

    def nothing(self): pass

    def render(self, screen:pg.Surface, hover=False):
        self.hover = hover
        if self.bg:
            if not hover:
                screen.fill(self.bg, self.rect)
            else:
                off = 50
                screen.blit(self.font.render('~ ', False, self.color), (self.rect.x+5-self.font.size('~ ')[0], self.rect.y))
                screen.fill((abs(self.bg.r-off), abs(self.bg.g-off),abs(self.bg.b-off)), (self.rect.x, self.rect.y,self.rect.w+20, self.rect.h))
        if self.img: screen.blit(pg.image.load(self.img), self.rect.topleft)
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
    def __init__(self, pos, color, text, font: Union[int, pg.font.Font], bg=None, size=None, callback_f=None, args: tuple = None):
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
    
    def update(self, event):
        if self.active and event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE: self.active = False
            elif event.key == pg.K_RETURN:
                self.active = False
                if self.func: self.func()
            elif event.key == pg.K_BACKSPACE:
                    if len(self.text) >= 1: self.text = self.text[:-1]
            else:
                self.text += event.unicode

    def render(self, screen:pg.Surface, hover=False):
        self.hover = hover
        if self.bg:
            if not hover:
                screen.fill(self.bg, self.rect)
            else:
                off = 50
                screen.fill((abs(self.bg.r-off), abs(self.bg.g-off),abs(self.bg.b-off)), (self.rect.x, self.rect.y,self.rect.w+20, self.rect.h))
        # if self.img: screen.blit(pg.image.load(self.img), self.pos)
        screen.blit(self.font.render(self.text + "|" if self.active else self.text, True, self.color), self.pos)
    
class ProgressBar:
    def __init__(self, pos, img_full, img_empty=None, value=1, colorkey='black'):
        self.img = img_full
        self.empty_img = img_empty
        self.value = value
        self.rect = img_full.get_rect()
        self.rect.topleft = pos
        self.key = colorkey
    
    def render(self, screen):
        if self.empty_img: screen.blit(self.empty_img, self.rect.topleft)
        sf = pg.Surface((self.rect.w, self.rect.h))
        sf.fill(self.key)
        sf.set_colorkey(self.key)
        sf.blit(self.img, (0,0))
        sf.fill(self.key, (self.rect.w*self.value, 0, self.rect.w, self.rect.h))
        screen.blit(sf,self.rect.topleft)

class Interface:
    def __init__(self, sounds:bool=False):
        self.buttons:List[Button] = []
        self.pos = 0,0
        self.sounds = sounds
        if self.sounds:
            self.sound = pg.mixer.Sound('game/content/sounds/menu2.wav')
            self.sound.set_volume(0.2)

    def clear(self):
        self.buttons = []

    def set_ui(self, buttons: list):
        self.buttons = buttons

    def draw(self, screen: pg.Surface):
        for b in self.buttons:
            if type(b)==ProgressBar:
                b.render(screen)
                continue
            if pg.Rect.collidepoint(b.rect, self.pos):
                
                if self.sounds and not b.hover:
                    self.sound.play()
                b.render(screen, True)
            else:
                b.render(screen)

    def update_buttons(self, event):
        if event.type == pg.MOUSEBUTTONDOWN and event.button == pg.BUTTON_LEFT:
            for b in self.buttons:
                if type(b)==TextField: b.active = False
                if pg.Rect.collidepoint(b.rect, event.pos):
                    
                    if type(b) == Button:
                        if b.args: b.func(b.args)
                        else: b.func()
                    elif type(b)==TextField:
                        b.active = True 
                        b.text = ''
                    
        elif event.type == pg.MOUSEMOTION: self.pos = event.pos
        [b.update(event) for b in self.buttons if type(b)==TextField and b.active]


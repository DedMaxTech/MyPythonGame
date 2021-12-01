from typing import Union, List
import pygame as pg
from .utils import *
import cfg

sounds = not pg.mixer.get_init() is None
if sounds:
    SOUNDS = {
        'hover':pg.mixer.Sound('game/content/sounds/menu2.wav'),
    }
    SOUNDS['hover'].set_volume(0.1)

class Widget:
    def __init__(self, pos,size) -> None:
        self.rect = pg.Rect(*pos,*size)
        self.hovered = False
        self.active=False
        self.die=False
        self.die_timer=1000
        self._delete=False
        self.sounds = sounds
    def update(self,event,delta,offset=(0,0)):
        if self.die:
            if self.die_timer>0: self.die_timer-=delta
            else: self._delete=True
        if event:
            if hasattr(event,'pos'): pos = event.pos[0]-offset[0],event.pos[1]-offset[1]
            if event.type==pg.MOUSEBUTTONDOWN and event.button == pg.BUTTON_LEFT:
                if self.rect.collidepoint(*pos):
                    self.press()
                    self.active=True
                else: 
                    self.active=False
                    self.unactive(event.pos)
            if event.type==pg.MOUSEBUTTONUP and event.button == pg.BUTTON_LEFT and self.rect.collidepoint(*pos):self.release()
            if event.type==pg.MOUSEMOTION and not self.hovered and self.rect.collidepoint(*pos):
                if self.sounds: SOUNDS['hover'].play()
                self.hovered=True
                self.hover()
            if event.type==pg.MOUSEMOTION and self.hovered and not self.rect.collidepoint(*pos):
                self.hovered=False
                self.unhover()
            if event.type==pg.KEYDOWN: self.key_pressed(event.key, event.unicode)
    def hover(self):pass
    def unhover(self):pass
    def press(self):pass
    def release(self):pass
    def unactive(self, pos):pass
    def key_pressed(self, key, unicode):pass
    def delete(self, time=0): 
        self.die=True
        self.die_timer=time
    def render(self, screen:pg.Surface, offset=(0,0)): pass

class Button(Widget):
    def __init__(self, pos, color, text, font: Union[int, pg.font.Font], callback_f=None, bg=None,bg_hover=None, img=None, size=None,
                 args: tuple = None, textfield=None, autodel=None):
        
        self.pos = self.x, self.y = pos
        self.color = pg.Color(color)
        self.font: pg.font.Font = font if type(font) == pg.font.Font else pg.font.Font('game/content/pixel_font.ttf', font)
        self.size = self.font.size(text) if size is None else size
        super().__init__(pos,self.size)
        self.bg = bg if bg is None else pg.Color(bg)
        self.img = pg.image.load(img).convert_alpha() if img is not None else None
        self.text = text
        self.func = callback_f if callback_f is not None else self.nothing
        self.args = args
        self.rect = pg.Rect(self.x, self.y, self.size[0]+10, self.size[1])
        # self.hover = False
        self.texfield=textfield
        if autodel: self.delete(autodel)
        
    def nothing(self): pass
    def press(self):
        if not self.func: return
        args = (() if not self.args else (self.args,))+(() if not self.texfield else (self.texfield.text,))
        self.func(*args)

    def render(self, screen:pg.Surface,offset=(0,0)):
        if self.bg:
            if not self.hovered:
                screen.fill(self.bg, (self.rect.x-offset[0], self.rect.y-offset[1], self.rect.w,self.rect.h))
            else:
                off = 50
                screen.blit(self.font.render('~ ', False, self.color), (self.rect.x-offset[0]+5-self.font.size('~ ')[0], self.rect.y-offset[1]))
                screen.fill((abs(self.bg.r-off), abs(self.bg.g-off),abs(self.bg.b-off)), (self.rect.x-offset[0], self.rect.y-offset[1],self.rect.w+20, self.rect.h))
        if self.img: screen.blit(self.img, (self.rect.x-offset[0], self.rect.y-offset[1]))
        screen.blit(self.font.render(self.text, False, self.color), (self.rect.x-offset[0]+5, self.rect.y-offset[1]))

def vertical(margin, buttons:List[Button], invert=False):
    x,y = buttons[0].rect.topleft
    k = 1 if not invert else 1
    for b in buttons:
        b.rect.topleft = (x,y)
        y+=(b.size[1]+margin)*k
    return buttons
def horizontal(margin, buttons:List[Button],invert=False):
    x,y = buttons[0].rect.topleft
    k = 1 if not invert else 1
    for b in buttons:
        b.rect.topleft = (x,y)
        x+=(b.size[0]+margin)*k
    return buttons

class TextField(Widget):
    def __init__(self, pos, color, text, font: Union[int, pg.font.Font], bg=None, size=None, callback_f=None, args: tuple = None, add_text=False, clear_on_click=False):
        self.pos = self.x, self.y = pos
        self.color = pg.Color(color)
        self.font: pg.font.Font = font if type(font) == pg.font.Font else pg.font.Font('game/content/pixel_font.ttf', font)
        self.size = self.font.size(text) if size is None else size
        super().__init__(pos,self.size)
        self.bg = bg if bg is pg.Color('white') else pg.Color(bg)
        self.text = text
        self.func = callback_f
        self.args = args
        self.rect = pg.Rect(self.x-5, self.y, self.size[0]+5, self.size[1])
        self.add = add_text
        self.clear_on_click=clear_on_click
        self.ind = len(self.text) if not clear_on_click else 0
    
    def press(self):
        if self.clear_on_click: self.text=''

    def key_pressed(self, key,uni):
        if not self.active: return
        if key == pg.K_ESCAPE: self.active = False
        elif key == pg.K_RETURN:
            self.active = False
            add = (self.text,) if self.add else ()
            if self.func: self.func(*((*self.args,) + add))
        elif key == pg.K_BACKSPACE:
            if self.ind >= 1:
                self.text = self.text[:self.ind-1]+self.text[self.ind:]
                self.ind -=1
        elif key== pg.K_LEFT: 
            self.ind = limit(self.ind-1, min=0)
            print(self.ind)
        elif key== pg.K_RIGHT:
            self.ind = limit(self.ind+1, max=len(self.text))
            print(self.ind)
        else:
            self.text = self.text[:self.ind]+uni+self.text[self.ind:]
            self.ind = limit(self.ind+1, max=len(self.text))
    
    def unactive(self, pos):
        add = (self.text,) if self.add else ()
        if self.func: self.func(*((*self.args,) + add))

    def render(self, screen:pg.Surface, offset=(0,0)):
        if self.bg:
            if not self.hovered:
                screen.fill(self.bg, (self.rect.x-offset[0], self.rect.y-offset[1], self.rect.w,self.rect.h))
            else:
                off = 50
                screen.fill((abs(self.bg.r-off), abs(self.bg.g-off),abs(self.bg.b-off)), (self.rect.x-offset[0], self.rect.y-offset[1],self.rect.w+20, self.rect.h))
        # if self.img: screen.blit(pg.image.load(self.img), self.pos)
        screen.blit(self.font.render(f'{self.text[:self.ind]}{"|" if self.active else ""}{self.text[self.ind:]}', False, self.color), (self.rect.x-offset[0]+5, self.rect.y-offset[1]))
    
class ProgressBar(Widget):
    def __init__(self, pos, img_full, img_empty=None, value=1, colorkey='black'):
        super().__init__(pos,img_full.get_size())
        self.img = img_full.convert_alpha()
        self.empty_img = img_empty.convert_alpha() if img_empty else None
        self.value = value
        self.cur_val = value
        self.rect = img_full.get_rect()
        self.rect.topleft = pos
        self.key = colorkey
    
    def update(self, event, delta,offset=(0,0)):
        self.cur_val += (self.value - self.cur_val) / 20
        return super().update(event, delta,offset)
    
    def render(self, screen, offset=(0,0)):
        if self.empty_img: screen.blit(self.empty_img, (self.rect.x-offset[0]+5, self.rect.y-offset[1]))
        sf = pg.Surface((self.rect.w, self.rect.h))
        sf.fill(self.key)
        sf.set_colorkey(self.key)
        sf.blit(self.img, (0,0))
        sf.fill(self.key, (self.rect.w*self.cur_val, 0, self.rect.w, self.rect.h))
        screen.blit(sf,(self.rect.x-offset[0]+5, self.rect.y-offset[1]))



class Interface(Widget):
    VERTICAL = 'v'
    HORIZONTAL = 'h'
    FREE = 'f'
    def __init__(self,widgets=[],pos=(0,0),size=cfg.res, anims=False,relative=True):
        super().__init__(pos,size)
        self.widgets:List[Widget]=[]
        self.w=0
        self.anims=anims
        self.relative=relative
        # self.orientation = orientation
        # self.invert=invert
        self.last_frame = pg.Surface(size)
        self.set_ui(widgets)

    def clear(self):
        self.widgets = []
    
    def set_ui(self, buttons: list, anim=False):
        self.render(self.last_frame)
        self.widgets = buttons
        if anim: self.w = 0
    
    def add_ui(self, widgets):
        self.widgets+=widgets
        self.update_ui()

    def render(self, screen: pg.Surface, offset=(0,0)):
        offset = offset if self.relative else (0,0)
        if self.w<cfg.screen_h: self.w+=10
        for b in self.widgets:
            b.render(screen,(-self.rect.x+offset[0],-self.rect.y+offset[1]))
        if self.anims and self.w<cfg.screen_h:
            sf=pg.Surface(cfg.res)
            sf.blit(self.last_frame,(0,0))
            sf.fill('green',(0,0,self.w,cfg.screen_v))
            sf.set_colorkey('green')    
            screen.blit(sf,(0,0))
    
    def update_ui(self):
        pass

    def update(self, event=None, delta=0, offset=(0,0)):
        # if event and event.type == pg.MOUSEBUTTONDOWN and event.button == pg.BUTTON_LEFT:
        #     for b in self.buttons:
        #         if type(b)==TextField: b.active = False
        #         collide = pg.Rect.collidepoint(b.rect, event.pos)
        #         if collide:
        #             if self.sounds:
        #                 self.sound.play()
        #             if type(b) == Button:
        #                 add = () if not b.texfield else (b.texfield.text)
        #                 if b.args: b.func(*((b.args,) + add))
        #                 else: b.func(*add)
        #             elif type(b)==TextField:
        #                 b.active = True 
        #                 b.text = ''
        # if event and event.type == pg.MOUSEMOTION:
        #     for b in self.buttons:
        #         collide = pg.Rect.collidepoint(b.rect, event.pos)
        #         if collide and self.sounds and not b.hover:
        #             self.sound.play()
        #         b.hover = collide
                    
        # elif event and event.type == pg.MOUSEMOTION: self.pos = event.pos
        # [b.update(event) for b in self.buttons if event and type(b)==TextField and b.active]
        # [i.update() for i in self.buttons if type(i)==ProgressBar]
        offset = offset if self.relative else (0,0)
        [w.update(event, delta, (self.rect.x+offset[0],self.rect.y+offset[1])) for w in self.widgets]
        flag=False
        for i in self.widgets:
            if i._delete:
                del self.widgets[self.widgets.index(i)]
                flag=True
        if flag: self.update_ui()
UP = 'u'
DOWN = 'd' 
RIGHT='r'
LEFT='l'
FILL='f'
class Box(Interface):
    def __init__(self,margin=0,pos=(0, 0),size=cfg.res,anchor_h:Union[RIGHT,LEFT,FILL]=LEFT,anchor_v:Union[UP,DOWN,FILL]=UP, widgets=[]):
        print(pos)
        super().__init__(widgets=widgets, pos=pos,size=size, anims=False, relative=True)
        self.margin=margin
        self.anchor_h, self.anchor_v= anchor_h, anchor_v
        self.update_ui()
class VBox(Box):
    def update_ui(self):
        if self.anchor_v==UP:
            y=0
            for w in self.widgets:
                w.rect.y=y
                y+=w.rect.h+self.margin
        elif self.anchor_v==DOWN:
            y=self.rect.h
            for w in self.widgets:
                w.rect.bottom=y
                y-=w.rect.h+self.margin
        elif self.anchor_v==FILL:
            h=self.rect.h/len(self.widgets) - self.margin
            for w in self.widgets: w.rect.h=h
            y=0
            for w in self.widgets:
                w.rect.y=y
                y+=w.rect.h+self.margin
        
        if self.anchor_h==LEFT:
            for w in self.widgets:
                w.rect.x=0
        elif self.anchor_h==RIGHT:
            for w in self.widgets:
                w.rect.right=self.rect.w
        elif self.anchor_h==FILL:
            for w in self.widgets: w.rect.w = self.rect.w


class HBox(Box):
    def update_ui(self):
        if self.anchor_v==UP:
            for w in self.widgets:
                w.rect.y=0
        elif self.anchor_v==DOWN:
            for w in self.widgets:
                w.rect.bottom=self.rect.h
        elif self.anchor_v==FILL:
            for w in self.widgets: w.rect.h = self.rect.h
        
        if self.anchor_h==LEFT:
            x=0
            for w in self.widgets:
                w.rect.x=x
                x+=w.rect.w+self.margin
        elif self.anchor_h==RIGHT:
            x=self.rect.right
            for w in self.widgets:
                w.rect.right=x
                x-=w.rect.w+self.margin
        elif self.anchor_h==FILL:
            w = self.rect.w/len(self.widgets)-self.margin
            for wid in self.widgets: wid.rect.w = w
            x=0
            for wid in self.widgets:
                wid.rect.x=x
                x+=wid.rect.w+self.margin
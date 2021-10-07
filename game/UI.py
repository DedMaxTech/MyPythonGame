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
        self.rect = pg.Rect(self.x-5, self.y, self.size[0]+5, self.size[1])
        self.hover = False
        self.sound = pg.mixer.Sound('game/content/sounds/menu2.wav')
        self.sound.set_volume(0.2)
        

    def nothing(self): pass

    def render(self, screen:pg.Surface, hover=False):
        if hover and not self.hover:
            self.sound.play()
        self.hover = hover
        if self.bg:
            if not hover:
                screen.fill(self.bg, self.rect)
            else:
                off = 50
                screen.fill((abs(self.bg.r-off), abs(self.bg.g-off),abs(self.bg.b-off)), (self.rect.x, self.rect.y,self.rect.w+20, self.rect.h))
        if self.img: screen.blit(pg.image.load(self.img), self.pos)
        screen.blit(self.font.render(self.text, True, self.color), self.pos)



class Interface:
    def __init__(self):
        self.buttons:List[Button] = []
        self.pos = 0,0

    def clear(self):
        self.buttons = []

    def set_ui(self, buttons: list):
        self.buttons = buttons

    def draw(self, screen: pg.Surface):
        for b in self.buttons:
            b.render(screen, pg.Rect.collidepoint(b.rect, self.pos))

    def update_buttons(self, event):
        if event.type == pg.MOUSEBUTTONDOWN and event.button == pg.BUTTON_LEFT:
            for b in self.buttons:
                if pg.Rect.collidepoint(b.rect, event.pos):
                    if b.args:
                        b.func(b.args)
                    else:
                        b.func()
        elif event.type == pg.MOUSEMOTION: self.pos = event.pos


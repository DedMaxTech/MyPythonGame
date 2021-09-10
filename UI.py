from typing import Union
import pygame as pg


class Button:
    def __init__(self, pos, color, text, font: Union[int, pg.font.Font],callback_f=None, bg=None, size=None, args:tuple=None):
        self.pos = self.x, self.y = pos
        self.color = color
        self.font:pg.font.Font = font if type(font) == pg.font.Font else pg.font.SysFont('Arial', font)
        self.size = self.font.size(text) if size is None else size
        self.bg = bg; self.text = text
        self.func = callback_f; self.args=args
        self.rect = pg.Rect(self.x,self.y, self.size[0], self.size[1])
        if callback_f is None: callback_f=self.nothing()

    def nothing(self):pass
    def render(self):
        return self.font.render(self.text, True, self.color, self.bg)

class Interface:
    def __init__(self):
        self.buttons = []

    def clear(self):
        self.buttons = []

    def set_ui(self, buttons:list):
        self.buttons = buttons
    
    def draw(self, screen:pg.Surface):
        for b in self.buttons:
            screen.blit(b.render(), b.pos)

    def update_buttons(self, event):
        if event.button == pg.BUTTON_LEFT:
            print('click')
            for b in self.buttons:
                if pg.Rect.collidepoint(b.rect, event.pos):
                    if b.args: b.func(*b.args) 
                    else: b.func()
    

from typing import Union, List
import pygame as pg


class Button:
    def __init__(self, pos, color, text, font: Union[int, pg.font.Font], callback_f=None, bg=None, img=None, size=None,
                 args: tuple = None):
        self.pos = self.x, self.y = pos
        self.color = color
        self.font: pg.font.Font = font if type(font) == pg.font.Font else pg.font.SysFont('Arial', font)
        self.size = self.font.size(text) if size is None else size
        self.bg = bg;
        self.img = img
        self.text = text
        self.func = callback_f if callback_f is not None else self.nothing
        self.args = args
        self.rect = pg.Rect(self.x, self.y, self.size[0], self.size[1])

    def nothing(self): pass

    def render(self, screen:pg.Surface):
        if self.bg: screen.fill(self.bg, self.rect)
        if self.img: screen.blit(pg.image.load(self.img), self.pos)
        screen.blit(self.font.render(self.text, True, self.color), self.pos)



class Interface:
    def __init__(self):
        self.buttons:List[Button] = []

    def clear(self):
        self.buttons = []

    def set_ui(self, buttons: list):
        self.buttons = buttons

    def draw(self, screen: pg.Surface):
        for b in self.buttons:
            b.render(screen)

    def update_buttons(self, event):
        if event.button == pg.BUTTON_LEFT:

            for b in self.buttons:
                if pg.Rect.collidepoint(b.rect, event.pos):
                    print('click')
                    if b.args:
                        b.func(b.args)
                    else:
                        b.func()


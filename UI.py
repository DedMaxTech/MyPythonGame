import pygame as pg


class Button:
    def __init__(self, pos, color, text, callback_f, font: [int, pg.font.Font], size=None):
        self.x, self.y = pos
        self.font = font if type(font) == pg.font.Font else pg.font.SysFont('Arial', font)
        # if size is None:

class Interface:
    def __init__(self):
        pass

    def main_menu(self):
        pass


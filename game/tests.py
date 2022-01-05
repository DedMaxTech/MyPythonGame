# # import test2
# # [print(repr(k),' - ',type(v)) for k,v in test2.__dict__.items()]
# # print(issubclass(test2.C,test2.A))
# # print()

# import pygame as pg
# from pygame import image

# def rotate(surface, angle, pivot, offset):
#     """Rotate the surface around the pivot point.

#     Args:
#         surface (pygame.Surface): The surface that is to be rotated.
#         angle (float): Rotate by this angle.
#         pivot (tuple, list, pygame.math.Vector2): The pivot point.
#         offset (pygame.math.Vector2): This vector is added to the pivot.
#     """
#     rotated_image = pg.transform.rotozoom(surface, -angle, 1)  # Rotate the image.
#     rotated_offset = offset.rotate(angle)  # Rotate the offset vector.
#     # Add the offset vector to the center/pivot point to shift the rect.
#     rect = rotated_image.get_rect(center=pivot+rotated_offset)
#     return rotated_image, rect  # Return the rotated image and shifted rect.


# pg.init()
# screen = pg.display.set_mode((640, 480))
# clock = pg.time.Clock()
# BG_COLOR = pg.Color('gray12')
# # The original image will never be modified.
# IMAGE = pg.Surface((140, 60), pg.SRCALPHA)
# pg.draw.polygon(IMAGE, pg.Color('dodgerblue3'), ((0, 0), (140, 30), (0, 60)))
# # IMAGE = pg.image.load('game/content/player2/player.png')
# # Store the original center position of the surface.
# pivot = [200, 250]
# # This offset vector will be added to the pivot point, so the
# # resulting rect will be blitted at 'rect.topleft + offset'.
# offset = pg.math.Vector2(-70,0)
# print((5,5)-offset.xy)
# angle = 0

# running = True
# while running:
#     angle+=1
#     for event in pg.event.get():
#         if event.type == pg.QUIT:
#             running = False

#     keys = pg.key.get_pressed()
#     if keys[pg.K_d] or keys[pg.K_RIGHT]:
#         angle += 1
#     elif keys[pg.K_a] or keys[pg.K_LEFT]:
#         angle -= 1
#     if keys[pg.K_f]:
#         pivot[0] += 2

#     # Rotated version of the image and the shifted rect.
#     rotated_image, rect = rotate(IMAGE, angle, pivot, offset)

#     # Drawing.
#     screen.fill(BG_COLOR)
#     screen.blit(rotated_image, rect)  # Blit the rotated image.
#     pg.draw.circle(screen, (30, 250, 70), pivot, 3)  # Pivot point.
#     pg.draw.rect(screen, (30, 250, 70), rect, 1)  # The rect.
#     pg.display.set_caption('Angle: {}'.format(angle))
#     pg.display.flip()
#     clock.tick(30)

# pg.quit()

import time, math
import threading, pickle
from typing import Tuple, Union
import pygame as pg


a = Vec(-1,1)
print(a.angle())
# print(a.x)
# print(a.length())
# print(math.sqrt(a.x*a.x+a.y*a.y))
# print(a.x/a.length())
# b = math.acos(a.x/a.length())
# print(b)
# print(math.degrees(b))
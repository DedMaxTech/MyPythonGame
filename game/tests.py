import pygame as pg
import time
import zlib

screen = pg.display.set_mode((854,480),pg.SCALED)

for _ in range(10):
    print('||||||||||||||||||||||||||||||||||||\n||||||||||||||||||||||||||||||||||||')
    for cl in range(10):
        print('уровень сжатия:', cl)
        img = pg.transform.scale(pg.image.load('game/content/bg2.png'),(854,480))
        print(img.get_size())

        t=time.time()
        a = pg.image.tostring(img,'RGB')
        print('img to str',(time.time()-t)*1000,'ms')
        l = len(a)
        print('размер до сжатия',l)

        t=time.time()
        a = zlib.compress(a,cl)
        print('compress',(time.time()-t)*1000,'ms')
        print('размер после', len(a), ', меньше в', l/len(a),'раз')

        t=time.time()
        a = zlib.decompress(a)
        print('decompress',(time.time()-t)*1000,'ms')

        t=time.time()
        img = pg.image.fromstring(a,screen.get_size(),'RGB')
        print('img from str',(time.time()-t)*1000,'ms')
        print('------------------------------')
        screen.blit(img,(0,0))
        pg.display.flip()
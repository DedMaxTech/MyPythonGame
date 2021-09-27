import pygame as pg
pg.init()
cl = pg.time.Clock()
screen = pg.display.set_mode((1280, 720))
r = pg.Rect(0,0,50,50)
p1 = pg.Rect(0,300,30,200)
p2 = pg.Rect(1250,300,30,200)
x,y = 10,10
font = pg.font.SysFont('Arial', 30)
score1 = 0
score2 = 0
plaing = True
while True:
    for e in pg.event.get():
        if e.type == pg.QUIT: exit()
    keys = pg.key.get_pressed()
    if plaing:
        if r.x < 0 or r.right > 1280: plaing = False
        if r.y < 0 or r.bottom > 720: y = -y


        if keys[pg.K_w] and p1.y > 0:
            p1.y -= 10
        if keys[pg.K_s] and p1.bottom < 720:
            p1.y += 10
        if keys[pg.K_UP] and p2.y > 0:
            p2.y -= 10
        if keys[pg.K_DOWN] and p2.bottom < 720:
            p2.y += 10
        r.x += x;
        r.y += y
        if p1.colliderect(r) or p2.colliderect(r):
            x = -x
            if p1.colliderect(r): score1 += 1
            if p2.colliderect(r): score2 += 1
        screen.fill('white')
        screen.fill('red', r)
        screen.fill('green', p1)
        screen.fill('green', p2)
        screen.blit(font.render(f'{score1}:{score2}', True, 'black'), (600, 0))
    else:
        screen.fill('black')
        screen.blit(font.render(f'GAME OVER', True, 'white'), (530, 300))
        screen.blit(font.render(f'{score1}:{score2}', True, 'white'), (600, 350))
        if keys[pg.K_RETURN]:
            r = pg.Rect(0, 0, 50, 50)
            x, y = 10, 10
            score1 = score2 = 0
            p1.y = p2.y = 250
            plaing = True
    pg.display.update()
    cl.tick(60)

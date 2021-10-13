x1,y1,x2,y2,x3,y3 = map(int, input('x1,y1,x2,y2,x3,y3').split(' '))

print('Случай с ладьями')
if x1 == x3 or y1 == y3:
    if x2 == x3 or y2 == y3:print('может но будет срублена')
    else: print('может')
else: print('не может')

print('Случай с королём и ферзём')
if abs(x1-x3) <=1 and abs(y1-y3) <=1:
    if x2 == x3 or y2 == y3 or x2-x3 == y2-y3:print('может но будет срублена')
    else: print('может')
else: print('не может')
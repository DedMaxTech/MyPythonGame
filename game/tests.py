def remap(val, in_boubds, out_bounds=(0,1)):
    return (val - in_boubds[0]) * (out_bounds[1] - out_bounds[0]) / (in_boubds[1] - in_boubds[0]) + out_bounds[0]
print(remap(0.2, (-1,0)))
def limit(val, min=None, max=None):
    if min is not None and min>val:return min
    elif max is not None and val>max: return max
    else:return val

print(limit(3, max=2))
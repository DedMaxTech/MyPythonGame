def count(self, a,b):
    return a+b

A = object
A.count = count
a = A()
print(a.count())
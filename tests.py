class A(object):
    def __init__(self):
        pass
    def stop(self):
        del self
    def dele

a = A()
a.stop()
print(a)
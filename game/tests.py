class Btn:
    def __init__(self) -> None:
        self.timer=0
    def update(self, delta):
        if self.timer>0: self.timer-=delta
        
    def draw(self):
        if self.timer>0:
            pass
        else:
            pass
    
    def click(self):
        self.timer=1000
    
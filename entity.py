import time
from helper import distance

class Entity:
    """
    """
    def __init__(self, x, y, char):
        self.x = x
        self.y = y
        self.char = char
        self.walkable = True

class Player(Entity):
    def __init__(self, x, y):
        super(Player, self).__init__(x, y, "@")
        self.walkable = True
        self.light_range = 10

class Enemy(Entity):
    def __init__(self, x, y, char="?"):
        super(Enemy, self).__init__(x, y, char)
        self.move_interval = 1
        self.last_move_time = time.time()
    
    def next_move(self, target_x, target_y):
        next_x = self.x
        next_y = self.y
        if(target_x > self.x):
            next_x += 1
        elif(target_x < self.x):
            next_x -= 1
        if(target_y > self.y):
            next_y += 1
        elif(target_y < self.y):
            next_y -= 1
        return next_x, next_y
    
class SneakyEnemy(Enemy):
    def __init__(self, x, y, distance_thresh=5):
        super(SneakyEnemy, self).__init__(x, y, "#")
        self.distance_thresh = distance_thresh
        self.move_interval = 0.7
    
    def next_move(self, target_x, target_y):
        next_x = self.x
        next_y = self.y
        if(distance([target_x, target_y], [self.x, self.y]) < self.distance_thresh):
            self.char = "0"
            if(target_x > self.x):
                next_x += 1
            elif(target_x < self.x):
                next_x -= 1
            if(target_y > self.y):
                next_y += 1
            elif(target_y < self.y):
                next_y -= 1
        else:
            self.char = "#"
        return next_x, next_y

class LibrarianEnemy(Enemy):
    def __init__(self, x, y):
        super(LibrarianEnemy, self).__init__(x, y, " ")
        self.move_interval = 2
    
    # This is messy and should be fixed, 
    def next_move(self, target_x, target_y, area):
        move_list = area.best_path_between((self.x, self.y), (target_x, target_y))
        if len(move_list) == 0:
            return self.x, self.y
        return move_list[1]
import os
import random
import math
import time

class Roguelike:
    def __init__(self):
        self.WIDTH = 40
        self.HEIGHT = 20
        self.FOV_RADIUS = 5
        
        self.EMPTY = ' '
        self.WALL = '#'
        self.FLOOR = '.'
        self.PLAYER = '@'
        
        self.map = []
        self.visible = []
        self.explored = []
        self.playerX = 1
        self.playerY = 1
        self.gameRunning = True
        
        self.initialize_arrays()
        self.generate_map()
        self.update_fov()
    
    def initialize_arrays(self):
        self.map = [[self.EMPTY for _ in range(self.WIDTH)] for _ in range(self.HEIGHT)]
        self.visible = [[False for _ in range(self.WIDTH)] for _ in range(self.HEIGHT)]
        self.explored = [[False for _ in range(self.WIDTH)] for _ in range(self.HEIGHT)]
    
    def cast_ray(self, x1, y1, x2, y2):
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy
        
        x, y = x1, y1
        
        while True:
            if 0 <= x < self.WIDTH and 0 <= y < self.HEIGHT:
                self.visible[y][x] = True
                self.explored[y][x] = True
                
                if self.map[y][x] == self.WALL:
                    break
            
            if x == x2 and y == y2:
                break
            
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy
    
    def update_fov(self):
        for y in range(self.HEIGHT):
            for x in range(self.WIDTH):
                self.visible[y][x] = False
        
        self.visible[self.playerY][self.playerX] = True
        self.explored[self.playerY][self.playerX] = True
        
        for angle in range(0, 360, 5):
            rad = angle * math.pi / 180.0
            endX = self.playerX + int(self.FOV_RADIUS * math.cos(rad))
            endY = self.playerY + int(self.FOV_RADIUS * math.sin(rad))
            self.cast_ray(self.playerX, self.playerY, endX, endY)
    
    def generate_map(self):
        for y in range(self.HEIGHT):
            for x in range(self.WIDTH):
                if x == 0 or y == 0 or x == self.WIDTH-1 or y == self.HEIGHT-1:
                    self.map[y][x] = self.WALL
                elif random.randint(0, 99) < 30:
                    self.map[y][x] = self.WALL
                else:
                    self.map[y][x] = self.FLOOR
        
        self.map[self.playerY][self.playerX] = self.PLAYER
        self.clear_area_around_player()
    
    def clear_area_around_player(self):
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                newY = self.playerY + dy
                newX = self.playerX + dx
                if 0 <= newY < self.HEIGHT and 0 <= newX < self.WIDTH:
                    self.map[newY][newX] = self.FLOOR
        self.map[self.playerY][self.playerX] = self.PLAYER
    
    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def render(self):
        self.clear_screen()
        
        print("Управление: WASD - движение, Q - выход")
        print("Символы: @ - вы, # - стены")
        
        for y in range(self.HEIGHT):
            for x in range(self.WIDTH):
                if self.visible[y][x]:
                    print(self.map[y][x], end='')
                elif self.explored[y][x]:
                    if self.map[y][x] == self.WALL:
                        print('#', end='')
                    else:
                        print('.', end='')
                else:
                    print(' ', end='')
            print()
    
    def is_valid_move(self, x, y):
        return 0 <= x < self.WIDTH and 0 <= y < self.HEIGHT and self.map[y][x] != self.WALL
    
    def move_player(self, dx, dy):
        newX = self.playerX + dx
        newY = self.playerY + dy
        
        if self.is_valid_move(newX, newY):
            self.map[self.playerY][self.playerX] = self.FLOOR
            self.playerX = newX
            self.playerY = newY
            self.map[self.playerY][self.playerX] = self.PLAYER
            self.update_fov()
    
    def getch(self):
        if os.name == 'nt':
            import msvcrt
            return msvcrt.getch().decode('utf-8')
        else:
            import sys
            import tty
            import termios
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(sys.stdin.fileno())
                ch = sys.stdin.read(1)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            return ch
    
    def process_input(self):
        try:
            input_char = self.getch().lower()
            
            if input_char == 'w':
                self.move_player(0, -1)
            elif input_char == 's':
                self.move_player(0, 1)
            elif input_char == 'a':
                self.move_player(-1, 0)
            elif input_char == 'd':
                self.move_player(1, 0)
            elif input_char == 'q':
                self.gameRunning = False
                return True
        except:
            pass
        return False
    
    def run(self):
        while self.gameRunning:
            self.render()
            if self.process_input():
                break
            time.sleep(0.05)
        print("Спасибо за игру!")

if __name__ == "__main__":
    game = Roguelike()
    game.run()

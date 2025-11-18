import os
import random
import math
import msvcrt

class RoguelikeWithWalls:
    def __init__(self, width=40, height=20):  # ИСПРАВЛЕНО: должно быть __init__
        self.width = width
        self.height = height
        self.player_x = 5
        self.player_y = 10
        self.torch_radius = 5
        
        self.wall = '#'
        self.floor = '.'
        self.player = '@'
        self.dark = ' '
        self.explored = set()
        
        self.generate_map()
    
    def generate_map(self):
        """Генерация более сложной карты с комнатами"""
        self.map = [['#' for _ in range(self.width)] for _ in range(self.height)]
        
        # Создаем несколько комнат
        rooms = []
        for _ in range(8):
            room_width = random.randint(4, 8)
            room_height = random.randint(4, 6)
            room_x = random.randint(1, self.width - room_width - 1)
            room_y = random.randint(1, self.height - room_height - 1)
            
            # Рисуем комнату
            for y in range(room_y, room_y + room_height):
                for x in range(room_x, room_x + room_width):
                    if 0 <= x < self.width and 0 <= y < self.height:
                        self.map[y][x] = self.floor
            
            rooms.append((room_x + room_width//2, room_y + room_height//2))
        
        # Соединяем комнаты коридорами
        for i in range(len(rooms) - 1):
            x1, y1 = rooms[i]
            x2, y2 = rooms[i + 1]
            
            # Горизонтальный коридор
            for x in range(min(x1, x2), max(x1, x2) + 1):
                if 0 <= x < self.width and 0 <= y1 < self.height:
                    self.map[y1][x] = self.floor
            
            # Вертикальный коридор
            for y in range(min(y1, y2), max(y1, y2) + 1):
                if 0 <= x2 < self.width and 0 <= y < self.height:
                    self.map[y][x2] = self.floor
        
        # Устанавливаем игрока в первую комнату
        self.player_x, self.player_y = rooms[0]
    
    def has_line_of_sight(self, x1, y1, x2, y2):
        """Проверяет, есть ли прямая видимость между двумя точками"""
        dx = x2 - x1
        dy = y2 - y1
        distance = max(abs(dx), abs(dy))
        
        if distance == 0:
            return True
        
        # Используем алгоритм Брезенхэма для проверки всех точек на пути
        for i in range(distance + 1):
            t = i / distance
            x = int(x1 + dx * t)
            y = int(y1 + dy * t)
            
            # Если на пути встретилась стена - нет видимости
            if (0 <= x < self.width and 0 <= y < self.height and 
                self.map[y][x] == self.wall):
                return False
        
        return True
    
    def get_visible_cells(self):
        """Возвращает множество видимых клеток с учетом стен"""
        visible = set()
        
        # Проверяем все клетки в квадрате вокруг игрока
        for y in range(max(0, self.player_y - self.torch_radius), 
                      min(self.height, self.player_y + self.torch_radius + 1)):
            for x in range(max(0, self.player_x - self.torch_radius), 
                          min(self.width, self.player_x + self.torch_radius + 1)):
                
                # Проверяем расстояние
                distance = math.sqrt((x - self.player_x)**2 + (y - self.player_y)**2)
                if distance <= self.torch_radius:
                    # Проверяем видимость
                    if self.has_line_of_sight(self.player_x, self.player_y, x, y):
                        visible.add((x, y))
        
        return visible
    
    def draw(self):
        os.system('cls')
        print("=== ROGUELIKE WITH TORCH ===")
        print("WASD - move, +/- - torch radius, Q - quit")
        print(f"Torch radius: {self.torch_radius}")
        print("=" * 40)
        
        visible_cells = self.get_visible_cells()  # ИСПРАВЛЕНО: добавлена эта строка
        
        for y in range(self.height):
            line = ""
            for x in range(self.width):
                if x == self.player_x and y == self.player_y:
                    line += self.player
                elif (x, y) in visible_cells:
                    self.explored.add((x, y))
                    line += self.map[y][x]
                elif (x, y) in self.explored:
                    # Показываем исследованные области
                    if self.map[y][x] == self.wall:
                        line += '+'  # ИСПРАВЛЕНО: простой символ
                    else:
                        line += '-'  # ИСПРАВЛЕНО: простой символ
                else:
                    line += self.dark  # Неисследованная область
            print(line)
    
    def move(self, dx, dy):
        new_x = self.player_x + dx
        new_y = self.player_y + dy
        
        if (0 <= new_x < self.width and 0 <= new_y < self.height and 
            self.map[new_y][new_x] == self.floor):
            self.player_x, self.player_y = new_x, new_y
            return True
        return False
    
    def run(self):
        print("Loading game...")
        while True:
            self.draw()
            
            key = msvcrt.getch().decode('latin-1').lower()  # ИСПРАВЛЕНО: кодировка
            
            if key == 'q':
                print("Thanks for playing!")
                break
            elif key == 'w':
                self.move(0, -1)
            elif key == 's':
                self.move(0, 1)
            elif key == 'a':
                self.move(-1, 0)
            elif key == 'd':
                self.move(1, 0)
            elif key == '+' or key == '=':
                self.torch_radius = min(12, self.torch_radius + 1)
            elif key == '-' or key == '_':
                self.torch_radius = max(3, self.torch_radius - 1)

if __name__ == "__main__":
    game = RoguelikeWithWalls()
    game.run()

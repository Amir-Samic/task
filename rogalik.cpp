import os
import random
import msvcrt


class SimpleRoguelike:
    def __init__(self, width=30, height=15):
        self.width = width
        self.height = height
        self.player_x = 5
        self.player_y = 5
        self.torch_radius = 4

        self.wall = '#'
        self.floor = '.'
        self.player = '@'
        self.dark = ' '

        self.generate_map()

    def generate_map(self):
        self.map = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                if random.random() > 0.3 or (x == self.player_x and y == self.player_y):
                    row.append(self.floor)
                else:
                    row.append(self.wall)
            self.map.append(row)

    def is_visible(self, x, y):
        return ((x - self.player_x) ** 2 + (y - self.player_y) ** 2) <= self.torch_radius ** 2

    def draw(self):
        os.system('cls')
        print("Рогалик с фонариком - WASD движение, Q выход")
        print(f"Фонарик: радиус {self.torch_radius}\n")

        for y in range(self.height):
            line = ""
            for x in range(self.width):
                if x == self.player_x and y == self.player_y:
                    line += self.player
                elif self.is_visible(x, y):
                    line += self.map[y][x]
                else:
                    line += self.dark
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
        while True:
            self.draw()

            key = msvcrt.getch().decode('utf-8').lower()

            if key == 'q':
                break
            elif key == 'w':
                self.move(0, -1)
            elif key == 's':
                self.move(0, 1)
            elif key == 'a':
                self.move(-1, 0)
            elif key == 'd':
                self.move(1, 0)
            elif key == '+':
                self.torch_radius = min(8, self.torch_radius + 1)
            elif key == '-':
                self.torch_radius = max(2, self.torch_radius - 1)


if __name__ == "__main__":
    game = SimpleRoguelike()
    game.run()

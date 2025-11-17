#include <iostream>
#include <vector>
#include <cstdlib>
#include <ctime>
#include <conio.h>  // для _getch() на Windows
// #include <unistd.h>  // для getch() на Linux

#ifdef _WIN32
#include <windows.h>
#endif

using namespace std;

class Roguelike {
private:
    const int WIDTH = 40;
    const int HEIGHT = 20;
    const int FOV_RADIUS = 5;  // радиус обзора фонарика
    
    vector<vector<char>> map;
    int playerX, playerY;
    bool gameRunning;
    
    enum Tile {
        EMPTY = ' ',
        WALL = '#',
        FLOOR = '.',
        PLAYER = '@',
        ENEMY = 'E',
        TREASURE = 'T'
    };
    
public:
    Roguelike() {
        srand(time(0));
        map.resize(HEIGHT, vector<char>(WIDTH, EMPTY));
        playerX = 1;
        playerY = 1;
        gameRunning = true;
        generateMap();
    }
    
    void generateMap() {
        // Создаем случайные комнаты и коридоры
        for (int y = 0; y < HEIGHT; y++) {
            for (int x = 0; x < WIDTH; x++) {
                if (x == 0  y == 0  x == WIDTH-1 || y == HEIGHT-1) {
                    map[y][x] = WALL;
                } else if (rand() % 100 < 30) {  // 30% chance для стен
                    map[y][x] = WALL;
                } else {
                    map[y][x] = FLOOR;
                }
            }
        }
        
        // Добавляем игрока
        map[playerY][playerX] = PLAYER;
        
        // Добавляем врагов
        for (int i = 0; i < 5; i++) {
            int x, y;
            do {
                x = rand() % (WIDTH-2) + 1;
                y = rand() % (HEIGHT-2) + 1;
            } while (map[y][x] != FLOOR);
            map[y][x] = ENEMY;
        }
        
        // Добавляем сокровища
        for (int i = 0; i < 3; i++) {
            int x, y;
            do {
                x = rand() % (WIDTH-2) + 1;
                y = rand() % (HEIGHT-2) + 1;
            } while (map[y][x] != FLOOR);
            map[y][x] = TREASURE;
        }
        
        // Гарантируем проходимость вокруг игрока
        for (int dy = -1; dy <= 1; dy++) {
            for (int dx = -1; dx <= 1; dx++) {
                if (playerY+dy >= 0 && playerY+dy < HEIGHT && 
                    playerX+dx >= 0 && playerX+dx < WIDTH) {
                    map[playerY+dy][playerX+dx] = FLOOR;
                }
            }
        }
        map[playerY][playerX] = PLAYER;
    }
    
    void clearScreen() {
        #ifdef _WIN32
        system("cls");
        #else
        system("clear");
        #endif
    }
    
    bool isInFOV(int x, int y) {
        // Простая проверка расстояния для фонарика
        int dx = x - playerX;
        int dy = y - playerY;
        return (dx*dx + dy*dy) <= FOV_RADIUS * FOV_RADIUS;
    }
    
    void render() {
        clearScreen();
        
        cout << "=== КОНСОЛЬНЫЙ РОГАЛИК С ФОНАРИКОМ ===" << endl;
        cout << "Управление: WASD - движение, Q - выход" << endl;
        cout << "Фонарик освещает область вокруг игрока" << endl;
        cout << "Символы: @ - вы, # - стены, E - враги, T - сокровища" << endl;
        cout << string(WIDTH + 2, '-') << endl;
        
        for (int y = 0; y < HEIGHT; y++) {
            cout << '|';
            for (int x = 0; x < WIDTH; x++) {
                if (isInFOV(x, y) || map[y][x] == PLAYER) {
                    cout << map[y][x];
                } else {
                    cout << ' ';  // неосвещенная область
                }
            }
            cout << '|' << endl;
        }
        
        cout << string(WIDTH + 2, '-') << endl;
    }
    
    bool isValidMove(int x, int y) {
        return x >= 0 && x < WIDTH && y >= 0 && y < HEIGHT && map[y][x] != WALL;
    }
    
    void movePlayer(int dx, int dy) {
        int newX = playerX + dx;
        int newY = playerY + dy;if (isValidMove(newX, newY)) {
            // Проверяем, что на новой клетке
            if (map[newY][newX] == ENEMY) {
                cout << "Вы встретили врага! Игра окончена." << endl;
                gameRunning = false;
                return;
            } else if (map[newY][newX] == TREASURE) {
                cout << "Вы нашли сокровище! Поздравляем!" << endl;
                gameRunning = false;
                return;
            }
            
            // Перемещаем игрока
            map[playerY][playerX] = FLOOR;
            playerX = newX;
            playerY = newY;
            map[playerY][playerX] = PLAYER;
        }
    }
    
    void processInput() {
        char input = _getch();  // на Windows
        // char input = getch();  // на Linux
        
        switch (tolower(input)) {
            case 'w': movePlayer(0, -1); break;
            case 's': movePlayer(0, 1); break;
            case 'a': movePlayer(-1, 0); break;
            case 'd': movePlayer(1, 0); break;
            case 'q': gameRunning = false; break;
        }
    }
    
    void run() {
        while (gameRunning) {
            render();
            processInput();
            
            // Небольшая задержка для плавности
            #ifdef _WIN32
            Sleep(50);
            #else
            usleep(50000);
            #endif
        }
        
        cout << "Спасибо за игру!" << endl;
    }
};

int main() {
    // Настройка кодировки для Windows
    #ifdef _WIN32
    SetConsoleOutputCP(65001);
    #endif
    
    Roguelike game;
    game.run();
    return 0;
}

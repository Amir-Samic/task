import requests
from bs4 import BeautifulSoup
import csv
import time


def scrape_acmp_tasks():
    base_url = "https://acmp.ru/index.asp"
    tasks = []

    # Параметры запроса
    params = {
        'main': 'tasks',
        'str': ' ',
        'page': 1,
        'id_type': 0
    }

    # Создаем CSV файлы
    with open('tasks.csv', 'w', newline='', encoding='utf-8') as tasks_file, \
            open('categories.csv', 'w', newline='', encoding='utf-8') as cats_file, \
            open('task_categories.csv', 'w', newline='', encoding='utf-8') as task_cats_file:

        # Tasks table
        tasks_writer = csv.writer(tasks_file)
        tasks_writer.writerow(['task_id', 'name', 'complexity', 'solved_count', 'description'])

        # Categories table
        cats_writer = csv.writer(cats_file)
        cats_writer.writerow(['category_id', 'category_name'])

        # Task-Categories relationship table
        task_cats_writer = csv.writer(task_cats_file)
        task_cats_writer.writerow(['task_id', 'category_id'])

        categories_map = {}
        category_counter = 1

        # Обрабатываем несколько страниц (можно увеличить)
        for page in range(1, 4):  # первые 3 страницы
            print(f"Обрабатывается страница {page}...")

            params['page'] = page
            response = requests.get(base_url, params=params)
            response.encoding = 'windows-1251'
            soup = BeautifulSoup(response.text, 'html.parser')

            # Находим таблицу с задачами
            table = soup.find('table', {'class': None})  # основная таблица
            if not table:
                continue

            rows = table.find_all('tr')[1:]  # пропускаем заголовок

            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 6:
                    # Извлекаем данные из строки таблицы
                    task_id = cols[0].text.strip()

                    # Проверяем, что это номер задачи (число)
                    if not task_id.isdigit():
                        continue

                    name = cols[1].text.strip()
                    description = cols[2].text.strip()
                    complexity = cols[4].text.strip()
                    solved_count = cols[5].text.strip()

                    # Извлекаем категории из описания или названия
                    categories = extract_categories(name, description)

                    # Записываем задачу
                    tasks_writer.writerow([task_id, name, complexity, solved_count, description])

                    # Обрабатываем категории
                    for category in categories:
                        if category not in categories_map:
                            categories_map[category] = category_counter
                            cats_writer.writerow([category_counter, category])
                            category_counter += 1

                        # Связываем задачу с категорией
                        task_cats_writer.writerow([task_id, categories_map[category]])

            # Пауза между запросами
            time.sleep(1)

    print("Данные успешно сохранены в CSV файлы!")
    print(f"Обработано категорий: {len(categories_map)}")


def extract_categories(name, description):
    """Извлекает категории из названия и описания задачи"""
    categories = []
    text = (name + " " + description).lower()

    # Ключевые слова для категорий
    category_keywords = {
        'математика': ['сумма', 'произведение', 'число', 'последовательность', 'делитель'],
        'строки': ['строка', 'символ', 'слово', 'текст'],
        'графы': ['граф', 'вершина', 'ребро', 'путь', 'связность'],
        'динамическое программирование': ['динамическое', 'динамика', 'dp'],
        'перебор': ['перебор', 'комбинация', 'вариант'],
        'геометрия': ['точка', 'прямая', 'координата', 'расстояние'],
        'сортировка': ['сортировка', 'упорядочить', 'минимальный', 'максимальный']
    }

    for category, keywords in category_keywords.items():
        if any(keyword in text for keyword in keywords):
            categories.append(category)

    # Если категории не найдены, добавляем "общая"
    if not categories:
        categories.append('общая')

    return categories


# Запуск скрапера
if __name__ == "__main__":
    scrape_acmp_tasks()

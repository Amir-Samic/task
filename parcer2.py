import requests
from bs4 import BeautifulSoup
import csv
import yaml
import time
import re

def scrape_acmp_tasks():
    base_url = "https://acmp.ru/index.asp"
    task_base_url = "https://acmp.ru/index.asp?main=task&id_task="
    
    params = {
        'main': 'tasks',
        'str': ' ',
        'page': 1,
        'id_type': 0
    }

    all_tasks_data = []
    categories_map = {}
    category_counter = 1
    task_counter = 0
    max_tasks = 10

    with open('tasks.csv', 'w', newline='', encoding='utf-8') as tasks_file, \
            open('categories.csv', 'w', newline='', encoding='utf-8') as cats_file, \
            open('task_categories.csv', 'w', newline='', encoding='utf-8') as task_cats_file, \
            open('task_conditions.csv', 'w', newline='', encoding='utf-8') as conditions_file, \
            open('full_tasks.yaml', 'w', encoding='utf-8') as yaml_file:

        tasks_writer = csv.writer(tasks_file)
        tasks_writer.writerow(['task_id', 'name', 'complexity', 'solved_count', 'description'])

        cats_writer = csv.writer(cats_file)
        cats_writer.writerow(['category_id', 'category_name'])

        task_cats_writer = csv.writer(task_cats_file)
        task_cats_writer.writerow(['task_id', 'category_id'])

        conditions_writer = csv.writer(conditions_file)
        conditions_writer.writerow(['task_id', 'условие_задачи', 'входные_данные', 'выходные_данные', 'примеры'])

        page = 1
        while task_counter < max_tasks:
            print(f"Обрабатывается страница {page}...")

            params['page'] = page
            try:
                response = requests.get(base_url, params=params, timeout=10)
                response.encoding = 'windows-1251'
                soup = BeautifulSoup(response.text, 'html.parser')
            except Exception as e:
                print(f"Ошибка при загрузке страницы {page}: {e}")
                break

            table = soup.find('table', {'class': None})
            if not table:
                print("Таблица с задачами не найдена")
                break

            rows = table.find_all('tr')[1:]

            for row in rows:
                if task_counter >= max_tasks:
                    break
                    
                cols = row.find_all('td')
                if len(cols) >= 6:
                    task_id = cols[0].text.strip()

                    if not task_id.isdigit():
                        continue

                    name = cols[1].text.strip()
                    description = cols[2].text.strip()
                    complexity = cols[4].text.strip()
                    solved_count = cols[5].text.strip()

                    print(f"Обрабатывается задача {task_counter + 1}/{max_tasks}: {task_id} - {name}")

                    condition_data = get_task_condition(task_id, task_base_url)
                    
                    categories = extract_categories(name, description, condition_data.get('условие_задачи', ''))

                    task_data = {
                        'id': task_id,
                        'название': name,
                        'сложность': complexity,
                        'решили': solved_count,
                        'описание': description,
                        'условие': condition_data.get('условие_задачи', ''),
                        'входные_данные': condition_data.get('входные_данные', ''),
                        'выходные_данные': condition_data.get('выходные_данные', ''),
                        'примеры': condition_data.get('примеры', ''),
                        'категории': categories
                    }
                    all_tasks_data.append(task_data)

                    tasks_writer.writerow([task_id, name, complexity, solved_count, description])

                    conditions_writer.writerow([
                        task_id,
                        condition_data.get('условие_задачи', 'Не удалось получить условие'),
                        condition_data.get('входные_данные', 'Не удалось получить входные данные'),
                        condition_data.get('выходные_данные', 'Не удалось получить выходные данные'),
                        condition_data.get('примеры', 'Не удалось получить примеры')
                    ])

                    for category in categories:
                        if category not in categories_map:
                            categories_map[category] = category_counter
                            cats_writer.writerow([category_counter, category])
                            category_counter += 1

                        task_cats_writer.writerow([task_id, categories_map[category]])

                    task_counter += 1
                    time.sleep(1)

            page += 1
            time.sleep(2)
            
            if not has_next_page(soup):
                print("Достигнута последняя страница")
                break

        save_to_yaml(all_tasks_data, categories_map, yaml_file)

    print("Данные успешно сохранены в CSV и YAML файлы!")
    print(f"Обработано задач: {task_counter}")
    print(f"Обработано категорий: {len(categories_map)}")

def save_to_yaml(tasks_data, categories_map, yaml_file):
    yaml_data = {
        'источник': 'https://acmp.ru',
        'время_сбора': time.strftime('%Y-%m-%d %H:%M:%S'),
        'всего_задач': len(tasks_data),
        'всего_категорий': len(categories_map),
        'категории': {v: k for k, v in categories_map.items()},
        'задачи': tasks_data
    }
    
    yaml.dump(yaml_data, yaml_file, allow_unicode=True, default_flow_style=False, indent=2, encoding='utf-8')

def has_next_page(soup):
    navigation = soup.find_all('a', href=True)
    for link in navigation:
        if 'page=' in link['href'] and 'Следующая' in link.text:
            return True
    return False

def get_task_condition(task_id, base_url):
    try:
        url = base_url + task_id
        print(f"  Загружаем условие задачи {task_id}...")
        
        response = requests.get(url, timeout=10)
        response.encoding = 'windows-1251'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        condition_data = {
            'условие_задачи': '',
            'входные_данные': '',
            'выходные_данные': '',
            'примеры': ''
        }
        
        main_content = soup.find('div', {'class': 'text'})
        if not main_content:
            main_content = soup.find('td', {'class': 'text'})
        if not main_content:
            main_content = soup.find('table', {'class': 'main'})
        
        if main_content:
            full_text = main_content.get_text(separator='\n', strip=True)
            condition_data = parse_condition_text(full_text)
            
            if not condition_data['условие_задачи']:
                condition_data['условие_задачи'] = full_text[:1500]
        
        if not condition_data['условие_задачи']:
            condition_data['условие_задачи'] = extract_alternative_condition(soup)
            
        print(f"  Условие получено: {len(condition_data['условие_задачи'])} символов")
        return condition_data
        
    except Exception as e:
        print(f"  Ошибка при получении условия задачи {task_id}: {e}")
        return {
            'условие_задачи': f'Ошибка загрузки: {str(e)}',
            'входные_данные': 'Ошибка загрузки',
            'выходные_данные': 'Ошибка загрузки', 
            'примеры': 'Ошибка загрузки'
        }

def parse_condition_text(text):
    data = {
        'условие_задачи': '',
        'входные_данные': '',
        'выходные_данные': '',
        'примеры': ''
    }
    
    lines = text.split('\n')
    
    current_section = 'условие_задачи'
    sections = {'условие_задачи': [], 'входные_данные': [], 'выходные_данные': [], 'примеры': []}
    
    input_keywords = ['входные данные', 'input', 'входной', 'input data']
    output_keywords = ['выходные данные', 'output', 'выходной', 'output data'] 
    example_keywords = ['пример', 'example', 'sample', 'тест']
    
    for line in lines:
        line_lower = line.lower().strip()
        
        if any(keyword in line_lower for keyword in input_keywords):
            current_section = 'входные_данные'
        elif any(keyword in line_lower for keyword in output_keywords):
            current_section = 'выходные_данные'
        elif any(keyword in line_lower for keyword in example_keywords):
            current_section = 'примеры'
        
        if line.strip():
            sections[current_section].append(line.strip())
    
    data['условие_задачи'] = '\n'.join(sections['условие_задачи'])[:2000]
    data['входные_данные'] = '\n'.join(sections['входные_данные'])[:1000]
    data['выходные_данные'] = '\n'.join(sections['выходные_данные'])[:1000] 
    data['примеры'] = '\n'.join(sections['примеры'])[:1500]
    
    return data

def extract_alternative_condition(soup):
    texts = []
    
    for tag in ['p', 'div', 'td', 'span']:
        elements = soup.find_all(tag)
        for elem in elements:
            text = elem.get_text(strip=True)
            if len(text) > 50:
                texts.append(text)
    
    return ' '.join(texts)[:2000]

def extract_categories(name, description, condition_text):
    categories = []
    text = (name + " " + description + " " + condition_text).lower()

    category_keywords = {
        'математика': ['сумма', 'произведение', 'число', 'последовательность', 'делитель', 'простые числа', 
                      'арифметика', 'уравнение', 'формула', 'модуль', 'остаток', 'четность'],
        'строки': ['строка', 'символ', 'слово', 'текст', 'подстрока', 'палиндром', 'замена', 'поиск'],
        'графы': ['граф', 'вершина', 'ребро', 'путь', 'связность', 'дерево', 'обход', 'компонента', 'цикл'],
        'динамическое программирование': ['динамическое', 'динамика', 'dp', 'рекуррент', 'мемоизация'],
        'перебор': ['перебор', 'комбинация', 'вариант', 'перестановка', 'сочетание', 'брутфорс'],
        'геометрия': ['точка', 'прямая', 'координата', 'расстояние', 'площадь', 'вектор', 'отрезок', 'треугольник'],
        'сортировка': ['сортировка', 'упорядочить', 'минимальный', 'максимальный', 'отсортировать', 'ранг'],
        'поиск': ['поиск', 'бинарный поиск', 'найти', 'поиск в ширину', 'поиск в глубину'],
        'структуры данных': ['массив', 'список', 'очередь', 'стек', 'дерево', 'хэш', 'множество', 'куча'],
        'алгоритмы': ['алгоритм', 'эффективный', 'оптимальный', 'сложность', 'время работы'],
        'рекурсия': ['рекурсия', 'рекурсивный', 'факториал', 'фибоначчи']
    }

    for category, keywords in category_keywords.items():
        if any(keyword in text for keyword in keywords):
            categories.append(category)

    if not categories:
        categories.append('общая')

    return list(set(categories))

def print_sample_tasks():
    try:
        with open('full_tasks.yaml', 'r', encoding='utf-8') as file:
            data = yaml.safe_load(file)
            
        print("\n" + "="*60)
        print("ПРИМЕРЫ ЗАДАЧ ИЗ YAML ФАЙЛА:")
        print("="*60)
        
        for i, task in enumerate(data['задачи'][:3]):
            print(f"\n--- Задача {i+1} ---")
            print(f"ID: {task['id']}")
            print(f"Название: {task['название']}")
            print(f"Сложность: {task['сложность']}")
            print(f"Решили: {task['решили']}")
            print(f"Описание: {task['описание']}")
            print(f"Условие: {task['условие'][:200]}...")
            print(f"Категории: {', '.join(task['категории'])}")
            print("-" * 40)
            
    except FileNotFoundError:
        print("YAML файл не найден")

if __name__ == "__main__":
    scrape_acmp_tasks()
    print_sample_tasks()

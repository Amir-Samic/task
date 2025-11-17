import requests
from bs4 import BeautifulSoup
import csv
import time
import re

def get_tasks_list():
    """Получает список задач с основной страницы"""
    url = "https://acmp.ru/index.asp?main=tasks"
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'windows-1251'
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        tasks = []
        
        table = soup.find('table', class_='main')
        if not table:
            print("Таблица с задачами не найдена")
            return tasks
            
        rows = table.find_all('tr')[1:]
        
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 5:
                task_id = cols[0].text.strip()
                if task_id and task_id.isdigit():
                    task = {
                        "id": task_id,
                        "name": cols[1].text.strip() if len(cols) > 1 else "",
                        "description": cols[2].text.strip() if len(cols) > 2 else "",
                        "solved_count": cols[3].text.strip() if len(cols) > 3 else "",
                        "complexity": cols[4].text.strip() if len(cols) > 4 else "",
                        "time": "Не найдено",
                        "memory": "Не найдено",
                        "condition": ""
                    }
                    tasks.append(task)
        
        return tasks
        
    except requests.RequestException as e:
        print(f"Ошибка при получении списка задач: {e}")
        return []

def get_task_details(task_id):
    """Получает детальную информацию о задаче"""
    task_url = f"https://acmp.ru/index.asp?main=task&id_task={task_id}"
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(task_url, headers=headers, timeout=10)
        response.encoding = 'windows-1251'
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        time_limit = "Не найдено"
        memory_limit = "Не найдено"
        condition = ""
        
        text = soup.get_text()
        
        # Поиск ограничений
        time_match = re.search(r'(\d+\.?\d*)\s*сек', text)
        memory_match = re.search(r'(\d+)\s*Мб', text)
        
        if time_match:
            time_limit = f"{time_match.group(1)} сек"
        if memory_match:
            memory_limit = f"{memory_match.group(1)} Мб"
        
        # Поиск условия
        main_content = soup.find('div', class_='main') or soup.find('table', class_='main')
        if main_content:
            paragraphs = main_content.find_all('p')
            for p in paragraphs:
                text = p.get_text().strip()
                if (len(text) > 50 and 
                    'сек' not in text and 
                    'Мб' not in text):
                    condition = text[:200] + "..." if len(text) > 200 else text
                    break
        
        return {
            "time": time_limit,
            "memory": memory_limit,
            "condition": condition
        }
        
    except requests.RequestException as e:
        print(f"Ошибка при получении задачи {task_id}: {e}")
        return {
            "time": "Ошибка",
            "memory": "Ошибка", 
            "condition": "Ошибка загрузки"
        }

def main():
    print("Парсинг задач с acmp.ru и сохранение в CSV...")
    
    tasks = get_tasks_list()
    
    if not tasks:
        print("Не удалось получить список задач")
        return
    
    print(f"Найдено {len(tasks)} задач. Получаем детальную информацию...")
# Открываем CSV файл для записи
    with open('tasks.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['id', 'name', 'description', 'solved_count', 'complexity', 'time', 'memory', 'condition']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        # Обрабатываем первые 10 задач для примера
        for i, task in enumerate(tasks[:10], 1):
            print(f"Обрабатываем задачу {i}/10 (ID: {task['id']})")
            
            details = get_task_details(task['id'])
            task.update(details)
            
            # Записываем задачу в CSV
            writer.writerow(task)
            
            time.sleep(1)
    
    print("Данные успешно сохранены в tasks.csv")

if name == "main":
    main()

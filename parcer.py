import requests
from bs4 import BeautifulSoup
import json
import time

url = "https://acmp.ru/index.asp?main=tasks&page=0"
response = requests.get(url)
response.encoding = 'windows-1251'
soup = BeautifulSoup(response.text, 'html.parser')

table = soup.find('table')
rows = table.find_all('tr')[1:]

tasks = []

for row in rows:
    cols = row.find_all('td')
    if len(cols) >= 7:
        first_col = cols[0].text.strip()
        if first_col and first_col.isdigit():
            task = {
                "id": cols[0].text.strip(),
                "complexity": cols[4].text.strip(),
                "name": cols[1].text.strip(),
                "description": cols[2].text.strip(),
            }
            tasks.append(task)

for task in tasks:
    task_url = f"https://acmp.ru/index.asp?main=task&id_task={task['id']}"
    response = requests.get(task_url)
    response.encoding = 'windows-1251'
    soup = BeautifulSoup(response.text, 'html.parser')

    text = soup.get_text()

    task['time'] = "Не найдено"
    task['memory'] = "Не найдено"

    for line in text.split('\n'):
        line = line.strip()
        if 'сек' in line and 'Мб' in line:
            parts = line.split('Память:')
            if len(parts) > 1:
                time_part = parts[0]
                memory_part = parts[1].split('Сложность:')[0]

                task['time'] = time_part.strip()
                task['memory'] = 'Память:' + memory_part.strip()
            break

    task['condition'] = ""
    for p in soup.find_all('p'):
        text = p.get_text().strip()
        if text and 'сек' not in text and 'Мб' not in text and len(text) > 50:
            task['condition'] = text[:200]
            break

    time.sleep(1)

with open('tasks.json', 'w', encoding='utf-8') as f:
    json.dump(tasks, f, ensure_ascii=False, indent=2)

print(f"Сохранено {len(tasks)} задач")

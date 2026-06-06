# Лабораторная работа №13
## Мультиагентные системы: разработка распределённых интеллектуальных агентов

Студент: Туманян Лина Врежовна
Группа: 220032-11
Вариант: 27 (Автоматизация тестирования ПО)
Уровень сложности: Средний

---

## Выполненные задания
- Задание 1 — Определение агентов и их ролей
- Задание 2 — Разработка прототипа агента на Go
- Задание 3 — Разработка оркестратора на Python
- Задание 4 — Настройка коммуникации через NATS
- Задание 5 — Логирование и мониторинг
- Задание 6 — Обработка ошибок и таймаутов
- Задание 7 — Запуск нескольких агентов одного типа
- Задание 8 — Создание API для запуска задач
- Задание 9 — Тестирование системы
- Задание 10 — Документирование архитектуры

---

## Стек
- Go 1.22 — агенты
- Python 3.11 — оркестратор, FastAPI
- NATS 2.10 — брокер сообщений
- Docker / Docker Compose — инфраструктура

---

## Структура проекта
```
lab13/
├── agents/
│   └── test-generator/
│       ├── main.go
│       ├── main_test.go
│       └── go.mod
├── orchestartor/
│   ├── orchestrator.py
│   ├── api.py
│   ├── requirements.txt
│   └── tests/
│       └── test_orchestrator.py
├── docs/
│   ├── agents.md
│   └── architecture.md
├── docker-compose.yml
├── .gitignore
├── .dockerignore
├── PROMPT_LOG.md
└── README.md
```

---

## Быстрый старт

```powershell
# 1. Поднять NATS
docker-compose up -d

# 2. Запустить агент
cd agents/test-generator
$env:INSTANCE_ID="1"; go run main.go

# 3. Установить зависимости оркестратора
cd orchestartor
pip install -r requirements.txt

# 4. Запустить API
python -m uvicorn api:app --reload --port 8000
```

---

## Задание 1 — Определение агентов и их ролей

Описание всех агентов системы находится в `docs/agents.md`.

| Агент | Роль |
|---|---|
| test-generator | Принимает описание модуля и генерирует тест-кейсы |
| test-runner | Запускает тесты и возвращает результаты |
| coverage-analyzer | Анализирует покрытие кода тестами |
| report-generator | Формирует итоговый отчёт по результатам |

---

## Задание 2 — Разработка прототипа агента на Go

Агент `test-generator` подписывается на топик `tasks.generate` в NATS,
принимает JSON-задачу, генерирует тест-кейсы и публикует результат в `tasks.completed`.

### Запуск
```powershell
cd agents/test-generator
go mod tidy
go run main.go
```

### Вывод
```
2026/05/22 00:15:21 [INFO] test-generator connected to NATS at nats://127.0.0.1:4222
2026/05/22 00:15:21 [INFO] test-generator listening on tasks.generate
```

---

## Задание 3 — Разработка оркестратора на Python

Оркестратор на asyncio и nats-py отправляет задачи агентам, ожидает результаты
и обрабатывает таймауты.

### Установка зависимостей
```powershell
cd orchestartor
pip install -r requirements.txt
```

### Файлы
- `orchestartor/orchestrator.py` — класс Orchestrator
- `orchestartor/requirements.txt` — зависимости

---

## Задание 4 — Настройка коммуникации через NATS

NATS разворачивается через Docker Compose. Агент слушает `tasks.generate`,
оркестратор публикует туда задачи и слушает `tasks.completed`.

### Запуск NATS
```powershell
docker-compose up -d
```

### Проверка
Открыть в браузере: http://localhost:8222/healthz

### Вывод
```json
{"status": "ok"}
```

---

## Задание 5 — Логирование и мониторинг

Агент пишет логи одновременно в консоль и файл `agent-{instance_id}.log`.
Оркестратор пишет в консоль и `orchestrator.log`.
Каждые 30 секунд оркестратор выводит метрики: tasks_sent, tasks_completed, pending.

### Формат логов агента
```
[instance:1] 2026/05/22 00:28:39 [INFO] received task test-0 for module calculator
[instance:1] 2026/05/22 00:28:39 [INFO] task test-0 completed: 3 test cases generated, total processed: 1
```

---

## Задание 6 — Обработка ошибок и таймаутов

В оркестраторе реализован метод `send_task_with_retry` — повторяет отправку
задачи до 3 раз при сбое с задержкой 2 секунды между попытками.

### Логика
- Таймаут ожидания результата — 30 секунд
- При таймауте или ошибке — повтор, не более 3 раз
- После 3 неудач — исключение с логом

---

## Задание 7 — Запуск нескольких агентов одного типа

Используется NATS Queue Groups — механизм балансировки нагрузки.
Агенты подписываются на одну группу `test-generator-group` и NATS
автоматически распределяет задачи между ними.

### Запуск 3 агентов
```powershell
# Терминал 1
$env:INSTANCE_ID="1"; go run main.go

# Терминал 2
$env:INSTANCE_ID="2"; go run main.go

# Терминал 3
$env:INSTANCE_ID="3"; go run main.go
```

### Вывод — распределение 6 задач между агентами
```
[instance:1] received task test-0 → completed (total: 1)

[instance:2] received task test-1 → completed (total: 1)
[instance:2] received task test-4 → completed (total: 2)

[instance:3] received task test-2 → completed (total: 1)
[instance:3] received task test-3 → completed (total: 2)
[instance:3] received task test-5 → completed (total: 3)
```

6 задач распределились между тремя агентами автоматически.

---

## Задание 8 — Создание API для запуска задач

REST API на FastAPI принимает HTTP запросы, передаёт задачи оркестратору и возвращает результат.

### Эндпоинты
| Метод | Путь | Описание |
|---|---|---|
| GET | /health | Проверка состояния сервиса |
| POST | /tasks/generate | Отправить задачу агенту |

### Запуск
```powershell
cd orchestartor
python -m uvicorn api:app --reload --port 8000
```

### Вывод
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Waiting for application startup.
2026-05-22 00:45:13,511 [INFO] orchestrator connected to NATS at nats://localhost:4222
2026-05-22 00:45:13,511 [INFO] API started
INFO:     Application startup complete.
```

### Проверка health
Открыть в браузере: http://localhost:8000/health
```json
{"status":"ok","tasks_sent":0,"tasks_completed":0}
```

### Отправка задачи через /docs
Открыть в браузере: http://localhost:8000/docs

### Результат выполнения задачи
```
2026-05-22 00:46:03,368 [INFO] attempt 1/3 for task type generate
2026-05-22 00:46:03,369 [INFO] task d62b907f sent to tasks.generate
2026-05-22 00:46:03,375 [INFO] task d62b907f completed
2026-05-22 00:46:03,376 [INFO] task type generate succeeded on attempt 1
2026-05-22 00:46:13,537 [INFO] metrics: tasks_sent=1 tasks_completed=1 pending=0
```

---

## Задание 9 — Тестирование системы

### Тесты агента на Go — `agents/test-generator/main_test.go`

| Тест | Что проверяет |
|---|---|
| TestGenerateTestCases_Success | Успешная генерация 3 тест-кейсов для модуля на Go |
| TestGenerateTestCases_EmptyDescription | Возвращает ошибку если description пустой |
| TestGenerateTestCases_UnsupportedLanguage | Возвращает ошибку для неподдерживаемого языка (java) |
| TestGenerateTestCases_PythonLanguage | Успешная генерация тест-кейсов для модуля на Python |

#### Запуск
```powershell
cd agents/test-generator
go test ./... -v
```

#### Вывод
```
=== RUN   TestGenerateTestCases_Success
--- PASS: TestGenerateTestCases_Success (0.00s)
=== RUN   TestGenerateTestCases_EmptyDescription
--- PASS: TestGenerateTestCases_EmptyDescription (0.00s)
=== RUN   TestGenerateTestCases_UnsupportedLanguage
--- PASS: TestGenerateTestCases_UnsupportedLanguage (0.00s)
=== RUN   TestGenerateTestCases_PythonLanguage
--- PASS: TestGenerateTestCases_PythonLanguage (0.00s)
PASS
ok      github.com/lab13/agents/test-generator  1.813s
```

---

### Тесты оркестратора на Python — `orchestartor/tests/test_orchestrator.py`

NATS замокан через `unittest.mock` — тесты работают без реального подключения.

| Тест | Что проверяет |
|---|---|
| test_orchestrator_initial_state | Начальное состояние: tasks_sent=0, tasks_completed=0, pending={} |
| test_send_task_increments_tasks_sent | После отправки задачи tasks_sent увеличивается на 1, результат успешный |
| test_on_result_completes_future | При получении результата future завершается, tasks_completed увеличивается, задача удаляется из pending |
| test_on_result_ignores_unknown_task | Неизвестный task_id игнорируется, tasks_completed не меняется |
| test_send_task_timeout | При таймауте выбрасывается TimeoutError |

#### Запуск
```powershell
cd orchestartor
python -m pytest tests/ -v
```

#### Вывод
```
tests/test_orchestrator.py::test_orchestrator_initial_state PASSED        [ 20%]
tests/test_orchestrator.py::test_send_task_increments_tasks_sent PASSED   [ 40%]
tests/test_orchestrator.py::test_on_result_completes_future PASSED        [ 60%]
tests/test_orchestrator.py::test_on_result_ignores_unknown_task PASSED    [ 80%]
tests/test_orchestrator.py::test_send_task_timeout PASSED                 [100%]
5 passed in 0.63s
```

---

## Задание 10 — Документирование архитектуры

Диаграмма взаимодействия и описание компонентов находятся в `docs/architecture.md`.

### Компоненты
| Компонент | Технология | Описание |
|---|---|---|
| FastAPI | Python | REST API, точка входа для клиентов |
| Orchestrator | Python + asyncio | Управляет задачами, retry, таймауты |
| NATS Broker | Docker | Брокер сообщений между компонентами |
| test-generator | Go | Агент генерации тест-кейсов |

### Топики NATS
| Топик | Направление | Описание |
|---|---|---|
| tasks.generate | Orchestrator → Agent | Задача на генерацию тестов |
| tasks.completed | Agent → Orchestrator | Результат выполнения |

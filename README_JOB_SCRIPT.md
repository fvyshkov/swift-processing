# Job Script Management

## Файлы

### swift_job_script.py
Основной скрипт обработки SWIFT сообщений (метод `job`).
Извлечен из `swift.objects/ao/swiftIncome.json` для удобного редактирования.

**Размер:** ~42 KB (1021 строк)

### sync_job_script_to_json.py
Скрипт для синхронизации изменений обратно в JSON.

## Workflow

### 1. Редактирование скрипта
Редактируй `swift_job_script.py` в любом редакторе с подсветкой синтаксиса Python.

### 2. Синхронизация в JSON
После изменений запусти:
```bash
python3 sync_job_script_to_json.py
```

### 3. Обновление пакета
```bash
cd swift.objects
zip -r ../swift.objects.zip . -x "*.DS_Store"
```

## Тестовые данные

### test_data/folder_in/camt053_example.xml
Расширенный тестовый файл camt.053 с:

**Балансы (4 шт):**
- OPBD - Opening Booked: 4,645,498.54 NOK
- CLBD - Closing Booked: 7,010,498.54 NOK
- ITBD - Interim Booked: 6,175,498.54 NOK
- CLAV - Closing Available: 6,800,000.00 NOK

**Транзакции (4 шт):**
1. **NTRY-2021-001** (CRDT, BOOK): 2,365,000 NOK
   - 1 TxDtls: ACME Corporation → Nordic Supplies
   - Полная информация о сторонах, счетах, BIC кодах

2. **NTRY-2021-002** (DBIT, BOOK): 530,000 NOK
   - 1 TxDtls: Salary payment
   - Purpose: SALA

3. **NTRY-2021-003** (CRDT, PDNG): 175,000 NOK
   - 1 TxDtls: Pending payment

4. **NTRY-2021-004-BATCH** (CRDT, BOOK): 1,000,000 NOK
   - 3 TxDtls: Batch payment (Bergen, Stavanger, Trondheim)

**Итого:**
- 4 баланса
- 4 транзакции (Ntry)
- 6 деталей транзакций (TxDtls)

## Что тестируется

✅ Парсинг балансов с разными типами
✅ Обработка CRDT и DBIT транзакций
✅ Разные статусы (BOOK, PDNG)
✅ Batch payments (несколько TxDtls в одном Ntry)
✅ Полная информация о сторонах (Debtor/Creditor)
✅ Remittance info (RmtInf/Ustrd)
✅ Purpose codes (Purp/Cd)
✅ UETR, InstrId, EndToEndId
✅ Bank Transaction Codes (Domain/Family/SubFamily)

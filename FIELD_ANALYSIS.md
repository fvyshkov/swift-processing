# АНАЛИЗ ПОЛЕЙ SWIFT_INPUT

## 📋 СУЩЕСТВУЮЩИЕ ПОЛЯ (38 полей)

### Системные поля:
- `id` - UUID primary key
- `file_name` - имя файла
- `state` - статус обработки
- `content` - полный XML
- `imported` - дата импорта
- `error` - ошибки

### Идентификация сообщения:
- `msg_id` - MsgId из GrpHdr
- `msg_def_idr` - MsgDefIdr из AppHdr (например, "pacs.008.001.08")
- `msg_type` - тип сообщения (pacs.008, pacs.009, camt.053, camt.054, camt.056)
- `cre_dt_tm` - CreDtTm дата создания

### Для выписок (camt.053):
- `stmt_id` - ID выписки
- `elctrnc_seq_nb` - электронный порядковый номер
- `acct_id` - ID счета
- `acct_ccy` - валюта счета

### Данные платежа:
- `amount` - сумма
- `currency_code` - валюта
- `dval` - дата валютирования
- `message` - сообщение (Ustrd)
- `code` - EndToEndId или InstrId

### Отправитель (Debtor):
- `snd_acc` - счет отправителя
- `snd_name` - имя отправителя
- `snd_bank` - BIC банка отправителя
- `snd_bank_name` - название банка отправителя

### Промежуточный банк:
- `snd_mid_bank` - BIC промежуточного банка
- `snd_mid_bank_name` - название промежуточного банка
- `snd_mid_bank_acc` - счет промежуточного банка

### Получатель (Creditor):
- `rcv_acc` - счет получателя
- `rcv_name` - имя получателя
- `rcv_bank` - BIC банка получателя
- `rcv_bank_name` - название банка получателя

### Неясные поля:
- `pk` - ???
- `snd_mid_bank_acc_val` - ???

---

## 🔍 АНАЛИЗ ПО ТИПАМ СООБЩЕНИЙ

### 1️⃣ **pacs.008** - Customer Credit Transfer
**Статус:** ✅ Все поля есть

**Что используется:**
- Основные: msg_id, msg_type, amount, currency_code, dval, code, message
- Отправитель: snd_name, snd_acc, snd_bank, snd_bank_name
- Получатель: rcv_name, rcv_acc, rcv_bank, rcv_bank_name
- Промежуточный: snd_mid_bank, snd_mid_bank_name

**Что НЕ используется:** -

---

### 2️⃣ **pacs.009** - FI Credit Transfer (Cover Payment)

**Особенность:** Дебитор и Кредитор = БАНКИ (не клиенты!)

#### Структура pacs.009:
```xml
<CdtTrfTxInf>
  <!-- Банки-участники (это НЕ клиенты!) -->
  <InstgAgt>MYMBGB2LXXX</InstgAgt>  <!-- Instructing Agent -->
  <InstdAgt>INGBROBUXXX</InstdAgt>  <!-- Instructed Agent -->
  
  <Dbtr>
    <FinInstnId>
      <BICFI>MYMBGB2LXXX</BICFI>  <!-- Банк-дебитор -->
    </FinInstnId>
  </Dbtr>
  
  <Cdtr>
    <FinInstnId>
      <BICFI>GEBABEBBXXX</BICFI>  <!-- Банк-кредитор -->
    </FinInstnId>
  </Cdtr>
  
  <!-- РЕАЛЬНЫЕ клиенты - в подсекции! -->
  <UndrlygCstmrCdtTrf>
    <Dbtr>
      <Nm>Debtor Co</Nm>  <!-- Настоящий клиент-отправитель -->
    </Dbtr>
    <DbtrAcct>
      <Id>25698745</Id>  <!-- Счет клиента -->
    </DbtrAcct>
    <Cdtr>
      <Nm>Ardent Finance</Nm>  <!-- Настоящий клиент-получатель -->
    </Cdtr>
    <CdtrAcct>
      <Id>65479512</Id>  <!-- Счет клиента -->
    </CdtrAcct>
  </UndrlygCstmrCdtTrf>
</CdtTrfTxInf>
```

**Что используется из СУЩЕСТВУЮЩИХ полей:**
- `msg_id`, `msg_type`, `amount`, `currency_code`, `dval`, `code`
- `snd_bank` = Dbtr/FinInstnId/BICFI (банк, не клиент!)
- `rcv_bank` = Cdtr/FinInstnId/BICFI (банк, не клиент!)
- `snd_name` = ??? (это будет BIC, а не имя клиента)
- `rcv_name` = ??? (это будет BIC, а не имя клиента)

**🔴 ПРОБЛЕМА:** 
- Поля `snd_name`, `rcv_name` для pacs.009 будут содержать BIC банков, а не имена клиентов
- Имена РЕАЛЬНЫХ клиентов из `UndrlygCstmrCdtTrf` негде хранить!

**✅ НУЖНЫ НОВЫЕ ПОЛЯ:**
```sql
-- Instructed Agent (кому направлена инструкция)
instd_agt text,           -- BICFI из InstdAgt/FinInstnId/BICFI
instd_agt_name text,      -- Nm из InstdAgt/FinInstnId/Nm (если есть)

-- Underlying (реальные) клиенты из UndrlygCstmrCdtTrf
underlying_dbtr_name text,  -- UndrlygCstmrCdtTrf/Dbtr/Nm
underlying_dbtr_acc text,   -- UndrlygCstmrCdtTrf/DbtrAcct/Id
underlying_cdtr_name text,  -- UndrlygCstmrCdtTrf/Cdtr/Nm
underlying_cdtr_acc text,   -- UndrlygCstmrCdtTrf/CdtrAcct/Id

-- Underlying банки (могут отличаться от основных участников)
underlying_dbtr_agt text,      -- UndrlygCstmrCdtTrf/DbtrAgt/FinInstnId/BICFI
underlying_cdtr_agt text,      -- UndrlygCstmrCdtTrf/CdtrAgt/FinInstnId/BICFI
```

---

### 3️⃣ **camt.053** - Bank to Customer Statement
**Статус:** ✅ Все основные поля есть + дочерние таблицы

**Что используется:**
- `msg_id`, `stmt_id`, `elctrnc_seq_nb`, `acct_id`, `acct_ccy`
- Дочерние таблицы: `swift_stmt_bal`, `swift_stmt_ntry`, `swift_entry_tx_dtls`

**Что НЕ используется:** -

---

### 4️⃣ **camt.054** - Debit Credit Notification

#### Структура camt.054:
```xml
<BkToCstmrDbtCdtNtfctn>
  <GrpHdr>
    <MsgId>cmt054bizmsgidr-002</MsgId>
  </GrpHdr>
  <Ntfctn>
    <Id>cmt054NtfctnId-001</Id>  <!-- ID уведомления -->
    <Acct>
      <Id>9875687</Id>
      <Ccy>RON</Ccy>
    </Acct>
    <Ntry>
      <NtryRef>cmt054NtryRef001</NtryRef>
      <Amt Ccy="RON">591636</Amt>
      <!-- ... аналогично camt.053/Ntry ... -->
    </Ntry>
  </Ntfctn>
</BkToCstmrDbtCdtNtfctn>
```

**Отличия от camt.053:**
- Вместо `Stmt` используется `Ntfctn`
- Нет `ElctrncSeqNb`, `StmtPgntn`
- Нет балансов (Bal)

**Что используется из СУЩЕСТВУЮЩИХ полей:**
- `msg_id`, `msg_type`, `acct_id`, `acct_ccy`

**✅ НУЖНЫ НОВЫЕ ПОЛЯ:**
```sql
ntfctn_id text  -- Ntfctn/Id
```

**✅ НУЖНЫ НОВЫЕ ТАБЛИЦЫ:**
```sql
-- Таблица для уведомлений (аналог swift_stmt_ntry)
swift_ntfctn_ntry (
  id, swift_input_id, ntfctn_id, ntry_ref, 
  amt, amt_ccy, cdt_dbt_ind, sts_cd, ...
)

-- Детали транзакций для уведомлений (аналог swift_entry_tx_dtls)
swift_ntfctn_tx_dtls (
  id, ntry_id, instr_id, end_to_end_id, uetr, amt, ...
)
```

---

### 5️⃣ **camt.056** - FI Payment Cancellation Request

#### Структура camt.056 (ПРИМЕРНАЯ, без реального примера):
```xml
<FIToFIPmtCxlReq>
  <Assgnmt>
    <Id>CASE123456</Id>  <!-- Case ID -->
    <Assgnr>
      <Agt>
        <FinInstnId>
          <BICFI>MYMBGB2LXXX</BICFI>  <!-- Кто создал кейс -->
        </FinInstnId>
      </Agt>
    </Assgnr>
  </Assgnmt>
  
  <Undrlyg>
    <TxInf>
      <OrgnlInstrId>pacs8bizmsgidr02</OrgnlInstrId>
      <OrgnlEndToEndId>pacs008EndToEndId-001</OrgnlEndToEndId>
      <OrgnlTxId>TX123</OrgnlTxId>
      <OrgnlUETR>7a562c67-ca16-48ba-b074-65581be6f001</OrgnlUETR>
      <CxlRsnInf>
        <Rsn>
          <Cd>DUPL</Cd>  <!-- Duplicate -->
        </Rsn>
        <AddtlInf>Duplicate payment</AddtlInf>
      </CxlRsnInf>
    </TxInf>
  </Undrlyg>
</FIToFIPmtCxlReq>
```

**Что используется из СУЩЕСТВУЮЩИХ полей:**
- `msg_id`, `msg_type`

**✅ НУЖНЫ НОВЫЕ ПОЛЯ:**
```sql
-- Case information
case_id text,                    -- Assgnmt/Id
case_assgnr text,               -- Assgnmt/Assgnr/Agt/FinInstnId/BICFI

-- Original message reference
orgnl_msg_id text,              -- Undrlyg/OrgnlGrpInfAndSts/OrgnlMsgId
orgnl_msg_nm_id text,           -- Undrlyg/OrgnlGrpInfAndSts/OrgnlMsgNmId

-- Original transaction reference
orgnl_instr_id text,            -- Undrlyg/TxInf/OrgnlInstrId
orgnl_end_to_end_id text,       -- Undrlyg/TxInf/OrgnlEndToEndId
orgnl_tx_id text,               -- Undrlyg/TxInf/OrgnlTxId
orgnl_uetr uuid,                -- Undrlyg/TxInf/OrgnlUETR

-- Cancellation reason
cxl_rsn_cd text,                -- CxlRsnInf/Rsn/Cd
cxl_rsn_addtl_inf text          -- CxlRsnInf/AddtlInf
```

---

## 📝 ИТОГОВЫЙ СПИСОК НОВЫХ ПОЛЕЙ

### Для pacs.009 (6-8 полей):
```sql
-- Обязательные
instd_agt text,                  -- Instructed Agent BIC
underlying_dbtr_name text,       -- Реальное имя отправителя
underlying_cdtr_name text,       -- Реальное имя получателя

-- Опциональные (можно добавить позже)
instd_agt_name text,            -- Instructed Agent название
underlying_dbtr_acc text,        -- Реальный счет отправителя
underlying_cdtr_acc text,        -- Реальный счет получателя
underlying_dbtr_agt text,        -- Банк реального отправителя
underlying_cdtr_agt text         -- Банк реального получателя
```

### Для camt.054 (1 поле + таблицы):
```sql
ntfctn_id text                   -- Notification ID
-- + 2 новые таблицы: swift_ntfctn_ntry, swift_ntfctn_tx_dtls
```

### Для camt.056 (10 полей):
```sql
case_id text,                    -- Case ID
case_assgnr text,                -- Case creator BIC
orgnl_msg_id text,               -- Original message ID
orgnl_msg_nm_id text,            -- Original message type
orgnl_instr_id text,             -- Original InstrId
orgnl_end_to_end_id text,        -- Original EndToEndId
orgnl_tx_id text,                -- Original TxId
orgnl_uetr uuid,                 -- Original UETR
cxl_rsn_cd text,                 -- Cancellation reason code
cxl_rsn_addtl_inf text           -- Additional cancellation info
```

---

## 🎯 РЕКОМЕНДАЦИЯ

### Минимальный набор (17 полей):
1. **pacs.009:** `instd_agt`, `underlying_dbtr_name`, `underlying_cdtr_name`
2. **camt.054:** `ntfctn_id`
3. **camt.056:** все 10 полей + индексы

### Расширенный набор (23 поля):
Добавить к минимальному:
- `instd_agt_name`
- `underlying_dbtr_acc`
- `underlying_cdtr_acc`
- `underlying_dbtr_agt`
- `underlying_cdtr_agt`

### Новые таблицы (2 шт):
- `swift_ntfctn_ntry` - для camt.054 уведомлений
- `swift_ntfctn_tx_dtls` - для деталей транзакций в уведомлениях

---

## ❓ ВОПРОСЫ ДЛЯ ОБСУЖДЕНИЯ

1. **Нужны ли ВСЕ поля для pacs.009 или только основные 3?**
   - Минимум: `instd_agt`, `underlying_dbtr_name`, `underlying_cdtr_name`
   - Полный: + счета и банки underlying

2. **Для camt.056 нужны ВСЕ 10 полей или можно сократить?**
   - Критичные: `case_id`, `orgnl_uetr`, `cxl_rsn_cd`
   - Остальные: опционально

3. **Поля `pk` и `snd_mid_bank_acc_val` - что это? Удалить?**

4. **Нужны ли отдельные таблицы для camt.054 или можно использовать существующие `swift_stmt_ntry`?**
   - Плюсы отдельных: четкое разделение Stmt vs Ntfctn
   - Минусы: дублирование структуры


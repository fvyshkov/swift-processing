# ISO 20022 Message Formats Documentation

Документация по основным форматам сообщений ISO 20022, используемых в межбанковских платежных системах SWIFT.

---

## Содержание

1. [pacs.008 - Customer Credit Transfer](#pacs008---customer-credit-transfer)
2. [pacs.009 - Financial Institution Credit Transfer (COV)](#pacs009---financial-institution-credit-transfer-cov)
3. [camt.053 - Bank to Customer Statement](#camt053---bank-to-customer-statement)
4. [camt.054 - Bank to Customer Debit/Credit Notification](#camt054---bank-to-customer-debitcredit-notification)
5. [camt.056 - FI to FI Payment Cancellation Request](#camt056---fi-to-fi-payment-cancellation-request)
6. [Общие коды и справочники](#общие-коды-и-справочники)

---

## pacs.008 - Customer Credit Transfer

### Назначение
Используется для межбанковского кредитового перевода средств от клиента одного банка клиенту другого банка. Это основной формат для клиентских платежей между финансовыми институтами через SWIFT.

### Структура сообщения

#### Корневой элемент
```xml
<pacs:Document xmlns:pacs="urn:iso:std:iso:20022:tech:xsd:pacs.008.001.08">
  <pacs:FIToFICstmrCdtTrf>
    ...
  </pacs:FIToFICstmrCdtTrf>
</pacs:Document>
```

#### 1. Group Header (GrpHdr) - Заголовок группы

| Элемент | Тип | Описание | Обязательность |
|---------|-----|----------|----------------|
| `MsgId` | Text | Уникальный идентификатор сообщения | Обязательный |
| `CreDtTm` | DateTime | Дата и время создания сообщения | Обязательный |
| `NbOfTxs` | Number | Количество транзакций в сообщении | Обязательный |
| `CtrlSum` | Decimal | Контрольная сумма (общая сумма всех транзакций) | Опциональный |
| `SttlmInf` | Complex | Информация о расчете | Обязательный |

**Settlement Information (SttlmInf):**
- `SttlmMtd` - Метод расчета:
  - `INDA` - Indirect Agent (косвенный агент)
  - `INGA` - Instructing Agent (инструктирующий агент)
  - `CLRG` - Clearing (клиринг)

#### 2. Credit Transfer Transaction Information (CdtTrfTxInf) - Информация о кредитовом переводе

##### Payment Identification (PmtId) - Идентификация платежа

| Элемент | Тип | Описание | Обязательность |
|---------|-----|----------|----------------|
| `InstrId` | Text | Идентификатор инструкции (от инициирующего банка) | Опциональный |
| `EndToEndId` | Text | End-to-end идентификатор (от клиента-отправителя) | Обязательный |
| `TxId` | Text | Идентификатор транзакции | Опциональный |
| `UETR` | UUID | Unique End-to-end Transaction Reference (UUID формат) | Обязательный |

**UETR** - уникальный идентификатор для отслеживания платежа на всем пути следования.

##### Payment Type Information (PmtTpInf) - Тип платежа

| Элемент | Тип | Описание |
|---------|-----|----------|
| `InstrPrty` | Code | Приоритет: `HIGH`, `NORM` |
| `SvcLvl/Cd` | Code | Уровень сервиса: `SEPA`, `SDVA`, `NURG` |
| `LclInstrm/Cd` | Code | Локальный инструмент |
| `CtgyPurp/Cd` | Code | Категория назначения |

##### Основные атрибуты транзакции

| Элемент | Тип | Описание | Обязательность |
|---------|-----|----------|----------------|
| `IntrBkSttlmAmt` | Amount + Ccy | Сумма межбанковского расчета | Обязательный |
| `IntrBkSttlmDt` | Date | Дата межбанковского расчета (YYYY-MM-DD) | Обязательный |
| `InstdAmt` | Amount + Ccy | Инструктированная сумма | Опциональный |
| `ChrgBr` | Code | Оплата комиссии | Опциональный |
| `ChrgsInf` | Complex | Информация о комиссиях | Опциональный |

**Коды оплаты комиссии (ChrgBr):**
- `DEBT` - Borne by Debtor (комиссия за счет плательщика)
- `CRED` - Borne by Creditor (комиссия за счет получателя)
- `SHAR` - Shared (разделенная комиссия)
- `SLEV` - Service Level (по уровню сервиса)

##### Агенты (Banks)

**Instructing Agent (InstgAgt) - Инициирующий банк:**
- `FinInstnId/BICFI` - BIC код банка
- `FinInstnId/ClrSysMmbId` - ID в клиринговой системе
- `FinInstnId/Nm` - Название банка
- `FinInstnId/PstlAdr` - Адрес банка

**Instructed Agent (InstdAgt) - Инструктированный банк:**
- Аналогичная структура

**Debtor Agent (DbtrAgt) - Банк плательщика:**
- Аналогичная структура

**Creditor Agent (CdtrAgt) - Банк получателя:**
- Аналогичная структура

**Intermediary Agent (IntrmyAgt) - Банк-посредник:**
- Аналогичная структура (может быть несколько)

##### Debtor (Dbtr) - Дебитор (плательщик)

| Элемент | Тип | Описание |
|---------|-----|----------|
| `Nm` | Text | Имя плательщика | Обязательный |
| `PstlAdr` | Complex | Почтовый адрес | Опциональный |
| `Id` | Complex | Идентификация | Опциональный |
| `CtryOfRes` | Code | Страна резидентства | Опциональный |
| `CtctDtls` | Complex | Контактные данные | Опциональный |

**Postal Address (PstlAdr):**
- `StrtNm` - Улица
- `BldgNb` - Номер здания
- `PstCd` - Почтовый индекс
- `TwnNm` - Город
- `CtrySubDvsn` - Регион/область
- `Ctry` - Страна (ISO 3166, 2 символа)
- `AdrLine` - Строки адреса (до 7 строк)

##### Debtor Account (DbtrAcct) - Счет плательщика

| Элемент | Тип | Описание |
|---------|-----|----------|
| `Id/IBAN` | Text | IBAN счета | Один из вариантов |
| `Id/Othr/Id` | Text | Другой идентификатор счета | Альтернатива |
| `Tp/Cd` | Code | Тип счета: `CACC`, `SVGS`, `TRAN` | Опциональный |
| `Ccy` | Code | Валюта счета (ISO 4217) | Опциональный |
| `Nm` | Text | Название счета | Опциональный |

##### Creditor (Cdtr) - Кредитор (получатель)

Структура аналогична Debtor:
- `Nm` - Имя получателя (обязательно)
- `PstlAdr` - Почтовый адрес
- `Id` - Идентификация
- `CtryOfRes` - Страна резидентства
- `CtctDtls` - Контактные данные

##### Creditor Account (CdtrAcct) - Счет получателя

Структура аналогична DbtrAcct:
- `Id/IBAN` или `Id/Othr/Id` - Идентификатор счета
- `Tp` - Тип счета
- `Ccy` - Валюта
- `Nm` - Название

##### Purpose (Purp) - Назначение платежа

| Элемент | Тип | Описание |
|---------|-----|----------|
| `Cd` | Code | Стандартный код назначения | Один из вариантов |
| `Prtry` | Text | Проприетарный код назначения | Альтернатива |

**Коды назначения (External Purpose Code):**
- `SALA` - Salary Payment (зарплата)
- `PENS` - Pension Payment (пенсия)
- `SUPP` - Supplier Payment (платеж поставщику)
- `TRAD` - Trade (торговля)
- `CASH` - Cash Management
- `LOAN` - Loan (кредит)
- `INTC` - Intra-Company Payment (внутрикорпоративный)

##### Remittance Information (RmtInf) - Информация о платеже

| Элемент | Тип | Описание |
|---------|-----|----------|
| `Ustrd` | Text | Неструктурированная информация (до 140 символов) | Опциональный |
| `Strd` | Complex | Структурированная информация | Опциональный |

**Structured Remittance (Strd):**
- `RfrdDocInf` - Ссылка на документ:
  - `Tp/CdOrPrtry/Cd` - Тип документа: `CINV` (Commercial Invoice), `DNFA` (Debit Note), и т.д.
  - `Nb` - Номер документа
  - `RltdDt` - Дата документа
- `RfrdDocAmt` - Суммы документа:
  - `DuePyblAmt` - Сумма к оплате
  - `DscntApldAmt` - Скидка
  - `CdtNoteAmt` - Кредит-нота
  - `TaxAmt` - Налог

##### Regulatory Reporting (RgltryRptg) - Регуляторная отчетность

| Элемент | Тип | Описание |
|---------|-----|----------|
| `DbtCdtRptgInd` | Code | Индикатор: `CRED`, `DEBT`, `BOTH` |
| `Authrty` | Complex | Орган власти |
| `Dtls/Tp` | Text | Тип отчета |
| `Dtls/Cd` | Code | Код |
| `Dtls/Amt` | Amount | Сумма |
| `Dtls/Inf` | Text | Информация |

### Структура обработки в системе

В таблице `swift_input` для pacs.008 хранятся следующие поля:

| Поле БД | Источник XML | Описание |
|---------|--------------|----------|
| `file_name` | - | Имя файла |
| `msg_type` | `MsgDefIdr` | Тип сообщения: "pacs.008" |
| `msg_id` | `GrpHdr/MsgId` | ID сообщения |
| `snd_name` | `Dbtr/Nm` | Имя плательщика |
| `snd_acc` | `DbtrAcct/Id` | Счет плательщика |
| `snd_bank` | `DbtrAgt/FinInstnId/BICFI` | BIC банка плательщика |
| `snd_bank_name` | `DbtrAgt/FinInstnId/Nm` | Название банка плательщика |
| `rcv_name` | `Cdtr/Nm` | Имя получателя |
| `rcv_acc` | `CdtrAcct/Id` | Счет получателя |
| `rcv_bank` | `CdtrAgt/FinInstnId/BICFI` | BIC банка получателя |
| `rcv_bank_name` | `CdtrAgt/FinInstnId/Nm` | Название банка получателя |
| `snd_mid_bank` | `IntrmyAgt/FinInstnId/BICFI` | BIC банка-посредника |
| `snd_mid_bank_name` | `IntrmyAgt/FinInstnId/Nm` | Название банка-посредника |
| `amount` | `IntrBkSttlmAmt` | Сумма |
| `currency_code` | `IntrBkSttlmAmt@Ccy` | Валюта |
| `dval` | `IntrBkSttlmDt` | Дата расчета |
| `code` | `PmtId/EndToEndId` | End-to-end ID |
| `message` | `RmtInf/Ustrd` | Назначение платежа |

### Пример pacs.008

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Envelope xmlns="urn:swift:xsd:envelope">
	<head:AppHdr xmlns:head="urn:iso:std:iso:20022:tech:xsd:head.001.001.02">
		<head:Fr><head:FIId><head:FinInstnId><head:BICFI>DSBAHKHH</head:BICFI></head:FinInstnId></head:FIId></head:Fr>
		<head:To><head:FIId><head:FinInstnId><head:BICFI>ID521122</head:BICFI></head:FinInstnId></head:FIId></head:To>
		<head:BizMsgIdr>pacs8bizmsgidr02</head:BizMsgIdr>
		<head:MsgDefIdr>pacs.008.001.08</head:MsgDefIdr>
		<head:BizSvc>swift.cbprplus.02</head:BizSvc>
		<head:CreDt>2022-10-20T10:25:00+01:00</head:CreDt>
	</head:AppHdr>
	<pacs:Document xmlns:pacs="urn:iso:std:iso:20022:tech:xsd:pacs.008.001.08">
		<pacs:FIToFICstmrCdtTrf>
			<pacs:GrpHdr>
				<pacs:MsgId>pacs8bizmsgidr02</pacs:MsgId>
				<pacs:CreDtTm>2022-10-20T10:25:00+01:00</pacs:CreDtTm>
				<pacs:NbOfTxs>1</pacs:NbOfTxs>
				<pacs:SttlmInf>
					<pacs:SttlmMtd>INDA</pacs:SttlmMtd>
				</pacs:SttlmInf>
			</pacs:GrpHdr>
			<pacs:CdtTrfTxInf>
				<pacs:PmtId>
					<pacs:InstrId>pacs8bizmsgidr02</pacs:InstrId>
					<pacs:EndToEndId>pacs008EndToEndId-001</pacs:EndToEndId>
					<pacs:UETR>7a562c67-ca16-48ba-b074-65581be6f001</pacs:UETR>
				</pacs:PmtId>
				<pacs:IntrBkSttlmAmt Ccy="USD">98725497</pacs:IntrBkSttlmAmt>
				<pacs:IntrBkSttlmDt>2022-10-20</pacs:IntrBkSttlmDt>
				<pacs:ChrgBr>SHAR</pacs:ChrgBr>
				<pacs:InstgAgt>
					<pacs:FinInstnId>
						<pacs:BICFI>DSBAHKHH</pacs:BICFI>
					</pacs:FinInstnId>
				</pacs:InstgAgt>
				<pacs:InstdAgt>
					<pacs:FinInstnId>
						<pacs:BICFI>ID521122</pacs:BICFI>
					</pacs:FinInstnId>
				</pacs:InstdAgt>
				<pacs:Dbtr>
					<pacs:Nm>A Capone</pacs:Nm>
					<pacs:PstlAdr>
						<pacs:Ctry>US</pacs:Ctry>
					</pacs:PstlAdr>
				</pacs:Dbtr>
				<pacs:DbtrAcct>
					<pacs:Id>
						<pacs:Othr>
							<pacs:Id>ACPN-2569874</pacs:Id>
						</pacs:Othr>
					</pacs:Id>
				</pacs:DbtrAcct>
				<pacs:DbtrAgt>
					<pacs:FinInstnId>
						<pacs:BICFI>DSBAHKHH</pacs:BICFI>
						<pacs:Nm>Deutsche Bank Hong Kong</pacs:Nm>
					</pacs:FinInstnId>
				</pacs:DbtrAgt>
				<pacs:CdtrAgt>
					<pacs:FinInstnId>
						<pacs:BICFI>ID521122</pacs:BICFI>
						<pacs:Nm>Recipient Bank</pacs:Nm>
					</pacs:FinInstnId>
				</pacs:CdtrAgt>
				<pacs:Cdtr>
					<pacs:Nm>J Smith</pacs:Nm>
				</pacs:Cdtr>
				<pacs:CdtrAcct>
					<pacs:Id>
						<pacs:Othr>
							<pacs:Id>65479512</pacs:Id>
						</pacs:Othr>
					</pacs:Id>
				</pacs:CdtrAcct>
				<pacs:Purp>
					<pacs:Cd>SUPP</pacs:Cd>
				</pacs:Purp>
				<pacs:RmtInf>
					<pacs:Ustrd>Invoice #12345 Payment</pacs:Ustrd>
				</pacs:RmtInf>
			</pacs:CdtTrfTxInf>
		</pacs:FIToFICstmrCdtTrf>
	</pacs:Document>
</Envelope>
```

### Отличия pacs.008 от pacs.009

| Характеристика | pacs.008 | pacs.009 |
|----------------|----------|----------|
| Назначение | Клиентский платеж (от клиента к клиенту) | Cover payment (покрывающий платеж между банками) |
| Дебитор/Кредитор | Клиенты банков | Финансовые институты |
| Underlying | Нет | Содержит UndrlygCstmrCdtTrf с информацией о клиентах |
| Использование | Прямой платеж | Расчет между банками-корреспондентами |
| Связь | Может быть независимым | Обычно связан с pacs.008 через UETR |

---

## pacs.009 - Financial Institution Credit Transfer (COV)

### Назначение
Используется для перевода средств между финансовыми институтами (межбанковский перевод) с информацией о базовом клиентском платеже. "COV" означает "Cover Payment" - покрывающий платеж.

### Структура сообщения

#### Корневой элемент
```xml
<pacs:Document xmlns:pacs="urn:iso:std:iso:20022:tech:xsd:pacs.009.001.08">
  <pacs:FICdtTrf>
    ...
  </pacs:FICdtTrf>
</pacs:Document>
```

#### 1. Group Header (GrpHdr) - Заголовок группы

| Элемент | Тип | Описание | Обязательность |
|---------|-----|----------|----------------|
| `MsgId` | Text | Уникальный идентификатор сообщения | Обязательный |
| `CreDtTm` | DateTime | Дата и время создания сообщения | Обязательный |
| `NbOfTxs` | Number | Количество транзакций в сообщении | Обязательный |
| `SttlmInf` | Complex | Информация о расчете | Обязательный |
| `SttlmInf/SttlmMtd` | Code | Метод расчета | Обязательный |

**Коды методов расчета (SttlmMtd):**
- `INDA` - Indirect Agent (косвенный агент)
- `INGA` - Instructing Agent
- `CLRG` - Clearing (клиринг)
- `COVE` - Cover (покрытие)

#### 2. Credit Transfer Transaction Information (CdtTrfTxInf) - Информация о переводе

##### Payment Identification (PmtId) - Идентификация платежа

| Элемент | Тип | Описание | Обязательность |
|---------|-----|----------|----------------|
| `InstrId` | Text | Идентификатор инструкции | Опциональный |
| `EndToEndId` | Text | End-to-end идентификатор | Обязательный |
| `UETR` | UUID | Unique End-to-end Transaction Reference | Обязательный |

##### Основные атрибуты транзакции

| Элемент | Тип | Описание | Обязательность |
|---------|-----|----------|----------------|
| `IntrBkSttlmAmt` | Amount + Ccy | Сумма межбанковского расчета | Обязательный |
| `IntrBkSttlmDt` | Date | Дата межбанковского расчета | Обязательный |
| `InstgAgt` | Agent | Инициирующий агент (банк) | Обязательный |
| `InstdAgt` | Agent | Инструктированный агент (банк) | Обязательный |
| `Dbtr` | Agent | Дебитор (банк-плательщик) | Обязательный |
| `DbtrAgt` | Agent | Агент дебитора | Опциональный |
| `CdtrAgt` | Agent | Агент кредитора | Обязательный |
| `Cdtr` | Agent | Кредитор (банк-получатель) | Обязательный |

**Структура Agent (FinInstnId):**
- `BICFI` - BIC код финансового института (11 символов)
- `ClrSysMmbId` - Идентификатор в клиринговой системе (опционально)
- `Nm` - Название (опционально)

##### Underlying Customer Credit Transfer (UndrlygCstmrCdtTrf) - Базовый клиентский перевод

**Дебитор (Dbtr):**
- `Nm` - Имя дебитора
- `PstlAdr` - Почтовый адрес:
  - `StrtNm` - Улица
  - `BldgNb` - Номер здания
  - `PstCd` - Почтовый индекс
  - `TwnNm` - Город
  - `CtrySubDvsn` - Регион/область
  - `Ctry` - Страна (ISO 3166 код, 2 символа)

**Счет дебитора (DbtrAcct):**
- `Id/IBAN` - IBAN счета
- `Id/Othr/Id` - Другой идентификатор счета
- `Ccy` - Валюта счета

**Кредитор (Cdtr):**
- Аналогичная структура как у дебитора

**Счет кредитора (CdtrAcct):**
- Аналогичная структура как у счета дебитора

### Пример использования
```xml
<pacs:IntrBkSttlmAmt Ccy="RON">591636</pacs:IntrBkSttlmAmt>
<pacs:IntrBkSttlmDt>2022-10-20</pacs:IntrBkSttlmDt>
```

---

## camt.053 - Bank to Customer Statement

### Назначение
Банковская выписка, отправляемая банком клиенту с полной информацией о движении средств по счету за определенный период.

### Структура сообщения

#### Корневой элемент
```xml
<camt:Document xmlns:camt="urn:iso:std:iso:20022:tech:xsd:camt.053.001.08">
  <camt:BkToCstmrStmt>
    ...
  </camt:BkToCstmrStmt>
</camt:Document>
```

#### 1. Group Header (GrpHdr) - Заголовок группы

| Элемент | Тип | Описание | Обязательность |
|---------|-----|----------|----------------|
| `MsgId` | Text | Уникальный идентификатор сообщения | Обязательный |
| `CreDtTm` | DateTime | Дата и время создания | Обязательный |
| `MsgRcpt` | Party | Получатель сообщения | Опциональный |
| `MsgPgntn` | Pagination | Пагинация сообщений | Опциональный |

#### 2. Statement (Stmt) - Выписка

**Важно:** Выписка содержит два **независимых списка на одном уровне**:
1. **Список балансов (Bal)** - показывает балансы счета (начальный, конечный)
2. **Список транзакций (Ntry)** - показывает все операции за период

**Структура выписки:**
```xml
<camt:Stmt>
  <!-- Идентификация выписки -->
  <camt:Id>STMNTID</camt:Id>
  <camt:StmtPgntn>...</camt:StmtPgntn>
  <camt:ElctrncSeqNb>32145</camt:ElctrncSeqNb>

  <!-- Информация о счете -->
  <camt:Acct>
    <camt:Id>...</camt:Id>
    <camt:Ccy>NOK</camt:Ccy>
  </camt:Acct>

  <!-- СПИСОК БАЛАНСОВ (несколько элементов Bal) -->
  <camt:Bal>  <!-- Баланс на начало -->
    <camt:Tp><camt:CdOrPrtry><camt:Cd>OPBD</camt:Cd></camt:CdOrPrtry></camt:Tp>
    <camt:Amt Ccy="NOK">4645498.54</camt:Amt>
    ...
  </camt:Bal>
  <camt:Bal>  <!-- Баланс на конец -->
    <camt:Tp><camt:CdOrPrtry><camt:Cd>CLBD</camt:Cd></camt:CdOrPrtry></camt:Tp>
    <camt:Amt Ccy="NOK">7010498.54</camt:Amt>
    ...
  </camt:Bal>

  <!-- СПИСОК ТРАНЗАКЦИЙ (несколько элементов Ntry) -->
  <camt:Ntry>  <!-- Транзакция 1 -->
    <camt:Amt Ccy="NOK">2365000</camt:Amt>
    <camt:NtryDtls>
      <camt:TxDtls>...</camt:TxDtls>  <!-- Детали транзакции -->
    </camt:NtryDtls>
  </camt:Ntry>
  <camt:Ntry>  <!-- Транзакция 2 -->
    ...
  </camt:Ntry>
</camt:Stmt>
```

##### Идентификация выписки

| Элемент | Тип | Описание | Обязательность |
|---------|-----|----------|----------------|
| `Id` | Text | Идентификатор выписки | Обязательный |
| `ElctrncSeqNb` | Number | Электронный порядковый номер | Опциональный |
| `LglSeqNb` | Number | Юридический порядковый номер | Опциональный |
| `CreDtTm` | DateTime | Дата создания выписки | Опциональный |

##### Pagination (StmtPgntn) - Пагинация

| Элемент | Тип | Описание |
|---------|-----|----------|
| `PgNb` | Number | Номер страницы |
| `LastPgInd` | Boolean | Индикатор последней страницы (true/false) |

##### Account (Acct) - Счет

| Элемент | Тип | Описание | Обязательность |
|---------|-----|----------|----------------|
| `Id/IBAN` | Text | IBAN счета | Один из вариантов |
| `Id/Othr/Id` | Text | Другой идентификатор | Один из вариантов |
| `Tp` | Code | Тип счета | Опциональный |
| `Ccy` | Code | Валюта счета (ISO 4217) | Обязательный |
| `Nm` | Text | Название счета | Опциональный |
| `Ownr` | Party | Владелец счета | Опциональный |
| `Svcr` | Agent | Обслуживающий банк | Опциональный |

#### 3. Balance (Bal) - Список балансов (несколько элементов Bal на одном уровне внутри Stmt)

| Элемент | Тип | Описание | Обязательность |
|---------|-----|----------|----------------|
| `Tp/CdOrPrtry/Cd` | Code | Тип баланса | Обязательный |
| `Amt` | Amount + Ccy | Сумма и валюта | Обязательный |
| `CdtDbtInd` | Code | Индикатор кредит/дебет | Обязательный |
| `Dt/Dt` | Date | Дата баланса | Обязательный |
| `Dt/DtTm` | DateTime | Дата и время баланса | Альтернатива |

**Коды типов баланса (Tp/CdOrPrtry/Cd):**
- `OPBD` - Opening Booked (начальный проведенный баланс)
- `CLBD` - Closing Booked (конечный проведенный баланс)
- `CLAV` - Closing Available (конечный доступный баланс)
- `FWAV` - Forward Available (прогнозный доступный)
- `ITBD` - Interim Booked (промежуточный проведенный)
- `ITAV` - Interim Available (промежуточный доступный)
- `OPAV` - Opening Available (начальный доступный)
- `PRCD` - Previously Closed Booked (предыдущий закрытый)

**Коды индикатора кредит/дебет (CdtDbtInd):**
- `CRDT` - Credit (кредит, положительный баланс)
- `DBIT` - Debit (дебет, отрицательный баланс)

#### 4. Entry (Ntry) - Список записей/транзакций (несколько элементов Ntry на одном уровне внутри Stmt)

**Структура Entry:**
```xml
<camt:Ntry>
  <!-- Основная информация о записи -->
  <camt:Amt Ccy="NOK">2365000</camt:Amt>
  <camt:CdtDbtInd>CRDT</camt:CdtDbtInd>
  <camt:Sts><camt:Cd>BOOK</camt:Cd></camt:Sts>
  <camt:BookgDt>...</camt:BookgDt>
  <camt:BkTxCd>...</camt:BkTxCd>

  <!-- ДЕТАЛИ ЗАПИСИ - может содержать список TxDtls -->
  <camt:NtryDtls>
    <camt:TxDtls>  <!-- Детали транзакции 1 -->
      <camt:Refs>...</camt:Refs>
      <camt:Amt>...</camt:Amt>
    </camt:TxDtls>
    <camt:TxDtls>  <!-- Детали транзакции 2 (если несколько) -->
      ...
    </camt:TxDtls>
  </camt:NtryDtls>
</camt:Ntry>
```

| Элемент | Тип | Описание | Обязательность |
|---------|-----|----------|----------------|
| `NtryRef` | Text | Ссылка на запись | Опциональный |
| `Amt` | Amount + Ccy | Сумма транзакции | Обязательный |
| `CdtDbtInd` | Code | Кредит или дебет | Обязательный |
| `RvslInd` | Boolean | Индикатор сторно | Опциональный |
| `Sts/Cd` | Code | Статус записи | Обязательный |
| `BookgDt/Dt` | Date | Дата проводки | Обязательный |
| `ValDt/Dt` | Date | Дата валютирования | Обязательный |
| `AcctSvcrRef` | Text | Ссылка обслуживающего банка | Опциональный |
| `BkTxCd` | Complex | Банковский код транзакции | Обязательный |
| `NtryDtls` | Complex | Детали записи (содержит список TxDtls) | Опциональный |

**Коды статуса (Sts/Cd):**
- `BOOK` - Booked (проведено)
- `PDNG` - Pending (в ожидании)
- `INFO` - Information (информационная запись)
- `FUTR` - Future (будущая транзакция)

##### Bank Transaction Code (BkTxCd) - Банковский код транзакции

**Структура:**
```xml
<camt:BkTxCd>
  <camt:Domn>
    <camt:Cd>PMNT</camt:Cd>
    <camt:Fmly>
      <camt:Cd>RCDT</camt:Cd>
      <camt:SubFmlyCd>XBCT</camt:SubFmlyCd>
    </camt:Fmly>
  </camt:Domn>
  <camt:Prtry>
    <camt:Cd>ProprietaryCode</camt:Cd>
  </camt:Prtry>
</camt:BkTxCd>
```

**Коды доменов (Domn/Cd):**
- `PMNT` - Payments (платежи)
- `ACMT` - Account Management (управление счетом)
- `CAMT` - Cash Management (управление наличностью)
- `XTND` - Extended Domain (расширенный домен)
- `LDAS` - Loans and Deposits (кредиты и депозиты)
- `CMDT` - Commodities (товары)
- `FORX` - Foreign Exchange (валютные операции)
- `TRAD` - Trade Services (торговые услуги)
- `SECU` - Securities (ценные бумаги)

**Коды семейства для PMNT (Fmly/Cd):**
- `RCDT` - Received Credit Transfer (полученный кредитовый перевод)
- `ICDT` - Issued Credit Transfer (отправленный кредитовый перевод)
- `RDDT` - Received Direct Debit (полученное прямое дебетование)
- `IDDT` - Issued Direct Debit (отправленное прямое дебетование)
- `CCRD` - Customer Card Transaction (карточная транзакция клиента)
- `MCRD` - Merchant Card Transaction (карточная транзакция продавца)

**Коды подсемейства (SubFmlyCd):**
- `XBCT` - Cross Border Credit Transfer (трансграничный кредитовый перевод)
- `DMCT` - Domestic Credit Transfer (внутренний кредитовый перевод)
- `STDO` - Standing Order (постоянное поручение)
- `RRTN` - Return (возврат)
- `REQL` - Request for Liquidity (запрос ликвидности)

#### 5. Entry Details (NtryDtls) - Детали записи

**Важно:** `NtryDtls` находится внутри элемента `Ntry` и содержит **список `TxDtls`** (один или несколько элементов).

##### Transaction Details (TxDtls) - Список деталей транзакций (несколько элементов TxDtls внутри NtryDtls)

Одна запись `Ntry` может содержать несколько транзакций `TxDtls`. Например, пакетный платеж может отображаться как одна запись `Ntry` с несколькими детальными транзакциями `TxDtls`.

| Элемент | Тип | Описание |
|---------|-----|----------|
| `Refs` | Complex | Ссылки на транзакцию |
| `Amt` | Amount + Ccy | Сумма транзакции |
| `CdtDbtInd` | Code | Индикатор кредит/дебет |
| `AmtDtls` | Complex | Детали суммы |
| `RltdPties` | Complex | Связанные стороны |
| `RltdAgts` | Complex | Связанные агенты |
| `RmtInf` | Complex | Информация для перевода |
| `RltdDts` | Complex | Связанные даты |
| `Purp` | Complex | Назначение платежа |

**References (Refs) - Ссылки:**
- `MsgId` - ID сообщения
- `AcctSvcrRef` - Ссылка обслуживающего банка
- `PmtInfId` - ID информации о платеже
- `InstrId` - ID инструкции
- `EndToEndId` - End-to-end ID
- `TxId` - ID транзакции
- `MndtId` - ID мандата
- `ChqNb` - Номер чека
- `ClrSysRef` - Ссылка клиринговой системы
- `UETR` - Unique End-to-end Transaction Reference

### Визуальная иерархия camt.053

```
Document (корень)
└── BkToCstmrStmt
    ├── GrpHdr (заголовок группы)
    └── Stmt (выписка) ← может быть несколько выписок
        ├── Id, ElctrncSeqNb, StmtPgntn (идентификация)
        ├── Acct (информация о счете)
        ├── Bal (баланс 1: OPBD - начальный) ← СПИСОК
        ├── Bal (баланс 2: CLBD - конечный)  ← СПИСОК
        ├── Ntry (запись/транзакция 1) ← СПИСОК
        │   ├── Amt, CdtDbtInd, Sts, BookgDt, ValDt
        │   ├── BkTxCd (код транзакции)
        │   └── NtryDtls (детали)
        │       ├── TxDtls (детали транзакции 1) ← СПИСОК
        │       │   ├── Refs (ссылки)
        │       │   ├── Amt, CdtDbtInd
        │       │   ├── RltdPties (стороны)
        │       │   ├── RltdAgts (агенты)
        │       │   └── RmtInf (назначение)
        │       └── TxDtls (детали транзакции 2) ← СПИСОК
        ├── Ntry (запись/транзакция 2) ← СПИСОК
        └── Ntry (запись/транзакция N) ← СПИСОК
```

### Пример использования
```xml
<camt:Bal>
  <camt:Tp>
    <camt:CdOrPrtry>
      <camt:Cd>OPBD</camt:Cd>
    </camt:CdOrPrtry>
  </camt:Tp>
  <camt:Amt Ccy="NOK">4645498.54</camt:Amt>
  <camt:CdtDbtInd>CRDT</camt:CdtDbtInd>
  <camt:Dt>
    <camt:Dt>2021-06-03</camt:Dt>
  </camt:Dt>
</camt:Bal>
```

---

## camt.054 - Bank to Customer Debit/Credit Notification

### Назначение
Уведомление банка клиенту о дебетовой или кредитовой операции по счету. Более оперативное уведомление, чем выписка (camt.053). Отправляется для каждой отдельной транзакции или группы транзакций.

### Структура сообщения

#### Корневой элемент
```xml
<camt:Document xmlns:camt="urn:iso:std:iso:20022:tech:xsd:camt.054.001.08">
  <camt:BkToCstmrDbtCdtNtfctn>
    ...
  </camt:BkToCstmrDbtCdtNtfctn>
</camt:Document>
```

#### 1. Group Header (GrpHdr) - Заголовок группы

| Элемент | Тип | Описание | Обязательность |
|---------|-----|----------|----------------|
| `MsgId` | Text | Уникальный идентификатор сообщения | Обязательный |
| `CreDtTm` | DateTime | Дата и время создания | Обязательный |
| `MsgRcpt` | Party | Получатель сообщения | Опциональный |
| `MsgPgntn` | Pagination | Пагинация | Опциональный |
| `AddtlInf` | Text | Дополнительная информация | Опциональный |

#### 2. Notification (Ntfctn) - Список уведомлений

##### Идентификация уведомления

| Элемент | Тип | Описание | Обязательность |
|---------|-----|----------|----------------|
| `Id` | Text | Идентификатор уведомления | Обязательный |
| `CreDtTm` | DateTime | Дата создания уведомления | Опциональный |
| `Acct` | Complex | Информация о счете | Обязательный |

##### Account (Acct) - Счет

| Элемент | Тип | Описание |
|---------|-----|----------|
| `Id/IBAN` | Text | IBAN счета |
| `Id/Othr/Id` | Text | Другой идентификатор счета |
| `Tp` | Code | Тип счета |
| `Ccy` | Code | Валюта счета (ISO 4217) |
| `Nm` | Text | Название счета |
| `Ownr` | Party | Владелец счета |
| `Svcr` | Agent | Обслуживающий банк |

#### 3. Entry (Ntry) - Список записей

| Элемент | Тип | Описание | Обязательность |
|---------|-----|----------|----------------|
| `NtryRef` | Text | Ссылка на запись | Опциональный |
| `Amt` | Amount + Ccy | Сумма операции | Обязательный |
| `CdtDbtInd` | Code | Кредит или дебет | Обязательный |
| `RvslInd` | Boolean | Индикатор сторно | Опциональный |
| `Sts/Cd` | Code | Статус записи | Обязательный |
| `BookgDt/Dt` | Date | Дата проводки | Опциональный |
| `ValDt/Dt` | Date | Дата валютирования | Опциональный |
| `AcctSvcrRef` | Text | Ссылка банка | Опциональный |
| `BkTxCd` | Complex | Банковский код транзакции | Обязательный |
| `NtryDtls` | List | Детали записи | Опциональный |

**Коды статуса (Sts/Cd):**
- `BOOK` - Booked (проведено в системе банка)
- `PDNG` - Pending (ожидает проведения)
- `INFO` - Information (информационное)

##### Bank Transaction Code (BkTxCd)
Аналогичен структуре в camt.053 (см. выше).

#### 4. Entry Details (NtryDtls) - Детали записи

##### Transaction Details (TxDtls)

| Элемент | Тип | Описание |
|---------|-----|----------|
| `Refs` | Complex | Ссылки |
| `Amt` | Amount + Ccy | Сумма |
| `CdtDbtInd` | Code | Индикатор кредит/дебет |
| `AmtDtls` | Complex | Детали суммы |
| `RltdPties` | Complex | Связанные стороны |
| `RltdAgts` | Complex | Связанные банки |
| `Purp` | Complex | Назначение |
| `RltdDts` | Complex | Связанные даты |
| `RmtInf` | Complex | Платежная информация |

**References (Refs):**
- `InstrId` - ID инструкции
- `EndToEndId` - End-to-end ID
- `TxId` - ID транзакции
- `UETR` - Unique End-to-end Transaction Reference
- `MndtId` - ID мандата
- `ChqNb` - Номер чека
- `ClrSysRef` - Ссылка клиринга

**Related Dates (RltdDts):**
- `AccptncDtTm` - Дата и время принятия
- `IntrBkSttlmDt` - Дата межбанковского расчета
- `TradDt` - Дата сделки
- `StartDt` - Дата начала
- `EndDt` - Дата окончания

### Отличия от camt.053

| Характеристика | camt.053 | camt.054 |
|----------------|----------|----------|
| Периодичность | Периодическая (дневная, еженедельная) | Немедленная, для каждой транзакции |
| Балансы | Включает начальный и конечный балансы | Не включает балансы |
| Детализация | Полная выписка за период | Одна или несколько транзакций |
| Использование | Отчетность, сверка | Оперативное информирование |

### Пример использования
```xml
<camt:Ntry>
  <camt:NtryRef>cmt054NtryRef001</camt:NtryRef>
  <camt:Amt Ccy="RON">591636</camt:Amt>
  <camt:CdtDbtInd>CRDT</camt:CdtDbtInd>
  <camt:Sts>
    <camt:Cd>BOOK</camt:Cd>
  </camt:Sts>
  <camt:BkTxCd>
    <camt:Domn>
      <camt:Cd>PMNT</camt:Cd>
      <camt:Fmly>
        <camt:Cd>RCDT</camt:Cd>
        <camt:SubFmlyCd>XBCT</camt:SubFmlyCd>
      </camt:Fmly>
    </camt:Domn>
  </camt:BkTxCd>
</camt:Ntry>
```

---

## camt.056 - FI to FI Payment Cancellation Request

### Назначение
Запрос от одного финансового института другому на отмену ранее отправленного платежа (pacs.008 или pacs.009). Используется когда отправитель обнаруживает ошибку или клиент запрашивает отмену.

### Структура сообщения

#### Корневой элемент
```xml
<camt:Document xmlns:camt="urn:iso:std:iso:20022:tech:xsd:camt.056.001.08">
  <camt:FIToFIPmtCxlReq>
    ...
  </camt:FIToFIPmtCxlReq>
</camt:Document>
```

#### 1. Assignment (Assgnmt) - Назначение

| Элемент | Тип | Описание | Обязательность |
|---------|-----|----------|----------------|
| `Id` | Text | Уникальный ID назначения | Обязательный |
| `Assgnr` | Party | Назначающая сторона (отправитель запроса) | Обязательный |
| `Assgne` | Party | Назначенная сторона (получатель запроса) | Обязательный |
| `CreDtTm` | DateTime | Дата и время создания | Обязательный |

**Party (Assgnr/Assgne):**
- `Pty/Nm` - Название стороны
- `Pty/PstlAdr` - Почтовый адрес
- `Pty/Id` - Идентификация
- `Agt/FinInstnId/BICFI` - BIC финансового института

#### 2. Case (Case) - Дело (опционально)

| Элемент | Тип | Описание |
|---------|-----|----------|
| `Id` | Text | ID дела |
| `Cretr` | Party | Создатель дела |

#### 3. Underlying (Undrlyg) - Базовая информация

##### Original Group Information (OrgnlGrpInf)

| Элемент | Тип | Описание | Обязательность |
|---------|-----|----------|----------------|
| `OrgnlMsgId` | Text | ID оригинального сообщения | Обязательный |
| `OrgnlMsgNmId` | Text | Название оригинального сообщения (например, "pacs.008.001.08") | Обязательный |
| `OrgnlCreDtTm` | DateTime | Дата создания оригинала | Опциональный |

##### Transaction Information (TxInf) - Список транзакций для отмены

| Элемент | Тип | Описание | Обязательность |
|---------|-----|----------|----------------|
| `CxlId` | Text | ID запроса на отмену | Опциональный |
| `OrgnlGrpInf` | Complex | Оригинальная групповая информация | Условно обязательный |
| `OrgnlInstrId` | Text | Оригинальный ID инструкции | Опциональный |
| `OrgnlEndToEndId` | Text | Оригинальный end-to-end ID | Опциональный |
| `OrgnlTxId` | Text | Оригинальный ID транзакции | Опциональный |
| `OrgnlUETR` | UUID | Оригинальный UETR | Опциональный |
| `OrgnlIntrBkSttlmAmt` | Amount + Ccy | Оригинальная сумма расчета | Обязательный |
| `OrgnlIntrBkSttlmDt` | Date | Оригинальная дата расчета | Опциональный |
| `Assgnr` | Party | Назначающая сторона | Опциональный |
| `Assgne` | Party | Назначенная сторона | Опциональный |
| `CxlRsnInf` | Complex | Информация о причине отмены | Опциональный |
| `OrgnlTxRef` | Complex | Ссылка на оригинальную транзакцию | Опциональный |

#### 4. Cancellation Reason Information (CxlRsnInf) - Информация о причине отмены

| Элемент | Тип | Описание | Обязательность |
|---------|-----|----------|----------------|
| `Orgtr` | Party | Инициатор отмены | Опциональный |
| `Rsn/Cd` | Code | Код причины отмены | Условно обязательный |
| `Rsn/Prtry` | Text | Проприетарный код причины | Альтернатива |
| `AddtlInf` | Text | Дополнительная информация | Опциональный |

**Коды причин отмены (Rsn/Cd):**
- `DUPL` - Duplicate Payment (дублирующий платеж)
- `FRAD` - Fraudulent Origin (мошенничество)
- `TECH` - Technical Problems (технические проблемы)
- `CUST` - Requested By Customer (запрошено клиентом)
- `CUTA` - Requested By Customer - Technical Problem (запрошено клиентом - технические проблемы)
- `UPAY` - Undue Payment (необоснованный платеж)
- `AM09` - Wrong Amount (неверная сумма)
- `AC03` - Invalid Creditor Account Number (неверный счет кредитора)
- `AC04` - Closed Account (закрытый счет)
- `AG01` - Transaction Forbidden (транзакция запрещена)
- `AG02` - Invalid Bank Operation Code (неверный операционный код банка)
- `AGNT` - Incorrect Agent (неверный агент)
- `CURR` - Incorrect Currency (неверная валюта)
- `FOCR` - Following Cancellation Request (следуя запросу на отмену)
- `LEGL` - Legal Decision (судебное решение)

#### 5. Original Transaction Reference (OrgnlTxRef) - Ссылка на оригинальную транзакцию

Содержит копию основных элементов из оригинального платежа:
- `IntrBkSttlmAmt` - Сумма
- `Dbtr` - Дебитор
- `DbtrAcct` - Счет дебитора
- `DbtrAgt` - Агент дебитора
- `CdtrAgt` - Агент кредитора
- `Cdtr` - Кредитор
- `CdtrAcct` - Счет кредитора

### Ответные сообщения

На camt.056 может быть отправлен один из ответов:
- **camt.029** - Resolution of Investigation (разрешение расследования)
  - Положительный ответ - отмена принята
  - Отрицательный ответ - отмена отклонена

### Пример использования
```xml
<camt:Undrlyg>
  <camt:TxInf>
    <camt:CxlId>CANCEL123456</camt:CxlId>
    <camt:OrgnlInstrId>pacs8bizmsgidr01</camt:OrgnlInstrId>
    <camt:OrgnlEndToEndId>E2E04044506271305</camt:OrgnlEndToEndId>
    <camt:OrgnlUETR>174c245f-2682-4291-ad67-2a41e530cd27</camt:OrgnlUETR>
    <camt:OrgnlIntrBkSttlmAmt Ccy="EUR">15000.00</camt:OrgnlIntrBkSttlmAmt>
    <camt:CxlRsnInf>
      <camt:Rsn>
        <camt:Cd>DUPL</camt:Cd>
      </camt:Rsn>
      <camt:AddtlInf>Duplicate payment detected</camt:AddtlInf>
    </camt:CxlRsnInf>
  </camt:TxInf>
</camt:Undrlyg>
```

---

## Общие коды и справочники

### Коды валют (ISO 4217)

Наиболее используемые:
- `EUR` - Euro
- `USD` - US Dollar
- `GBP` - British Pound
- `CHF` - Swiss Franc
- `JPY` - Japanese Yen
- `RON` - Romanian Leu
- `NOK` - Norwegian Krone
- `SEK` - Swedish Krona
- `DKK` - Danish Krone
- `PLN` - Polish Zloty
- `RUB` - Russian Ruble

### Коды стран (ISO 3166-1 alpha-2)

- `GB` - United Kingdom
- `RO` - Romania
- `BE` - Belgium
- `NO` - Norway
- `DE` - Germany
- `FR` - France
- `NL` - Netherlands
- `IT` - Italy
- `ES` - Spain
- `CH` - Switzerland

### Формат BIC (SWIFT) кода

Формат: `AAAABBCCXXX`
- `AAAA` - Код банка (4 буквы)
- `BB` - Код страны (ISO 3166-1)
- `CC` - Код местоположения (2 символа)
- `XXX` - Код филиала (опционально, 3 символа)

Примеры:
- `MYMBGB2LXXX` - Metro Bank, UK, London
- `INGBROBUXXX` - ING Bank, Romania, Bucharest
- `GEBABEBBXXX` - BNP Paribas Fortis, Belgium, Brussels

### Credit/Debit Indicator (Индикатор кредит/дебет)

- `CRDT` - Credit
  - В контексте счета: поступление средств, увеличение баланса
  - В контексте платежа: кредитовая транзакция
- `DBIT` - Debit
  - В контексте счета: списание средств, уменьшение баланса
  - В контексте платежа: дебетовая транзакция

### Коды назначения платежа (Purpose Codes)

Часто используемые коды (ExternalPurposeCode):
- `SALA` - Salary Payment (выплата зарплаты)
- `PENS` - Pension Payment (пенсионный платеж)
- `SUPP` - Supplier Payment (платеж поставщику)
- `TRAD` - Trade Settlement (торговый расчет)
- `CASH` - Cash Management Transfer (управление наличностью)
- `TREA` - Treasury Payment (казначейский платеж)
- `GOVT` - Government Payment (государственный платеж)
- `INTC` - Intra-Company Payment (внутрикорпоративный платеж)
- `LOAN` - Loan (кредит)
- `BONU` - Bonus Payment (бонусный платеж)
- `CBFF` - Capital Building (капитальное строительство)
- `DIVI` - Dividend (дивиденд)
- `CHAR` - Charity Payment (благотворительный платеж)

### Связь между сообщениями

#### Типичный платежный поток CBPR+:

1. **pacs.008** - Исходный платеж от банка A к банку B (клиентский платеж)
2. **pacs.009 (COV)** - Cover payment между банками-корреспондентами
3. **camt.054** - Уведомление банка B клиенту о зачислении
4. **camt.053** - Периодическая выписка с итогами операций
5. **camt.056** - Запрос на отмену (если необходимо)
6. **camt.029** - Ответ на запрос отмены

#### Диаграмма потока:

```
Debtor → Bank A → Intermediary Bank(s) → Bank B → Creditor
           ↓              ↓                   ↓         ↓
        pacs.008      pacs.009            camt.054  camt.053
                                              ↑
                                         (notification)
```

---

## Полезные ссылки

- **ISO 20022 Official**: https://www.iso20022.org/
- **SWIFT Standards**: https://www.swift.com/standards/iso-20022
- **ExternalCodeSets**: https://www.iso20022.org/external_code_list.page

---

## Примечания по версиям

Данная документация описывает версию **001.08** сообщений:
- `pacs.009.001.08`
- `camt.053.001.08`
- `camt.054.001.08`
- `camt.056.001.08`

Более новые версии могут содержать дополнительные поля и функциональность.

---

## Changelog

- **2025-10-13**: Первая версия документации

import logging
from datetime import datetime, timedelta
import pandas as pd
import requests
import asyncio
from apscheduler.schedulers.background import BackgroundScheduler
from web3 import Web3
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    CallbackContext,
    filters,
)

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Константы для состояний диалога
MIN_AMOUNT, NUM_TRANSACTIONS = range(2)

# Подключение к Ethereum node (Infura или локальный узел)
infura_url = "https://mainnet.infura.io/v3/YOUR_INFURA_PROJECT_ID"
web3 = Web3(Web3.HTTPProvider(infura_url))

# Проверка подключения к Infura
if not web3.is_connected():
    logger.error("Не удалось подключиться к Infura.")
else:
    logger.info("Успешное подключение к Infura.")

# Глобальные переменные для хранения транзакций
transactions_df = pd.DataFrame()
last_update_time = datetime.now()


# Функция для получения текущего курса ETH/USDT через API Binance
def get_eth_to_usdt_rate(max_retries: int = 3) -> float:
    url = "https://api.binance.com/api/v3/ticker/price?symbol=ETHUSDT"
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            if "price" in data:
                rate = float(data["price"])
                logger.info(f"Курс ETH/USDT получен: {rate}")
                return rate
            else:
                logger.warning(f"Неожиданный формат ответа от API: {data}")
                continue
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при запросе к API (попытка {attempt + 1}): {e}")
        except ValueError as e:
            logger.error(f"Ошибка при разборе JSON (попытка {attempt + 1}): {e}")
    logger.error("Не удалось получить курс ETH/USDT после нескольких попыток.")
    return None


# Функция для создания клавиатуры с кнопками "Перезапустить" и "Скачать файл"
def get_custom_keyboard():
    reply_keyboard = [["Перезапустить", "Скачать файл"]]
    return ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)


# Асинхронная функция для получения блока
async def fetch_block(block_num):
    try:
        block = web3.eth.get_block(block_num, full_transactions=True)
        logger.info(f"Блок {block_num} получен. Количество транзакций: {len(block.transactions)}")
        return block
    except Exception as e:
        logger.error(f"Ошибка при получении блока {block_num}: {e}")
        return None


# Асинхронная функция для получения транзакций за диапазон блоков
async def fetch_transactions(start_block, end_block, min_amount_eth):
    tasks = [fetch_block(block_num) for block_num in range(start_block, end_block + 1)]
    blocks = await asyncio.gather(*tasks)

    transactions = []
    for block in blocks:
        if block and block.transactions:
            for tx in block.transactions:
                value_eth = web3.fromWei(tx.value, 'ether')
                if value_eth >= min_amount_eth:
                    logger.info(f"Найдена транзакция: {tx.hash.hex()} на сумму {value_eth} ETH")
                    transactions.append({
                        'hash': tx.hash.hex(),
                        'from': tx['from'],
                        'to': tx['to'],
                        'value': value_eth,
                        'timestamp': datetime.fromtimestamp(block.timestamp)
                    })
    return transactions


# Функция для обновления транзакций
async def update_transactions(context: CallbackContext):
    global transactions_df, last_update_time

    # Получаем текущий блок и блок один день назад
    current_block = web3.eth.block_number
    blocks_per_day = 6500  # Примерное количество блоков в день
    block_one_day_ago = current_block - blocks_per_day

    # Получаем новые транзакции
    new_transactions = await fetch_transactions(block_one_day_ago, current_block, 0)  # 0 — минимальная сумма

    if new_transactions:
        # Преобразуем новые транзакции в DataFrame
        new_df = pd.DataFrame(new_transactions)

        # Объединяем с существующими транзакциями
        transactions_df = pd.concat([transactions_df, new_df]).drop_duplicates(subset=['hash'])

        # Удаляем транзакции старше трех дней
        three_days_ago = datetime.now() - timedelta(days=3)
        transactions_df = transactions_df[transactions_df['timestamp'] >= three_days_ago]

        # Сохраняем в файл
        transactions_df.to_excel('transactions.xlsx', index=False)

        last_update_time = datetime.now()
        logger.info(f"Транзакции обновлены. Всего транзакций: {len(transactions_df)}")
    else:
        logger.warning("Новых транзакций не найдено.")


# Функция для запуска обновления транзакций по расписанию
def start_scheduler(application):
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        update_transactions,
        'interval',
        hours=1,
        args=[application],
    )
    scheduler.start()


async def start(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text(
        "Привет! Я бот, который поможет тебе найти крупные транзакции в Ethereum.\n"
        "Введи минимальную сумму транзакции в USDT:",
        reply_markup=get_custom_keyboard(),
    )
    return MIN_AMOUNT


async def get_min_amount(update: Update, context: CallbackContext) -> int:
    if update.message.text == "Перезапустить":
        await update.message.reply_text(
            "Бот перезапущен. Введи минимальную сумму транзакции в USDT:",
            reply_markup=get_custom_keyboard(),
        )
        return MIN_AMOUNT

    try:
        min_amount_usdt = float(update.message.text)
        eth_to_usdt_rate = get_eth_to_usdt_rate()

        if eth_to_usdt_rate is None:
            await update.message.reply_text(
                "Не удалось получить курс ETH/USDT. Попробуйте позже.",
                reply_markup=get_custom_keyboard(),
            )
            return MIN_AMOUNT

        # Переводим USDT в ETH
        min_amount_eth = min_amount_usdt / eth_to_usdt_rate
        context.user_data['min_amount_eth'] = min_amount_eth

        await update.message.reply_text(
            f"Минимальная сумма установлена: {min_amount_usdt} USDT (~{min_amount_eth:.6f} ETH).\n"
            "Сколько транзакций вывести в Telegram?",
            reply_markup=get_custom_keyboard(),
        )
        return NUM_TRANSACTIONS
    except ValueError:
        await update.message.reply_text("Пожалуйста, введите корректное число.", reply_markup=get_custom_keyboard())
        return MIN_AMOUNT


async def get_transactions(update: Update, context: CallbackContext) -> int:
    if update.message.text == "Перезапустить":
        await update.message.reply_text(
            "Бот перезапущен. Введи минимальную сумму транзакции в USDT:",
            reply_markup=get_custom_keyboard(),
        )
        return MIN_AMOUNT

    if update.message.text == "Скачать файл":
        try:
            await update.message.reply_document(
                document=open('transactions.xlsx', 'rb'),
                reply_markup=get_custom_keyboard(),
            )
        except FileNotFoundError:
            await update.message.reply_text(
                "Файл с транзакциями не найден. Сначала выполните поиск транзакций.",
                reply_markup=get_custom_keyboard(),
            )
        return NUM_TRANSACTIONS

    try:
        num_transactions = int(update.message.text)
        min_amount_eth = context.user_data['min_amount_eth']

        # Фильтруем транзакции по минимальной сумме
        filtered_transactions = transactions_df[transactions_df['value'] >= min_amount_eth]

        # Сортируем транзакции по дате и величине
        filtered_transactions = filtered_transactions.sort_values(by=['timestamp', 'value'], ascending=[False, False])

        # Ограничиваем количество транзакций
        filtered_transactions = filtered_transactions.head(num_transactions)

        # Отправляем первые транзакции в Telegram
        for _, tx in filtered_transactions.iterrows():
            await update.message.reply_text(
                f"Hash: {tx['hash']}\n"
                f"From: {tx['from']}\n"
                f"To: {tx['to']}\n"
                f"Value: {tx['value']:.6f} ETH\n"
                f"Timestamp: {tx['timestamp']}\n",
                reply_markup=get_custom_keyboard(),
            )

        await update.message.reply_text("Хотите перезапустить бота или скачать файл?",
                                        reply_markup=get_custom_keyboard())

        return ConversationHandler.END
    except ValueError:
        await update.message.reply_text("Пожалуйста, введите корректное число.", reply_markup=get_custom_keyboard())
        return NUM_TRANSACTIONS


async def cancel(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("Операция отменена.", reply_markup=get_custom_keyboard())
    return ConversationHandler.END


def main() -> None:
    # Вставьте сюда ваш токен
    application = Application.builder().token("7032048660:AAG6EUeYuo5snQgyz9jdFQBpie7wWUy7qgw").build()

    # Запускаем планировщик для обновления транзакций
    start_scheduler(application)

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            MIN_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_min_amount)],
            NUM_TRANSACTIONS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_transactions)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    application.add_handler(conv_handler)

    application.run_polling()


if __name__ == '__main__':
    main()
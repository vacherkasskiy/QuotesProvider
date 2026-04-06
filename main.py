import logging

import telebot

from config import TOKEN
from extensions import APIException, CurrencyConverter


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

if not logger.handlers:
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)s | %(name)s | %(message)s'
    )

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)


bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start', 'help'])
def send_help(message: telebot.types.Message):
    logger.info(
        'команда help/start | user_id=%s | username=%s | chat_id=%s',
        message.from_user.id,
        message.from_user.username,
        message.chat.id
    )

    text = (
        'чтобы узнать стоимость валюты, отправьте сообщение в формате:\n'
        '<имя валюты> <в какой валюте узнать цену> <количество>\n\n'
        'можно вводить как русские названия, так и коды:\n'
        'доллар рубль 10\n'
        'USD RUB 10\n'
        'евро доллар 1\n'
        'EUR USD 1\n\n'
        'доступные команды:\n'
        '/help — инструкция\n'
        '/values — список доступных валют'
    )
    bot.reply_to(message, text)


@bot.message_handler(commands=['values'])
def send_values(message: telebot.types.Message):
    logger.info(
        'команда values | user_id=%s | username=%s | chat_id=%s',
        message.from_user.id,
        message.from_user.username,
        message.chat.id
    )

    text = (
        'доступные валюты:\n'
        '- евро (EUR)\n'
        '- доллар (USD)\n'
        '- рубль (RUB)'
    )
    bot.reply_to(message, text)


@bot.message_handler(content_types=['text'])
def convert_currency(message: telebot.types.Message):
    logger.info(
        'входящее сообщение | user_id=%s | username=%s | chat_id=%s | text=%s',
        message.from_user.id,
        message.from_user.username,
        message.chat.id,
        message.text
    )

    try:
        values = message.text.split()

        if len(values) != 3:
            raise APIException(
                'неверное количество параметров.\n'
                'нужно вводить так:\n'
                '<имя валюты> <в какой валюте узнать цену> <количество>'
            )

        base, quote, amount = values
        total_price = CurrencyConverter.get_price(base, quote, amount)

    except APIException as e:
        logger.warning(
            'ошибка пользователя | user_id=%s | username=%s | chat_id=%s | text=%s | error=%s',
            message.from_user.id,
            message.from_user.username,
            message.chat.id,
            message.text,
            str(e)
        )
        bot.reply_to(message, f'ошибка пользователя.\n{type(e).__name__}: {e}')

    except Exception:
        logger.exception(
            'непредвиденная ошибка | user_id=%s | username=%s | chat_id=%s | text=%s',
            message.from_user.id,
            message.from_user.username,
            message.chat.id,
            message.text
        )
        bot.reply_to(message, 'не удалось обработать команду.')

    else:
        logger.info(
            'успешная конвертация | user_id=%s | username=%s | chat_id=%s | base=%s | quote=%s | amount=%s | result=%.4f',
            message.from_user.id,
            message.from_user.username,
            message.chat.id,
            base,
            quote,
            amount,
            total_price
        )

        text = f'цена {amount} {base} в {quote} — {total_price:.4f}'
        bot.send_message(message.chat.id, text)


if __name__ == '__main__':
    logger.info('бот запущен')
    try:
        bot.polling(none_stop=True)
    except Exception:
        logger.exception('критическая ошибка при запуске polling')
        raise
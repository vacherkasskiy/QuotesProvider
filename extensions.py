import json
import requests


class APIException(Exception):
    pass


class CurrencyConverter:
    currencies = {
        'евро': 'EUR',
        'доллар': 'USD',
        'рубль': 'RUB',
        'eur': 'EUR',
        'usd': 'USD',
        'rub': 'RUB',
    }

    @staticmethod
    def normalize_currency(currency: str) -> str:
        key = currency.strip().lower()

        try:
            return CurrencyConverter.currencies[key]
        except KeyError:
            raise APIException(f'не удалось обработать валюту "{currency}"')

    @staticmethod
    def get_price(base: str, quote: str, amount: str) -> float:
        base_ticker = CurrencyConverter.normalize_currency(base)
        quote_ticker = CurrencyConverter.normalize_currency(quote)

        if base_ticker == quote_ticker:
            raise APIException(f'нельзя переводить одинаковые валюты: {base}')

        try:
            amount_value = float(amount)
        except ValueError:
            raise APIException(f'не удалось обработать количество "{amount}"')

        if amount_value <= 0:
            raise APIException('количество валюты должно быть больше нуля')

        response = requests.get(
            'https://api.frankfurter.dev/v2/rates',
            params={
                'base': base_ticker,
                'quotes': quote_ticker,
            },
            timeout=10
        )

        if response.status_code != 200:
            raise APIException(
                f'не удалось получить данные от сервиса валют. '
                f'код ответа: {response.status_code}. '
                f'ответ: {response.text}'
            )

        data = json.loads(response.text)

        if not isinstance(data, list) or len(data) == 0:
            raise APIException('сервис валют вернул пустой или некорректный ответ')

        rate_info = data[0]

        if 'rate' not in rate_info:
            raise APIException('в ответе сервиса отсутствует поле rate')

        rate = float(rate_info['rate'])
        return rate * amount_value
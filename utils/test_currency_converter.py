# from forex_python.converter import CurrencyRates
# c = CurrencyRates()
# print(c.get_rates("USD"))
# # c.convert("USD", "INR", 10)


from currency_converter import CurrencyConverter
from datetime import date

c = CurrencyConverter()
val = c.convert(1, 'USD', 'IDR', date=date(2022, 3, 31))
print(val)
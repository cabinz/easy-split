from easysplit.exr import ExchangeRates


exrs = ExchangeRates(std_currency="HKD")
exrs.add_rate("USD", "HKD", 7.8)
print("USD to HKD: ", exrs.get_rate("USD", "HKD"))

res = exrs.to_std("USD", 100)
print("100 USD to std (HKD): ", exrs.to_std("USD", 100))
print("Convert back to USD", exrs.get_rate("HKD", "USD") * res)

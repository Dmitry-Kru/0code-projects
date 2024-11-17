class Store:
    def __init__(self, name, address, items={}):
        self.name = name
        self.address = address
        self.items = items

    def add_item(self, product, price):
        self.items[product] = price
        print(f'Добавили в магазин "{self.name}" товар "{product}" по цене {price}')

    def del_item(self, product):
        del self.items[product]
        print(f'Удален из магазина "{self.name}" товар "{product}"')

    def price_item(self, product):
        try:
            print(f'Цена товара "{product}" в магаине "{self.name}" - {self.items[product]}')
        except:
            print(None)

    def change_price(self, product, price):
        self.items[product] = price
        print(f'Новая цена товара "{product}" в магазине "{self.name}" - {price}')


store_1 = Store('Кренделёк', 'Гороховая, 14')
store_2 = Store('Молочник', 'Бобовая, 4')
store_3 = Store('Пармезанчик', 'Стручковая, 1')
store_1.add_item('Батон', 80)
store_1.add_item('Хлеб ржаной', 70)
store_1.add_item('Круассан', 40)
store_2.add_item('Молоко, 1л', 100)
store_2.add_item('Кефир, 1л', 120)
store_2.add_item('Сметана, 200г', 110)
store_3.add_item('Сыр Российский, 1кг', 740)
store_3.add_item('Сыр Пошехонский, 1 кг', 840)
store_3.add_item('Сыр Литовский, 1кг', 1040)
print()
store_1.del_item('Батон')
store_1.price_item('Круассан')
store_1.price_item('Сметана')
store_1.change_price('Круассан', 50)

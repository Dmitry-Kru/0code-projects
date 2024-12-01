class User:
    def __init__(self, id, name, access='user'):
        self.__id = id
        self.__name = name
        self.__access = access

    def get_id(self):
        return self.__id

    def get_name(self):
        return self.__name

    def get_access(self):
        return self.__access

    def set_access(self):
        self.__access = 'admin'

class Admin(User):
    def __init__(self, id, name):
        super().__init__(id, name, 'admin')

    def add_user(self, user_list, user):
        user_list.append(user)
        print(f'Пользователь "{user.get_name()}" добавлен.')

    def remove_user(self, user_list, user_id):
        for user in user_list:
            if user.get_id() == user_id:
                user_list.remove(user)
                print(f'Пользователь "{user.get_name()}" удален.')
                return
        print(f'Пользователь с ID {user_id} не найден.')

users = []
# Создаем администратора
admin1 = Admin(12345, 'Админ Вася')
users.append(admin1)
# Создаем обычных пользователей
user1 = User(1, "Маша")
user2 = User(2, "Катя")
user3 = User(3, "Петя")
user4 = User(4, "Сережа")
# Админ добавляет пользователей
admin1.add_user(users, user1)
admin1.add_user(users, user2)
admin1.add_user(users, user3)
admin1.add_user(users, user4)

# Проверяем список пользователей
for user in users:
    print(f'ID пользователя: {user.get_id()}, '
          f'имя: {user.get_name()}, '
          f'доступ: {user.get_access()}')
print()
# Администратор удаляет пользователя
admin1.remove_user(users, 1)
admin1.remove_user(users, 5)
print()
# Проверяем список пользователей
for user in users:
    print(f'ID пользователя: {user.get_id()}, '
          f'имя: {user.get_name()}, '
          f'доступ: {user.get_access()}')





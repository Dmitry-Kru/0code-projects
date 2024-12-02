from abc import ABC, abstractmethod

class Weapon(ABC):
    @abstractmethod
    def attack(self):
        pass

class Sword(Weapon):
    def attack(self):
        return "Боец наносит удар мечом."

class Bow(Weapon):
    def attack(self):
        return "Боец стреляет из лука."

class Monster:
    def __init__(self, name):
        self.name = name
        self.is_alive = True

    def defeat(self):
        self.is_alive = False
        print(f"{self.name} побежден!")

class Fighter:
    def __init__(self, name):
        self.name = name
        self.weapon = None

    def change_weapon(self, weapon: Weapon):
        self.weapon = weapon
        print(f"{self.name} выбирает {self.weapon.__class__.__name__.lower()}.")

    def attack_monster(self, monster: Monster):
        if self.weapon:
            print(self.weapon.attack())
            monster.defeat()
        else:
            print(f"У {self.name} нет оружия!")

# Создаем бойца и монстра
fighter = Fighter("Артур")
monster = Monster("Дракон")

# Боец выбирает меч
sword = Sword()
fighter.change_weapon(sword)
fighter.attack_monster(monster)

# Создаем нового монстра
monster = Monster("Тролль")

# Боец выбирает лук
bow = Bow()
fighter.change_weapon(bow)
fighter.attack_monster(monster)

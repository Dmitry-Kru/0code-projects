import random

class Hero:
    def __init__(self, name, health=100, attack_power=20):
        self.name = name
        self.health = health
        self.attack_power = attack_power

    def attack(self, other):
        other.health -= self.attack_power
        print(f"{self.name} атакует {other.name} и наносит {self.attack_power} урона!")
        print(f"{other.name} здоровье: {other.health}")

    def is_alive(self):
        return self.health > 0


class Game:
    def __init__(self, player_name):
        self.player = Hero(player_name)
        self.computer = Hero("Компьютер", attack_power=random.randint(15, 25))

    def start(self):
        print("Игра началась!")
        while self.player.is_alive() and self.computer.is_alive():
            self.player_turn()
            if self.computer.is_alive():
                self.computer_turn()

        self.end_game()

    def player_turn(self):
        self.player.attack(self.computer)

    def computer_turn(self):
        self.computer.attack(self.player)

    def end_game(self):
        if self.player.is_alive():
            print(f"{self.player.name} победил!")
        else:
            print(f"{self.computer.name} победил!")



player_name = input("Введите имя вашего героя: ")
game = Game(player_name)
game.start()
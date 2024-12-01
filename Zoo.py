class Animal:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def make_sound(self):
        return "Звук {self.name}"

    def eat(self):
        return f"{self.name} кого-то или что-то ест"


class Bird(Animal):
    def make_sound(self):
        return "Ку-ку"


class Mammal(Animal):
    def make_sound(self):
        return "Муррр"


class Reptile(Animal):
    def make_sound(self):
        return "Шшшш"


def animal_sound(animals):
    for animal in animals:
        print(f"{animal.name}: '{animal.make_sound()}'")


class Zoo:
    def __init__(self):
        self.animals = []
        self.staff = []

    def add_animal(self, animal):
        self.animals.append(animal)

    def add_staff(self, staff_member):
        self.staff.append(staff_member)

    def save_to_file(self, filename):
        with open(filename, 'w') as f:
            f.write("Зверушки:\n")
            for animal in self.animals:
                f.write(f"{animal.__class__.__name__},{animal.name},{animal.age}\n")

            f.write("Персонал:\n")
            for staff_member in self.staff:
                f.write(f"{staff_member.__class__.__name__},{staff_member.name}\n")

    def load_from_file(self, filename):
        with open(filename, 'r') as f:
            lines = f.readlines()
            section = None
            for line in lines:
                line = line.strip()
                if line == "Зверушки:":
                    section = "animals"
                    continue
                elif line == "Персонал:":
                    section = "staff"
                    continue

            if section == "animals":
                animal_data = line.split(',')
                if animal_data[0] == 'Bird':
                    animal = Bird(animal_data[1], int(animal_data[2]))
                elif animal_data[0] == 'Mammal':
                    animal = Mammal(animal_data[1], int(animal_data[2]))
                elif animal_data[0] == 'Reptile':
                    animal = Reptile(animal_data[1], int(animal_data[2]))
                self.add_animal(animal)
            elif section == "staff":
                staff_data = line.split(',')
                if staff_data[0] == 'ZooKeeper':
                    man = ZooKeeper(staff_data[1])
                elif staff_data[0] == 'Veterinarian':
                    man = Veterinarian(staff_data[1])
                self.add_staff(man)


class ZooKeeper:
    def __init__(self, name):
        self.name = name

    def feed_animal(self, animal):
        return f"{self.name} кормит {animal.name}."


class Veterinarian:
    def __init__(self, name):
        self.name = name

    def heal_animal(self, animal):
        return f"{self.name} лечит {animal.name}."


zoo = Zoo()

# Добавляем животных
bird = Bird("воробей", 2)
mammal = Mammal("шимпанзе", 5)
reptile = Reptile("черепаха", 3)

zoo.add_animal(bird)
zoo.add_animal(mammal)
zoo.add_animal(reptile)

# Добавляем сотрудников
zookeeper = ZooKeeper("Маша")
veterinarian = Veterinarian("Вася")

zoo.add_staff(zookeeper)
zoo.add_staff(veterinarian)

# Демонстрируем полиморфизм
animal_sound(zoo.animals)

# Сохраняем состояние зоопарка
zoo.save_to_file('zoo_data.txt')

# Загружаем состояние зоопарка
new_zoo = Zoo()
new_zoo.load_from_file('zoo_data.txt')

# Проверяем загруженные данные
animal_sound(new_zoo.animals)

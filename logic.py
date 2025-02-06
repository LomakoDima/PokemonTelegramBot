# logic.py <--- Author: DimaLab, License: MIT ---->
from random import randint
import requests
from datetime import datetime, timedelta


class Pokemon:
    pokemons = {}  # { username : pokemon}

    # Инициализация объекта (конструктор)
    def __init__(self, pokemon_trainer):

        self.pokemon_trainer = pokemon_trainer

        self.last_time = datetime.now()

        self.pokemon_number = randint(1, 1000)
        self.img = self.get_img()
        self.name = self.get_name()

        self.power = randint(30, 60)
        self.hp = randint(200, 400)

        self.hunger = 100

        self.last_training = datetime.now() - timedelta(days=1)

        Pokemon.pokemons[pokemon_trainer] = self

    # Метод для получения картинки покемона через API
    def get_img(self):
        url = f'https://pokeapi.co/api/v2/pokemon/{self.pokemon_number}'
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return (data['sprites']["other"]['official-artwork']["front_default"])
        else:
            return "https://static.wikia.nocookie.net/anime-characters-fight/images/7/77/Pikachu.png/revision/latest/scale-to-width-down/700?cb=20181021155144&path-prefix=ru"

    # Метод для получения имени покемона через API
    def get_name(self):
        url = f'https://pokeapi.co/api/v2/pokemon/{self.pokemon_number}'
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return (data['forms'][0]['name'])
        else:
            return "Pikachu"

    # Метод класса для получения информации
    def info(self):
        return f"""Имя твоего покеомона: {self.name}
Cила покемона: {self.power}
Здоровье покемона: {self.hp}"""

    # Метод класса для получения картинки покемона
    def show_img(self):
        return self.img

    def attack(self, enemy):
        if isinstance(enemy, Wizard):
            chance = randint(1, 5)
            if chance == 1:
                return "Покемон-волшебник применил щит в сражении"
        if enemy.hp > self.power:
            enemy.hp -= self.power
            return f"""Сражение @{self.pokemon_trainer} с @{enemy.pokemon_trainer}
Здоровье @{enemy.pokemon_trainer} теперь {enemy.hp}"""
        else:
            enemy.hp = 0
            return f"Победа @{self.pokemon_trainer} над @{enemy.pokemon_trainer}! "

    def feed(self, feed_interval=20, hunger_increase=10):
        current_time = datetime.now()
        delta_time = timedelta(seconds=feed_interval)

        if self.hunger >= 100:
            return "Покемон уже сыт и не хочет есть!"

        if (current_time - self.last_time) > delta_time:
            self.hunger = min(100, self.hunger + hunger_increase)  # Увеличиваем сытость, но не превышаем 100
            self.last_time = current_time
            return f"Сытость покемона восстановлена. Текущая сытость: {self.hunger}"
        else:
            remaining_time = (self.last_time + delta_time - current_time).total_seconds()
            minutes = int(remaining_time // 60)
            seconds = int(remaining_time % 60)
            return f"Следующее кормление можно будет через {minutes} минут {seconds} секунд."


class Wizard(Pokemon):
    """Подкласс Pokemon, представляющий покемона-волшебника."""
    def feed(self):
        return super().feed(feed_interval=10)

    def info(self):
        """Возвращает информацию о покемоне-волшебнике."""
        return "У тебя покемон-волшебник \n\n" + super().info()


class Fighter(Pokemon):
    def attack(self, enemy):
        super_power = randint(5, 15)
        self.power += super_power
        result = super().attack(enemy)
        self.power -= super_power
        return result + f"\nБоец применил супер-атаку силой:{super_power} "

    def info(self):
        """Возвращает информацию о покемоне-бойце."""
        return "У тебя покемон-боец \n\n" + super().info()

    def feed(self):
        return super().feed(feed_interval=10)


# class *Какой то покемон*:


wizard = Wizard("username1")
fighter = Fighter("username2")

# Выводим информацию о покемонах
print(wizard.info())
print("#" * 10)
print(fighter.info())
print("#" * 10)

# Проводим сражение между покемонами
print(wizard.attack(fighter))
print(fighter.attack(wizard))




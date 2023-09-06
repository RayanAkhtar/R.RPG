# ------------------------------------------------------------------  Setup  -------------------------------------------
import sqlite3
import random
from math import floor

positive_responses = ['yes', 'y', 'ya', 'yep', 'sure']
negative_responses = ['no', 'n', 'na', 'nah', 'nope']
response_list = positive_responses + negative_responses

# ----------------------------------------------------------------   Extra Additions ------------------------------------

class Colours:  # Will be used to create coloured text
    def __init__(self):
        self.colour_dictionary = self.get_colour_dictionary()

    @staticmethod
    def get_colour_dictionary():
        dictionary = {
            "defeated": "9;31m",  # This will produce a streak through the enemy name, indicating that they are dead
            "red": "38;5;1m",  # This will be used for hp and fire status
            "dark green": "38;5;2m",
            "orange": "38;5;3m",
            "blue": "38;5;4m",
            "purple": "38;5;5m",
            "lime": "38;5;46m",
            "light blue": "38;5;14m",
            "dark blue": "38;5;17m",
            "light purple": "38;5;93m",
            "yellow": "38;5;190m",
            "dark yellow": "38;5;142m",
            "pink": "38;5;199m",
            "None": "1m",
            "dark red": "38;5;88m",
            "dark purple": "38;5;53m",
            "teal": "38;5;49m",
            "underline": "1;4m"
        }
        return dictionary

    def return_colour_text(self, colour, text):
        colour = self.colour_dictionary[colour]
        return f"\033[{colour}{text}\033[0;0m"

    def return_multiple_colour(self, colour, array):
        colour = self.colour_dictionary[colour]
        string = ','.join(self.return_colour_text(colour, *array))
        return string

    def effect_colour(self, status_effect_name):
        dictionary = {
            "burn": "red",
            "wet": "teal",
            "jolt": "pink",
            "chill": "blue",
            "dark": "purple",
            "light": "yellow",
            "shock": "dark yellow",
            "backfire": "dark red",
            "freeze": "light blue",
            "holy fire": "orange",
            "dark flame": "dark purple",
            "heal percentage atk": "dark green",
            "heal percentage hp": "dark green",
            "drain_atk": "dark red",
            "mana": "dark blue",
            "hp": "dark red",
            "aoe": "red",
            "aggro": "orange"
        }
        if status_effect_name in dictionary:
            colour = dictionary[status_effect_name]
            return self.return_colour_text(colour, status_effect_name.title())
        else:
            return status_effect_name.title()

# ----------------------------------------------------------------  Database Setup  ------------------------------------


connection = sqlite3.connect('RPG_game_file_database')
cursor = connection.cursor()

# Creating the user table, decided to remove the one-to-one relationships in the previous database
cursor.execute('''
            CREATE TABLE IF NOT EXISTS USER
            (user_id INTEGER PRIMARY KEY, 
            save_file_name TEXT, 
            lvl INTEGER DEFAULT 0,
            exp INTEGER DEFAULT 0,
            gold INTEGER DEFAULT 0,
            pvp_games_won DEFAULT 0,
            games_played INTEGER DEFAULT 0,
            games_won INTEGER DEFAULT 0,
            games_fled INTEGER DEFAULT 0,
            games_lost INTEGER DEFAULT 0,
            enemies_defeated INTEGER DEFAULT 0,
            bosses_defeated INTEGER DEFAULT 0,
            potions_used INTEGER DEFAULT 0,
            lesser_hp_potion INTEGER DEFAULT 0, 
            medium_hp_potion INTEGER DEFAULT 0,
            grand_hp_potion INTEGER DEFAULT 0,
            ph_atk_potion INTEGER DEFAULT 0,
            ph_def_potion INTEGER DEFAULT 0,
            sp_atk_potion INTEGER DEFAULT 0,
            sp_def_potion INTEGER DEFAULT 0, 
            crit_chance_potion INTEGER DEFAULT 0,
            crit_damage_potion INTEGER DEFAULT 0
            )''')

# Creating the teams table, creating a relationship between the user id from both tables
cursor.execute('''
            CREATE TABLE IF NOT EXISTS TEAMS
            (team_id INTEGER PRIMARY KEY,
            user_id INTEGER,
            hero_id_1 INTEGER,
            hero_id_2 INTEGER,
            hero_id_3 INTEGER,
            hero_id_4 INTEGER,
            hero_id_5 INTEGER,
            hero_id_6 INTEGER,
            FOREIGN KEY (user_id) REFERENCES USER (user_id))''')

# Creating the heroes table, decided to shift them together and make user_id = None when they are built in
cursor.execute('''
            CREATE TABLE IF NOT EXISTS HEROES
            (hero_id INTEGER PRIMARY KEY,
            user_id INTEGER,
            hero_name TEXT,
            hp TEXT,
            ph_atk TEXT, 
            ph_def TEXT, 
            sp_atk TEXT, 
            sp_def TEXT, 
            crit_rate TEXT, 
            crit_damage TEXT,
            FOREIGN KEY (user_id) REFERENCES USER (user_id))''')

# Creating the status effects table
cursor.execute('''
            CREATE TABLE IF NOT EXISTS STATUS_EFFECTS
            (status_id INTEGER PRIMARY KEY,
            status_name TEXT,
            status_description TEXT,
            status_effect_1 TEXT,
            status_effect_1_percentage INTEGER,
            status_effect_2 TEXT,
            status_effect_2_percentage INTEGER,
            duration INTEGER DEFAULT 0,
            condition_1 TEXT,
            condition_2 TEXT
            )''')  # Condition refers to the two effects combined to make that special attack

# Creating the special attack table, this will store the built in special attacks
cursor.execute('''
            CREATE TABLE IF NOT EXISTS SP_ATK
            (sp_atk_id INTEGER PRIMARY KEY,
            sp_atk_name TEXT,
            sp_atk_percentage INTEGER,
            sp_atk_duration INTEGER,
            status_id INTEGER,
            mana_cost INTEGER,
            FOREIGN KEY (status_id) REFERENCES STATUS_EFFECTS (status_id))''')

# Creates the relationship between heroes and special attack in order to resolve a many-to-many relationship
cursor.execute('''
            CREATE TABLE IF NOT EXISTS HEROES_SP_ATK
            (hero_id INTEGER,
            sp_atk_id INTEGER,
            FOREIGN KEY (hero_id) REFERENCES HEROES (hero_id),
            FOREIGN KEY (sp_atk_id) REFERENCES SP_ATK (sp_atk_id))''')

# Creates the monsters table
cursor.execute('''
            CREATE TABLE IF NOT EXISTS MONSTERS
            (monster_id INTEGER PRIMARY KEY,
            enemy_name TEXT,
            enemy_type TEXT,
            hp TEXT,
            ph_atk TEXT, 
            ph_def TEXT,
            sp_atk TEXT,
            sp_def TEXT,
            gold INTEGER,
            exp INTEGER)''')

# Creates the shop_prices table, stores general data about items
cursor.execute('''
            CREATE TABLE IF NOT EXISTS SHOP_PRICES
            (item_id INTEGER PRIMARY KEY,
            item_name TEXT,
            price INTEGER,
            description TEXT)''')

# Creates the POTIONS table to store the data for potions that will be used in battle
cursor.execute('''
            CREATE TABLE IF NOT EXISTS POTIONS
            (item_id INTEGER PRIMARY KEY,
            item_name TEXT,
            percentage INTEGER,
            stat TEXT,
            duration INTEGER)''')

connection = sqlite3.connect('RPG_game_file_database')
cursor = connection.cursor()

query = cursor.execute("SELECT * FROM HEROES")  # A check to see if data exists in the database
if not query.fetchall():  # if data is already made, nothing will happen
    # This section will create some fake users to test, this will be deleted towards the end of this project
    records = [('save_1', 3000, 21, 2300000),
               ('save_2', 23, 45, 54),
               ('save_3', 45, 43, 32)]  # Some template user data
    insert = """INSERT INTO USER (save_file_name, lvl, exp, gold)
                VALUES (?, ?, ?, ?)"""
    cursor.executemany(insert, [i for i in records])

    # This section will create the built-in status effects
    description = {
        # Status effects
        "wet": 'Inflicts the target the "wet" status, 10% chance for the affected entity to miss their attack.',
        "jolt": 'Inflicts the target the "jolt" status, 5% chance to miss an attack and the target loses 2.5% hp'
                ' each turn.',
        "burn": 'Inflicts the target with the "burn" status, target loses 5% hp per turn and will also have their '
                'physical attack lowered by 5%.',
        "chill": 'Inflicts the target with the "chill" status, target loses 5% hp per turn and will also '
                 'have their physical defence lowered by 5%.',
        "dark": 'Inflicts the target with the "dark" status, target will have a 50% chance to miss an attack, however, '
                'they will have an increased 50% physical attack.',
        "light": 'Inflicts the target with the "light "status, the target will have a 50% chance to miss an attack, '
                 'however they will have an increased 50% special attack.',
        "shock": 'Inflicts the target with the "shock" status, user loses 5% hp per turn and there is also a 25% '
                 'chance for them to miss an attack.',
        "backfire": 'This status will be applied if the user attempts to attack while under jolt and fire, there will '
                    'be a 30% chance of taking 50% of attack as damage. If avoided, there is a 10% chance of dealing '
                    '200% of you attack to all enemies',
        "freeze": 'This status will be applied when chill + wet statuses are applied to the target, the frozen target '
                  'will not be able to attack for 4 turns and also take 50% extra damage from enemy attacks',
        "holy_fire": 'This status will be applied when the light + burn statuses are applied to a target, all of their '
                     'attacks will have a 20% chance to deal double damage. They will also lose 15% hp per turn',
        "dark_flame": 'This status will be applied when light + burn statuses are applied to a target, all of their '
                      'attacks will have a 10% chance to instantly kill their target, however, they will '
                      'lose 30% hp per turn.',
        # Heal effect
        "heal_percentage": "The selected entity will be healed based on certain factors",
        # Drain effect
        "drain_atk": "The selected entity will be healed for 30% of their damage dealt to the enemy",
        # Aoe effect
        "aoe": "Damage worth 100% of special attack will be dealt to all enemies",
        # Aggro effect
        "aggro": "Deals some damage to the enemy and focuses the enemies attention to the attacker"
    }
    records = [
        # Numbers refer to the effect if in the database
        # Status effects
        ("wet", description["wet"], "miss", 10, None, None, None, None),  # 1
        ("jolt", description["jolt"], "miss", 5, "damage", 2, None, None),  # 2
        ("burn", description["burn"], "damage", 5, "ph_atk_down", 5, None, None),  # 3
        ("chill", description["chill"], "damage", 5, "ph_def_down", 5, None, None),  # 4
        ("dark", description["dark"], "miss", 50, "ph_atk_up", 150, None, None),  # 5
        ("light", description["light"], "miss", 50, "sp_atk_up", 150, None, None),  # 6
        ("shock", description["shock"], "miss", 25, "damage", 5, "wet", "jolt"),  # 7
        ("backfire", description["backfire"], "damage", 50, "aoe", 200, "jolt", "burn"),  # 8
        ("freeze", description["freeze"], "miss", 100, "ph_def_down", 50, "chill", "wet"),  # 9
        ("holy fire", description["holy_fire"], "double_dmg", 20, "damage", 15, "light", "burn"),  # 10
        ("dark flame", description["dark_flame"], "instakill", 1000000, "damage", 30, "dark", "burn"),  # 11

        # Healing effects
        ("heal percentage hp", description["heal_percentage"], "heal_percentage", 20, None, None, None, None),  # 12
        ("heal percentage atk", description["heal_percentage"], "heal_percentage", 30, None, None, None, None),  # 13

        # Draining effects
        ("drain_atk", description["drain_atk"], "drain_atk", 10, None, None, None, None),  # 14

        # Aoe effects
        ("aoe", description["aoe"], "aoe", 100, None, None, None, None),  # 15

        # Aggro effects
        ("aggro", description["aggro"], "aggro", 100, None, None, None, None)  # 16
    ]
    insert = """INSERT INTO STATUS_EFFECTS (status_name, status_description, status_effect_1, 
    status_effect_1_percentage, status_effect_2, status_effect_2_percentage, condition_1, condition_2)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)"""
    cursor.executemany(insert, [i for i in records])

    # This section will create the built-in special attacks
    records = [('Fire Strike', 120, 3, 3, 50),
               ('Frost Strike', 110, 3, 4, 40),
               ('Fire Ball', 130, 2, 3, 50),
               ('Frost Ball', 120, 2, 4, 50),
               ('Lightning Strike', 150, 2, 2, 50),
               ('Thunder Bolt', 130, 3, 2, 40),
               ('Rain Slash', 120, 4, 1, 30),
               ('Blinding Light', 150, 2, 6, 50),
               ('Holy Smash', 130, 3, 6, 30),
               ('Dark Ball', 120, 2, 5, 50),
               ('Dark Slash', 110, 3, 5, 30),
               ('Heal', 100, 1, 13, 30),
               ('Soul Siphon', 130, 1, 14, 50),
               ('Life Steal', 120, 1, 14, 50),
               ('Electricute', 130, 3, 2, 50),
               ('Hellish Fire', 160, 3, 3, 40),
               ('Frozen Winds', 150, 3, 4, 60),
               ('Corrupt', 140, 2, 5, 50),
               ('Water Ball', 120, 3, 1, 30),
               ('Purify', 120, 2, 6, 30),
               ('Frost Arrow', 150, 3, 4, 50),
               ('Flaming Arrow', 130, 2, 3, 40),
               ('Holy Arrow', 160, 3, 6, 50),
               ('Corrupt Arrow', 130, 2, 5, 40),
               ('Heal', 10, 3, 12, 30),
               ('Explode', 100, 1, 15, 40),
               ('Taunt', 130, 3, 16, 50)
               ]
    insert = """INSERT INTO SP_ATK (sp_atk_name, sp_atk_percentage, sp_atk_duration, status_id, mana_cost)
                VALUES (?, ?, ?, ?, ?)"""
    cursor.executemany(insert, [i for i in records])

    # This section will create the built-in Heroes
    records = [('0', 'Knight 1', 'v high', 'high', 'e low', 'low', 'medium', 5, 150),
               ('0', 'Knight 2', 'high', 'high', 'medium', 'medium', 'e low', 5, 150),
               ('0', 'Knight 3', 'high', 'high', 'high', 'medium', 'medium', 5, 150),
               ('0', 'Knight 4', 'v high', 'high', 'high', 'medium', 'medium', 5, 150),
               ('0', 'Knight 5', 'medium', 'high', 'high', 'medium', 'e low', 5, 150),
               ('0', 'Archer 1', 'low', 'high', 'high', 'medium', 'medium', 5, 150),
               ('0', 'Archer 2', 'medium', 'high', 'high', 'medium', 'e low', 5, 150),
               ('0', 'Archer 3', 'low', 'high', 'high', 'medium', 'medium', 5, 150),
               ('0', 'Archer 4', 'e high', 'high', 'high', 'medium', 'medium', 5, 150),
               ('0', 'Archer 5', 'low', 'high', 'medium', 'high', 'e low', 5, 150),
               ('0', 'Wizard 1', 'high', 'high', 'high', 'medium', 'medium', 5, 150),
               ('0', 'Wizard 2', 'e high', 'high', 'high', 'medium', 'medium', 5, 150),
               ('0', 'Wizard 3', 'low', 'high', 'e low', 'medium', 'medium', 5, 150),
               ('0', 'Wizard 4', 'e low', 'high', 'medium', 'e high', 'e low', 5, 150),
               ('0', 'Wizard 5', 'high', 'e low', 'high', 'medium', 'medium', 5, 150),
               ('0', 'Tank 1', 'e high', 'high', 'e high', 'low', 'e high', 5, 150),
               ('0', 'Tank 2', 'high', 'medium', 'e high', 'high', 'v high', 5, 150),
               ('0', 'Healer 1', 'medium', 'high', 'e low', 'medium', 'e low', 5, 150),
               ('0', 'Healer 2', 'e high', 'e low', 'high', 'medium', 'medium', 5, 150),
               ]
    # The 0 for user_id means that it will be picked up by the system as a hero available for all users
    insert = """INSERT INTO HEROES (user_id, hero_name, hp, ph_atk, ph_def, sp_atk, sp_def, crit_rate, crit_damage)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"""
    cursor.executemany(insert, [i for i in records])

    # This section will create the built-in Monsters
    records = [('Lesser Goblin', 'weak', 'e low', 'e low', 'low', 'v low', 'v low', 10, 5),
               ('Lesser Demon', 'weak', 'v low', 'v low', 'low', 'v low', 'v low', 12, 6),
               ('Lesser Orc', 'weak', 'low', 'e low', 'medium', 'e low', 'v low', 13, 7),
               ('Lesser Troll', 'weak', 'v low', 'medium', 'low', 'v low', 'v low', 13, 12),
               ('Lesser Bandit', 'weak', 'e low', 'medium', 'medium', 'low', 'v low', 9, 12),
               ('Fallen Knight', 'weak', 'v low', 'medium', 'low', 'v low', 'v low', 12, 12),
               ('Lesser Witch', 'weak', 'e low', 'e low', 'low', 'low', 'low', 13, 14),
               ('Lesser Reptile', 'weak', 'medium', 'e low', 'medium', 'medium', 'v low', 12, 9),
               ('Lesser Wizard', 'weak', 'high', 'medium', 'low', 'v low', 'medium', 13, 12),
               ('Armed Goblin', 'medium', 'high', 'e low', 'low', 'medium', 'v low', 20, 21),
               ('Armed Bandit', 'medium', 'medium', 'medium', 'low', 'medium', 'medium', 23, 19),
               ('Armed Knight', 'medium', 'high', 'e low', 'low', 'medium', 'v low', 15, 25),
               ('Witch Apprentice', 'medium', 'e high', 'medium', 'low', 'medium', 'v low', 23, 21),
               ('Corrupt Knight', 'medium', 'e high', 'medium', 'low', 'v low', 'medium', 23, 22),
               ('Fallen Angel', 'medium', 'e high', 'medium', 'medium', 'medium', 'v low', 22, 19),
               ('Giant Orc', 'strong', 'e high', 'medium', 'medium', 'v low', 'v low', 30, 23),
               ('Giant Troll', 'strong', 'e low', 'e low', 'medium', 'v low', 'v low', 35, 25),
               ('Bandit Leader', 'strong', 'medium', 'e low', 'medium', 'v low', 'v low', 32, 25),
               ('Goblin Leader', 'strong', 'v high', 'e low', 'medium', 'v low', 'v low', 29, 35),
               ('Arch Wizard', 'strong', 'high', 'e low', 'medium', 'high', 'v high', 35, 32),
               ('Arch Demon', 'strong', 'high', 'medium', 'medium', 'medium', 'v high', 32, 34),
               ('Arch Witch', 'strong', 'medium', 'high', 'high', 'high', 'v high', 33, 36),
               ('Cthulhu', 'boss', 'e high', 'e high', 'high', 'v high', 'v high', 100, 100),
               ('Cerberus', 'boss', 'e high', 'v high', 'e high', 'medium', 'v high', 100, 100),
               ('Demon King', 'boss', 'e high', 'e high', 'v high', 'v high', 'v high', 100, 100),
               ('Corrupt King', 'boss', 'e high', 'e high', 'high', 'v high', 'v high', 100, 100),
               ]
    insert = """INSERT INTO MONSTERS (enemy_name, enemy_type, hp, ph_atk, ph_def, sp_atk, sp_def, gold, exp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"""
    cursor.executemany(insert, [i for i in records])

    # This section will create the link between built in heroes and sp_atk
    records = [(1, 1), (1, 2), (2, 2), (2, 3), (3, 4), (3, 6),
               (4, 5), (4, 8), (5, 5), (5, 9), (6, 21), (6, 22),
               (7, 22), (7, 23), (8, 24), (8, 23), (9, 22),
               (9, 21), (10, 22), (10, 21), (11, 10), (11, 12),
               (12, 15), (12, 7), (13, 19), (13, 16), (14, 17),
               (14, 16), (15, 18), (15, 19), (16, 20), (16, 21),
               (17, 22), (17, 23), (18, 14), (18, 12), (19, 13),
               (19, 12)
               ]
    insert = """INSERT INTO HEROES_SP_ATK (hero_id, sp_atk_id)
                VALUES (?, ?)"""
    cursor.executemany(insert, [i for i in records])

    # This section will create the shop prices table
    records = [('Lesser Hp Potion', 500, 'Heals the selected user for 5-10% of max hp.'),
               ('Medium Hp Potion', 2000, 'Heals the selected user for 10-20%% of max hp.'),
               ('Grand Hp Potion', 20000, 'Heals the selected user for 20-50% of max hp.'),
               ('Ph Atk Potion', 1000, 'Increases the selected user\'s ph_atk by 20% for 3 turns'),
               ('Ph Def Potion', 300, 'Increases the selected user\'s ph_def by 30% for 4 turns'),
               ('Sp Atk Potion', 1000, 'Increases the selected user\'s sp_atk by 20% for 3 turns'),
               ('Sp Def Potion', 300, 'Increases the selected user\'s sp_def by 30% for 4 turns'),
               ('Crit Rate potion', 500, 'Increases the selected user\'s crit rate by 5% for 5 turns'),
               ('Crit Damage Potion', 500, 'Increases the user\'s crit damage by 100% for 5 turns'),
               ('Hero', 10000, 'You will be given a unique hero with randomly generated stats and sp_atks.'
                               'Re-rolling the stats/sp_atks will cost 1000 gold per roll')
               ]
    insert = """INSERT INTO SHOP_PRICES (item_name, price, description)
                VALUES (?, ?, ?)"""
    cursor.executemany(insert, [i for i in records])

    records = [('Lesser Hp Potion', 5, 'hp', 0),
               ('Medium Hp Potion', 10, 'hp', 0),
               ('Grand Hp Potion', 20, 'hp', 0),
               ('Ph Atk Potion', 20, 'ph_atk', 3),
               ('Ph Def Potion', 30, 'ph_def', 4),
               ('Sp Atk Potion', 20, 'sp_atk', 3),
               ('Sp Def Potion', 30, 'sp_def', 4),
               ('Crit Rate Potion', 5, 'crit_rate', 5),
               ('Crit Damage Potion', 100, 'crit_damage', 5)
               ]
    insert = """INSERT INTO POTIONS (item_name, percentage, stat, duration)
                VALUES  (?, ?, ?, ?)"""
    cursor.executemany(insert, [i for i in records])

    connection.commit()
    # Saves the file


# ---------------------------------------------------------------  Classes  --------------------------------------------


class SQLite:
    def __init__(self):
        self.file_name = 'RPG_game_file_database'

    def create_connection(self):  # creates a connection to the database, allowing the use of SQL
        conn = sqlite3.connect(self.file_name)
        return conn

    def get_cursor(self):  # Without a cursor, I cannot execute SQL statements
        conn = self.create_connection()
        cursor = conn.cursor()
        return cursor

    def query(self, sql_statement):  # stores all records by using a 2d array
        cursor = self.get_cursor()
        cursor.execute(sql_statement)
        data = cursor.fetchall()
        return data

    def print_records(self, table_name, minimum_value, maximum_value):  # prints off the record, index starts at 1
        data = self.query(sql_statement="""
        SELECT * 
        FROM {}
        """.format(table_name))
        for row in range(minimum_value - 1, maximum_value):
            print(data[row])

    def update_record(self, table_name, attr_name, attr_value, p_key, record_number):
        # Need to include the rest of the details in parameters
        conn = self.create_connection()
        cursor = conn.cursor()
        cursor.execute("""
        UPDATE {} 
        SET {} = '{}' 
        WHERE {} = {}""".format(table_name, attr_name, attr_value, p_key, record_number))
        conn.commit()

    def delete_record(self, table_name, attr_name, record_number):  # record number = primary key number
        conn = self.create_connection()
        cursor = conn.cursor()
        cursor.execute("""
        DELETE FROM {} 
        WHERE {} = {}
        """.format(table_name, attr_name, record_number))
        conn.commit()

    def create_record(self, table_name, attr_name, attr_value):
        conn = self.create_connection()
        cursor = conn.cursor()
        if attr_name == "all":
            cursor.execute("""
            INSERT INTO {}
            VALUES({})""".format(table_name, attr_value))
        else:
            cursor.execute("""
            INSERT INTO {}({})
            VALUES({})
            """.format(table_name, attr_name, attr_value))
        conn.commit()

    def clear_table(self, table_name):
        conn = self.create_connection()
        cursor = conn.cursor()
        cursor.execute("""
        DELETE * FROM {}
        """.format(table_name))
        conn.commit()

    def increment_value(self, table_name, attr_name, p_key_name, p_key_value):
        data = self.query(f"""
        SELECT {attr_name}
        FROM {table_name}
        WHERE {p_key_name} = {p_key_value}""")[0][0]
        data = int(data) + 1
        self.update_record(table_name, attr_name, data, p_key_name, p_key_value)


class Leaderboard:
    def __init__(self):
        self.user_data = SQLite()
        self.dictionary = self.create_dictionary("attribute to name")

    def create_dictionary(self, purpose):
        if purpose == "attribute to name":
            dictionary = {
                "pvp_games_won": "Most Pvp Battles Won",
                "games_played": "Most Battles Played",
                "games_won": "Most Battles Won",
                "games_fled": "Most Battles Fled",
                "games_lost": "Most Battles Lost",
                "enemies_defeated": "Most Enemies Defeated",
                "bosses_defeated": "Most Bosses Defeated",
                "potions_used": "Most Potions Used",
                "gold": "Richest",
                "lvl": "Highest Level"
            }
            return dictionary

    def receive_highest_data(self, purpose):
        data = self.user_data.query(f'''
        SELECT save_file_name, MAX({purpose})
        FROM USER''')
        return data

    def present_stats(self):
        for key, value in self.dictionary.items():
            data = self.receive_highest_data(key)
            print(f"{value} - {data[0][0]}")
            print(f"    Currently: {data[0][1]}\n")


class MainMenu:
    def __init__(self):
        self.db_data = SQLite()  # composition
        self.colour = Colours()

    def menu(self):  # Polymorphism
        print("""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~       WELCOME TO R.RPG       ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        1. New Game 
        2. Load Game 
        3. Help 
        4. Delete a file 
        5. Full wipe of database 
        6. See The Leaderboard 
        7. Exit""")
        response = right_format_response_number("\nEnter a number between 1 and 7", 1, 7)

        if response == 1:
            self.create_new_game()

        elif response == 2:
            self.load_game()

        elif response == 3:
            self.help_menu()

        elif response == 4:
            self.print_save_files()
            data = self.get_save_files()
            dictionary = self.number_save_file_dictionary()
            number = right_format_response_number(f"Enter a value between 1 and {len(data)}", 1, len(data))
            if number == False:
                self.menu()
            save_file_number = dictionary[number]
            self.db_data.delete_record("USER", "user_id", save_file_number)

        elif response == 5:
            response = right_response_list("Are you sure you want to do this?", response_list)
            if response in positive_responses:
                self.db_data.clear_table("USER")  # clears all users built in heroes and profiles
                self.db_data.clear_table("HEROES")
                print("Data has been cleared successfully")

        elif response == 6:  # Leaderboard
            leaderboard = Leaderboard()
            leaderboard.present_stats()

        elif response == 7:
            exit()

        else:
            print("There is no where to go back to")
            self.menu()

    def create_new_game(self):
        data = self.get_save_files()
        if len(data) == 0:
            print("There are no current save files created")
        else:
            print("Current save file names: ")
            for name in data:
                print(name[1])
        save_file_name = response_check("Enter a suitable name for the file", [name for name in data])
        self.db_data.create_record("USER", "save_file_name", f"'{save_file_name}'")
        data = self.get_save_files()  # This method is repeated to get the new primary key
        response = input("Save file created, enter any value to return to the main menu")

    def load_game(self):
        self.print_save_files()
        data = self.get_save_files()
        dictionary = self.number_save_file_dictionary()
        number = right_format_response_number(f"Enter a value between 1 and {len(data)}", 1, len(data))
        if number == False:
            self.menu()  # Recursion
        else:
            save_file_number = dictionary[number]
            game = Rpg(save_file_number)
            game.menu()

    def print_save_files(self):
        data = self.get_save_files()
        if len(data) == 0:
            response = input("There are no save files, please create one to play:")
            self.menu()

        for record in range(len(data)):
            print(f"""
    {self.colour.return_colour_text('None', f'{record + 1})  Save {record + 1}')}
        Name: {data[record][1]}
        Level: {data[record][2]}
        Exp: {data[record][3]}
        Gold: {data[record][4]}""")
        print()

    def get_save_files(self):
        data = self.db_data.query("SELECT * FROM USER")
        return data  # 2d array

    def number_save_file_dictionary(self):  # creates a dictionary from 1 to n, this will link to the user id
        data = self.get_save_files()
        dictionary = {}
        for key in range(len(data)):
            dictionary.update({(key + 1): data[key][0]})  # links number entered to user id
        return dictionary

    def help_menu(self):
        print("""
        1. Help on Stats
        2. Help on Special Attacks
        3. Help on Effects
        4. Help on Battles
        """)
        response = right_format_response_number("Please enter a number between 1 and 4", 1, 4)
        if response == 1:
            self.print_stat_help()
        elif response == 2:
            self.print_sp_atk_help()
        elif response == 3:
            self.print_effect_help()
        elif response == 4:
            self.print_battle_help()
        response = input("Enter any key to return to the main menu: ")

    @staticmethod
    def print_battle_help():
        print("""
        There are 3 types of battles in R.RPG:

        Monster Battles - In these kinds of battles, the user will be paired up against 3-6 enemies based on the 
        difficulty selected and random number generation. At the end of the battle, the user will be given rewards 
        in the form of gold and exp. 

        PVP (2P) Battles - In these kinds of battles, the user will be given the option to battle a team of their
        choice. In this mode specifically, there will be 2 players battling each other simultaneously on the same 
        device. At the end of the battle, while there may be no rewards, there will be a count for the number of wins 
        which can be viewed in the leaderboard section of this game.

        PVP (AI) Battles - In these kinds of battles, the user will be given the option to battle a team of their
        choice. In this mode specifically, the CPU will be responsible for the moves that 'Player 2' makes, this will
        be dependant on the difficulty chosen. At the end of the battle, the user will be given rewards in the form of
        gold and exp.
        """)

    def print_effect_help(self):
        data = self.db_data.query("""
        SELECT status_name, status_description
        FROM STATUS_EFFECTS
        WHERE status_id > 0 and status_id < 12""")
        for status_effect in data:
            print(f"        {status_effect[0].title()} - {status_effect[1]}\n")

    @staticmethod
    def print_sp_atk_help():
        print("""
        In R.RPG, there are 5 types of special attacks:

        Status Effect Attacks - Using these kind of special attacks will leave an 'effect' on the defending
        character. These status effects can affect the character both positively or negatively. For more help, 
        check the 'effect help' option in the help menu 

        Healing Special Attacks - Using these kind of special attacks will recover the selected characters Hp.

        Draining Special Attacks - Using these kind of special attacks will damage the defending enemy while also
        healing the attacker for a % of damage dealt.

        Aggro Special Attacks - Using these kind of special attacks will damage the enemy and will also set the 
        enemy to target that individual until he is defeated.

        AOE Special Attacks - Using these kind of special attacks will cause mass damage to all enemies.
        """)

    @staticmethod
    def print_stat_help():
        print("""
        Hp - The 'Health Points' of a character, in the battle system, both sides will experience changes to their
        overall Hp. A hero will be 'defeated' when their Hp hits 0.

        Physical Attack - Part of the overall damage caused by a normal attack. This will also be combined with
        other factors in order to determine the damage that a hero deals every turn.

        Physical Defence - This stat refers to how well a character can 'tank' a physical shot, the higher the 
        physical defence, the lower damage the defending character will receive.

        Special Attack - Part of the damage caused by a special attack. This will also be taken into consideration
        in healing aswell.

        Special Defence - This refers to how well a character can 'tank' a special attack, the higher the special
        defence, the lower the damage the defending character will receive.

        Mana - The 'energy' of a hero, it will be consumed when a hero uses a special attack. Enemies have no
        mana cap.

        Critical Hit Chance - The % chance that a hero has to deal abnormal damage. Critical hits are limited
        to heroes only.

        Critical Hit Damage - The extra % of damage dealt with a critical hit. 
        """)


class Rpg:
    def __init__(self, user_id):
        self.user_data = SQLite()
        self.user_id = user_id
        self.level = self.get_stat("lvl")
        self.gold = self.get_stat("gold")
        self.exp = self.get_stat("exp")
        self.colours = Colours

    def menu(self):  # Polymorphism
        print("""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~       MAIN MENU       ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    1. Battle (monsters or pvp)
    2. See stats (heroes, enemies, profile) #DONE
    3. Access the Shop
    4. Rename Data
    5. Access Teams #DONE
    6. Load a Different Game #DONE
    7. Leave #DONE""")
        response = right_format_response_number("\nEnter a number between 1 and 7", 1, 7)

        if response == 1:
            battle = Battle(self.user_id)
            battle.menu()

        elif response == 2:
            print("""
            See stats for:
                1. Profile stats
                2. Built-in Heroes
                3. Unique Heroes
                4. Monsters

            See special attacks for:
                5. Built-in Heroes
                6. Unique Heroes""")
            response = right_format_response_number("\nEnter a value between 1 and 6: ", 1, 6)
            dictionary = False

            if response == False:
                self.menu()
            elif response == 1:
                data = self.get_data("profile")[0]  # 1d list
                titles = ["User ID", "Save Name", "Level", "Exp", "Gold", "Games Played", "Games Won",
                          "Enemies Defeated", "Bosses Defeated", "Lesser Hp Potions", "Medium Hp Potions",
                          "Grand Hp Potions", "Physical Attack Potions", "Physical Defence Potion",
                          "Special Attack Potions", "Special Defence Potions",
                          "Critical Chance Potions", "Critical Damage Potions"]
                dictionary = {titles[i]: data[i] for i in range(len(data))}  # normal dictionary

            elif response == 2 or response == 3:
                if response == 2:
                    purpose = "built in hero"
                else:
                    purpose = "user hero"
                    self.check("user hero exists")
                dictionary = []
                data = self.get_data(purpose)  # 2d list
                titles = ["Hero id", "User Id", "Hero Name", "Hp", "Physical Attack", "Physical defence",
                          "Special Attack",
                          "Special Defence", "Critical Hit Chance", "Critical Hit Damage"]
                for hero in data:
                    mini_dictionary = {titles[i]: self.convert(hero[i], i - 2) for i in range(len(titles))}
                    dictionary.append(mini_dictionary)  # creating a list of dictionaries

            elif response == 4:
                dictionary = []
                data = self.get_data("monster")
                titles = ["Enemy ID", "Enemy Name", "Enemy Type", "Hp", "Physical Attack", "Physical Defence",
                          "Special Attack",
                          "Special Defence", "Gold", "Exp"]
                for enemy in data:
                    mini_dictionary = {titles[i]: self.convert(enemy[i], i - 3) for i in range(len(titles))}
                    dictionary.append(mini_dictionary)  # list of dictionaries

            elif response == 5 or 6:
                sp_atk_names = 0
                if response == 5:
                    user_id = 0
                else:
                    user_id = self.user_id
                    self.check("user hero exists")
                data = []
                temp = self.user_data.query("""
                SELECT hero_id, hero_name
                FROM HEROES
                WHERE user_id = {}""".format(user_id))
                for i in range(len(temp)):
                    hero_id = temp[i][0]
                    sp_atk_names = self.user_data.query("""
                    SELECT SP_ATK.sp_atk_name
                    FROM ((HEROES
                    INNER JOIN HEROES_SP_ATK ON HEROES.hero_id = HEROES_SP_ATK.hero_id)
                    INNER JOIN SP_ATK ON HEROES_SP_ATK.sp_atk_id = SP_ATK.sp_atk_id)
                    WHERE HEROES.hero_id = {}""".format(hero_id))  # Higher level of SQL
                    temp_2 = [*temp[i], *sp_atk_names]
                    data.append(temp_2)
                dictionary = []
                titles = ["Hero ID", "Hero Name"]
                for i in range(len(sp_atk_names)):
                    titles.append(f"Special attack {i + 1}")
                for item in data:
                    try:
                        mini_dictionary = {titles[i]: item[i] for i in range(len(item))}  # built in heroes
                    except:
                        mini_dictionary = {titles[i]: item[i] for i in range(len(titles))}  # user heroes
                    dictionary.append(mini_dictionary)

            if not dictionary:
                response = input("Something went wrong, returning to the main menu, enter any key to return: ")
                self.menu()

            elif dictionary is None:
                print("There is no instance of this, please only check the stats of data that exists.")

            elif isinstance(dictionary, list):
                for i in dictionary:
                    for key, value in i.items():
                        print(f"{key} : {value}")
                    print()
            else:
                for key, value in dictionary.items():
                    print(f"{key} : {value}")

        elif response == 3:
            shop = Shop(self.user_id)
            shop.menu()
        elif response == 4:
            pass

        elif response == 5:
            team = Team(self.user_id)
            team.team_menu()

        elif response == 6:
            main_menu = MainMenu()
            main_menu.menu()
        elif response == 7:
            exit()
        self.menu()

    def get_data(self, purpose):
        data = False

        if purpose == "built in hero":
            data = self.user_data.query("""
            SELECT *
            FROM HEROES
            WHERE user_id = 0""")  # 2d list

        elif purpose == "user hero":
            data = self.user_data.query("""
            SELECT *
            FROM HEROES
            WHERE user_id = {}""".format(self.user_id))  # stored as a 2d list

        elif purpose == "monster":
            data = self.user_data.query("""
            SELECT *
            FROM MONSTERS""")  # 2d list

        elif purpose == "profile":
            data = self.user_data.query("""
            SELECT *
            FROM USER
            WHERE user_id = {}""".format(self.user_id))  # single list

        elif purpose == "inventory":
            data = self.user_data.query("""
            SELECT *
            FROM INVENTORY
            WHERE user_id = {}""".format(self.user_id))  # single list

        elif purpose == "user":
            data = self.user_data.query("""
            SELECT *
            FROM USER
            WHERE user_id = {}""".format(self.user_id))  # single list

        if not data:
            print("An unknown error occurred, please try again")
            return
        return data

    def get_user_id(self):
        return self.user_id

    def convert(self, stat, number):
        dictionary = {
            "e low": 0.5,
            "v low": 0.75,
            "low": 1.25,
            "medium": 1.5,
            "high": 1.75,
            "v high": 3,
            "e high": 5
        }
        if stat in dictionary.keys():
            stat = dictionary[stat] * self.level + 15
        return stat

    def get_stat(self, stat):
        stat = self.user_data.query("""
        SELECT {}
        FROM USER
        WHERE user_id = {}""".format(stat, self.user_id))
        return stat[0][0]

    def check(self, purpose):
        if purpose == "user hero exists":
            test = self.user_data.query("""
                SELECT hero_id
                FROM HEROES
                WHERE user_id = {}""".format(self.user_id))
            if not test:
                response = input("""
                No user-specific heroes have been created
                Please go to the shop to create one
                Enter any key to return to the main menu:
                """)
                self.menu()
        return


class Team:
    def __init__(self, user_id):
        self.user_data = SQLite()
        self.user_id = user_id

    def team_menu(self):
        print("""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~       TEAM BUILDING       ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        1. See all teams  
        2. Delete a team  
        3. Create a team  
        4. Change characters in a team  
        5. Exit""")
        response = right_format_response_number("\nEnter a number between 1 and 5", 1, 5)
        if response == 1:
            self.print_team_formations()
        elif response == 2:
            self.delete_a_team()
        elif response == 3:
            self.create_a_team()
        elif response == 4:
            self.team_edit()
        elif response == 5:
            game = Rpg(self.user_id)
            game.menu()
        elif response == False:
            self.team_menu()  # recursion

    def check(self, purpose, data_to_check_1, data_to_check_2):  # Overloading
        if purpose == "team length":
            team = self.get_single_team(data_to_check_1)
            if len(team) > 8:
                return False  # means that theres too many heroes in the team
            return True  # another hero can be added

        elif purpose == "hero in team":
            heroes = self.get_all_heroes()
            dictionary = {i: heroes[i] for i in range(len(heroes))}
            hero = dictionary[data_to_check_1]
            if hero[1] in data_to_check_2:
                return True  # means the hero is already in the team
            return False  # means the hero isn't in the team

    def get_team_formations(self):
        teams = self.user_data.query(f"""
        SELECT *
        FROM TEAMS
        WHERE user_id = {self.user_id}""")  # hero id 1-6 = index 2-7
        return teams

    def print_team_formations(self):
        teams = self.get_team_formations()
        if len(teams) == 0:
            print("There are no current teams for this account, please create one first")
        else:
            print()
            for i in range(len(teams)):
                print(f"~~~~~~~~~~~~~~~~~~~~~~   Team {i + 1}   ~~~~~~~~~~~~~~~~~~~~~~")
                for j in range(2, 8):
                    hero = self.convert("hero id to name", teams[i][j])
                    print("     Hero {} - {}".format(j - 1, hero))
                print()

    def get_single_team(self, team_number):
        teams = self.user_data.query(f"""
        SELECT *
        FROM TEAMS
        WHERE user_id = {self.user_id}""")
        single_team = teams[team_number]
        return single_team

    def delete_a_team(self):
        self.print_team_formations()
        teams = self.get_team_formations()
        team_number = right_format_response_number("Enter the number of the team you wish to delete", 1, len(teams)) - 1
        if team_number == False:
            self.team_menu()
        else:
            response = right_response_list("Are you sure you want to do this? ", response_list)
            if response in positive_responses:
                # need to convert the number into a team id to delete
                team_id = self.convert("number to team id", team_number)
                print(team_id)
                self.user_data.delete_record("TEAMS", "team_id", team_id)
                response = input("Team deleted, enter any key to return to the team menu: ")
                self.team_menu()  # recursion
            elif response in negative_responses:
                response = input("Deletion of teams cancelled, enter any key to return to the main menu: ")
                game = Rpg(self.user_id)
                game.menu()

    def create_a_team(self):
        heroes = self.get_all_heroes()
        self.print_all_heroes(heroes)
        dictionary = {i: heroes[i] for i in range(len(heroes))}
        team_list = []
        hero_number = 0  # only here to stop pythons "referenced before assignment" message
        for i in range(1, 7):
            valid = False
            while not valid:
                hero_number = right_format_response_number(f"Enter the number of hero {i} in your team", 1,
                                                           len(heroes))
                if hero_number == False:
                    self.team_menu()
                else:
                    hero_number -= 1
                    if self.check("hero in team", hero_number, team_list):
                        print("You have already added this hero, please add a different one")
                    else:
                        valid = True
                        team_list.append(dictionary[hero_number][1])
        print("Team: ")
        for hero in team_list:
            print(hero)
        self.user_data.create_record("TEAMS",
                                     "user_id, hero_id_1, hero_id_2, hero_id_3, hero_id_4, hero_id_5, hero_id_6",
                                     "{}, {}, {}, {}, {}, {}, {}".format(self.user_id, *team_list))
        response = input("Team has been created, enter any value to return to the teams menu: ")
        self.team_menu()

    def team_edit(self):
        hero_to_add = 0  # here to prevent the same error
        self.print_team_formations()
        teams = self.get_team_formations()
        response = right_format_response_number(
            "Enter the number of the team you wish to change the members of: ", 1, len(teams) + 1)
        if response == False:
            repsonse = input("Returning to the main menu, enter any key to return: ")
            self.team_menu()
        else:
            response -= 1
            team = self.get_single_team(response)

        for i in range(2, 8):
            print("Hero {} : {}".format(i - 1, self.convert("hero id to name", team[i])))
        hero_to_remove = right_format_response_number("Enter the number of the hero you wish to change:", 1, 6)
        if response == False:
            response = input("Returning to the main menu, enter any key to return: ")
            self.team_menu()
        else:
            hero_to_remove += 1
            heroes = self.get_all_heroes()
            self.print_all_heroes(heroes)
            dictionary = {i: heroes[i] for i in range(len(heroes))}
            valid = False
            while not valid:
                hero_to_add = right_format_response_number("Enter the number of the hero you want in the team", 1,
                                                           len(heroes) + 1)
                if hero_to_add == False:
                    response = input("Returning to the menu, enter any key to return: ")
                    self.team_menu()
                else:
                    hero_to_add -= 1
                    if self.check("hero in team", hero_to_add, team):
                        print("This hero is already in the team, please select another")
                    else:
                        valid = True
            hero_id_string = "hero_id_" + str(dictionary[hero_to_remove][1] - 2)
            new_hero_id = dictionary[hero_to_add][1]
            team_id = team[0]
            self.user_data.update_record("TEAMS", hero_id_string, new_hero_id, "team_id", team_id)

    def convert(self, purpose, number):  # Overloading
        if purpose == "number to team id":
            team = self.get_single_team(number)
            team_id = team[0]
            return team_id

        elif purpose == "hero id to name":
            heroes = self.get_all_heroes()
            dictionary = {i + 1: heroes[i] for i in range(len(heroes))}
            hero = dictionary[number][0]
            return hero

    def get_all_heroes(self):
        heroes = self.user_data.query("""
        SELECT hero_name, hero_id
        FROM HEROES
        WHERE user_id in (0, 1)""".format(self.user_id))
        return heroes

    @staticmethod
    def print_all_heroes(heroes):
        for i in range(len(heroes)):
            print(f"""  Hero {i + 1}:
        Hero Name : {heroes[i][0]}""")


class Battle:
    def __init__(self, user_id):
        self.user_id = user_id
        self.user_data = SQLite()  # Composition
        self.game_mode = 0
        self.level = self.get_stat("lvl")  # will help speed up some processes as less SQL will be needed
        self.gold = self.get_stat("gold")
        self.exp = self.get_stat("exp")
        self.team_1 = []
        self.team_2 = []
        self.potion_list = self.generate_potions()
        self.aggro = None
        self.colour = Colours()  # Composition

    def menu(self):  # Polymorphism
        print("""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~       BATTLE MENU       ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        1. Battle a monster
        2. Battle another player AI
        3. Battle another player (2P)\n""")
        response = right_format_response_number(f"Enter a number between 1 and 3", 1, 3)
        if response == 1:
            self.pve_menu()
        elif response == 2:
            self.pvp_ai_menu()
        elif response == 3:
            self.pvp_non_ai_menu()
        elif response == False:
            response = input("Returning to the main menu, enter any key to return")
        rpg = Rpg(self.user_id)
        rpg.menu()

    def get_game_mode(self):
        print("""
        Select difficulty:
            1. Easy
            2. Medium
            3. Hard
            4. Extreme
            5. Leave\n""")
        response = right_format_response_number("Please select a number between 1 and 5: ", 1, 5)
        if response == 5:
            exit()
        elif response == False:
            response = input("Returning to the game menu, enter any key to return: ")
            self.menu()
        else:
            return response

    def pve_menu(self):
        response = self.get_game_mode()
        self.game_mode = self.convert("number to game mode type", response)
        self.team_1 = self.get_user_team(self.user_id)
        self.start_pve_battle()

    def pvp_ai_menu(self):
        self.team_1 = self.get_user_team(self.user_id)
        enemy_id = self.get_user_id()  # Gets the user id of the opposing team
        self.team_2 = self.get_user_team(enemy_id)
        response = self.get_game_mode()
        self.game_mode = self.convert("number to game mode type", response)
        self.start_pvp_battle("ai")

    def pvp_non_ai_menu(self):
        self.team_1 = self.get_user_team(self.user_id)
        enemy_id = self.get_user_id()  # Gets the user id of the opposing team
        self.team_2 = self.get_user_team(enemy_id)
        self.start_pvp_battle("2p")

    def get_user_id(self):
        list_of_users = self.user_data.query("""
        SELECT user_id, save_file_name
        FROM USER""")
        dictionary = {i + 1: list_of_users[i][0] for i in range(len(list_of_users))}
        print("Select a save file")
        for i in range(len(list_of_users)):
            print(f"    {i + 1}. - {list_of_users[i][1]}")
        response = right_format_response_number("Please enter the number of the save file you wish to battle: ", 1,
                                                len(list_of_users))
        if response == False:
            self.menu()
        else:
            user_id = dictionary[response]
            return user_id

    def start_pvp_battle(self, mode):
        self.user_data.increment_value("USER", "games_played", "user_id", self.user_id)
        self.team_1 = self.generate_heroes(self.team_1, "hero")

        if mode == "2p":
            self.team_2 = self.generate_heroes(self.team_2, "hero")
        elif mode == "ai":
            self.team_2 = self.generate_heroes(self.team_2, "")
        else:
            print("An unknown error has occured, returning to the main menu")
            self.menu()

        battle = True
        while battle == True:
            battle = self.main_battle(mode, self.team_1, self.team_2)

        if battle == "win":
            self.user_data.increment_value("USER", "games_won", "user_id", self.user_id)
            if mode == "ai":
                for i in range(2):
                    self.generate_rewards("win")
            elif mode == "2p":
                self.user_data.increment_value("USER", "pvp_games_won", "user_id", self.user_id)
                print("Player 1 wins")

        elif battle == "lose":
            self.user_data.increment_value("USER", "games_lost", "user_id", self.user_id)
            if mode == "ai":
                self.generate_rewards("lose")
            elif mode == "2p":
                print("Player 2 wins")

        elif battle == "flee":
            self.user_data.increment_value("USER", "games_fled", "user_id", self.user_id)
            if mode == "ai":
                self.generate_rewards("flee")
            elif mode == "2p":
                print("The battle was not decided")

        rpg = Rpg(self.user_id)
        rpg.menu()

    def start_pve_battle(self):
        self.user_data.increment_value("USER", "games_played", "user_id", self.user_id)
        self.team_1 = self.generate_heroes(self.team_1, "hero")
        self.team_2 = self.generate_enemies(self.game_mode)
        battle = True

        while battle == True:
            battle = self.main_battle("pve", self.team_1, self.team_2)
        if battle == 'win':
            self.user_data.increment_value("USER", "games_won", "user_id", self.user_id)
            self.generate_rewards("win")
        elif battle == 'lose':
            self.user_data.increment_value("USER", "games_lost", "user_id", self.user_id)
            self.generate_rewards("lose")
        elif battle == 'flee':
            self.user_data.increment_value("USER", "games_fled", "user_id", self.user_id)
            self.generate_rewards("flee")

    def select_entity(self, team, text):
        while True:
            number = 0
            if type(team[0]) == Hero or type(team[0]) == AiHero:
                self.print_hp(team)
                number = right_format_response_number(text, 1, 6)
                if number == False:
                    return - 1
                else:
                    number -= 1
                    if team[number].is_dead:
                        print("This hero is already dead, please select another one")
                        number = self.select_entity(team, text)

            elif type(team[0]) == Enemy:
                print()
                self.print_hp(team)
                number = right_format_response_number("Please select an enemy to attack: ", 1, len(team))
                print()
                if number == False:
                    return -1
                else:
                    number -= 1
                    if team[number].is_dead:
                        print("This enemy is already dead, please select another one")
                        number = self.select_entity(team, text)
            return number

    def select_sp_atk(self, entity):
        for i in range(len(entity.sp_atk_list)):
            attack_type = "Attack Type"
            if type(entity.sp_atk_list[i]) == StatusSpecialAttack:
                attack_type = "Element"
            special_attack_number = self.colour.return_colour_text("None", "Special Attack " + str(i + 1))
            print(f"\n{special_attack_number}: {entity.sp_atk_list[i].name}\n"
                  f"{self.colour.return_colour_text('None', 'Mana Cost')}: {entity.sp_atk_list[i].mana_cost}\n"
                  f"{self.colour.return_colour_text('None', attack_type)}: "
                  f"{self.colour.effect_colour(entity.sp_atk_list[i].status_effect.name)}\n")
        print()
        response = right_format_response_number(f"""Please select a number between  1 and  {len(entity.sp_atk_list)}""",
                                                1, len(entity.sp_atk_list))
        if response == False:
            return False
        else:
            response -= 1
            if not self.check_mana(entity, entity.sp_atk_list[response]):
                print("You do not have enough mana for this special attack: ")
                return False
            else:
                return entity.sp_atk_list[response]

    @staticmethod
    def check_mana(entity, sp_atk):
        if entity.mana < sp_atk.mana_cost:
            return False
        return True

    def use_mana(self, entity, sp_atk):
        print(f"{self.colour.effect_colour('mana')}: {entity.mana} -> {entity.mana - sp_atk.mana_cost}\n")
        entity.mana -= sp_atk.mana_cost

    def backfire(self, entity_attacking, entity_receiving_team):
        damage = 0
        crit_damage = 0
        for entity in entity_receiving_team:
            crit_damage = self.get_crit_damage(entity_attacking)
            damage = round((entity_attacking.sp_atk * 2) - entity.sp_def * 0.5)
            entity.damage(round(damage * crit_damage))
        print(
            f"Damage equal to {damage * crit_damage} has been dealt to all of the monsters due to the 'backfire' status")

    def sp_atk(self, e_attacking, e_defending, sp_atk):  # Launches a special attack on an entity
        print(self.colour.return_colour_text("None", f"\n------ {e_attacking.name} ------"))

        number = random.randint(1, 100)
        if e_attacking.miss_rate >= number:
            total_damage = 0
            print(f"{e_attacking.name} missed the attack, no damage was dealt to {e_defending.name}")
            return

        if type(sp_atk) == HealingSpecialAttack:
            print(f"{e_attacking.name} has used {sp_atk.name} to heal {e_defending.name}")
        else:
            print(f"{e_attacking.name} has used {sp_atk.name} on {e_defending.name}")

        if sp_atk.type == "status_effect":  # to save until the end
            crit_damage = self.get_crit_damage(e_attacking)
            damage = round((e_attacking.sp_atk * (sp_atk.percentage * 0.01)) - e_defending.sp_def * 0.5)
            e_defending.damage(round(damage * crit_damage))  # Deals sp_atk damage
            e_defending.effect_count.add_to_list(sp_atk.name, sp_atk)  # Creates a timer for the sp_atk effects
            print(f"The '{self.colour.effect_colour(sp_atk.status_effect.name)}' status effect has been applied to "
                  f"{e_defending.name}")
            element = e_defending.effect_count.check_other_effects()  # Checks if any other sp_atks can be combined
            if element == None:
                e_defending.status_effect_initial(sp_atk)
            else:
                attack = e_defending.status_effect_initial(element)  # Deals the initial de buffs of an effects
                if attack == "aoe":
                    self.backfire(e_attacking, self.team_2)

        elif sp_atk.type == "draining":
            crit_damage = self.get_crit_damage(e_attacking)
            damage = round((e_attacking.sp_atk * (sp_atk.percentage * 0.01)) - e_defending.sp_def * 0.5)
            e_defending.damage(round(damage * crit_damage))
            heal_amount = round(damage * (sp_atk.status_effect.effect_1_percentage * 0.01))
            e_attacking.heal(round(heal_amount))
            print(f"{e_attacking.name} has dealt {damage * crit_damage} damage to {e_defending.name}")
            print(f"{e_attacking.name} has healed by {heal_amount} hit points")

        elif sp_atk.type == "aggro":
            crit_damage = self.get_crit_damage(e_attacking)
            damage = round((e_attacking.sp_atk * (sp_atk.percentage * 0.01)) - e_defending.sp_def * 0.5)
            e_defending.damage(round(damage * crit_damage))
            print(f"{e_attacking.name} has dealt {damage * crit_damage} damage to {e_defending.name}")
            self.aggro = self.team_1.index(e_attacking)
            print(f"Enemies will now target {e_attacking.name}")

        elif sp_atk.type == "heal_percentage":
            heal_amount = round(self.get_crit_damage(e_attacking) * (sp_atk.percentage * 0.01) * e_attacking.hp)
            e_defending.heal(round(heal_amount))
            print(f"{e_attacking.name} has healed {e_defending.name} for {heal_amount} hit points")

        e_defending.check_status(self.user_id)

    def aoe_attack(self, entity_attacking, entity_receiving_team, sp_atk):
        print(self.colour.return_colour_text("None", f"\n------ {entity_attacking.name} ------"))
        damage = 0
        crit_damage = 0
        for entity in entity_receiving_team:
            crit_damage = self.get_crit_damage(entity_attacking)
            try:
                sp_atk.percentage = sp_atk.percentage
            except:
                sp_atk.percentage = 200  # If it is an AOE due to backfire
            damage = round((entity_attacking.sp_atk * (sp_atk.percentage * 0.01)) - entity.sp_def * 0.5)
            entity.damage(round(damage * crit_damage))
        print(f"An AOE attack worth of {damage * crit_damage} has been dealt to all of the monsters")

    def main_battle(self, mode, team_attacking, team_defending):
        turn = None

        if team_attacking == self.team_1:
            print(self.colour.return_colour_text("underline", "~~~~~~ PLAYER 1's turn: ~~~~~~"))
        else:
            print(self.colour.return_colour_text("underline", "~~~~~~ PLAYER 2's turn: ~~~~~~"))

        response = self.print_options()
        for hero in self.team_1:
            hero.check_status(self.user_id)
        for enemy in self.team_2:
            enemy.check_status(self.user_id)

        if response == 1:  # attack
            hero_number = self.select_entity(team_attacking, "Please select a hero to attack with: ")
            if hero_number + 1 == False:
                turn = 'skip'
            else:
                enemy_number = self.select_entity(team_defending, "Please select an enemy to attack: ")
                if enemy_number + 1 == False:
                    turn = 'skip'
                else:
                    hero_attacking = team_attacking[hero_number]
                    enemy_defending = team_defending[enemy_number]
                    self.attack(hero_attacking, enemy_defending)
                    if mode == "ai" or mode == "pve":
                        self.enemy_turn()

        elif response == 2:  # sp atk
            entity_selected = 0
            number = self.select_entity(team_attacking, "Select a hero to see their special attack: ")
            if number + 1 == False:
                turn = "skip"
            else:
                hero_attacking = team_attacking[number]
                sp_atk_selected = self.select_sp_atk(hero_attacking)

                if sp_atk_selected == False:
                    turn = 'skip'

                elif sp_atk_selected.type != "aoe":
                    if sp_atk_selected.type == "heal_percentage":
                        number = self.select_entity(team_attacking, "Please select a hero to heal: ")
                        if number + 1 == False:
                            turn = 'skip'
                        else:
                            entity_selected = team_attacking[number]
                    else:
                        number = self.select_entity(team_defending, "Please select an enemy to attack: ")
                        if number + 1 == False:
                            turn = 'skip'
                        else:
                            entity_selected = team_defending[number]
                    if number + 1 == False:
                        turn = 'skip'
                    else:
                        self.sp_atk(hero_attacking, entity_selected, sp_atk_selected)
                elif sp_atk_selected.type == "aoe":
                    self.aoe_attack(team_attacking[number], team_defending, sp_atk_selected)
                if turn == 'skip':
                    pass
                else:
                    self.use_mana(hero_attacking, sp_atk_selected)
                    if mode == "ai" or mode == "pve":
                        self.enemy_turn()

        elif response == 3:  # item
            potion_selected, hero_selected = self.print_potions()
            if potion_selected == False or hero_selected == False:
                turn = 'skip'
            else:
                self.apply_potion(potion_selected, hero_selected)
                self.user_data.increment_value("USER", "potions_used", "user_id", self.user_id)
                if mode == "ai" or mode == "pve":
                    self.enemy_turn()

        elif response == 4:
            self.see_detailed_stats()
            turn = "skip"

        elif response == 5:  # fleeing
            return "flee"

        if mode == "2p" and turn != 'skip' and not self.is_dead(self.team_1) and not self.is_dead(self.team_2):
            self.main_battle("", self.team_2, self.team_1)

        if turn != 'skip' and mode != "2p":
            valid = self.check_effect_list()
            if valid:
                print(self.colour.return_colour_text("None", "\n------ End Of Turn ------"))

            for hero in self.team_1:
                hero.end_of_turn()
                hero.decrease_duration()
            for enemy in self.team_2:
                enemy.end_of_turn()
                enemy.decrease_duration()
            print()

        if self.is_dead(self.team_1):
            return "lose"
        elif self.is_dead(self.team_2):
            return "win"
        return True

    def check_effect_list(self):  # Checks if any entity in the list has an effect or not
        for hero in self.team_1:
            if len(hero.effect_count.counter) != 0:
                return True
        for enemy in self.team_2:
            if len(enemy.effect_count.counter) != 0:
                return False

    def generate_potions(self):
        potions = self.user_data.query("""
        SELECT item_name, percentage, stat, duration
        FROM POTIONS""")
        potion_list = []
        for potion in potions:
            if potion[3] == 0:  # Means that it is a restoration potion
                potion_list.append(Potion(potion[0], potion[1]))
            else:
                potion_list.append(BuffPotion(potion[0], potion[1], potion[2], potion[3]))
        return potion_list

    def apply_potion(self, potion_selected, hero_selected):
        potion = self.potion_list[potion_selected]
        hero_selected.use_potion(potion)
        potion_name = self.convert("USER potion name", potion.item_name)
        potions = self.user_data.query(f"""
        SELECT {potion_name}
        FROM USER
        WHERE user_id = {self.user_id}""")[0][0]
        potions -= 1
        self.user_data.update_record("USER", potion_name, potions, "user_id", self.user_id)

    def get_potions(self):
        potions = self.user_data.query(f"""
    SELECT lesser_hp_potion, medium_hp_potion, grand_hp_potion, ph_atk_potion, ph_def_potion, sp_atk_potion, 
    sp_def_potion, crit_chance_potion, crit_damage_potion
    FROM USER
    WHERE user_id = {self.user_id}""")
        return potions

    def print_potions(self):
        potions = self.get_potions()[0]
        titles = ["Lesser Hp Potion", "Medium Hp Potion", "Grand Hp Potion", "Physical Attack Potion",
                  "Physical Defence Potion", "Special Attack Potion", "Special Defence Potion",
                  "Critical Chance Potion", "Critical Attack Potion"]

        for i in range(len(titles)):
            print(f"{i + 1}. {titles[i]} : {potions[i]}")
        potion_selected = right_format_response_number("\nEnter the number of the potion: ", 1, len(potions))
        if potion_selected == False:
            return False, False
        else:
            potion_selected -= 1
            if potions[potion_selected] == 0:
                print("You have not got enough potions, returning back to the option screen")
                return False, False

        self.print_hp(self.team_1)
        hero_selected = right_format_response_number("\nEnter the number of the hero: ", 1, 6)
        if hero_selected == False:
            return False, False
        else:
            hero_selected -= 1
            if self.team_1[hero_selected].is_dead:
                print("This hero is dead, you cannot use a potion on him, returning to the option screen")
                return False, False
            else:
                return potion_selected, self.team_1[hero_selected]

    def attack(self, e_attacking, e_defending):
        print(self.colour.return_colour_text("None", f"\n------ {e_attacking.name} ------"))
        crit_damage = self.get_crit_damage(e_attacking)
        additional_atk = round(0.1 * e_attacking.ph_atk)
        var_atk = random.randint(round(e_attacking.ph_atk - additional_atk), round(e_attacking.ph_atk + additional_atk))
        hero_damage = var_atk * crit_damage
        total_damage = round(hero_damage - 0.05 * e_defending.ph_def)
        number = random.randint(1, 100)
        if e_attacking.miss_rate >= number:
            total_damage = 0
            print(f"{e_attacking.name} missed the attack, no damage was dealt to {e_defending.name}")
        else:
            print(f"{e_attacking.name} dealt {total_damage} damage to {e_defending.name}")
        e_defending.damage(total_damage)
        e_defending.check_status(self.user_id)

    @staticmethod
    def get_crit_damage(entity_selected):
        crit_rate = random.randint(1, 100)
        if entity_selected.crit_rate <= crit_rate:
            crit_damage = entity_selected.crit_damage / 100
        else:
            crit_damage = 1
        return crit_damage

    def enemy_turn(self):
        # 50% chance of sp atk, 50% chance of normal attack
        # takes difficulty into consideration of targets
        self.enemy_target()  # adjusts targets
        enemy_chosen = self.enemy_choice()
        if enemy_chosen is None:
            pass
        else:
            number = random.randint(0, 100)
            if number <= 50:
                self.attack(self.team_2[enemy_chosen], self.team_1[self.team_2[0].target])
            else:
                special_attack = self.generate_enemy_special_attack()
                if special_attack.status_effect.effect_1 == "heal_percentage" or \
                        special_attack.status_effect.effect_2 == "heal_percentage":
                    target_to_heal = self.set_heal_target(self.team_2)
                    self.sp_atk(self.team_2[enemy_chosen], target_to_heal, special_attack)
                else:
                    self.sp_atk(self.team_2[enemy_chosen], self.team_1[self.team_2[0].target], special_attack)

    def set_heal_target(self, entity_team):
        chosen_entity = entity_team[0]
        for entity in entity_team:
            if not (self.is_dead(entity)) and (entity.hp - entity.current_hp) > chosen_entity.hp:
                chosen_entity = entity
        return chosen_entity

    def generate_enemy_special_attack(self):
        sp_atk_id_list = self.user_data.query("""
        SELECT SP_ATK.sp_atk_id, STATUS_EFFECTS.status_effect_1, STATUS_EFFECTS.status_effect_2, SP_ATK.sp_atk_duration
        FROM SP_ATK
        INNER JOIN STATUS_EFFECTS
        ON STATUS_EFFECTS.status_id = SP_ATK.status_id
        WHERE NOT STATUS_EFFECTS.status_effect_1 = 'aggro' AND NOT STATUS_EFFECTS.status_effect_2 = 'aggro'""")
        # Excluding aggro to prevent the restriction of freedom on the user's side
        sp_atk = random.choice(sp_atk_id_list)
        if sp_atk[1] == "aoe" or sp_atk[2] == "aoe":
            sp_atk = AOESpecialAttack(sp_atk[0])
        elif sp_atk[1] == "drain_atk" or sp_atk[2] == "drain_atk":
            sp_atk = DrainingSpecialAttack(sp_atk[0])
        elif sp_atk[1] == "heal_percentage" or sp_atk[2] == "heal_percentage":
            sp_atk = HealingSpecialAttack(sp_atk[0], sp_atk[3])
        else:
            sp_atk = StatusSpecialAttack(sp_atk[0])
        return sp_atk

    @staticmethod
    def is_dead(entity_list):
        count = 0
        for i in range(len(entity_list)):
            if entity_list[i].current_hp == 0:  # if an enemy is dead
                count += 1
        if count == len(entity_list):
            return True
        return False

    def print_options(self):
        print("""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~       BATTLE       ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        1. Attack 
        2. SP Attack  
        3. Use Item  
        4. See Detailed stats
        5. Flee
        """)
        response = right_format_response_number("Please enter a number between 1 and 5: ", 1, 5)
        if response == False:
            self.print_options()
        else:
            return response

    def generate_enemies(self, game_mode):
        enemy_type = self.convert("game mode to enemy type", game_mode)
        selected_enemies = []
        main_enemy_list = []
        number_of_enemies = 0
        if isinstance(enemy_type, list):  # Checking the types of monsters that will be brought along
            enemies = self.user_data.query("""
            SELECT monster_id
            FROM MONSTERS
            WHERE enemy_type = '{}'
            UNION ALL
            SELECT monster_id
            FROM MONSTERS
            WHERE enemy_type = '{}'""".format(enemy_type[0], enemy_type[1]))
        else:
            enemies = self.user_data.query("""
            SELECT monster_id
            FROM MONSTERS
            WHERE enemy_type = '{}'""".format(enemy_type))  # selecting monster id only will help save space

        if game_mode == "easy":
            number_of_enemies = random.randint(3, 5)
            # generate a random amount of enemies
        elif game_mode == "medium":
            number_of_enemies = random.randint(3, 6)
        elif game_mode == "hard":
            number_of_enemies = random.randint(4, 6)
        elif game_mode == "extreme":
            number_of_enemies = random.randint(4, 5)

        for enemy in range(number_of_enemies):
            monster_id = random.choice(enemies)
            temp = self.user_data.query("""
            SELECT *
            FROM MONSTERS
            WHERE monster_id = {}""".format(monster_id[0]))
            # Created the monsters after finding ids, this way, I will only need 6 full records at most compared to 30
            # This reduces the total memory used
            selected_enemies.append(temp)

        if self.game_mode == 'extreme':
            data = self.user_data.query("""
            SELECT *
            FROM MONSTERS
            WHERE enemy_type = 'boss'""")
            selected_enemies.append(random.choice(data))

        for enemy in selected_enemies:  # creates an enemy class
            try:
                main_enemy_list.append(Enemy(self.level, *enemy[0]))  # For most enemies
            except:
                main_enemy_list.append(Enemy(self.level, *enemy))  # For bosses
        return main_enemy_list

    def enemy_choice(self):
        if self.is_dead(self.team_2) or self.is_dead(self.team_1):
            pass
        elif self.game_mode in ["easy", "medium"]:
            valid = True
            while valid:
                enemy_choice = random.randint(1, len(self.team_2)) - 1
                if not self.team_2[enemy_choice].is_dead:
                    return enemy_choice
        else:
            sp_atk, ph_atk, enemy_choice = 0, 0, 0
            for i in range(len(self.team_2)):
                if self.team_2[i].sp_atk >= sp_atk or self.team_2[i].ph_atk >= ph_atk:
                    sp_atk, ph_atk, enemy_choice = self.team_2[i].sp_atk, self.team_2[i].ph_atk, i
            return enemy_choice

    def enemy_target(self):
        number = 0
        if self.aggro is not None and not self.team_1[self.aggro].is_dead:
            for enemy in self.team_2:
                enemy.target = self.aggro
                return
        elif self.team_2[0].target is not None and not self.team_1[self.team_2[0].target].is_dead:
            if self.game_mode == "easy":
                valid = True
                while valid:
                    number = random.randint(0, 5)
                    if not self.team_1[number].is_dead:
                        valid = False

        elif self.game_mode == "medium":  # they have no target, random attacking
            valid = True
            while valid:
                if not self.team_1[number].is_dead:
                    valid = False
                else:
                    number = random.randint(0, 5)

        elif self.game_mode == "hard":  # they target heroes low on sp_def or ph_def
            current_sp_def, current_ph_def, number = 0, 0, 0
            for i in range(0, 6):  # linear search since the data will not be ordered by sp_def and ph_def
                if current_sp_def <= 0 and current_ph_def <= 0:
                    current_ph_def, current_sp_def = self.team_1[i].ph_def, self.team_1[i].sp_def
                    number = i
                else:
                    sp_def, ph_def = self.team_1[i].sp_def, self.team_1[i].ph_def
                    if (sp_def <= current_sp_def or ph_def <= current_ph_def) and not self.team_1[i].sp_atk:
                        current_ph_def, current_sp_def = self.team_1[i].ph_def, self.team_1[i].sp_def
                        number = i

        elif self.game_mode == "extreme":  # they target heroes high in sp_atk or ph_atk
            current_sp_atk, current_ph_atk, number = 0, 0, 0
            for i in range(0, 6):  # linear search since the data will not be ordered by sp_def and ph_def
                if current_sp_atk <= 0 and current_ph_atk <= 0:
                    current_ph_atk, current_sp_atk = self.team_1[i].ph_atk, self.team_1[i].sp_atk
                    number = i
                else:
                    sp_atk, ph_atk = self.team_1[i].sp_atk, self.team_1[i].ph_atk
                    if (sp_atk >= current_sp_atk or ph_atk >= current_ph_atk) and not self.team_1[i].is_dead:
                        current_ph_atk, current_sp_atk = self.team_1[i].ph_atk, self.team_1[i].sp_atk
                        number = i

        for enemy in self.team_2:
            enemy.target = number  # makes all enemies have a common target

    def generate_heroes(self, user_team, purpose):
        main_hero_list = []
        hero_list_temp = self.user_data.query("""
        SELECT hero_id, hero_name, hp, ph_atk, ph_def, sp_atk, sp_def, crit_rate, crit_damage
        FROM HEROES
        WHERE hero_id in {}
        """.format(user_team[2:8]))
        for hero in hero_list_temp:
            if purpose == "hero":
                main_hero_list.append(Hero(self.level, *hero))
            else:
                main_hero_list.append(AiHero(self.level, *hero))
        return main_hero_list

    def print_hp(self, entity_list):
        x = 1
        for entity in entity_list:
            if entity.effect_count.counter == []:
                effect_list = None
            else:
                effect_list = []
                for count in entity.effect_count.counter:
                    for key, value in count.items():
                        if type(value) == StatusSpecialAttack:
                            effect_list.append(f"{self.colour.effect_colour(value.status_effect.name)}")
                        else:
                            effect_list.append(f"{self.colour.effect_colour(value.name)}")
            if entity.is_dead:
                defeated = "defeated"
            else:
                defeated = "None"

            if type(entity) == Hero:
                print(f"{self.colour.return_colour_text(defeated, f'{x}. {entity.name}')}: " +
                      f"\n      {self.colour.effect_colour('hp')}: {round(entity.current_hp)} / {entity.hp}" +
                      f"\n      {self.colour.effect_colour('mana')}: {entity.mana} / 100")

            elif type(entity) == Enemy or type(entity) == AiHero:
                print(f"{self.colour.return_colour_text(defeated, f'{x}. {entity.name}')} :" +
                      f"\n      {self.colour.effect_colour('hp')}:{entity.current_hp} / {entity.hp}")
            if effect_list is None:
                print("      Effects: None\n")
            else:
                print("      Effects: " + ", ".join(effect for effect in effect_list) + "\n")
            x += 1

    def get_stat(self, stat):
        stat = self.user_data.query("""
                    SELECT {}
                    FROM USER
                    WHERE user_id = {}""".format(stat, self.user_id))
        return stat[0][0]

    def convert(self, purpose, data):  # Overloading
        if purpose == "status_id to name":
            data = self.user_data.query("""
            SELECT status_name
            FROM STATUS_EFFECTS
            WHERE status_id = {}""".format(data))[0][0]
            return data

        if purpose == "number to game mode type":
            dictionary = {1: "easy",
                          2: "medium",
                          3: "hard",
                          4: "extreme"}
            value = dictionary[data]
            return value

        elif purpose == "stat":
            if 0 <= data <= 4:
                data = round(data * self.level + 15)
            return data

        elif purpose == "game mode to enemy type":
            dictionary = {"easy": "weak",
                          "medium": ["weak", "medium"],
                          "hard": ["medium", "strong"],
                          "extreme": "strong"}
            enemy_type = dictionary[data]
            return enemy_type

        elif purpose == "USER potion name":
            keys = ["Lesser Hp Potion", "Medium Hp Potion", "Grand Hp Potion", "Ph Atk Potion",
                    "Ph Def Potion", "Sp Atk Potion", "Sp Def Potion", "Crit Rate Potion", "Crit Damage Potion"]
            values = ["lesser_hp_potion", "medium_hp_potion", "grand_hp_potion", "ph_atk_potion", "ph_def_potion",
                      "sp_atk_potion", "sp_def_potion", "crit_rate_potion", "crit_damage_potion"]
            dictionary = {keys[i]: values[i] for i in range(len(values))}
            potion = dictionary[data]
            return potion

    def get_user_team(self, user_id):
        teams = Team(user_id)
        team_list = teams.get_team_formations()
        if len(team_list) == 0:
            print("You need to create a team first, please try to create a team before starting a battle")
            rpg = Rpg(user_id)
            rpg.menu()  # recursion
        teams.print_team_formations()
        response = right_format_response_number(f"Enter the number of the team you wish to play with: ",
                                                1, len(team_list))
        print()
        if response == False:
            self.menu()
        else:
            response -= 1
            try:
                user_team = teams.get_single_team(response)
                return user_team
            except:
                print("Something went wrong, please try again")

    def generate_rewards(self, battle_outcome):
        number = 0
        self.level += 1
        if battle_outcome == "win":  # gain 60-200% of gold, exp
            number = random.randint(6, 20)
            gold, exp = 0, 0
            dictionary = {
                "easy": 1,
                "medium": 1.5,
                "hard": 2,
                "extreme": 3
            }

            try:
                for enemy in self.team_2:
                    gold += round(enemy.gold * (number / 10) * (1.05 * self.level) * (dictionary[self.game_mode]))
                    exp += round(enemy.exp * (number / 10) * (1.05 * self.level) * dictionary[self.game_mode])
            except:
                gold = round(1000 * (number / 10) * (1.1 * self.level) * dictionary[self.game_mode])
                exp = round(750 * (number / 10) * (1.1 * self.level) * dictionary[self.game_mode])
            print(f"""
            Defeated {len(self.team_2)} enemies on {self.game_mode} mode.
            Rewards:
                {self.colour.return_colour_text('None', "Gold")} : {gold}
                {self.colour.return_colour_text('None', 'Exp')} : {exp}""")
            new_gold = self.gold + gold
            current_exp = self.exp + exp
            check, new_exp, previous_level = self.check_level_up(current_exp)
            if check:
                print(f"""
                You have Leveled Up!
                {self.colour.return_colour_text('None', 'Level')} : {previous_level}  -> {self.level}
                {self.colour.return_colour_text('None', 'Exp')} :    {current_exp}  -> {new_exp}""")
            self.user_data.update_record("USER", "lvl", self.level, "user_id", self.user_id)
            self.user_data.update_record("USER", "exp", new_exp, "user_id", self.user_id)
            self.user_data.update_record("USER", "gold", new_gold, "user_id", self.user_id)
            response = input("Returning to the main menu, enter any button to return to the main menu: ")
            rpg = Rpg(self.user_id)
            rpg.menu()

        elif battle_outcome == "lose":  # lose up to 5% of balance
            number = random.randint(0, 5)
        elif battle_outcome == "flee":  # lose up to 10% of balance
            number = random.randint(0, 10)

        if number == 0:
            print("You have lost, however, you shall not be penalised this time")
        else:
            number = 0.01 * number  # converting to a usable percentage
            new_gold = round(self.gold - (number * self.gold))
            print("""
            The enemies have taken {}% of your balance
            You are now at {} gold.
            """.format(number * 100, new_gold))
            self.user_data.update_record("USER", "gold", new_gold, "user_id", self.user_id)
        response = input("Enter any button to return to the main menu")
        rpg = Rpg(self.user_id)
        rpg.menu()

    def check_level_up(self, exp):
        previous_level = self.level
        if exp >= 200 + (300 * self.level):
            exp -= 200 + (300 * self.level)
            self.level += 1
            self.check_level_up(exp)
            return True, exp, previous_level
        return False, exp, previous_level

    def see_detailed_stats(self):
        responses = ["h", "e", "no"]
        response = right_response_list("Enter 'h' to see Hero stats or 'e' to see enemy stats or 'no' to go back: ",
                                       responses)
        dictionary = {
            "ph_atk": "Highest Physical Attack",
            "ph_def": "Highest Physical Defence",
            "sp_atk": "Highest Special Attack",
            "sp_def": "Highest Special Defence"
        }
        if response == "h":
            team = self.team_1
            dictionary.update({
                "crit_rate": "Highest Critical Hit Chance",
                "crit_damage": "Highest Critical Hit Damage"
            })
        elif response == "e":
            team = self.team_2
        if response != "no":
            self.present_stats(dictionary, team)

    @staticmethod
    def get_highest_stat(attribute, entity_list):
        old_stat = 0
        old_entity = None
        for entity in entity_list:
            if not entity.is_dead:
                new_stat = getattr(entity, attribute)
                if new_stat > old_stat:
                    old_stat = new_stat
                    old_entity = entity
        return old_stat, old_entity.name

    def present_stats(self, dictionary, data):
        for key, value in dictionary.items():
            stat, hero_name = self.get_highest_stat(key, data)
            print(f"""
            {value} - {hero_name}
                Currently - {stat}""")


class Potion:
    def __init__(self, item_name, percentage):
        self.item_name = item_name
        self.percentage = percentage


class BuffPotion(Potion):  # Inheritance and subclass
    def __init__(self, item_name, percentage, stat, duration):
        super().__init__(item_name, percentage)
        self.stat = stat
        self.duration = duration


class Effect:
    def __init__(self, effect_id):
        self.user_data = SQLite()
        self.id = effect_id
        self.name = self.get_data("status_name")
        self.description = self.get_data("status_description")
        self.effect_1 = self.get_data("status_effect_1")
        self.effect_1_percentage = self.get_data("status_effect_1_percentage")
        self.effect_2 = self.get_data("status_effect_2")
        self.effect_2_percentage = self.get_data("status_effect_2_percentage")
        self.duration = self.get_data("duration")  # differs from special attack duration for chained effects
        self.condition_1 = self.get_data("condition_1")
        self.condition_2 = self.get_data("condition_2")

    def get_data(self, attribute):
        data = self.user_data.query(f"""
        SELECT {attribute}
        FROM STATUS_EFFECTS
        WHERE status_id = {self.id}""")[0][0]
        return data


class SpecialAttack:
    def __init__(self, sp_atk_id):
        self.user_data = SQLite()
        self.id = sp_atk_id
        self.name = self.get_data("sp_atk_name")
        self.percentage = self.get_data("sp_atk_percentage")
        self.status_effect = Effect(self.get_data("status_id"))
        self.mana_cost = self.get_data("mana_cost")
        self.type = None

    def get_data(self, attribute):
        data = self.user_data.query(f"""
        SELECT {attribute}
        FROM SP_ATK
        WHERE sp_atk_id = {self.id}""")[0][0]
        return data


class StatusSpecialAttack(SpecialAttack):
    def __init__(self, sp_atk_id):
        super().__init__(sp_atk_id)
        self.duration = self.get_data("sp_atk_duration")
        self.type = "status_effect"


class AOESpecialAttack(SpecialAttack):
    def __init__(self, sp_atk_id):
        super().__init__(sp_atk_id)
        self.type = "aoe"


class HealingSpecialAttack(SpecialAttack):
    def __init__(self, sp_atk_id, duration):
        super().__init__(sp_atk_id)
        self.duration = duration
        self.type = "heal_percentage"


class DrainingSpecialAttack(SpecialAttack):
    def __init__(self, sp_atk_id):
        super().__init__(sp_atk_id)
        self.type = "draining"


class AggroSpecialAttack(SpecialAttack):
    def __init__(self, sp_atk_id):
        super().__init__(sp_atk_id)
        self.type = "aggro"


class Queue:  # Will be used in the counting of buffs as well as effects on the user/enemy
    def __init__(self):
        self.user_data = SQLite()
        self.counter = []  # Will hold dictionaries

    def add_to_list(self, name, duration):
        self.counter.append({name: duration})

    def remove_from_list(self, item):
        data = list(item.keys())[0]
        self.counter.remove(item)
        return data

    def decrease_duration(self):  # Occurs at the end of a turn
        stat_list = []
        for count in self.counter:
            for key, value in count.items():
                count[key] -= 1
                if count[key] == -1:  # When the potion wears off
                    stat = self.remove_from_list(count)
                    stat_list.append(stat)
        return stat_list  # Used in the hero class to restore a certain stat


class PotionQueue(Queue):  # inheritance
    def __init__(self):
        self.potion_counter = super().__init__()
        self.potion = Potion


class EffectQueue(Queue):  # inheritance
    def __init__(self, name):  # This will be used to count the durations on special attacks
        self.effect_counter = super().__init__()
        self.colour = Colours()
        self.name = name

    def check_other_effects(self):  # Check for combinable effects
        status_effect = None
        values = self.check_condition()
        if values:
            for value in values:
                status_effect = Effect(value[0])  # value[0] contains the id of the specific status effect
                print(f"The '{self.colour.effect_colour(status_effect.name)}' status has been added to {self.name}")
                for count in self.counter:
                    for value_2 in count.values():
                        try:
                            sp_atk_effect = value_2.status_effect.name
                        except:
                            sp_atk_effect = value_2.name
                        if sp_atk_effect in status_effect.condition_1 or sp_atk_effect in status_effect.condition_2:
                            self.remove_from_list(sp_atk_effect)
            self.add_to_list(status_effect.name, status_effect)
            return status_effect

    def remove_from_list(self, sp_atk_effect):
        for count in self.counter:
            for value in count.values():
                if type(value) == StatusSpecialAttack:
                    self.counter.remove(count)
                    print(f"The '{self.colour.effect_colour(value.status_effect.name)}' status has been removed "
                          f"from {self.name}")

    def check_condition(self):
        values = []
        conditions = []
        for count in self.counter:
            for key, value in count.items():
                if type(value) == StatusSpecialAttack:
                    value = value.status_effect
                values.append(value.name)
        temp_conditions = self.user_data.query("""
        SELECT status_id, condition_1, condition_2
        FROM STATUS_EFFECTS
        WHERE condition_1 = '{0}' OR condition_2 = '{0}'""".format(*values))
        for condition in temp_conditions:
            if condition[1] in values and condition[2] in values:
                conditions.append(condition)
        return conditions  # returns id and conditions

    def add_to_list(self, name, object):  # Overriding
        self.counter.append({name: object})
        # name of special attack and special attack object

    def decrease_duration(self):
        effect_list = []
        for count in self.counter:
            for key in count.keys():
                count[key].duration -= 1
                if count[key].duration == -1:
                    if type(count[key]) == StatusSpecialAttack:
                        status_effect = count[key].status_effect.name
                    else:
                        status_effect = count[key].name
                    self.remove_from_list(status_effect)
                    effect_list.append(count)
        return effect_list


class Entity:
    def __init__(self, level, hp, ph_atk, ph_def, sp_atk, sp_def):
        self.name = None
        self.level = level
        self.hp = 100 + 5 * round(self.convert(hp))
        self.ph_atk = 5 + round(self.convert(ph_atk))
        self.ph_def = 3 + round(self.convert(ph_def))
        self.sp_atk = 3 + round(self.convert(sp_atk))
        self.sp_def = 3 + round(self.convert(sp_def))
        self.current_hp = self.hp
        self.is_dead = False  # Used to signal the amount of dead enemies
        self.effect_count = EffectQueue(self.name)  # Composition
        self.miss_rate = 0  # How likely an enemy will miss an attack in %
        self.instakill_rate = False
        self.stat_queue = Queue()
        self.colours = Colours()

    def damage(self, amount):
        self.current_hp -= amount
        if self.current_hp < 0:
            self.current_hp = 0

    def heal(self, amount):
        self.current_hp += amount
        if self.current_hp > self.hp:
            self.current_hp = self.hp

    def check_status(self, user_id):
        if self.current_hp == 0:
            self.is_dead = True
            print(f"{self.name} has been defeated")

    def convert(self, stat):  # Overloading
        dictionary = {
            "e low": 0.5,
            "v low": 0.75,
            "low": 1.25,
            "medium": 1.5,
            "high": 1.75,
            "v high": 3,
            "e high": 5}
        if stat in dictionary.keys():
            stat = dictionary[stat] * self.level + 15
        return stat

    def status_effect_initial(self, element_class):  # Taking damage at the end of turn
        # Only occurs when a special attack has been received with an effect
        try:
            if issubclass(type(element_class), SpecialAttack):
                element_class = element_class.status_effect
            duration = element_class.duration
        except AttributeError:
            duration = 3

        dictionary = {
            "wet": ['self.miss(10)'],
            "jolt": ['self.miss(5)'],
            "burn": [f'self.change_stat("ph_atk", 0.95, {duration})'],
            "chill": [f'self.change_stat("ph_def", 0.95, {duration})'],
            "dark": ['self.miss(50)', f'self.change_stat("ph_atk", 1.5, {duration})'],
            "light": ['self.miss(50)', f'self.change_stat("sp_atk", 1.5, {duration})'],
            "shock": ['self.miss(25)'],
            "backfire": ['effect = self.do_backfire()'],
            "freeze": ['self.miss(100)', f'self.change_stat("ph_def", 0.5, {duration})'],
            "holy fire": ['self.miss(20)', f'self.change_stat("ph_def", 2, {duration})',
                          f'self.change_stat("ph_atk", 2, {duration})']
        }  # Dictionary to hold commands related to the status effects, makes it easier to add more effects

        if issubclass(type(element_class), SpecialAttack):
            element_class = element_class.status_effect  # So I am only dealing with the Effect class

        if element_class.name in dictionary.keys():
            for command in dictionary[element_class.name]:
                global effect  # Couldn't return values with exec so I made a global statement
                effect = None
                exec(command)
                if effect == "aoe":
                    return "aoe"

    def end_of_turn(self):
        # Occurs at the end of every turn
        dictionary = {
            "jolt": ['self.damage(self.hp * 0.02)'],
            "burn": ['self.damage(0.05 * self.hp)'],
            "chill": ['self.damage(0.05 * self.hp)'],
            "shock": ['self.damage(0.05 * self.hp)'],
            "holy fire": ['self.damage(0.15 * self.hp)'],
            "dark flame": ['self.damage(0.3 * self.hp)', 'self.instakill(10)']
        }

        colours = [self.colours.effect_colour("jolt"), self.colours.effect_colour("burn"),
                   self.colours.effect_colour("chill"), self.colours.effect_colour("shock"),
                   self.colours.effect_colour("holy fire"), self.colours.effect_colour("dark flame")]
        messages = {
            "jolt": f"{self.name.title()} received {round(self.hp * 0.02)} damage due to the '{colours[0]}' status.",
            "burn": f"{self.name.title()} received {round(self.hp * 0.05)} damage due to the '{colours[1]}' status.",
            "chill": f"{self.name.title()} received {round(self.hp * 0.05)} damage due to the '{colours[2]}' status.",
            "shock": f"{self.name.title()} received {round(self.hp * 0.05)} damage due to the '{colours[3]}' status.",
            "holy fire": f"{self.name.title()} received {round(self.hp * 0.15)} damage due to the '{colours[4]}' status.",
            "dark flame": f"{self.name.title()} received {round(self.hp * 0.3)} damage due to the '{colours[5]}' status."
        }

        for count in self.effect_count.counter:
            for key, value in count.items():
                if issubclass(type(value), SpecialAttack):  # If it is a sp_atk, it will be converted to an effect
                    value = value.status_effect

                if value.name in dictionary.keys():
                    for command in dictionary[value.name]:
                        exec(command)  # executes the commands stored in the dictionary

                if value.name in messages.keys():
                    print(messages[value.name])

    def miss(self, percentage):
        self.miss_rate += percentage
        if self.miss_rate >= 100:
            self.miss_rate = 100
        print(f"{self.name.title()} now has a {self.miss_rate}% chance to miss an attack")
        self.stat_queue.add_to_list("miss_rate", 3)

    def change_stat(self, stat, percentage, duration):
        old_stat = round(self.__getattribute__(stat))
        new_stat = round(old_stat * percentage)
        if old_stat > new_stat:
            word = "decreased"
        else:
            word = "increased"
        print(f"{self.name.title()}'s {stat} has {word} from {old_stat} to {new_stat}")
        self.__setattr__(stat, new_stat)
        self.stat_queue.add_to_list(stat, duration + 2)

    def instakill(self, percentage_chance):
        self.instakill_rate += percentage_chance

    def do_backfire(self):
        global effect
        number = random.randint(1, 10)
        if number <= 3:  # 30% chance
            self.damage(0.5 * self.sp_atk)
            print(f"{self.name} has been hurt by Backfire")
        elif number <= 4:  # 10% chance
            effect = "aoe"

    def remove_effect(self, effect_to_remove, type):
        if type == "combo":
            for i in range(len(self.effect_count.counter) - 1, 0):
                if effect_to_remove == self.effect_count.counter[i]:
                    effect = self.effect_count.counter[i]
                    for value in effect.values():
                        if type(value) == StatusSpecialAttack:
                            effect = value.status_effect
                        else:
                            effect = value
                    print(f"The '{effect.name}' effect has been removed from {self.name}.")
                    del self.effect_count.counter[i]
        else:
            for i in range(len(self.effect_count.counter), 0):
                value = self.effect_count.counter[i].values()
                if type(value) == StatusSpecialAttack:
                    value = value.status_effect
                if value.name == effect_to_remove:
                    print(f"The '{value.name}' effect has been removed from {self.name}.")
                    del self.effect_count.counter[i]


class Hero(Entity):  # Inheritance and subclass
    def __init__(self, level, hero_id, name, hp, ph_atk, ph_def, sp_atk, sp_def, crit_rate, crit_damage):
        super().__init__(level, hp, ph_atk, ph_def, sp_atk, sp_def)
        self.user_data = SQLite()  # Composition
        self.hero_id = hero_id
        self.name = name
        self.crit_rate = int(crit_rate)
        self.crit_damage = int(crit_damage)
        self.sp_moves = 3
        self.potion_count = PotionQueue()  # Composition
        self.sp_atk_list = self.generate_sp_atks()
        self.mana = 100

    def generate_sp_atks(self):
        sp_atk_list = []
        temp_sp_atk_list = self.get_sp_atks()  # 2D array, index: 0-id, 1-effect1, 2-effect2

        # Grouping special attacks by their type makes it easier to work with in the battle system as there is less
        # Indexing needed for finding out the type of special attack
        for sp_atk in temp_sp_atk_list:
            if sp_atk[1] == "aggro" or sp_atk[2] == "aggro":
                sp_atk_list.append(AggroSpecialAttack(sp_atk[0]))
            elif sp_atk[1] == "aoe" or sp_atk[2] == "aoe":
                sp_atk_list.append(AOESpecialAttack(sp_atk[0]))
            elif sp_atk[1] == "drain_atk" or sp_atk[2] == "drain_atk":
                sp_atk_list.append(DrainingSpecialAttack(sp_atk[0]))
            elif sp_atk[1] == "heal_percentage" or sp_atk[2] == "heal_percentage":
                sp_atk_list.append(HealingSpecialAttack(sp_atk[0], sp_atk[3]))
            else:
                sp_atk_list.append(StatusSpecialAttack(sp_atk[0]))
        return sp_atk_list

    def get_sp_atks(self):
        sp_atk_list = self.user_data.query(f"""
        SELECT SP_ATK.sp_atk_id, STATUS_EFFECTS.status_effect_1, STATUS_EFFECTS.status_effect_2, SP_ATK.sp_atk_duration
        FROM ((HEROES_SP_ATK
        INNER JOIN SP_ATK 
        ON SP_ATK.sp_atk_id = HEROES_SP_ATK.sp_atk_id)
        INNER JOIN STATUS_EFFECTS
        ON STATUS_EFFECTS.status_id = SP_ATK.status_id)
        WHERE HEROES_SP_ATK.hero_id = {self.hero_id}""")  # Advanced SQL
        return sp_atk_list

    def reset_stat(self, stat_name):
        if stat_name == "miss_rate":
            self.miss_rate = 0
        else:
            original_stat = self.user_data.query(f"""
            SELECT ({stat_name})
            FROM HEROES
            WHERE hero_id = {self.hero_id}""")[0][0]
            original_stat = self.convert(original_stat)
            self.__setattr__(stat_name, original_stat)  # Got this using pycharm features and through various tests
            print(f"{self.name}'s {stat_name} has returned back to {original_stat}")

    def decrease_duration(self):  # Will be used for decreasing the count of sp_atk and buff durations
        indexes = self.potion_count.decrease_duration()
        for counter in indexes:
            self.reset_stat(counter)

        effect_list = self.effect_count.decrease_duration()
        for effect in effect_list:
            pass

        stat_list = self.stat_queue.decrease_duration()
        for stat in stat_list:
            self.reset_stat(stat)

    def use_potion(self, potion):
        if type(potion) is BuffPotion:
            dictionary = self.create_dictionary("stat name")
            stat_name = dictionary[potion.item_name]
            stat = self.__getattribute__(stat_name)
            new_stat = round(stat * ((100 + potion.percentage) / 100))
            self.__setattr__(stat_name, new_stat)
            self.potion_count.add_to_list(stat_name, potion.duration)
            print(f"{self.name}'s {stat_name} has increased from {stat} to {new_stat}")

        elif type(potion) is Potion:
            print(potion.percentage)
            hp_to_add = round(int(potion.percentage) * int(self.hp))
            self.current_hp += hp_to_add
            if self.current_hp > self.hp:
                self.current_hp = self.hp

    def create_dictionary(self, purpose):
        dictionary = []
        if purpose == "stat name":
            keys = ["Ph Atk Potion", "Ph Def Potion", "Sp Atk Potion", "Sp Def Potion", "Crit Rate Potion",
                    "Crit Damage Potion"]
            values = ["ph_atk", "ph_def", "sp_atk", "sp_def", "crit_rate", "crit_damage"]
            dictionary = {keys[i]: values[i] for i in range(len(values))}
        return dictionary


class AiHero(Hero):
    def __init__(self, level, hero_id, name, hp, ph_atk, ph_def, sp_atk, sp_def, crit_rate, crit_damage):
        super().__init__(level=level, hp=hp, ph_atk=ph_atk, ph_def=ph_def, sp_atk=sp_atk, sp_def=sp_def,
                         hero_id=hero_id, name=name, crit_rate=crit_rate, crit_damage=crit_damage)
        self.target = None

    def decrease_duration(self):  # Will be used for decreasing the count of sp_atk and buff durations
        effect_list = self.effect_count.decrease_duration()
        for effect in effect_list:
            self.remove_effect(effect, "duration")

        stat_list = self.stat_queue.decrease_duration()
        for stat in stat_list:
            self.reset_stat(stat)

    def reset_stat(self, stat_name):
        if stat_name == "miss_rate":
            self.miss_rate = 0
            original_stat = 0
        else:
            original_stat = self.user_data.query(f"""
            SELECT ({stat_name})
            FROM HEROES
            WHERE hero_id = {self.hero_id}""")[0][0]
            original_stat = self.convert(original_stat)
        self.__setattr__(stat_name, original_stat)  # Got this using pycharm features and through various tests
        print(f"{self.name}'s {stat_name} has returned back to {original_stat}")


class Enemy(Entity):  # Inheritance and subclass
    def __init__(self, level, monster_id, name, enemy_type, hp, ph_atk, ph_def, sp_atk, sp_def, gold, exp):
        super().__init__(level, hp, ph_atk, ph_def, sp_atk, sp_def)
        self.monster_id = monster_id
        self.name = name
        self.enemy_type = enemy_type
        self.gold = gold
        self.exp = exp
        self.target = None
        self.crit_rate = 5
        self.crit_damage = 125
        self.user_data = SQLite()

    def decrease_duration(self):  # Will be used for decreasing the count of sp_atk and buff durations
        effect_list = self.effect_count.decrease_duration()
        for effect in effect_list:
            self.remove_effect(effect, "duration")

        stat_list = self.stat_queue.decrease_duration()
        for stat in stat_list:
            self.reset_stat(stat)

    def reset_stat(self, stat_name):
        if stat_name == "miss_rate":
            self.miss_rate = 0
            original_stat = 0
        else:
            original_stat = self.user_data.query(f"""
            SELECT ({stat_name})
            FROM MONSTERS
            WHERE monster_id = {self.monster_id}""")[0][0]
            original_stat = self.convert(original_stat)
        self.__setattr__(stat_name, original_stat)  # Got this using pycharm features and through various tests
        print(f"{self.name}'s {stat_name} has returned back to {original_stat}")

    def check_status(self, user_id):  # Polymorphism
        if self.current_hp == 0:
            self.is_dead = True
            print(f"{self.name} has been defeated")
            self.user_data.increment_value("USER", "enemies_defeated", "user_id", user_id)
            if self.enemy_type == "boss":
                self.user_data.increment_value("USER", "bosses_defeated", "user_id", user_id)


class Shop:
    def __init__(self, user_id):
        self.user_id = user_id
        self.user_data = SQLite()
        self.colour = Colours()

    def menu(self):  # Polymorphism
        print("""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~       SHOP       ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

            1. Buy Items  
            2. Buy Heroes  
            3. Sell Heroes 
            4. Re-roll Hero stats/special attacks   
            5. Return to the main menu\n""")
        response = right_format_response_number("Please enter a number between 1 and 5: ", 1, 5)

        if response == False:
            response = 5

        elif response == 1:  # Buy Items
            items = self.get_items()
            item_chosen = self.print_shop_items()
            item_price = items[item_chosen][2]  # This chooses the price field from a 2D array
            quantity = self.check('balance', item_price)  # Returns false or the amount of items they can buy
            if not quantity:
                response = input("""
                You do not have enough money to buy this item
                Enter any number to return to the shop menu: """)
            else:
                print(f"You can buy up to {quantity} {items[item_chosen][1]}s")
                quantity = right_format_response_number("How many potions do you want to buy: ", 1, quantity)
                if quantity == False:
                    self.menu()
                balance = self.get_balance()
                new_balance = balance - (quantity * item_price)
                item_name = self.convert("item id to item name", item_chosen)
                prev_quantity = self.user_data.query(f"""
                SELECT {item_name}
                FROM USER
                WHERE user_id = {self.user_id}""")[0][0]
                new_quantity = quantity + prev_quantity
                self.user_data.update_record("USER", "gold", f"{new_balance}", "user_id", f"{self.user_id}")
                self.user_data.update_record("USER", item_name, f"{new_quantity}", "user_id", f"{self.user_id}")
                print(f"""You have bought {quantity} {items[item_chosen][1]}s
    Quantity: {prev_quantity} -> {new_quantity}
    Balance: {balance} -> {new_balance}""")
                response = input("Enter any key to return to the main menu: ")

        elif response == 2:  # Buy Heroes
            heroes = self.get_heroes()
            hero_price = 500 + 500 * (2 ** len(heroes))  # 500, 1500, 2500, 4500....
            balance = self.get_balance()
            print(f"Balance: {balance}")
            print(f"It will cost {hero_price} for hero number {len(heroes) + 1}")
            response = right_response_list("Do you wish to buy another hero", response_list)
            if response in positive_responses and balance >= hero_price:
                stats = self.generate_hero_stats()
                sp_attacks = self.generate_special_attacks()
                name = input("Please enter a name for the hero: ")
                records = (f'{self.user_id}', *stats, name)  # Some template user data
                insert = """INSERT INTO HEROES (user_id, hp, ph_atk, ph_def, sp_atk, sp_def, crit_rate, crit_damage, hero_name)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"""
                cursor.execute(insert, records)
                hero_id = self.user_data.query("""
                SELECT hero_id 
                FROM HEROES
                WHERE hero_id = (SELECT max(hero_id) FROM HEROES)""")
                for i in sp_attacks:
                    insert = """INSERT INTO HEROES_SP_ATK (hero_id, sp_atk_id)
                             VALUES (?, ?)"""
                    records = (f'{hero_id[0][0] + 1}', f'{i}')
                    cursor.execute(insert, records)
                    connection.commit()
                print(f"The new hero '{name}' has been created, their stats are:\n")
                self.print_hero_stats(stats, sp_attacks)
            response = input("Enter any key to return to the main menu: ")
            rpg = Rpg(self.user_id)
            rpg.menu()

        elif response == 3:  # Sell Heroes
            hero_list = self.user_data.query("""
            SELECT hero_name, hero_id
            FROM HEROES
            WHERE user_id = {}""".format(self.user_id))  # Gets the heroes as a 2d list or returns False
            if not hero_list:
                print("You have no heroes to sell, returning to the main menu, enter any key to continue: ")
            else:
                for i in range(len(hero_list)):
                    print(f"Hero {i + 1}: {hero_list[i][0]}")
                balance = self.user_data.query("""
                SELECT gold
                FROM USER
                WHERE user_id = {}""".format(self.user_id))[0][0]
                heroes = self.user_data.query("""
                SELECT hero_id
                FROM HEROES
                WHERE user_id = {}""".format(self.user_id))
                price = 250 + 250 * (2 ** len(heroes))
                print(f"Selling a hero will give you {price} gold")
                number = right_format_response_number(f"Enter a number between 1 and {len(hero_list)}", 1,
                                                      len(hero_list))
                if number == False:
                    self.menu()
                response = right_response_list("Are you sure you want to do this", response_list)
                if response in positive_responses:
                    hero_id = self.convert("number to hero id", number)
                    print(f"{balance} -> {balance + price}")
                    balance += price
                    self.user_data.delete_record("HEROES", "hero_id", hero_id)  # Deletes from hero table
                    self.user_data.delete_record("HEROES_SP_ATK", "hero_id", hero_id)  # Deletes from link table
                    self.user_data.update_record("USER", "gold", balance, "user_id", self.user_id)
                response = input("Returning to the shop menu, enter any key to continue: ")
            self.menu()  # Recursion

        elif response == 4:  # Re-roll Heroes
            heroes = self.check('user hero', 0)
            if not heroes:
                response = input("You have not got any heroes to re-roll, Enter any key to return to the shop menu: ")
                self.menu()
            else:
                self.re_roll_stats()

        elif response == 5:  # Returning to the main menu
            rpg = Rpg(self.user_id)
            rpg.menu()

        self.menu()  # Recursion

    def re_roll_stats(self):
        heroes = self.user_data.query("""
        SELECT hero_id, hero_name
        FROM HEROES
        WHERE user_id = {}""".format(self.user_id))
        balance = self.get_balance()
        print("Balance: {}".format(balance))
        response = right_response_list("Do you wish to spend 1000 gold to re-roll these stats: ", response_list)

        if response in negative_responses:
            self.menu()
        # To prevent the user re-rolling stats for heroes that don't exist
        balance -= 1000
        self.user_data.update_record("USER", "gold", balance, "user_id", self.user_id)
        for i in range(len(heroes)):
            print(f"Hero {i + 1} - {heroes[i][1]}")

        number = right_format_response_number("Please enter an appropriate number: ", 1, len(heroes))
        if number == False:
            self.menu()
        else:
            hero_id = self.convert("number to hero id", number)
            stats = self.generate_hero_stats()
            special_attacks = self.generate_special_attacks()
            self.user_data.query("""
            UPDATE HEROES
            SET hp = '{}', ph_atk = '{}', ph_def = '{}', sp_atk = '{}', sp_def = '{}', crit_rate = '{}', 
            crit_damage = '{}'
            WHERE hero_id = '{}' """.format(*stats, hero_id))
            self.user_data.delete_record("HEROES_SP_ATK", "hero_id", hero_id)

            for i in special_attacks:
                insert = """INSERT INTO HEROES_SP_ATK (hero_id, sp_atk_id)
                         VALUES (?, ?)"""
                records = (f'{hero_id}', f'{i}')
                cursor.execute(insert, records)
                connection.commit()

            print("The heroes stats have been re-rolled, the new stats are:\n")
            self.print_hero_stats(stats, special_attacks)
            self.re_roll_stats()  # Recursion

    def get_items(self):
        items = self.user_data.query("""
        SELECT *
        FROM SHOP_PRICES
        WHERE item_id BETWEEN 1 AND 9""")
        return items

    def print_hero_stats(self, stats, special_attacks):
        stat_list = ["Hp", "Physical Attack", "Physical Defence", "Special Attack", "Special Defence",
                     "Critical Hit Chance", "Critical Hit Damage"]
        for i in range(len(stat_list)):
            print(f"{stat_list[i]} - {stats[i]}")
        for i in range(len(special_attacks)):
            special_attack_number = self.colour.return_colour_text("None", "Special Attack " + str(i + 1))
            print(f"{special_attack_number} - {self.convert('special attack', special_attacks[i])}")
        print()

    def print_shop_items(self):
        items = self.get_items()
        for i in range(len(items)):
            print(f"""
        item {i + 1} : {items[i][1]}
            price : {items[i][2]}
            description : {items[i][3]}""")
        item_chosen = right_format_response_number("\nPlease enter a number between 1 and 9: ", 1, 9)
        if item_chosen == False:
            self.menu()
        else:
            item_chosen -= 1
            return item_chosen

    def check(self, purpose, data):  # Overloading
        if purpose == 'balance':
            balance = int(self.get_balance())
            data = int(data)
            if data > balance:
                return False
            elif data <= balance:
                quantity = floor(balance / data)
                return quantity

        elif purpose == 'user hero':
            heroes = self.user_data.query("""
            SELECT hero_id
            FROM HEROES
            WHERE hero_id = {}""".format(self.user_id))
            return heroes

    def get_balance(self):
        balance = self.user_data.query("""
        SELECT gold
        FROM USER
        WHERE user_id = {}""".format(self.user_id))
        return balance[0][0]

    def convert(self, purpose, data):  # Overloading
        dictionary = {}
        if purpose == 'item id to item name':
            dictionary = {
                0: "lesser_hp_potion",
                1: "medium_hp_potion",
                2: "grand_hp_potion",
                3: "ph_atk_potion",
                4: "ph_def_potion",
                5: "sp_atk_potion",
                6: "sp_def_potion",
                7: "crit_chance_potion",
                8: "crit_damage_potion"}

        elif purpose == "number to hero id":
            hero_data = self.user_data.query("""
            SELECT hero_id
            FROM HEROES
            WHERE user_id = {}""".format(self.user_id))
            dictionary = {i + 1: hero_data[i][0] for i in range(len(hero_data))}  # link user input to hero id

        elif purpose == 'special attack':
            attack_name = self.user_data.query("""
            SELECT sp_atk_name
            FROM SP_ATK
            WHERE sp_atk_id = {}""".format(data))[0][0]
            return attack_name
        return dictionary[data]

    def get_heroes(self):
        heroes = self.user_data.query("""
        SELECT hero_id
        FROM HEROES
        WHERE user_id = {}""".format(self.user_id))
        return heroes

    @staticmethod
    def generate_hero_stats():
        stats = []
        for i in range(5):
            number = random.randint(1, 20)
            if number <= 2:  # 10%  chance
                stats.append("e low")
            elif number <= 6:  # 20% chance
                stats.append("v low")
            elif number <= 12:  # 30% chance
                stats.append("medium")
            elif number <= 17:  # 25% chance
                stats.append("v high")
            else:  # 15% chance
                stats.append("e high")
        stats.append(random.randint(3, 10))  # Critical hit chance
        stats.append(random.randint(105, 160))  # Critical damage amount
        return stats

    def generate_special_attacks(self):
        sp_atk_ids = []
        loop = 2
        special_attack_list = self.user_data.query("""
        SELECT sp_atk_id
        FROM SP_ATK""")
        number = random.randint(1, 20)
        if 11 <= number <= 16:  # 30% chance of 3 special attacks
            loop = 3
        elif 17 <= number <= 20:  # 20% chance of 4 special attacks
            loop = 4
        for i in range(loop):
            valid = False
            while not valid:
                sp_atk_id = random.choice(special_attack_list)
                if sp_atk_id[0] not in sp_atk_ids:
                    sp_atk_ids.append(sp_atk_id[0])
                    valid = True
        return sp_atk_ids


# ------------------------------------------------------------------  Setup2  ------------------------------------------

menu = MainMenu()


# ---------------------------------------------------------  Functions/Procedures  -------------------------------------

# This function makes sure that any input is in the selected list
def right_response_list(text, array_list):
    while True:
        try:
            response = input(text).strip().lower()
            if response in array_list:
                return response
            else:
                print("Please enter the correct value")
        except:
            print("Something went wrong, please try again")


# This function makes sure that the number inputted is an integer in the correct range
def right_format_response_number(text, lower_limit, upper_limit):
    while True:
        try:
            print(text)
            response = input("Enter a value to continue or enter 'no' to go back: ")
            if response in negative_responses:  # to go back
                return False
            elif lower_limit <= int(response) <= upper_limit:  # to enter a number in the correct range
                return int(response)
            else:  # If the value is a number but not in range
                print("Please enter the value within the correct range")
        except:  # If the value entered is of an incorrect type
            print("Please enter the data in the correct format")


def response_check(text, list):
    while True:
        response = input(text)
        if response not in list:
            return response


# ---------------------------------------------------------- Main Program ----------------------------------------------
while True:
    menu.menu()

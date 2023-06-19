import hashlib
import struct
from io import BytesIO
from typing import List, BinaryIO


class Food:
    name = None
    hp_left = None
    stam_left = None


class Skill:
    name = None
    level = None
    unused = None


class World:
    worldId = None
    hasCustomSpawn = None
    spawnPoint = None
    hasLogoutPoint = None
    logoutPoint = None
    hasDeathPoint = None
    deathPoint = None
    homePoint = None
    hasMapData = None
    mapDataLength = None
    mapData = None


class Item:
    name = None
    stack = None
    durability = None
    pos = None
    equipped = None
    quality = None
    variant = None
    crafter_id = None
    crafter_name = None
    unknown = None


class Character:
    def __init__(self, filename):
        self.filename = filename
        self.reader = open(self.filename, "rb")

        self.file_size = self.get_int32()
        self.character_version = self.get_int32()
        self.kills = self.get_int32()
        self.deaths = self.get_int32()
        self.crafts = self.get_int32()
        self.builds = self.get_int32()
        self.num_worlds = self.get_int32()

        self.worlds: List[World] = []
        for i in range(self.num_worlds):
            w = World()
            w.worldId = self.get_int64()
            w.hasCustomSpawn = self.get_bool()
            w.spawnPoint = (self.get_float(), self.get_float(), self.get_float())
            w.hasLogoutPoint = self.get_bool()
            w.logoutPoint = (self.get_float(), self.get_float(), self.get_float())
            w.hasDeathPoint = self.get_bool()
            w.deathPoint = (self.get_float(), self.get_float(), self.get_float())
            w.homePoint = (self.get_float(), self.get_float(), self.get_float())

            w.hasMapData = self.get_bool()
            if w.hasMapData:
                w.mapDataLength = self.get_int32()
                w.mapData = self.unpack(w.mapDataLength)

            self.worlds.append(w)

        self.name = self.get_string()
        self.id = self.get_int64()
        self.start_seed = self.get_string()

        self.is_instantiated = self.get_bool()
        if not self.is_instantiated:
            self.reader.close()
            return

        self.data_length = self.get_int32()
        self.data_version = self.get_int32()
        self.max_hp = self.get_float()
        self.hp = self.get_float()
        self.stamina = self.get_float()
        self.is_first_spawn = self.get_bool()
        self.time_since_death = self.get_float()
        self.guardian_power = self.get_string()
        self.guardian_cooldown = self.get_float()

        self.inventory: List[Item] = []
        self.inventory_version = self.get_int32()
        self.num_items = self.get_int32()

        for i in range(self.num_items):
            item = Item()
            item.name = self.get_string()
            item.stack = self.get_int32()
            item.durability = self.get_float()
            item.pos = (self.get_int32(), self.get_int32())
            item.equipped = self.get_bool()
            item.quality = self.get_int32()
            item.variant = self.get_int32()
            item.crafter_id = self.get_int64()
            item.crafter_name = self.get_string()
            item.unknown = self.get_int32()  # todo figure out what this is

            if item.name:
                self.inventory.append(item)

        self.recipes = [self.get_string() for _ in range(self.get_int32())]
        self.stations = [(self.get_string(), self.get_int32()) for _ in range(self.get_int32())]
        self.known_materials = [self.get_string() for _ in range(self.get_int32())]
        self.shown_tutorials = [self.get_string() for _ in range(self.get_int32())]
        self.uniques = [self.get_string() for _ in range(self.get_int32())]
        self.trophies = [self.get_string() for _ in range(self.get_int32())]
        self.biomes = [self.get_int32() for _ in range(self.get_int32())]
        self.texts = [(self.get_string(), self.get_string()) for _ in range(self.get_int32())]

        self.beard = self.get_string()
        self.hair = self.get_string()
        self.skin_color = (self.get_float(), self.get_float(), self.get_float())
        self.hair_color = (self.get_float(), self.get_float(), self.get_float())
        self.model = self.get_int32()

        self.foods: List[Food] = []
        for i in range(self.get_int32()):
            food = Food()
            food.name = self.get_string()
            food.hp_left = self.get_float()
            food.stam_left = self.get_float()
            self.foods.append(food)

        self.skills_version = self.get_int32()
        self.skills: List[Skill] = []
        for i in range(self.get_int32()):
            skill = Skill()
            skill.name = self.get_int32()
            skill.level = self.get_float()
            skill.unused = self.get_float()
            self.skills.append(skill)

        self.reader.close()

    def unpack(self, n_bytes, fmt=None):
        x = self.reader.read(n_bytes)
        if fmt:
            return struct.unpack(fmt, x)[0]
        return x

    def get_bool(self):
        return self.unpack(1, '?')

    def get_float(self):
        return self.unpack(4, 'f')

    def get_int32(self):
        return self.unpack(4, 'i')

    def get_int64(self):
        return self.unpack(8, 'q')

    def get_uint16(self):
        return self.unpack(2, 'H')

    def get_uchar(self):
        return self.unpack(1, 'B')

    def get_string(self):
        length = self.get_uchar()
        return self.unpack(length, f'{length}s')

    def pack(self, content, override=None):
        fmt = None
        if isinstance(content, str):
            content = content.encode()

        if isinstance(content, bool):
            fmt = '?'
        elif isinstance(content, int):
            fmt = 'i'
        elif isinstance(content, float):
            fmt = 'f'

        if override:
            fmt = override

        if (fmt is None and isinstance(content, bytes)) or (override and override.endswith('s')):
            length = struct.pack('B', len(content))
            return length + struct.pack(f'{len(content)}s', content)

        return struct.pack(fmt, content)

    def dump(self, file_obj: BinaryIO):
        out_buffer = BytesIO()
        out_buffer.write(self.pack(self.character_version))
        out_buffer.write(self.pack(self.kills))
        out_buffer.write(self.pack(self.deaths))
        out_buffer.write(self.pack(self.crafts))
        out_buffer.write(self.pack(self.builds))
        out_buffer.write(self.pack(len(self.worlds)))
        for world in self.worlds:
            out_buffer.write(self.pack(world.worldId, 'q'))
            out_buffer.write(self.pack(world.hasCustomSpawn))
            out_buffer.write(self.pack(world.spawnPoint[0]))
            out_buffer.write(self.pack(world.spawnPoint[1]))
            out_buffer.write(self.pack(world.spawnPoint[2]))
            out_buffer.write(self.pack(world.hasLogoutPoint))
            out_buffer.write(self.pack(world.logoutPoint[0]))
            out_buffer.write(self.pack(world.logoutPoint[1]))
            out_buffer.write(self.pack(world.logoutPoint[2]))
            out_buffer.write(self.pack(world.hasDeathPoint))
            out_buffer.write(self.pack(world.deathPoint[0]))
            out_buffer.write(self.pack(world.deathPoint[1]))
            out_buffer.write(self.pack(world.deathPoint[2]))
            out_buffer.write(self.pack(world.homePoint[0]))
            out_buffer.write(self.pack(world.homePoint[1]))
            out_buffer.write(self.pack(world.homePoint[2]))
            out_buffer.write(self.pack(world.hasMapData))
            if world.hasMapData:
                out_buffer.write(self.pack(world.mapDataLength))
                out_buffer.write(world.mapData)
        out_buffer.write(self.pack(self.name))
        out_buffer.write(self.pack(self.id, 'q'))
        out_buffer.write(self.pack(self.start_seed))
        out_buffer.write(self.pack(self.max_hp != 0))

        temp_buffer = BytesIO()
        if self.max_hp != 0:
            temp_buffer.write(self.pack(self.data_version))
            temp_buffer.write(self.pack(self.max_hp))
            temp_buffer.write(self.pack(self.hp))
            temp_buffer.write(self.pack(self.stamina))
            temp_buffer.write(self.pack(self.is_first_spawn))
            temp_buffer.write(self.pack(self.time_since_death))
            temp_buffer.write(self.pack(self.guardian_power))
            temp_buffer.write(self.pack(self.guardian_cooldown))
            temp_buffer.write(self.pack(self.inventory_version))
            temp_buffer.write(self.pack(len(self.inventory)))
            for item in self.inventory:
                temp_buffer.write(self.pack(item.name))
                temp_buffer.write(self.pack(item.stack))
                temp_buffer.write(self.pack(item.durability))
                temp_buffer.write(self.pack(item.pos[0]))
                temp_buffer.write(self.pack(item.pos[1]))
                temp_buffer.write(self.pack(item.equipped))
                temp_buffer.write(self.pack(item.quality))
                temp_buffer.write(self.pack(item.variant))
                temp_buffer.write(self.pack(item.crafter_id, 'q'))
                temp_buffer.write(self.pack(item.crafter_name))
                temp_buffer.write(self.pack(item.unknown))  # todo figure out what this is

            temp_buffer.write(self.pack(len(self.recipes)))
            for recipe in self.recipes:
                temp_buffer.write(self.pack(recipe))

            temp_buffer.write(self.pack(len(self.stations)))
            for stations in self.stations:
                temp_buffer.write(self.pack(stations[0]))
                temp_buffer.write(self.pack(stations[1]))

            temp_buffer.write(self.pack(len(self.known_materials)))
            for mat in self.known_materials:
                temp_buffer.write(self.pack(mat))

            temp_buffer.write(self.pack(len(self.shown_tutorials)))
            for tut in self.shown_tutorials:
                temp_buffer.write(self.pack(tut))

            temp_buffer.write(self.pack(len(self.uniques)))
            for uni in self.uniques:
                temp_buffer.write(self.pack(uni))

            temp_buffer.write(self.pack(len(self.trophies)))
            for trophy in self.trophies:
                temp_buffer.write(self.pack(trophy))

            temp_buffer.write(self.pack(len(self.biomes)))
            for biome in self.biomes:
                temp_buffer.write(self.pack(biome))

            temp_buffer.write(self.pack(len(self.texts)))
            for text in self.texts:
                temp_buffer.write(self.pack(text[0]))
                temp_buffer.write(self.pack(text[1]))

            temp_buffer.write(self.pack(self.beard))
            temp_buffer.write(self.pack(self.hair))
            temp_buffer.write(self.pack(self.skin_color[0]))
            temp_buffer.write(self.pack(self.skin_color[1]))
            temp_buffer.write(self.pack(self.skin_color[2]))
            temp_buffer.write(self.pack(self.hair_color[0]))
            temp_buffer.write(self.pack(self.hair_color[1]))
            temp_buffer.write(self.pack(self.hair_color[2]))
            temp_buffer.write(self.pack(self.model))

            temp_buffer.write(self.pack(len(self.foods)))
            for food in self.foods:
                temp_buffer.write(self.pack(food.name))
                temp_buffer.write(self.pack(food.hp_left))
                temp_buffer.write(self.pack(food.stam_left))

            temp_buffer.write(self.pack(self.skills_version))
            temp_buffer.write(self.pack(len(self.skills)))
            for skill in self.skills:
                temp_buffer.write(self.pack(skill.name))
                temp_buffer.write(self.pack(skill.level))
                temp_buffer.write(self.pack(skill.unused))

        temp_buffer.seek(0)
        player_data = temp_buffer.read()

        out_buffer.write(self.pack(len(player_data)))
        out_buffer.seek(0)

        all_data = out_buffer.read()
        all_data += player_data

        result = self.pack(len(all_data)) + all_data + self.pack(64) + hashlib.sha512(all_data).digest()

        file_obj.write(result)

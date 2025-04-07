import math
from perlin_noise import PerlinNoise

import os.path
import pickle,threading
import pygame

import default,objects,entities,random


class chunk_data:
    def __init__(self,floor,spawn_data,temperature,elevation,size):
        self.floor = floor
        self.spawn_data = spawn_data
        self.temperature = temperature
        self.elevation = elevation
        self.size = size

class chuck:
    def __init__(self,pos,dimension,game,chunk_data):
        self.pos = pos
        self.dimension = dimension
        self.path = game.path
        self.chunk_data = chunk_data
        self.entities = []
        self.objects = []
        self.del_cooldown = 0
        self.floor = None

    def create(self,game):
        self.floor = objects.object(game,self.pos,self.dimension,default.get_object(self.chunk_data.floor),"floor")
        default.create_object(game.objects,self.floor)
        for object_data in self.chunk_data.spawn_data["objects"]:
            if random.random() < object_data["percent"]:
                random_amount = random.randint(object_data["min"],object_data["max"])
                for i in range(random_amount):
                    random_x = random.randint(self.floor.rect.rect.left, self.floor.rect.rect.right)
                    random_y = random.randint(self.floor.rect.rect.top, self.floor.rect.rect.bottom)

                    id = default.create_object(game.objects,objects.object(game,(random_x,random_y),self.floor.rect.dimension,default.get_object(object_data["name"])))
                    if game.objects[id].data.plant_data != None:
                        game.objects[id].stage = game.objects[id].data.plant_data.max_stage
        for entity_data in self.chunk_data.spawn_data["entities"]:
            if random.random() < entity_data["percent"]:
                random_amount = random.randint(entity_data["min"],entity_data["max"])
                for i in range(random_amount):
                    random_x = random.randint(self.floor.rect.rect.left, self.floor.rect.rect.right)
                    random_y = random.randint(self.floor.rect.rect.top, self.floor.rect.rect.bottom)
                    default.create_object(game.entities,entities.entity(game,default.get_entity(entity_data["name"]),(random_x,random_y),self.floor.rect.dimension))


    def updator(self,game):
        self.objects = []
        self.entities = []
        for outside_object in list(game.objects.values()):
            if outside_object.rect != None and self.floor.rect.collidepoint(*default.get_chunk(outside_object.rect.rect.x,outside_object.rect.rect.y),dimension=outside_object.rect.dimension):
                self.objects.append(outside_object)
        for outside_entity in list(game.entities.values()):
            if outside_entity.rect != None and self.floor.rect.collidepoint(*default.get_chunk(outside_entity.rect.rect.x,outside_entity.rect.rect.y),dimension=outside_entity.rect.dimension):
                self.entities.append(outside_entity)

    def unload(self, game):
        for event in game.event_list:
            if event.type == pygame.USEREVENT:
                self.del_cooldown += 1
                if self.del_cooldown == 2:
                    self.save(game)
                    return True
        return False

    def save(self,game):
        entities_list = []
        for entity in self.entities:

            entities_list.append(entity.to_dict())
            game.camera_group.remove(entity)
            game.entities.pop(entity.id)

        objects_list = []
        for object in self.objects:
            objects_list.append(object.to_dict())
            game.camera_group.remove(object)

            game.objects.pop(object.id)
        chunk_dict = {"entities": entities_list, "objects": objects_list}
        with open(f"{self.path}/{self.floor.rect.dimension}/chunk_{self.pos[0]}_{self.pos[1]}.pkl", "wb") as file:
            pickle.dump(chunk_dict, file)
        game.camera_group.remove(self.floor)

    def load(self,game):
        with open(f"{self.path}/{self.dimension}/chunk_{self.pos[0]}_{self.pos[1]}.pkl","rb") as file:
            chunk_dict = pickle.load(file)

            new_objects = chunk_dict["objects"]
            for i in range(len(new_objects)):
                id = default.load_object(game.objects,objects.object(game,(0,0),"null",default.get_object("rock"),None,False,new_objects[i]),new_objects[i]["id"])
                if game.objects[id].tag == "floor":
                    self.floor = game.objects[id]

            new_entities = chunk_dict["entities"]
            for i in range(len(new_entities)):
                default.load_object(game.entities,entities.entity(game,default.get_entity("cow"),(0,0),"null",entity_dict=new_entities[i]),new_entities[i]["id"])


class world_data:
    def __init__(self,chunks_data,name):
        self.chunks_data = chunks_data
        self.name = name

class dimension:
    def __init__(self,world_data,seed):
        self.chunks = {}
        self.world_data = world_data
        self.seed = seed
        self.biome_size = 2
        self.chunk_w = 520
        self.chunk_h = 400
        self.render_distance = 1
        self.player_chunk_locations = {}

    def updator(self,game):
        if not os.path.exists(f"{game.path}/{self.world_data.name}"):
            os.mkdir(f"{game.path}/{self.world_data.name}")
        used_chunks = []
        to_remove_chunks = []
        for player in list(game.players.values()):
            if player.rect.dimension == self.world_data.name:
                if self.player_chunk_locations.get(player.id,None) != default.get_chunk(player.rect.rect.x,player.rect.rect.y):
                    chunks = self.generate_visible_chunks(player.rect.rect.x,player.rect.rect.y)
                    self.player_chunk_locations[player.id] = default.get_chunk(player.rect.rect.x,player.rect.rect.y)
                    for chunk in chunks.keys():
                        chunk_x = chunk[0] * self.chunk_w
                        chunk_y = chunk[1] * self.chunk_h
                        if self.chunks.get(f"chunk_{chunk_x}_{chunk_y}",None) == None:
                            self.new_chunk(game,(chunk_x,chunk_y),chunks[chunk])
                        used_chunks.append(f"chunk_{chunk_x}_{chunk_y}")
                else:
                    for i in range(self.player_chunk_locations[player.id][0]-(self.chunk_w*self.render_distance),self.player_chunk_locations[player.id][0]+(self.chunk_w*(self.render_distance+1)),self.chunk_w):
                        for j in range(self.player_chunk_locations[player.id][1] - (self.chunk_h * self.render_distance), self.player_chunk_locations[player.id][1] + (self.chunk_h * (self.render_distance+1)), self.chunk_h):
                            used_chunks.append(f"chunk_{i}_{j}")
            else:
                try:
                    del self.player_chunk_locations[player.id]
                except:
                    pass

        for chunk_pos in self.chunks.keys():
            self.chunks[chunk_pos].updator(game)
            if not chunk_pos in used_chunks:
                to_remove_chunks.append(chunk_pos)
            else:
                try:
                    to_remove_chunks.remove(chunk_pos)
                    self.chunks[chunk_pos].del_cooldown = 0
                except:
                    pass
        for chunk in to_remove_chunks:
            if self.chunks[chunk].unload(game):
                del self.chunks[chunk]


    def save(self,game):
        for chunk_pos in self.chunks.keys():
            self.chunks[chunk_pos].updator(game)
            self.chunks[chunk_pos].save(game)

    def seeded_random(self,x, y, min=0,max=100):
        """Generate a deterministic random value based on coordinates."""
        return random.Random(hash((x, y, self.seed))).randint(min,max)


    def generate_temperature_elevation(self,bx, by):
        """Generate temperature and elevation for a biome region deterministically."""
        temp = self.seeded_random(bx, by,-20,50)# Scale temperature
        elev = self.seeded_random(bx + 1000, by - 1000, 0,60)# Shifted seed for elevation
        return temp, elev

    def get_biome(self,temp, elev):

        possible_biomes = []
        for biome in self.world_data.chunks_data.keys():
            temp_range, elev_range = self.world_data.chunks_data[biome].temperature, self.world_data.chunks_data[biome].elevation
            if temp_range[0] <= temp <= temp_range[1] and elev_range[0] <= elev <= elev_range[1]:
                possible_biomes.append(biome)
        return random.choice(possible_biomes) if possible_biomes else list(self.world_data.chunks_data.keys())[0]



    def generate_biome_region(self,bx, by):
        """Generate a biome for a specific biome region with variable size."""
        temp, elev = self.generate_temperature_elevation(bx, by)
        biome = self.get_biome(temp, elev)
        biome_size = self.world_data.chunks_data[biome].size
        return biome, biome_size


    def generate_chunk(self,cx, cy, biome_regions):
        """Generate a single chunk's biome based on its biome region."""
        for (bx, by), (biome, size) in biome_regions.items():
            if bx <= cx < bx + size and by <= cy < by + size:
                return biome
        return list(self.world_data.chunks_data.keys())[0]

    def generate_visible_chunks(self,player_x, player_y):
        """Generate chunks within the render distance using a fixed biome grid."""
        chunk_x, chunk_y = default.get_chunk(player_x,player_y)
        chunk_x = chunk_x//self.chunk_w
        chunk_y = chunk_y//self.chunk_h
        # chunk_x, chunk_y = player_x//self.chunk_w,player_y//self.chunk_h
        biome_regions = {}
        biome_map = {}

        # Assign biome regions deterministically on a fixed grid
        for dx in range(-self.render_distance, self.render_distance + 1):
            for dy in range(-self.render_distance, self.render_distance + 1):
                bx, by = ((chunk_x + dx) // 32) * 32, ((chunk_y + dy) // 32) * 32
                if (bx, by) not in biome_regions:
                    biome_regions[(bx, by)] = self.generate_biome_region(bx, by)

        # Generate chunks based on fixed biome regions
        for dx in range(-self.render_distance, self.render_distance + 1):
            for dy in range(-self.render_distance, self.render_distance + 1):
                cx, cy = chunk_x + dx, chunk_y + dy
                biome_map[(cx, cy)] = self.generate_chunk(cx, cy, biome_regions)
        return biome_map


    def new_chunk(self,game,pos,biome):

        biome = default.get_biome(biome)
        if os.path.exists(f"{game.path}/{self.world_data.name}/chunk_{pos[0]}_{pos[1]}.pkl"):
            self.chunks[f"chunk_{pos[0]}_{pos[1]}"] = chuck(pos, self.world_data.name, game, biome)
            self.chunks[f"chunk_{pos[0]}_{pos[1]}"].load(game)
        else:

            self.chunks[f"chunk_{pos[0]}_{pos[1]}"] = chuck(pos, self.world_data.name, game, biome)
            self.chunks[f"chunk_{pos[0]}_{pos[1]}"].create(game)
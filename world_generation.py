import os.path
import pickle,threading

import pygame

import default,objects,entities,random
# {objects:
# [
#   "name":"tree","percent":0.50,min:0,max:1],
#   "name":"tree","percent":0.05,min:1,max:1],
# entities:
# }

class chunk_data:
    def __init__(self,floor,spawn_data):
        self.floor = floor
        self.spawn_data = spawn_data

class chuck:
    def __init__(self,pos,dimension,game,chunk_data):
        self.pos = pos
        self.path = game.path
        self.chunk_data = chunk_data
        self.entities = []
        self.objects = []
        self.caves = []
        self.del_cooldown = 0
        self.floor = objects.object(game,pos,dimension,default.get_object(self.chunk_data.floor))

    def create(self,game):
        for object_data in self.chunk_data.spawn_data["objects"]:
            if random.random() < object_data["percent"]:
                random_amount = random.randint(object_data["min"],object_data["max"])
                for i in range(random_amount):
                    random_x = random.randint(self.floor.rect.rect.left, self.floor.rect.rect.right)
                    random_y = random.randint(self.floor.rect.rect.top, self.floor.rect.rect.bottom)

                    game.objects.append(objects.object(game,(random_x,random_y),self.floor.rect.dimension,default.get_object(object_data["name"])))
                    if game.objects[-1].data.plant_data != None:
                        game.objects[-1].stage = game.objects[-1].data.plant_data.max_stage
        for entity_data in self.chunk_data.spawn_data["entities"]:
            if random.random() < entity_data["percent"]:
                random_amount = random.randint(entity_data["min"],entity_data["max"])
                for i in range(random_amount):
                    random_x = random.randint(self.floor.rect.rect.left, self.floor.rect.rect.right)
                    random_y = random.randint(self.floor.rect.rect.top, self.floor.rect.rect.bottom)
                    game.entities.append(entities.entity(game,default.get_entity(entity_data["name"]),(random_x,random_y),self.floor.rect.dimension))
        for cave_data in self.chunk_data.spawn_data["caves"]:
            if random.random() < cave_data["percent"]:
                random_amount = random.randint(cave_data["min"],cave_data["max"])
                for i in range(random_amount):
                    random_x = random.randint(self.floor.rect.rect.left, self.floor.rect.rect.right)
                    random_y = random.randint(self.floor.rect.rect.top, self.floor.rect.rect.bottom)
                    game.caves.append(objects.cave((random_x,random_y),self.floor.rect.dimension,game))


    def updator(self,game):
        self.objects = []
        self.caves = []
        self.entities = []
        for outside_object in game.objects:
            if outside_object.rect != None and self.floor.rect.collidepoint(int(outside_object.rect.rect.x/416)*416,int(outside_object.rect.rect.y/304)*304,outside_object.rect.dimension):
                self.objects.append(outside_object)
        for outside_entity in game.entities:
            if outside_entity.rect != None and self.floor.rect.collidepoint(int(outside_entity.rect.rect.x/416)*416,int(outside_entity.rect.rect.y/304)*304,outside_entity.rect.dimension):
                self.entities.append(outside_entity)
        for outside_cave in game.caves:
            if outside_cave.rect != None and self.floor.rect.collidepoint(int(outside_cave.rect.rect.x/416)*416,int(outside_cave.rect.rect.y/304)*304,outside_cave.rect.dimension):
                self.caves.append(outside_cave)

    def offload(self, game):
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
            game.entities.remove(entity)
            entities_list.append(entity.to_dict())
            game.camera_group.remove(entity)
            del entity
        objects_list = []
        for object in self.objects:
            game.objects.remove(object)
            game.camera_group.remove(object)
            objects_list.append(object.to_dict())
            del object

        caves_list = []
        for cave in self.caves:
            game.camera_group.remove(cave)
            game.caves.remove(cave)
            caves_list.append(cave.to_dict())
            del cave
        chunk_dict = {"entities": entities_list, "objects": objects_list, "caves": caves_list}
        with open(f"{self.path}/{self.floor.rect.dimension}/chunk_{self.pos[0]}_{self.pos[1]}.pkl", "wb") as file:
            pickle.dump(chunk_dict, file)
        game.camera_group.remove(self.floor)

    def load(self,game):
        with open(f"{self.path}/{self.floor.rect.dimension}/chunk_{self.pos[0]}_{self.pos[1]}.pkl","rb") as file:
            chunk_dict = pickle.load(file)
            objects_list = []
            entities_list = []
            caves_list = []
            new_objects = chunk_dict["objects"]

            if len(objects_list) < len(new_objects):
                for i in range(len(new_objects) - len(objects_list)):
                    objects_list.append(objects.object(game, (10, 10),"world", default.get_object("rock")))
            for i in range(len(new_objects)):

                objects_list[i].from_dict(new_objects[i])
            new_entities = chunk_dict["entities"]
            if len(entities_list) < len(new_entities):
                for i in range(len(new_entities) - len(entities_list)):
                    entities_list.append(entities.entity(game, default.get_entity("cow"), (10, 10),"world"))
            for i in range(len(new_entities)):
                entities_list[i].from_dict(new_entities[i])

            new_caves = chunk_dict["caves"]
            if len(caves_list) < len(new_caves):
                for i in range(len(new_caves) - len(caves_list)):
                    caves_list.append(objects.cave((999999,99999),"world",game))
            for i in range(len(new_caves)):
                caves_list[i].from_dict(new_caves[i])
            game.caves += caves_list
            game.entities += entities_list
            game.objects += objects_list

class dimension:
    def __init__(self,name,chunk_data):
        self.chunks = {}
        self.name = name
        self.chunk_data = chunk_data

    def updator(self,game):
        if not os.path.exists(f"{game.path}/{self.name}"):
            os.mkdir(f"{game.path}/{self.name}")
        used_chunks = []
        to_remove_chunks = []
        render_distance = 2
        for player in game.players:

            if player.rect.dimension == self.name:

                current_chunk_location = (int(player.rect.rect.x/416)*416,int(player.rect.rect.y/304)*304)
                for i in range(current_chunk_location[0]-(416*render_distance),current_chunk_location[0]+(416*(render_distance+1)),416):
                    for j in range(current_chunk_location[1] - (304 * render_distance), current_chunk_location[1] + (304 * (render_distance+1)), 304):
                        if self.chunks.get(f"chunk_{i}_{j}",None) == None:
                            self.new_chunk(game,(i,j))
                        used_chunks.append(f"chunk_{i}_{j}")



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
            if self.chunks[chunk].offload(game):
                del self.chunks[chunk]


    def save(self,game):
        for chunk_pos in self.chunks.keys():
            self.chunks[chunk_pos].updator(game)
            self.chunks[chunk_pos].save(game)

    def new_chunk(self,game,pos):
        self.chunks[f"chunk_{pos[0]}_{pos[1]}"] = chuck(pos,self.name,game,self.chunk_data)
        if os.path.exists(f"{game.path}/{self.name}/chunk_{pos[0]}_{pos[1]}.pkl"):
            self.chunks[f"chunk_{pos[0]}_{pos[1]}"].load(game)
        else:
            self.chunks[f"chunk_{pos[0]}_{pos[1]}"].create(game)


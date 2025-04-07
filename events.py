import gif_pygame, pygame, random,items,gui,default,math,entities,objects

import particles


class event_data:
    def __init__(self,time,durability,name,theme_name=None,entities_list=None,objects_list=None,summon_delay=15,dimension="world"):
        self.time = time
        self.durability = durability
        self.name = name
        self.dimension = dimension
        self.theme_name = theme_name
        self.entities_list = entities_list
        self.objects_list = objects_list
        self.summon_delay = summon_delay

class event:
    def __init__(self,data):
        self.data = data
        self.id = None
        self.time_c = 0
        self.durability_c = 0
        self.summon_delay_c = 0
        self.particle_id= None
        self.currently = False

    def to_dict(self):
        return {
            "data":self.data,
            "time_c":self.time_c,
            "durability_c":self.durability_c,
            "summon_delay_c":self.summon_delay_c,
            "currently":self.currently,
            "particle_id":self.particle_id,
            "id":self.id,
        }

    def from_dict(self,event_dict):
        self.data = event_dict["data"]
        self.time_c = event_dict["time_c"]
        self.durability_c = event_dict["durability_c"]
        self.summon_delay_c = event_dict["summon_delay_c"]
        self.currently = event_dict["currently"]
        self.particle_id = event_dict["particle_id"]
        self.id = event_dict["id"]

    def updator(self,game):
        for Event in game.event_list:
            if Event.type == pygame.USEREVENT:
                if self.currently:
                    self.durability_c += 1
                    self.summon_delay_c += 1
                else:
                    self.time_c += 1
        if self.time_c >= self.data.time:
            self.start(game)
        if self.durability_c >= self.data.durability:
            self.end(game)
        if self.summon_delay_c >= self.data.summon_delay:
            for player in list(game.players.values()):
                if player.rect.dimension == self.data.dimension:
                    if self.data.objects_list != None:
                        random_x = random.randint(player.render.rect.left,player.render.rect.right)
                        random_y = random.randint(player.render.rect.up,player.render.rect.down)
                        default.create_object(game.objects,objects.object(game, (random_x, random_y),seld.data.dimension, default.get_object(random.choice(self.data.objects_list))))
                    if self.data.entities_list != None:
                        random_x = random.randint(player.render.rect.left, player.render.rect.right)
                        random_y = random.randint(player.render.rect.top, player.render.rect.bottom)
                        default.create_object(game.entities,entities.entity(game, default.get_entity(random.choice(self.data.entities_list)), (random_x, random_y),self.data.dimension))
                    self.summon_delay_c = 0

    def start(self,game):
        self.particle_id = default.create_object(game.particles,particles.particle(default.get_particle(self.data.theme_name),(0,0),self.data.dimension,game))
        self.currently = True
        self.time_c = 0

    def end(self,game):
        if not self.durability_c >= self.data.durability:
            game.particles[self.particle_id].cooldown = 0
        self.durability_c = 0
        self.summon_delay_c = 0
        self.currently = False
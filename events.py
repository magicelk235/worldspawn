import gif_pygame, pygame, random,items,gui,default,math,entities,objects

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

class theme(pygame.sprite.Sprite):
    def __init__(self,group,name,dimension):
        super().__init__(group)
        self.name = name
        self.path = f"assets/themes/{name}"
        self.image = default.image(self.path)
        self.rect = self.image.get_rect((0,0),dimension)


    def display(self):
        self.path = f"assets/themes/{self.name}"
        self.image.replace_path(self.path)

    def undisplay(self):
        self.path = f"assets/themes/None"
        self.image.replace_path(self.path)

class event:
    def __init__(self,game,data):
        self.data = data
        self.time_c = 0
        self.durability_c = 0
        self.summon_delay_c = 0
        self.theme = theme(game.camera_group,data.theme_name,data.dimension)
        self.theme.undisplay()
        self.currently = False

    def to_dict(self):
        return {
            "data":self.data,
            "time_c":self.time_c,
            "durability_c":self.durability_c,
            "summon_delay_c":self.summon_delay_c,
            "currently":self.currently,
        }

    def from_dict(self,event_dict):
        self.data = event_dict["data"]
        self.time_c = event_dict["time_c"]
        self.durability_c = event_dict["durability_c"]
        self.summon_delay_c = event_dict["summon_delay_c"]
        self.currently = event_dict["currently"]

    def updator(self,game):
        for Event in game.event_list:
            if Event.type == pygame.USEREVENT:
                if self.currently:
                    self.durability_c += 1
                    self.summon_delay_c += 1
                else:
                    self.time_c += 1
        if self.time_c >= self.data.time:
            self.start()
        if self.durability_c >= self.data.durability:
            self.end()
        if self.summon_delay_c >= self.data.summon_delay:
            for player in game.players:
                if player.rect.dimension == self.data.dimension:
                    if self.data.objects_list != None:
                        random_x = random.randint(player.render.rect.left,player.render.rect.right)
                        random_y = random.randint(player.render.rect.up,player.render.rect.down)
                        game.objects.append(objects.object(game, (random_x, random_y),seld.data.dimension, default.get_object(random.choice(self.data.objects_list))))
                    if self.data.entities_list != None:
                        random_x = random.randint(player.render.rect.left, player.render.rect.right)
                        random_y = random.randint(player.render.rect.top, player.render.rect.bottom)
                        game.entities.append(entities.entity(game, default.get_entity(random.choice(self.data.entities_list)), (random_x, random_y),self.data.dimension))
                    self.summon_delay_c = 0

    def start(self):
        self.theme.display()
        self.currently = True
        self.time_c = 0

    def end(self):
        self.theme.undisplay()
        self.durability_c = 0
        self.summon_delay_c = 0
        self.currently = False
import pygame, sys, gif_pygame, random,numpy, os,time,json,events,multiprocessing

from objects import *
from items import *
from entities import *
from default import *
from gui import *

class game:
    def __init__(self):
        # setup
        pygame.init()
        self.screen = pygame.display.set_mode((800, 400), pygame.SCALED | pygame.RESIZABLE)
        self.camera_group = CameraGroup()
        pygame.time.set_timer(pygame.USEREVENT, 1000)
        self.TIMER_EVENT = pygame.USEREVENT + 1
        pygame.time.set_timer(self.TIMER_EVENT, 100)
        self.game_started = False
        self.need_recover = False

        # start menu
        self.world_menu = world_menu((2000, 2000), self)
        self.world_menu_selector = world_menu_selector((200, 200), self)
        self.copy_right_text = text((1700 - 4, 2281), 19, "Magicelk235™ Copyright 2025© All Rights Reserved", self,(0, 0, 0), True)

        self.players = []
        # World_gen
        self.event_list = []
        self.objects = []
        self.caves = []
        self.entities = []
        self.drops = []
        self.events = []
        self.projectiles = []
        self.path = ""
        pygame.display.set_caption("WorldSpawn")
        pygame.display.set_icon(pygame.image.load(resource_path("assets/gui/world_icon.png")))

    def update(self):
        for Block in self.objects:
            if Block.render(self.player.render):
                if threading.thread(Block.updator,self):
                    self.objects.remove(Block)
                    del Block
        for Entity in self.entities:
            if Entity.render(self.player.render):
                if threading.thread(Entity.updator,self):
                    self.entities.remove(Entity)
                    del Entity
        for drop in self.drops:
            if drop.render(self.player.render):
                if drop.updator(self):
                    self.drops.remove(drop)
                    del drop
        for Projectile in self.projectiles:
            if Projectile.render(self.player.render):
                if Projectile.updator(self):
                    self.projectiles.remove(Projectile)
                    del Projectile
        for event in self.events:
            event.updator(self)
        for cave in self.caves:
            if cave.render(self.player.render):
                cave.updator(self)

    def world_gen(self):
        self.events.append(events.event(self,events.event_data(5*60,2.5*60,"night","night",["zombie", "skeleton", "troll", "ogre", "fungal", "cyclops","caveman","witch","stone_golem"])))
        self.events.append(events.event(self,events.event_data(20*60,2.5*60,"goblin_raid","goblin_gas",["goblin", "goblin_witch", "goblin_archer", "goblin_spikeball", "goblin_wolf_rider"],summon_delay=4)))
        self.events.append(events.event(self,events.event_data(10*60,2.5*60,"rain","rain",["water_golem", "tornado", "water_golem_mini", "tornado_mini"],summon_delay=6)))
        self.objects.append(object(self, (2954, 2970), get_object("spawn0")))

        used_places = []
        for i in range(500):
            while True:
                random_place = (random.randint(4, 184) * 32, random.randint(5, 255) * 23)
                if random_place not in used_places:
                    used_places.append(random_place)
                    self.objects.append(object(self, random_place,get_object("rock")))
                    break
            if i < 200:
                for name in ["tree_white","tree_swirling","tree_willow","tree_cherry","tree_oak","tree_spruce","bush","twig"]:
                    while True:
                        random_place = (random.randint(4, 184) * 32, random.randint(5, 255) * 23)
                        if random_place not in used_places:
                            used_places.append(random_place)
                            self.objects.append(object(self, random_place, get_object(name)))
                            break

            if i < 150:
                for name in ["pumpkin","tomato","potato","carrot","wheat","flower_red","flower_white","flower_blue","flower_green","flower_black"]:
                    while True:
                        random_place = (random.randint(4, 184) * 32, random.randint(5, 255) * 23)
                        if random_place not in used_places:
                            used_places.append(random_place)
                            self.objects.append(object(self, random_place, get_object(name)))
                            break
            if i < 50:
                for name in ["lake","cliff","mini_cliff"]:
                    while True:
                        random_place = (random.randint(4, 184) * 32, random.randint(5, 255) * 23)
                        if random_place not in used_places:
                            used_places.append(random_place)
                            self.objects.append(object(self, random_place, get_object(name)))
                            break
            if i < 12:
                for name in ["goat", "cow", "pig", "sheep", "chicken", "duck", "deer", "horse", "lion","dog"]:
                    self.entities.append(entity(self, get_entity(name),
                                                (random.randint(10, 178) * 32, random.randint(10, 151) * 23)))
                for name in ["coal_ore", "copper_ore", "iron_ore", "silver_ore", "gold_ore", "crystal","rock"]:
                    while True:
                        random_place = (random.randint(4, 184) * 32, random.randint(5, 255) * 23)
                        if random_place not in used_places:
                            used_places.append(random_place)
                            self.caves.append(cave(random_place, self, name, 15, self.objects))
                            break
            if i < 4:
                for name in ["sand_temple","olympos","ruined_village","cursed_olympos","knight_tower","defence_tower","ship"]:
                    while True:
                        random_place = (random.randint(4, 184) * 32, random.randint(5, 255) * 23)
                        if random_place not in used_places:
                            used_places.append(random_place)
                            self.objects.append(object(self, random_place, get_object(name)))
                            break




        for block in self.objects:
            if block.data.plant_data != None:
                block.stage = block.data.plant_data.max_stage
        self.objects.append(object(self, (0, 7061), get_object("cave_border_x")))
        self.objects.append(object(self, (0, 8020), get_object("cave_border_x")))
        self.objects.append(object(self, (0, 7061), get_object("cave_border_y")))
        self.objects.append(object(self, (959, 7061), get_object("cave_border_y")))
        self.objects.append(
            object(self, (0, -529), object_data("border_x", None, None, None, None, True)))
        self.objects.append(
            object(self, (0, 6000), object_data("border_x", None, None, None, None, True)))
        self.objects.append(
            object(self, (-529, -529), object_data("border_y", None, None, None, None, True)))
        self.objects.append(
            object(self, (6003, -529), object_data("border_y", None, None, None, None, True)))

    def close(self,path):
        
        self.camera_group.close()
        for projectile in self.projectiles:
            projectile.close(self)
        for i in range(len(self.objects)):
            self.objects[i].close()
        for i in range(len(self.entities)):
            self.entities[i].close()
        for i in range(len(self.caves)):
            self.caves[i].close()
        for event in self.events:
            event.close()
        for drop in self.drops:
            drop.close()
        for player in self.players:
            player.gui_open = False
            player.close()
            numpy.save(f"{path}/players/{player.id}.npy",[player])
        if not os.path.exists(path):
            os.mkdir(path)

        
        numpy.save(f"{path}/entities.npy", self.entities)
        numpy.save(f"{path}/blocks.npy", self.objects)
        numpy.save(f"{path}/caves.npy", self.caves)
        
        numpy.save(f"{path}/drops.npy", self.drops)
        numpy.save(f"{path}/events.npy", self.events)

        pygame.quit()
        sys.exit()

    def recover(self):
        if self.objects == self.objects:
            new_blocks = numpy.load(f"{self.path}/blocks.npy", None, True)
            if len(self.objects) < len(new_blocks):
                for i in range(len(new_blocks) - len(self.objects)):
                    self.objects.append(object(self, (10, 10), get_object("rock")))
            for i in range(len(new_blocks)):
                if new_blocks[i] != None:
                    self.objects[i].copy(new_blocks[i], self)
                else:
                    self.objects[i] = new_blocks[i]

        if self.entities == self.entities:
            new_entities = numpy.load(f"{self.path}/entities.npy", None, True)
            if len(self.entities) < len(new_entities):
                for i in range(len(new_entities) - len(self.entities)):
                    self.entities.append(entity(self, get_entity("cow"), (10, 10)))
            for i in range(len(new_entities)):
                if new_entities[i] != None:
                    self.entities[i].copy(new_entities[i], self)
                else:
                    self.entities[i] = None
        if self.caves == self.caves:
            new_caves = numpy.load(f"{self.path}/caves.npy", None, True)

            if len(self.caves) < len(new_caves):
                for i in range(len(new_caves) - len(self.caves)):
                    self.caves.append(cave((10, 10), self, "coal_ore", 0, self.objects))
            for i in range(len(new_caves)):
                self.caves[i].copy(new_caves[i], self.camera_group)
        if self.drops == self.drops:
            new_drops = numpy.load(f"{self.path}/drops.npy",None,True)
            if len(self.drops) < len(new_drops):
                for i in range(len(new_drops) - len(self.drops)):
                    self.drops.append(item(self, (10, 10), 1, get_material("wood")))
            for i in range(len(new_drops)):
                self.drops[i].copy(new_drops[i])
        
        if self.events == self.events:
            new_events = numpy.load(f"{self.path}/events.npy", None, True)
            if len(self.events) < len(new_events):
                for i in range(len(new_events) - len(self.events)):
                    self.events.append(events.event(self,events.event_data(1,1,"beer")))
            for i in range(len(new_events)):
                self.events[i].copy(new_events[i])


        
        self.need_recover = False

    def main(self):
        while True:
            self.event_list = pygame.event.get()
            if self.game_started:
                if self.need_recover:
                    self.recover(self.path)
                for event in self.event_list:
                    if event.type == pygame.QUIT:
                        self.close(self.path)
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.player.gui_open = False
                            self.player.inventory_display.close_inventory()
                            self.player.hotbar.close_hotbar()
                            self.close(self.path)
                        if event.key == pygame.K_F11:
                            pygame.display.toggle_fullscreen()

                self.update()
                
                self.camera_group.custom_draw(self.player,self.caves)
            else:
                self.path = self.world_menu_selector.updator(self.event_list, self.world_menu)
                self.camera_group.custom_draw(self.world_menu,[])
                for event in self.event_list:
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_F11:
                            pygame.display.toggle_fullscreen()
                        if event.key == pygame.K_ESCAPE:
                            pygame.quit()
                            sys.exit()
                        if event.key == pygame.K_RETURN:
                            self.world_menu_selector.delete()
                            self.world_menu.delete()
                            self.copy_right_text.delete()
                            self.player = Player((3001, 3008), self)
                            if os.path.exists(f"{self.path}/blocks.npy"):
                                self.need_recover = True
                            else:
                                self.world_gen()
                            self.game_started = True
            pygame.display.update()

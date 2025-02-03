import socket,entities,numpy,pygame,gui,random,events,default,entities,objects,items,json,threading,pickle
from zeroconf import Zeroconf, ServiceInfo

class server:
    def __init__(self,path):
        self.port = 55555
        self.lock = threading.Lock()

        self.game_running = True
        pygame.init()
        pygame.time.set_timer(pygame.USEREVENT, 1000)
        self.TIMER_EVENT = pygame.USEREVENT + 1
        pygame.time.set_timer(self.TIMER_EVENT, 100)
        self.camera_group = gui.CameraGroup()
        pygame.display.set_mode((800, 400), pygame.SCALED | pygame.RESIZABLE)
        self.game_started = False
        self.remove_player_list = []
        pygame.display.set_caption("WorldSpawn")
        pygame.display.set_icon(pygame.image.load(default.resource_path("assets/gui/world_icon.png")))
        self.players = [entities.Player((3001, 3008), self)]


        self.owner = self.players[0]
        self.update_data = []
        # World_gen
        self.event_list = []
        self.objects = []
        self.caves = []
        self.entities = []
        self.drops = []
        self.events = []
        self.projectiles = []

    def get_local_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))  # Google's DNS server
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except:
            return "127.0.0.1"

    def handle_client(self,conn, addr):
        print(f"New connection: {addr}")
        # id = conn.recv(1024).decode()
        # played_before = False
        # for player in self.players:
        #     if player.id == id:
        #         played_before = True
        #         break
        self.players.append(entities.Player((3001,3008),self))
        # self.players[-1] = id
        # if played_before:
        #     self.players[-1].load_from_file(self.path,id)
        player = self.players[-1]

        # try:
        while True:
            # Receive data from client
            data = default.recv_msg(conn)
            if not data:
                raise Exception("no data received from client")
            data = default.unserialize_pygame_inputs(data)
            self.update_data.append([player]+data)
            send_data = [self.camera_group.to_dict(player),{"rect":player.rect,"image":default.to_bytes(player.image),"size":player.image.get_size()}]
            default.send_msg(conn,send_data)
        # except Exception as e:
        #     print(e)
        #     print(f"Connection lost: {addr}")
        #     conn.close()
        #     self.remove_player_list.append(player)

    def close(self):
        self.camera_group.close()

    def world_gen(self):
        self.events.append(events.event(self,events.event_data(5*60,2.5*60,"night","night",["zombie", "skeleton", "troll", "ogre", "fungal", "cyclops","caveman","witch","stone_golem"])))
        self.events.append(events.event(self,events.event_data(20*60,2.5*60,"goblin_raid","goblin_gas",["goblin", "goblin_witch", "goblin_archer", "goblin_spikeball", "goblin_wolf_rider"],summon_delay=4)))
        self.events.append(events.event(self,events.event_data(10*60,2.5*60,"rain","rain",["water_golem", "tornado", "water_golem_mini", "tornado_mini"],summon_delay=6)))
        self.objects.append(objects.object(self, (2954, 2970), default.get_object("spawn0")))
        used_places = []
        for i in range(400):
            while True:
                random_place = (random.randint(4, 184) * 32, random.randint(5, 255) * 23)
                if random_place not in used_places:
                    used_places.append(random_place)
                    self.objects.append(objects.object(self, random_place,default.get_object("rock")))
                    break
            if i < 180:
                for name in ["tree_white","tree_swirling","tree_willow","tree_cherry","tree_oak","tree_spruce","bush","twig"]:
                    while True:
                        random_place = (random.randint(4, 184) * 32, random.randint(5, 255) * 23)
                        if random_place not in used_places:
                            used_places.append(random_place)
                            self.objects.append(objects.object(self, random_place, default.get_object(name)))
                            break

            if i < 100:
                for name in ["pumpkin","tomato","potato","carrot","wheat","flower_red","flower_white","flower_blue","flower_green","flower_black"]:
                    while True:
                        random_place = (random.randint(4, 184) * 32, random.randint(5, 255) * 23)
                        if random_place not in used_places:
                            used_places.append(random_place)
                            self.objects.append(objects.object(self, random_place, default.get_object(name)))
                            break
            if i < 50:
                for name in ["lake","cliff","mini_cliff"]:
                    while True:
                        random_place = (random.randint(4, 184) * 32, random.randint(5, 255) * 23)
                        if random_place not in used_places:
                            used_places.append(random_place)
                            self.objects.append(objects.object(self, random_place, default.get_object(name)))
                            break
            if i < 12:
                for name in ["goat", "cow", "pig", "sheep", "chicken", "duck", "deer", "horse", "lion","dog"]:
                    self.entities.append(entities.entity(self, default.get_entity(name),(random.randint(10, 178) * 32, random.randint(10, 151) * 23)))
                for name in ["coal_ore", "copper_ore", "iron_ore", "silver_ore", "gold_ore", "crystal","rock"]:
                    while True:
                        random_place = (random.randint(4, 184) * 32, random.randint(5, 255) * 23)
                        if random_place not in used_places:
                            used_places.append(random_place)
                            self.caves.append(objects.cave(random_place, self, name, 15, self.objects))
                            break
            if i < 4:
                for name in ["sand_temple","olympos","ruined_village","cursed_olympos","knight_tower","defence_tower","ship"]:
                    while True:
                        random_place = (random.randint(4, 184) * 32, random.randint(5, 255) * 23)
                        if random_place not in used_places:
                            used_places.append(random_place)
                            self.objects.append(objects.object(self, random_place, default.get_object(name)))
                            break
        for block in self.objects:
            if block.data.plant_data != None:
                block.stage = block.data.plant_data.max_stage
        self.objects.append(objects.object(self, (0, 7061), default.get_object("cave_border_x")))
        self.objects.append(objects.object(self, (0, 8020), default.get_object("cave_border_x")))
        self.objects.append(objects.object(self, (0, 7061), default.get_object("cave_border_y")))
        self.objects.append(objects.object(self, (959, 7061), default.get_object("cave_border_y")))
        self.objects.append(
            objects.object(self, (0, -529), objects.object_data("border_x", None, None, None, None, True)))
        self.objects.append(
            objects.object(self, (0, 6000), objects.object_data("border_x", None, None, None, None, True)))
        self.objects.append(
            objects.object(self, (-529, -529), objects.object_data("border_y", None, None, None, None, True)))
        self.objects.append(objects.object(self, (6003, -529), objects.object_data("border_y", None, None, None, None, True)))

    def recover(self):
        if self.objects == self.objects:
            new_blocks = numpy.load(f"{self.path}/blocks.npy", None, True)
            if len(self.objects) < len(new_blocks):
                for i in range(len(new_blocks) - len(self.objects)):
                    self.objects.append(objects.object(self, (10, 10), objects.get_object("rock")))
            for i in range(len(new_blocks)):
                if new_blocks[i] != None:
                    self.objects[i].copy(new_blocks[i], self)
                else:
                    self.objects[i] = new_blocks[i]

        if self.entities == self.entities:
            new_entities = numpy.load(f"{self.path}/entities.npy", None, True)
            if len(self.entities) < len(new_entities):
                for i in range(len(new_entities) - len(self.entities)):
                    self.entities.append(entities.entity(self, entities.get_entity("cow"), (10, 10)))
            for i in range(len(new_entities)):
                if new_entities[i] != None:
                    self.entities[i].copy(new_entities[i], self)
                else:
                    self.entities[i] = None
        if self.caves == self.caves:
            new_caves = numpy.load(f"{self.path}/caves.npy", None, True)

            if len(self.caves) < len(new_caves):
                for i in range(len(new_caves) - len(self.caves)):
                    self.caves.append(objects.cave((10, 10), self, "coal_ore", 0, self.objects))
            for i in range(len(new_caves)):
                self.caves[i].copy(new_caves[i], self.camera_group)
        if self.drops == self.drops:
            new_drops = numpy.load(f"{self.path}/drops.npy", None, True)
            if len(self.drops) < len(new_drops):
                for i in range(len(new_drops) - len(self.drops)):
                    self.drops.append(items.item(self, (10, 10), 1, default.get_material("wood")))
            for i in range(len(new_drops)):
                self.drops[i].copy(new_drops[i])

        if self.events == self.events:
            new_events = numpy.load(f"{self.path}/events.npy", None, True)
            if len(self.events) < len(new_events):
                for i in range(len(new_events) - len(self.events)):
                    self.events.append(events.event(self, events.event_data(1, 1, "beer")))
            for i in range(len(new_events)):
                self.events[i].copy(new_events[i])

    def main(self):
        with self.lock:
            threading.Thread(target=self.start_server).start()

            self.world_gen()
            while self.game_running:
                self.owner.mouse = pygame.mouse.get_pos()
                self.owner.events = pygame.event.get()
                self.event_list = self.owner.events
                self.owner.keys = pygame.key.get_pressed()
                self.owner.keys = default.get_pressed_key_names(self.owner.keys)
                for data in self.update_data:
                    data[0].keys = data[2]
                    data[0].events = data[1]
                    data[0].mouse = data[3]
                for event in self.owner.events:
                    if event.type == pygame.QUIT:
                        self.game_running = False
                
                self.game_update()
                try:
                    self.camera_group.custom_draw(self.owner)
                except:
                    pass
                pygame.display.flip()
                for player in self.remove_player_list:
                    player.gui_open = False
                    self.remove_player_list.remove(player)
                    player.close()
                    self.camera_group.remove(player)
                    self.players.remove(player)

            pygame.quit()

    def start_server(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(("0.0.0.0", self.port))
        server.settimeout(5)# Bind to all network interfaces
        server.listen(5)
        print(f"use {default.encrypt(self.get_local_ip())} to join")

        print("Server started!")
        print("Waiting for connections...")
        while self.game_running:
            try:
                conn, addr = server.accept()
                print(f"Client connected from {addr}")
                threading.Thread(target=self.handle_client,args=(conn,addr)).start()
            except:
                pass



        server.close()

    def game_update(self):
        for Block in self.objects:
            if Block.render(self.players):
                if Block.updator(self):
                    self.objects.remove(Block)
                    del Block
        for Entity in self.entities:
            if Entity.render(self.players):
                if Entity.updator(self):
                    self.entities.remove(Entity)
                    del Entity
        for drop in self.drops:
            if drop.render(self.players):
                if drop.updator(self):
                    self.drops.remove(drop)
                    del drop
        for Projectile in self.projectiles:
            if Projectile.render(self.players):
                if Projectile.updator(self):
                    self.projectiles.remove(Projectile)
                    del Projectile
        for event in self.events:
            event.updator(self)
        for cave in self.caves:
            if cave.render(self.players):
                cave.updator(self)

        for player in self.players:
            player.updator(self)

test = server("test")
test.main()
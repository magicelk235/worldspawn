import socket,pygame,gui,random,events,default,entities,objects,items,threading,pickle,os

class server:
    def __init__(self,path):
        self.port = 55555
        self.lock = threading.Lock()
        self.path = path
        self.banned_players = []
        self.game_running = True
        pygame.init()
        pygame.time.set_timer(pygame.USEREVENT, 1000)
        self.TIMER_EVENT = pygame.USEREVENT + 1
        pygame.time.set_timer(self.TIMER_EVENT, 100)
        self.camera_group = gui.CameraGroup()
        pygame.display.set_mode((800, 400), pygame.SCALED | pygame.RESIZABLE)
        self.game_started = False
        self.remove_player_list = []
        self.new_players = []
        pygame.display.set_caption(f"WorldSpawn Code:{default.encrypt(self.get_local_ip())}")
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
        self.events.append(events.event(self, events.event_data(5 * 60, 2.5 * 60, "night", "night",
                                                                ["zombie", "skeleton", "troll", "ogre", "fungal",
                                                                 "cyclops", "caveman", "witch", "stone_golem"])))
        self.events.append(events.event(self, events.event_data(20 * 60, 2.5 * 60, "goblin_raid", "goblin_gas",
                                                                ["goblin", "goblin_witch", "goblin_archer",
                                                                 "goblin_spikeball", "goblin_wolf_rider"],
                                                                summon_delay=4)))
        self.events.append(events.event(self, events.event_data(10 * 60, 2.5 * 60, "rain", "rain",
                                                                ["water_golem", "tornado", "water_golem_mini",
                                                                 "tornado_mini"], summon_delay=6)))
        try:
            self.recover()
        except:
            self.world_gen()

    def get_local_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))  # Google's DNS server
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except:
            return "127.0.0.1"

    def close(self):
        events_list = []
        for event in self.events:
            events_list.append(event.to_dict())
        with open(f"{self.path}/events.pkl","wb") as file:
            pickle.dump(events_list,file)

        entities_list = []
        for entity in self.entities:
            entities_list.append(entity.to_dict())
        with open(f"{self.path}/entities.pkl","wb") as file:
            pickle.dump(entities_list,file)

        objects_list = []
        for object in self.objects:
            objects_list.append(object.to_dict())
        with open(f"{self.path}/objects.pkl", "wb") as file:
            pickle.dump(objects_list, file)

        caves_list = []
        for cave in self.caves:
            caves_list.append(cave.to_dict())
        with open(f"{self.path}/caves.pkl", "wb") as file:
            pickle.dump(caves_list, file)

        if not os.path.exists(f"{self.path}/players"):
            os.mkdir(f"{self.path}/players")
        for player in self.players:
            player_data = player.to_dict()
            with open(f"{self.path}/players/{player.id}.pkl", "wb") as file:
                pickle.dump(player_data, file)

        server_data = [self.banned_players,self.owner.id]
        with open(f"{self.path}/server_data.pkl", "wb") as file:
            pickle.dump(server_data, file)

    def handle_client(self,conn, addr):
        print(f"New connection: {addr}")
        id = default.recv_msg(conn)
        self.new_players.append(id)

        player = None
        try:
            while True:
                if player == None:
                    player = default.get_player(self.players,id)
                else:
                    data = default.recv_msg(conn)
                    if not data:
                        raise Exception("no data received from client")
                    data = default.unserialize_pygame_inputs(data)
                    self.update_data.append([player]+data)
                    send_data = [self.camera_group.to_dict(player),{"rect":player.rect,"image":default.to_bytes(player.image),"size":player.image.get_size()}]
                    default.send_msg(conn,send_data)
        except Exception as e:
            print(e)
            print(f"Connection lost: {addr}")
            conn.close()
            self.remove_player_list.append(player)

    def world_gen(self):

        self.objects.append(objects.object(self, (2954, 2970), default.get_object("spawn0")))
        used_places = []
        for i in range(400):
            print(i)
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

        with open(f"{self.path}/server_data.pkl","rb") as file:
            server_data = pickle.load(file)
            self.banned_players = server_data[0]
            self.players[-1].from_dict(self.path,server_data[1])

        with open(f"{self.path}/objects.pkl","rb") as file:
            new_blocks = pickle.load(file)
            if len(self.objects) < len(new_blocks):
                for i in range(len(new_blocks) - len(self.objects)):
                    self.objects.append(objects.object(self, (10, 10), default.get_object("rock")))
            for i in range(len(new_blocks)):
                self.objects[i].from_dict(new_blocks[i])

        with open(f"{self.path}/entities.pkl","rb") as file:
            new_entities = pickle.load(file)
            if len(self.entities) < len(new_entities):
                for i in range(len(new_entities) - len(self.entities)):
                    self.entities.append(entities.entity(self, default.get_entity("cow"), (10, 10)))
            for i in range(len(new_entities)):
                self.entities[i].from_dict(new_entities[i])

        with open(f"{self.path}/caves.pkl","rb") as file:
            new_caves = pickle.load(file)
            if len(self.caves) < len(new_caves):
                for i in range(len(new_caves) - len(self.caves)):
                    self.caves.append(objects.cave((999999,99999),self,"rock",15,self.objects))
            for i in range(len(new_caves)):
                self.caves[i].from_dict(new_caves[i])

        with open(f"{self.path}/events.pkl","rb") as file:
            new_events = pickle.load(file)
            for i in range(len(new_events)):
                self.events[i].from_dict(new_events[i])

    def main(self):
        with self.lock:
            threading.Thread(target=self.start_server).start()
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
                for id in self.new_players:
                    self.players.append(entities.Player((3001, 3008), self))
                    if os.path.exists(f"{self.path}/players/{id}.pkl"):
                        self.players[-1].from_dict(self.path, id)
                    self.players[-1].id = id
                    self.new_players.remove(id)

                for event in self.owner.events:
                    if event.type == pygame.QUIT:
                        self.game_running = False

                self.game_update()
                try:
                    self.camera_group.custom_draw(self.owner,True)
                except:
                    pass
                pygame.display.flip()
                for player in self.remove_player_list:
                    player.gui_open = False
                    self.remove_player_list.remove(player)
                    if not os.path.exists(f"{self.path}/players"):
                        os.mkdir(f"{self.path}/players")
                    with open(f"{self.path}/players/{player.id}.pkl", "wb") as f:
                        pickle.dump(player.to_dict(),f)
                    player.to_dict()
                    self.camera_group.remove(player)
                    player.close()
                    self.players.remove(player)
                    del player
            self.close()
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
                    self.camera_group.remove(Block)
                    Block.rect = None
                    del Block
        for Entity in self.entities:
            if Entity.render(self.players):
                if Entity.updator(self):
                    self.entities.remove(Entity)
                    self.camera_group.remove(Entity)
                    Entity.rect = None
                    del Entity
        for drop in self.drops:
            if drop.render(self.players):
                if drop.updator(self):
                    self.drops.remove(drop)
                    self.camera_group.remove(drop)
                    del drop
        for Projectile in self.projectiles:
            if Projectile.render(self.players):
                if Projectile.updator(self):
                    self.projectiles.remove(Projectile)
                    self.camera_group.remove(Projectile)
                    del Projectile
        for event in self.events:
            event.updator(self)
        for cave in self.caves:
            if cave.render(self.players):
                cave.updator(self)

        for player in self.players:
            player.updator(self)

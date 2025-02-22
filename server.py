import socket,pygame,gui,random,events,default,entities,objects,items,threading,pickle,os,world_generation,cv2

class server:
    def __init__(self,path):
        self.port = 55555

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
        self.players = [entities.Player((0, 0),"world", self)]

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
        self.particles = []
        chunk_data = {"objects":[
            {"name":"tree_cherry","percent":1/3,"min":1,"max":3},
            {"name":"tree_oak","percent":1/3,"min":1,"max":3},
            {"name":"tree_spruce","percent":1/3,"min":1,"max":3},
            {"name":"bush","percent":1/2,"min":1,"max":3},

            {"name":"twig","percent":1/4,"min":1,"max":2},
            {"name":"rock","percent":1,"min":0,"max":2},

            {"name":"sand_temple","percent":1/50,"min":1,"max":1},
            {"name":"olympos","percent":1/50,"min":1,"max":1},
            {"name":"defence_tower","percent":1/50,"min":1,"max":1},
            {"name":"ruined_village","percent":1/50,"min":1,"max":1},
            {"name":"knight_tower","percent":1/50,"min":1,"max":1},
            {"name":"cursed_olympos","percent":1/50,"min":1,"max":1},
            {"name":"ship","percent":1/50,"min":1,"max":1},

            {"name": "flower_blue", "percent": 1 / 3, "min": 1, "max": 2},
            {"name": "flower_green", "percent": 1 / 3, "min": 1, "max": 2},
            {"name": "flower_red", "percent": 1 / 3, "min": 1, "max": 2},
            {"name": "flower_white", "percent": 1 / 3, "min": 1, "max": 2},
            {"name": "flower_black", "percent": 1 / 3, "min": 1, "max": 2},

            {"name": "wheat", "percent": 1 / 3, "min": 1, "max": 2},
            {"name": "potato", "percent": 1 / 3, "min": 1, "max": 2},
            {"name": "carrot", "percent": 1 / 3, "min": 1, "max": 2},
            {"name": "tomato", "percent": 1 / 3, "min": 1, "max": 2},
            {"name": "pumpkin", "percent": 1 / 3, "min": 1, "max": 2},

            {"name": "lake", "percent": 1 / 7, "min": 0, "max": 2},
            {"name": "cliff", "percent": 1 / 7, "min": 0, "max": 2},
            {"name": "mini_cliff", "percent": 1 / 7, "min": 0, "max": 2},
            {"name": "cave", "percent": 1 / 6, "min": 1, "max": 2},

        ]

,"entities":[
            {"name":"cow","percent":1/8,"min":0,"max":2},
            {"name":"lion","percent":1/8,"min":0,"max":2},
            {"name":"chicken","percent":1/8,"min":0,"max":2},
            {"name":"horse","percent":1/8,"min":0,"max":2},
            {"name":"deer","percent":1/8,"min":0,"max":2},
            {"name":"duck","percent":1/8,"min":0,"max":2},
            {"name":"pig","percent":1/8,"min":0,"max":2},
            {"name":"goat","percent":1/8,"min":0,"max":2},
            {"name":"dog","percent":1/8,"min":0,"max":2},
            {"name":"sheep","percent":1/8,"min":0,"max":2},
            ],
        "caves":[]}

        chunk_data =world_generation.chunk_data("grass",chunk_data)
        chunk_data1 = {"objects": [{"name": "cave_rock", "percent": 0.70, "min": 1, "max": 5},
                                   {"name": "coal_ore", "percent": 0.35, "min": 1, "max": 2},
                                   {"name": "copper_ore", "percent": 0.30, "min": 1, "max": 2},
                                   {"name": "iron_ore", "percent": 0.25, "min": 1, "max": 2},
                                   {"name": "silver_ore", "percent": 0.20, "min": 1, "max": 2},
                                   {"name": "gold_ore", "percent": 0.15, "min": 1, "max": 2},

                                   {"name": "cave_wall_x", "percent": 0.5, "min": 1, "max": 5},
                                   {"name": "cave_wall_y", "percent": 0.5, "min": 1, "max": 5},
                                   ],"entities": [],"caves":[]}
        chunk_data1 = world_generation.chunk_data("cave_ground", chunk_data1)
        self.dimensions = [world_generation.dimension("world",chunk_data),world_generation.dimension("cave",chunk_data1)]
        self.events.append(events.event(self, events.event_data(1, 10 ** 60, "night", "night",["zombie", "skeleton", "troll", "ogre", "fungal","cyclops", "caveman", "witch", "stone_golem"],summon_delay=6,dimension="cave")))
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
        self.objects.append(objects.object(self, (2954-3008, 2970-3003), "world", default.get_object("spawn0")))
        try:
            self.recover()
        except:
            pass

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

        if not os.path.exists(f"{self.path}/players"):
            os.mkdir(f"{self.path}/players")
        for player in self.players:
            player_data = player.to_dict()
            with open(f"{self.path}/players/{player.id}.pkl", "wb") as file:
                pickle.dump(player_data, file)

        server_data = [self.banned_players,self.owner.id]
        with open(f"{self.path}/server_data.pkl", "wb") as file:
            pickle.dump(server_data, file)
        for dimension in self.dimensions:
            dimension.save(self)

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
                    screen = self.camera_group.to_dict(player)
                    default.send_surface(conn,screen)
        except Exception as e:
            print(e)
            print(f"Connection lost: {addr}")
            conn.close()
            self.remove_player_list.append(player)

    def recover(self):

        with open(f"{self.path}/server_data.pkl","rb") as file:
            server_data = pickle.load(file)
            self.banned_players = server_data[0]
            self.players[-1].from_dict(self.path,server_data[1])

        with open(f"{self.path}/events.pkl","rb") as file:
            new_events = pickle.load(file)
            for i in range(len(new_events)):
                self.events[i].from_dict(new_events[i])

    def main(self):
        threading.Thread(target=self.start_server).start()
        while self.game_running:
            self.owner.mouse = pygame.mouse.get_pos()
            self.owner.events = pygame.event.get()
            self.event_list = self.owner.events
            self.owner.keys = pygame.key.get_pressed()
            self.owner.keys = default.get_pressed_key_names(self.owner.keys)
            updated_payers = []
            for data in self.update_data:
                if data[0] not in updated_payers:
                    data[0].keys = data[2]
                    data[0].events = data[1]
                    data[0].mouse = data[3]
                    updated_payers.append(data[0])
                    self.update_data.remove(data)
            for id in self.new_players:
                self.players.append(entities.Player((0, 0),"world", self))
                if os.path.exists(f"{self.path}/players/{id}.pkl"):
                    self.players[-1].from_dict(self.path, id)
                self.players[-1].id = id
                self.new_players.remove(id)
            for event in self.owner.events:
                if event.type == pygame.QUIT:
                    self.game_running = False
            self.game_update()
            try:
                self.camera_group.server_draw(self.owner, True)
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
        for dimension in self.dimensions:
            dimension.updator(self)
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
        for cave in self.caves:
            if cave.render(self.players):
                cave.updator(self)

        for particle in self.particles:
            if particle.render(self.players):
                if particle.updator(self):
                    self.particles.remove(particle)
                    self.camera_group.remove(particle)
                    del particle

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


        for player in self.players:
            player.updator(self)

import socket,pygame,gui,random,events,default,entities,objects,items,threading,pickle,os,world_generation,cv2,uuid

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
        self.ATTACK_EVENT = pygame.USEREVENT + 2

        self.camera_group = gui.CameraGroup()
        pygame.display.set_mode((800, 400), pygame.SCALED | pygame.RESIZABLE)
        self.remove_player_list = []
        self.new_players = []
        pygame.display.set_caption(f"WorldSpawn Code:{default.encrypt(self.get_local_ip())}")
        pygame.display.set_icon(pygame.image.load(default.resource_path("assets/gui/world_icon.png")))
        self.players = {}
        default.create_object(self.players,entities.Player((0, 0),"world", self))
        self.owner = list(self.players.values())[0]
        # World_gen
        self.event_list = []
        self.all_types = {}
        self.objects = {}
        self.entities = {}
        self.drops = {}
        self.events = {}
        self.projectiles = {}
        self.particles = {}
        self.update_dict_data = {}

        self.dimensions = []
        self.seed = random.randint(0,9999999)
        self.dimensions.append(world_generation.dimension(default.get_dimension("world"),self.seed))
        self.dimensions.append(world_generation.dimension(default.get_dimension("cave"),self.seed))
        default.create_object(self.events,events.event(default.get_event("night")))
        default.create_object(self.events,events.event(default.get_event("cave_night")))
        default.create_object(self.events,events.event(default.get_event("rain")))
        default.create_object(self.events,events.event(default.get_event("goblin_raid")))
        default.create_object(self.objects,objects.object(self, (0, 0), "world", default.get_object("spawn0")))
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
        for event in list(self.events.values()):
            events_list.append(event.to_dict())
        with open(f"{self.path}/events.pkl","wb") as file:
            pickle.dump(events_list,file)

        if not os.path.exists(f"{self.path}/players"):
            os.mkdir(f"{self.path}/players")
        for player in list(self.players.values()):
            player_data = player.to_dict()
            with open(f"{self.path}/players/{player.id}.pkl", "wb") as file:
                pickle.dump(player_data, file)

        server_data = [self.banned_players,self.owner.id,self.seed]
        with open(f"{self.path}/server_data.pkl", "wb") as file:
            pickle.dump(server_data, file)
        for dimension in self.dimensions:
            dimension.save(self)

    def post_event(self,event,**kwargs):
        self.event_list.append(pygame.event.Event(event, kwargs))

    def createObject(self,object,objectDict):
        while True:
            id = uuid.uuid4()
            if self.all_types.get(id) == None:
                break
        self.all_types[id] = object
        objectDict[id] = object

    def loadObject(self,object,id,objectDict):
        self.all_types[id] = object
        objectDict[id] = object


    def send_update(self,conn,addr,player):
        dict_data = self.update_dict_data.get(player.id,None)
        if dict_data == None:
            dict_data = {"objects":{},"entities":{},"players":{},"drops":{},"projectiles":{},"particles":{}}
        objects = {}
        entities = {}
        players = {}
        drops = {}
        projectiles = {}
        particles = {}
        default.delta_key_dict(dict_data["objects"],self.objects)
        default.delta_key_dict(dict_data["entities"],self.entities)
        default.delta_key_dict(dict_data["players"],self.players)
        default.delta_key_dict(dict_data["drops"],self.drops)
        default.delta_key_dict(dict_data["particles"],self.particles)
        default.delta_key_dict(dict_data["projectiles"],self.projectiles)
        for key in list(self.objects.keys()):
            if dict_data["objects"].get(key,None) != None:
                objects[key] = default.delta_dict(dict_data["objects"][key],self.objects[key].to_dict_client())
                for key_name in list(objects[key]):
                    dict_data["objects"][key][key_name] = objects[key][key_name]

            else:
                objects[key] = self.objects[key].to_dict_client()
                dict_data["objects"][key] = objects[key]

        for key in list(self.entities.keys()):
            if dict_data["entities"].get(key,None) != None:
                entities[key] = default.delta_dict(dict_data["entities"][key],self.entities[key].to_dict_client()) if key != player.ride_target_id else default.delta_dict(dict_data["entities"][key],self.entities[key].to_dict_client()) | {"rect":self.entities[key].rect.copy()}
                for key_name in list(entities[key]):
                    dict_data["entities"][key][key_name] = entities[key][key_name]
            else:
                entities[key] = self.entities[key].to_dict_client()
                dict_data["entities"][key] = entities[key]

        for key in list(self.players.keys()):
            if dict_data["players"].get(key,None) != None:
                players[key] = default.delta_dict(dict_data["players"][key],self.players[key].to_dict_client()) if key != player.id else self.players[key].to_dict_main_client()
                for key_name in list(players[key]):
                    dict_data["players"][key][key_name] = players[key][key_name]
            else:
                players[key] = self.players[key].to_dict_client() if key != player.id else self.players[key].to_dict_main_client()
                dict_data["players"][key] = players[key]

        for key in list(self.drops.keys()):
            if dict_data["drops"].get(key,None) != None:
                drops[key] = default.delta_dict(dict_data["drops"][key],self.drops[key].to_dict_client())
                for key_name in list(drops[key]):
                    dict_data["drops"][key][key_name] = drops[key][key_name]
            else:
                drops[key] = self.drops[key].to_dict_client()
                dict_data["drops"][key] = drops[key]

        for key in list(self.projectiles.keys()):
            if dict_data["projectiles"].get(key,None) != None:
                projectiles[key] = default.delta_dict(dict_data["projectiles"][key],self.projectiles[key].to_dict_client())
                for key_name in list(projectiles[key]):
                    dict_data["projectiles"][key][key_name] = projectiles[key][key_name]
            else:
                projectiles[key] = self.projectiles[key].to_dict_client()
                dict_data["projectiles"][key] = projectiles[key]

        for key in list(self.particles.keys()):
            if dict_data["particles"].get(key,None) != None:
                particles[key] = default.delta_dict(dict_data["particles"][key],self.particles[key].to_dict_client())
                for key_name in list(particles[key]):
                    dict_data["particles"][key][key_name] = particles[key][key_name]
            else:
                particles[key] = self.particles[key].to_dict_client()
                dict_data["particles"][key] = particles[key]

        default.send_msg(conn,{"objects":objects,"entities":entities,"players":players,"drops":drops,"projectiles":projectiles,"particles":particles})
        self.update_dict_data[player.id] = dict_data

    def handle_client(self,conn, addr):
        print(f"New connection: {addr}")
        id = default.recv_msg(conn)
        self.new_players.append(id)

        player = None
        try:
            while self.game_running:
                if player == None:
                    player = self.players.get(id,None)

                else:
                    data = default.recv_msg(conn)
                    if not data:
                        raise Exception("no data received from client")
                    data = default.unserialize_pygame_inputs(data)
                    player.events += data[0]
                    player.keys += data[1]
                    player.mouse = data[2]
                    self.send_update(conn,addr,player)
                    # screen = self.camera_group.to_dict(player)
                    # default.send_surface(conn,screen)

        except Exception as e:
            print(e)
            print(f"Connection lost: {addr}")
            conn.close()
            self.remove_player_list.append(player)

    def recover(self):
        with open(f"{self.path}/server_data.pkl","rb") as file:
            server_data = pickle.load(file)
            self.banned_players = server_data[0]
            with open(f"{path}/players/{server_data[1]}.pkl", "rb") as f:
                player_dict = pickle.load(f)
                default.load_object(self.players,entities.Player((0,0),"nu",self,player_dict=player_dict),server_data[1])
            self.seed = server_data[2]
            for dimension in self.dimensions:
                dimension.seed = self.seed


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

            for id in self.new_players:

                if os.path.exists(f"{self.path}/players/{id}.pkl"):
                    with open(f"{self.path}/players/{id}.pkl", "rb") as f:
                        player_dict = pickle.load(f)
                        default.load_object(self.players,entities.Player((0,0),"wds",self,player_dict=player_dict),id)
                else:
                    default.load_object(self.players, entities.Player((0, 0), "world", self),id)
                self.new_players.remove(id)
            for event in self.owner.events:
                if event.type == pygame.QUIT:
                    self.game_running = False
            self.game_update()
            self.camera_group.server_draw(self.owner)
            pygame.display.flip()
            for player in self.remove_player_list:
                player.gui_open = False
                self.remove_player_list.remove(player)
                if not os.path.exists(f"{self.path}/players"):
                    os.mkdir(f"{self.path}/players")
                with open(f"{self.path}/players/{player.id}.pkl", "wb") as f:
                    pickle.dump(player.to_dict(),f)
                del self.update_dict_data[player.id]
                self.camera_group.remove(player)
                player.close()
                del self.players[player.id]

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
        for key in list(self.objects.keys()):
            if self.objects[key].render(self.players):
                if self.objects[key].updator(self):
                    self.camera_group.remove(self.objects[key])
                    self.objects[key].rect = None
                    del self.objects[key]
        for key in list(self.entities.keys()):
            if self.entities[key].render(self.players):
                if self.entities[key].updator(self):

                    self.camera_group.remove(self.entities[key])

                    self.entities[key].rect = None
                    del self.entities[key]

        for key in list(self.particles.keys()):
            if self.particles[key].render(self.players):
                if self.particles[key].updator(self):

                    self.camera_group.remove(self.particles[key])
                    del self.particles[key]

        for key in list(self.drops.keys()):
            if self.drops[key].render(self.players):
                if self.drops[key].updator(self):

                    self.camera_group.remove(self.drops[key])
                    del self.drops[key]

        for key in list(self.projectiles.keys()):
            if self.projectiles[key].render(self.players):
                if self.projectiles[key].updator(self):

                    self.camera_group.remove(self.projectiles[key])
                    del self.projectiles[key]
        for key in list(self.events.keys()):
            self.events[key].updator(self)

        for key in list(self.players.keys()):
            self.players[key].updator(self)
            self.players[key].keys = []
            self.players[key].events = []
import socket,default,json,gui,uuid,numpy,threading,objects
import pygame
import pickle

import entities
import particles


class client:
    def __init__(self,path):

        self.server_ip = default.decrypt(path.split("/")[-1])
        PORT = 55555


# Connect to server
        try:
            with open(f"{path}/id.pkl","rb") as f:
                self.id = pickle.load(f)
        except:
            self.id = str(uuid.uuid4())
            with open(f"{path}/id.pkl","wb") as f:
                pickle.dump(self.id,f)

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((self.server_ip, PORT))
        default.send_msg(self.client,self.id)
# Pygame setup
        pygame.init()
        pygame.time.set_timer(pygame.USEREVENT, 1000)
        self.TIMER_EVENT = pygame.USEREVENT + 1
        pygame.time.set_timer(self.TIMER_EVENT, 100)
        pygame.display.set_caption("WorldSpawn")
        pygame.display.set_icon(pygame.image.load(default.resource_path("assets/gui/world_icon.png")))
        pygame.display.set_mode((800,400),pygame.SCALED | pygame.RESIZABLE)
        self.running = True
        self.camera_group = gui.CameraGroup()
        self.objects = {}
        self.player = None
        self.players = {}
        self.projectiles = {}
        self.entities = {}
        self.event_list = []
        self.particles = {}
        self.drops = {}

    def get_data(self,sock):
        dict_data = default.recv_msg(sock)
        unused_keys = list(self.objects.keys())
        for key in list(self.objects.keys()):
            if dict_data["objects"].get(key, None) != None:
                unused_keys.remove(key)
                for key_data in list(dict_data["objects"][key].keys()):
                    if key_data != "image_data":
                        default.set_attr(self.objects[key],key_data,dict_data["objects"][key][key_data])
                    elif default.get_attr(self.objects[key],"image").to_dict() != dict_data["objects"][key][key_data]:
                        default.get_attr(self.objects[key],"image").from_dict(dict_data["objects"][key][key_data])

                del dict_data["objects"][key]
        for key in list(dict_data["objects"].keys()):
            default.load_object(self.objects,objects.object(self,(0,0),"world",default.get_object("pumpkin"),client=True,object_data=dict_data["objects"][key]),key)
        for key in unused_keys:
            self.camera_group.remove(self.objects[key])
            del self.objects[key]

        unused_keys = list(self.entities.keys())
        for key in list(self.entities.keys()):
            if dict_data["entities"].get(key, None) != None:
                unused_keys.remove(key)
                for key_data in list(dict_data["entities"][key].keys()):
                    if key_data != "image_data":
                        default.set_attr(self.entities[key], key_data, dict_data["entities"][key][key_data])
                    else:
                        default.get_attr(self.entities[key],"image").from_dict(dict_data["entities"][key][key_data])

                del dict_data["entities"][key]
        for key in list(dict_data["entities"].keys()):
            default.load_object(self.entities,entities.entity(self,default.get_entity("cow"),(0,0),"world",client=True,entity_dict=dict_data["entities"][key]), key)
        for key in unused_keys:
            self.camera_group.remove(self.entities[key])
            del self.entities[key]

        unused_keys = list(self.particles.keys())
        for key in list(self.particles.keys()):
            if dict_data["particles"].get(key, None) != None:
                unused_keys.remove(key)
                for key_data in list(dict_data["particles"][key].keys()):
                    if key_data != "image_data":
                        default.set_attr(self.particles[key], key_data, dict_data["particles"][key][key_data])
                    elif default.get_attr(self.particles[key],"image").to_dict() != dict_data["particles"][key][key_data]:
                        default.get_attr(self.particles[key],"image").from_dict(dict_data["particles"][key][key_data])
                del dict_data["particles"][key]
        for key in list(dict_data["particles"].keys()):
            default.load_object(self.particles,particles.particle(default.get_particle("night_theme"),(0,0),"world",self,dict_data["particles"][key]), key)
        for key in unused_keys:
            self.camera_group.remove(self.particles[key])
            del self.particles[key]

        unused_keys = list(self.projectiles.keys())
        for key in list(self.projectiles.keys()):
            if dict_data["projectiles"].get(key, None) != None:
                unused_keys.remove(key)
                for key_data in list(dict_data["projectiles"][key].keys()):
                    if key_data != "image_data":
                        default.set_attr(self.projectiles[key], key_data, dict_data["projectiles"][key][key_data])
                    elif default.get_attr(self.projectiles[key],"image").to_dict() != dict_data["projectiles"][key][key_data]:
                        default.get_attr(self.projectiles[key],"image").from_dict(dict_data["projectiles"][key][key_data])
                del dict_data["projectiles"][key]
        for key in list(dict_data["projectiles"].keys()):
            default.load_object(self.projectiles,gui.display_sprite(dict_data["projectiles"][key],self.camera_group), key)
        for key in unused_keys:
            self.camera_group.remove(self.projectiles[key])
            del self.projectiles[key]

        unused_keys = list(self.drops.keys())
        for key in list(self.drops.keys()):
            if dict_data["drops"].get(key, None) != None:
                unused_keys.remove(key)
                for key_data in list(dict_data["drops"][key].keys()):
                    if key_data != "image_data":
                        default.set_attr(self.drops[key], key_data, dict_data["drops"][key][key_data])
                    elif default.get_attr(self.drops[key],"image").to_dict() != dict_data["drops"][key][key_data]:
                        default.get_attr(self.drops[key],"image").from_dict(dict_data["drops"][key][key_data])
                del dict_data["drops"][key]
        for key in list(dict_data["drops"].keys()):
            default.load_object(self.drops,gui.display_sprite(dict_data["drops"][key],self.camera_group), key)
        for key in unused_keys:
            self.camera_group.remove(self.drops[key])
            del self.drops[key]

        unused_keys = list(self.players.keys())
        for key in list(self.players.keys()):
            if dict_data["players"].get(key,None) != None:
                unused_keys.remove(key)
                for key_data in list(dict_data["players"][key].keys()):
                    if key_data != "image_data":
                        default.set_attr(self.players[key],key_data,dict_data["players"][key][key_data])
                        if key_data == "gui_open":
                            if self.players[key].gui_open and not self.players[key].inventory_display.opened:
                                self.players[key].inventory_display.open_inventory(self, self.players[key],self.players[key].inventory.inventory)
                            elif self.players[key].inventory_display.opened and not self.players[key].gui_open:
                                self.players[key].inventory_display.close_inventory()
                    elif default.get_attr(self.players[key],"image").to_dict() != dict_data["players"][key][key_data]:
                        default.get_attr(self.players[key],"image").from_dict(dict_data["players"][key][key_data])
                del dict_data["players"][key]
        for key in list(dict_data["players"].keys()):
            if key != self.id:
                default.load_object(self.players,gui.display_sprite(dict_data['players'][key],self.camera_group),key)
            else:
                default.load_object(self.players,entities.Player((0,0),"world",self,True,dict_data["players"][key]),key)
                self.player = self.players[key]
        del dict_data
        for key in unused_keys:
            self.camera_group.remove(self.players[key])
            del self.players[key]



    def main(self):
        try:
            while self.running:
                self.event_list = pygame.event.get()
                for event in self.event_list:
                    if event.type == pygame.QUIT:
                        raise Exception
                key_states = default.get_pressed_key_names(pygame.key.get_pressed())
                mouse_pos = pygame.mouse.get_pos()
                data = default.serialize_pygame_inputs(self.event_list,key_states,mouse_pos)
                default.send_msg(self.client,data)
                self.get_data(self.client)
                self.player.keys = key_states
                self.player.mouse = mouse_pos
                self.player.events = self.event_list
                self.player.updator(self,True)
                for sprite in self.camera_group.sprites():
                    if isinstance(sprite,gui.inventory_selector):
                        if self.player.inventory_display.selector != sprite:
                            self.camera_group.remove(sprite)
                            del sprite
                self.camera_group.server_draw(self.player)
                pygame.display.flip()
        except:
            pygame.quit()
            self.client.close()
import socket,default,json,gui,uuid
import pygame
import pickle
# uuid.uuid4()
class client:
    def __init__(self,path):

        HOST = default.decrypt(path.split("/")[-1])
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
        self.client.connect((HOST, PORT))
        default.send_msg(self.client,self.id)
# Pygame setup
        pygame.init()
        pygame.display.set_caption("WorldSpawn")
        pygame.display.set_icon(pygame.image.load(default.resource_path("assets/gui/world_icon.png")))
        pygame.display.set_mode((800,400),pygame.SCALED | pygame.RESIZABLE)
        self.running = True
        self.camera_group = gui.CameraGroup()

    def main(self):
        while self.running:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False


            key_states = pygame.key.get_pressed()
            mouse_pos = pygame.mouse.get_pos()
            data = default.serialize_pygame_inputs(events,key_states,mouse_pos)
            default.send_msg(self.client,data)

            server_data = default.recv_msg(self.client)

            self.camera_group.from_dict(server_data[0])

            self.camera_group.normal_draw(gui.fake_player(self.camera_group,server_data[1]["rect"],default.from_bytes(server_data[1]["image"],server_data[1]["size"]),server_data[1]["image"]))
            pygame.display.flip()

            
            
        pygame.quit()
        self.client.close()


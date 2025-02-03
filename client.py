import socket,default,json,gui
import pygame
import pickle




class client:
    def __init__(self):

        HOST = default.decrypt("ghfgyfxfsg")
        print(HOST)
        PORT = 55555

# Connect to server
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((HOST, PORT))

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

test = client()
test.main()

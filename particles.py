import pygame,default,textwrap

class particle_data:
    def __init__(self,name,cooldown,color=(255,255,255),custom_event=None):
        self.name = name
        self.cooldown = cooldown
        self.custom_event = custom_event
        if self.custom_event != None:
            self.custom_event = textwrap.dedent(self.custom_event)

        self.color = color

class particle(pygame.sprite.Sprite):
    def __init__(self, data, pos, dimension, game,particle_dict=None):
        super().__init__(game.camera_group)
        path = f"assets/particles/{data.name}"
        self.data = data
        self.id = None
        self.image = default.image(path)
        self.image.color_image(self.data.color)
        self.rect = self.image.get_rect(dimension,topleft=pos)
        self.cooldown = 0
        if particle_dict:
            self.from_dict_client(particle_dict)

    def to_dict_client(self):
        return {
            "rect":self.rect.copy(),
            "data":self.data,
            "image_data":self.image.to_dict(),
        }

    def from_dict_client(self,particle_dict):
        self.data = particle_dict["data"]
        self.rect = particle_dict["rect"]
        self.image.from_dict(particle_dict["image_data"])

    def render(self,players):
        for player in list(players.values()):
            if player.render.rect.colliderect(self.rect):
                return True

    def updator(self,game):
        if self.data.custom_event != None:
            exec(self.data.custom_event, {}, {"game": game, "self": self})
        for event in game.event_list:
            if event.type == pygame.USEREVENT:
                self.cooldown += 1
                if self.cooldown >= self.data.cooldown:
                    return True
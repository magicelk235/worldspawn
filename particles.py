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
    def __init__(self,particle_data,pos,dimension,game):
        super().__init__(game.camera_group)
        path = f"assets/particles/{particle_data.name}"
        self.particle_data = particle_data
        self.image = default.image(path)
        self.image.color_image(self.particle_data.color)
        self.rect = self.image.get_rect(pos,dimension)
        self.cooldown = 0

    def render(self,players):
        for player in players:
            if player.render.rect.colliderect(self.rect):
                return True

    def updator(self,game):
        if self.particle_data.custom_event != None:
            exec(self.particle_data.custom_event, {}, {"game": game, "self": self})
        for event in game.event_list:
            if event.type == pygame.USEREVENT:
                self.cooldown += 1
                if self.cooldown >= self.particle_data.cooldown:
                    return True

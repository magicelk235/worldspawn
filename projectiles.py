import math,items,pygame,default

class projectile_data:
    def __init__(self,name,max_distance,speed,damage,return_to_attacker=False):
        self.name = name
        self.return_to_attacker = return_to_attacker
        self.max_distance = max_distance
        self.speed = speed
        self.damage = damage

class projectile(pygame.sprite.Sprite):
    def __init__(self,game,dimension,pos1,pos2,data,attacker=None):
        super().__init__(game.camera_group)
        self.path = f"assets/projectiles/{data.name}"
        self.image = default.image(self.path)
        self.id = None
        self.past_path = 0
        self.angle = 0
        self.rect = self.image.get_rect(dimension,topleft=pos1)
        self.data = data
        self.attacker = attacker
        self.angle = (math.degrees(math.atan2(-(pos1[1]-pos2[1]),pos1[0]-pos2[0]))+180) % 360
        if 90 < self.angle < 270:
            self.image.flip(False,True)
        self.image.rotate(self.angle)

    def to_dict_client(self):
        return {
            "rect":self.rect.copy(),
            "image_data":self.image.to_dict(),
        }

    def close(self,game):
        if self.data.return_to_attacker:
            try:
                if not self.attacker.inventory.add_item(default.get_material(self.data.name),1):
                    raise Exception("cant")
            except:
                default.create_object(game.drops,items.item(game, self.attacker.rect.rect.center,self.rect.dimension, 1, default.get_material(self.data.name)))
        self.image = None
        self.rect = None
        self.attacker = None
        del self


    def angle_moving(self):
        radians = abs(math.radians(self.angle))

        dx = self.data.speed * math.cos(radians)
        dy = -self.data.speed * math.sin(radians)

        self.rect.rect.x += dx
        self.rect.rect.y += dy
        self.past_path += abs(dy) + abs(dx)

    def render(self,players):
        for player in list(players.values()):
            if self.rect.colliderect(player.render) or self.data.return_to_attacker:
                return True

    def updator(self,game):
        for object in list(game.objects.values()):
            if self.rect.colliderect(object.rect) and object.health != None and object != self.attacker and not default.has_one_tag(object,self.attacker):
                object.apply_damage(self.data.damage,game,self.attacker)
                self.close(game)

                return True

        for entity in list(game.entities.values()):
            if self.rect.colliderect(entity.rect) and entity != self.attacker and not default.has_one_tag(entity,self.attacker):
                entity.apply_damage(self.data.damage,game,self.attacker)
                self.close(game)
                return True
        for player in list(game.players.values()):
            if self.rect.colliderect(player.rect) and player != self.attacker and not default.has_one_tag(player,self.attacker):
                player.apply_damage(self.data.damage,game,self.attacker)
                self.close(game)
                return True
        if self.past_path > self.data.max_distance:
            self.close(game)
            return True
        self.angle_moving()
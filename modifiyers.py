import pygame,copy

import default

class modifiyer:
    def __init__(self,type,amount,set=True,hand_needed=True,right_click=False,choose_bigger=True,percent=False):
        """
        :param type: damage,shield,max_health
        :param amount: either int or float(%)
        :param set: false for add, true for set
        :param hand_needed: if the modifyer is needed to be on hand to apply
        :param right_click: if the modifiyer should apply on right click
        """
        self.type = type
        self.amount = amount
        self.set = set
        self.hand_needed = hand_needed
        self.right_click = right_click
        self.choose_bigger = choose_bigger
        self.percent = percent

    def __eq__(self, other):
        if isinstance(other,modifiyer):
            if self.type == other.type and self.amount == other.amount and self.set == other.set and self.hand_needed == other.hand_needed and self.right_click == other.right_click and self.choose_bigger == other.choose_bigger and self.percent == other.percent:
                return True
        return False

    @staticmethod
    def find(type,list):
        for object in list:
            if object.type == type:
                return object
            
    @staticmethod
    def get(type,list):
        for object in list:
            if object.type == type:
                return object.amount
        

    @staticmethod
    def set(modifiyers,object,right_click=False,hand=False):
        for modifiyer in modifiyers:
            if (not modifiyer.hand_needed or (modifiyer.hand_needed and hand)) and (not modifiyer.right_click or (modifiyer.right_click and right_click)):
                if modifiyer.set:
                    if modifiyer.choose_bigger and default.get_attr(object,modifiyer.type) < modifiyer.amount:
                        default.set_attr(object,modifiyer.type,modifiyer.amount)
                    elif not modifiyer.choose_bigger:
                        default.set_attr(object, modifiyer.type, modifiyer.amount)
                else:
                    if modifiyer.percent:
                        if isinstance(default.get_attr(object,modifiyer.type),float):
                            value = default.get_attr(object,modifiyer.type)*(modifiyer.amount+1.0)
                            value = int(value*10)

                            default.set_attr(object, modifiyer.type,value)
                        else:
                            default.set_attr(object,modifiyer.type,int(default.get_attr(object,modifiyer.type)*(modifiyer.amount+1.0)))
                    else:
                        default.set_attr(object, modifiyer.type, default.get_attr(object, modifiyer.type)+modifiyer.amount)

class potion_cloud(pygame.sprite.Sprite):
    def __init__(self, pos, game, color, cooldown, modifiyer,modifiyer_cooldown,only_players=False):
        super().__init__(game.camera_group)
        self.only_players = only_players

        self.image = default.load_image("assets/objects/potion_cloud")
        self.rect = self.image.get_rect(center=pos)


        default.color_image(self.image, color)

        self.modifiyer_cooldown = modifiyer_cooldown
        self.cooldown = cooldown
        self.modifiyer = modifiyer

    def render(self,players):
        for player in players:
            if self.rect.colliderect(player.render):
                return True

    def updator(self, game):
        for event in game.event_list:
            if event.type == pygame.USEREVENT:
                self.cooldown -= 1
                if self.cooldown == 0:
                    return True
        if not self.only_players:
            for entity in game.entities:
                if self.rect.colliderect(entity.rect):
                    has_modifiyer = False
                    for temp_modifiyer in entity.temporary_modifiyers:
                        if temp_modifiyer.modifiyer == self.modifiyer:
                            has_modifiyer = True
                            break
                    if not has_modifiyer:
                        entity.temporary_modifiyers.append(temporary_modifiyer(self.modifiyer,self.modifiyer_cooldown))
                        entity.apply_modifiyers()
        for player in game.players:
            if self.rect.colliderect(player.rect):
                has_modifiyer = False
                for temp_modifiyer in player.temporary_modifiyers:
                    if temp_modifiyer.modifiyer == self.modifiyer:
                        has_modifiyer = True
                        break
                if not has_modifiyer:
                    player.temporary_modifiyers.append(temporary_modifiyer(self.modifiyer,self.modifiyer_cooldown))
                    player.inventory.apply_modifiyers()

class temporary_modifiyer:
    def __init__(self,modifiyer,cooldown):
        self.modifiyer = modifiyer
        self.cooldown = cooldown
    def updator(self,game):
        for event in game.event_list:
            if event.type == pygame.USEREVENT:
                self.cooldown -= 1
                if self.cooldown == 0:
                    return True
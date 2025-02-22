import pygame,copy

import default

class modifier:
    def __init__(self,type,amount,set=True,hand_needed=True,right_click=False,choose_bigger=True,percent=False):
        """
        :param type: damage,shield,max_health
        :param amount: either int or float(%)
        :param set: false for add, true for set
        :param hand_needed: if the modifyer is needed to be on hand to apply
        :param right_click: if the modifier should apply on right click
        """
        self.type = type
        self.amount = amount
        self.set = set
        self.hand_needed = hand_needed
        self.right_click = right_click
        self.choose_bigger = choose_bigger
        self.percent = percent

    def __eq__(self, other):
        if isinstance(other,modifier):
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
    def set(modifiers,object,right_click=False,hand=False):
        for modifier in modifiers:
            if (not modifier.hand_needed or (modifier.hand_needed and hand)) and (not modifier.right_click or (modifier.right_click and right_click)):
                if modifier.set:
                    if modifier.choose_bigger and default.get_attr(object,modifier.type) < modifier.amount:
                        default.set_attr(object,modifier.type,modifier.amount)
                    elif not modifier.choose_bigger:
                        default.set_attr(object, modifier.type, modifier.amount)
                else:
                    if modifier.percent:
                        if isinstance(default.get_attr(object,modifier.type),float):
                            value = default.get_attr(object,modifier.type)*(modifier.amount+1.0)
                            value = int(value*10)

                            default.set_attr(object, modifier.type,value)
                        else:
                            default.set_attr(object,modifier.type,int(default.get_attr(object,modifier.type)*(modifier.amount+1.0)))
                    else:
                        default.set_attr(object, modifier.type, default.get_attr(object, modifier.type)+modifier.amount)

class temporary_modifier:
    def __init__(self,modifier,cooldown):
        self.modifier = modifier
        self.cooldown = cooldown
    def updator(self,game):
        for event in game.event_list:
            if event.type == pygame.USEREVENT:
                self.cooldown -= 1
                if self.cooldown == 0:
                    return True
import pygame,default,textwrap

class inventory_item:
    def __init__(self, item_data, count=1):

        self.item_data = item_data
        self.count = count

    def remove(self):
        self.item_data = default.get_material(None)
        self.count = 0


    def copy(self, other):
        self.item_data.copy(other.item_data)
        self.count = other.count

class inventory:
    def __init__(self,x,y,owner,has_modifiers):
        self.inventory = [[None for x in range(x)]for y in range(y)]
        self.x = x
        self.y = y
        self.owner = owner
        self.has_modifiers = has_modifiers
        self.clear_inventory()

    def get_has_parameter(self,parameter,value):
        for x in range(self.x):
            for y in range(self.y):
                if default.get_attr(self.inventory[y][x].item_data,parameter) != value:
                    return self.inventory[y][x]
        return False

    def get_item(self, item_name):
        for x in range(self.x):
            for y in range(self.y - 1, -1, -1):
                if self.inventory[y][x].item_data.item_name == item_name:
                    return self.inventory[y][x]
        return None

    def apply_modifiers(self,right_click=False):
        self.updator()
        if self.has_modifiers:
            self.owner.reset_modifiers()
            try:
                modifiyer.set(self.owner.hand.item_data.modifiyers, self.owner, right_click, True)
            except:pass
            item_name_list = []
            for row in self.inventory:
                for item in row:
                    if item.item_data.item_name not in item_name_list:
                        item_name_list.append(item.item_data.item_name)
                        modifiyer.set(item.item_data.modifiyers, self.owner, right_click, False)
            del item_name_list

    def find_item(self, item_name):
        for x in range(self.x):
            for y in range(self.y - 1, -1, -1):
                if self.inventory[y][x].item_data.item_name == item_name:
                    return [x, y]
        return [None, None]

    def add_item(self, item_data, amount):
        for y in range(self.y - 1, -1, -1):
            for x in range(self.x):
                if self.inventory[y][x].item_data.item_name == item_data.item_name and self.inventory[y][x].count + amount <= self.inventory[y][x].item_data.max:
                    temp = self.inventory[y][x].count
                    self.inventory[y][x].item_data.copy(item_data)
                    self.inventory[y][x].count = amount + temp
                    del temp
                    self.apply_modifiers()
                    return True
        for y in range(self.y - 1, -1, -1):
            for x in range(self.x):
                if self.inventory[y][x].item_data.item_name == None:
                    self.inventory[y][x].item_data.copy(item_data)
                    self.inventory[y][x].count = amount
                    self.apply_modifiers()
                    return True
        return False

    def remove_item_amount(self, item_name, amount):
        for y in range(self.y - 1, -1, -1):
            for x in range(self.x):
                if self.inventory[y][x].item_data.item_name == item_name and self.inventory[y][x].count >= amount:
                    self.inventory[y][x].count -= amount
                    self.apply_modifiers()
                    return True

        return False

    def remove_item(self, item_name):
        for y in range(self.y - 1, -1, -1):
            for x in range(self.x):
                if self.inventory[y][x].item_data.item_name == item_name:
                    self.inventory[y][x].remove()
                    self.apply_modifiers()
                    return True

        return False

    def remove_at(self,x,y):
        self.inventory[y][x].remove()
        self.apply_modifiers()

    def has_item(self, item_name, amount=None):
        for y in range(self.y - 1, -1, -1):
            for x in range(self.x):
                if self.inventory[y][x].item_data.item_name == item_name and (
                        amount == None or self.inventory[y][x].count >= amount):
                    return True
        return False

    def has_item_hand(self, item_name, amount=None):
        if self.hand.item_data.item_name == item_name and (amount == None or self.hand.count >= amount):
            return True
        return False

    def interact(self,x1,y1,x2,y2):
        if self.inventory[y1][x1].item_data.item_name == None:
            self.inventory[y1][x1].copy(self.inventory[y2][x2])
            self.inventory[y2][x2].remove()
        elif self.inventory[y1][x1].item_data.item_name == self.inventory[y2][x2].item_data.item_name and self.inventory[y2][x2].count + self.inventory[y1][x1].count <= self.inventory[y1][x1].item_data.max:
            self.inventory[y1][x1].count += self.inventory[y2][x2].count
            self.inventory[y2][x2].remove()
        elif self.inventory[y1][x1].item_data.item_name == self.inventory[y2][x2].item_data.item_name and self.inventory[y2][x2].count + self.inventory[y1][x1].count > self.inventory[y1][x1].item_data.max:
            self.inventory[y2][x2].count = self.inventory[y2][x2].count + self.inventory[y1][x1].count - self.inventory[y1][x1].item_data.max
            self.inventory[y1][x1].count = self.inventory[y1][x1].item_data.max
        else:
            temp1 = inventory_item(default.get_material(None), 1)
            temp1.copy(self.inventory[y2][x2])
            self.inventory[y2][x2].copy(self.inventory[y1][x1])
            self.inventory[y1][x1].copy(temp1)
            del temp1

    def updator(self):
        for item_row in self.inventory:
            for item in item_row:
                if item.count <= 0:
                    item.remove()

    def conver_to_drops(self,game):
        for row in self.inventory:
            for items in row:
                if items.item_data.item_name != None:
                    game.drops.append(item(game, self.owner.rect.center, items.count, items.item_data))
        self.clear_inventory()

    def drop(self,x,y,game):
        if self.inventory[y][x].item_data.item_name != None:
            game.drops.append(item(game, (self.owner.rect.x + 30, self.owner.rect.y + 30), self.inventory[y][x].count,self.inventory[y][x].item_data))
            self.remove_at(x,y)
            self.apply_modifiers()

    def clear_inventory(self):
        for x in range(self.x):
            for y in range(self.y):
                self.inventory[x][y] = inventory_item(default.get_material(None), 0)
        self.apply_modifiers()

    def copy(self,other):
        self.inventory = other.inventory
        self.x = other.x
        self.y = other.y
        self.owner = other.owner
        self.has_modifiers = other.has_modifiers

class item(pygame.sprite.Sprite):
    def __init__(self, game, pos, count, itemdata):
        super().__init__(game.camera_group)
        self.count = count
        self.path = f'assets/items/{itemdata.item_name}'
        self.image = default.load_image(self.path)
        self.item_data = item_data(None)
        self.cooldown = 0
        self.item_data.copy(itemdata)
        self.rect = self.image.get_rect(topleft=(pos[0],pos[1]))

    def remove(self):
        self.rect = None

    def updator(self, game):
        for player in game.players:
            if self.rect.colliderect(player.rect):
                if player.inventory.add_item(self.item_data,self.count):
                    self.remove()
                    return True
        for event in game.event_list:
            if event.type == pygame.USEREVENT:
                self.cooldown += 1
                if self.cooldown > 60*3:
                    self.remove()
                    return True

    def render(self,players):
        for player in players:
            if self.rect.colliderect(player.render):
                return True

    def close(self):
        self.image = None

    def copy(self,other):
        self.count = other.count
        self.path = other.path
        self.cooldown = other.cooldown
        self.image = default.load_image(self.path)
        self.item_data = other.item_data
        self.rect = other.rect

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

class item_data:

    def __init__(self, item_name, max=32, modifiyers=[modifiyer("damage",1),modifiyer("attack_cooldown",0.5)],tool_type=None,color=None,event=None):
        self.tool_type = tool_type
        self.event = event
        if self.event != None:
            self.event = textwrap.dedent(self.event)
        self.modifiyers = modifiyers
        self.item_name = item_name
        self.max = max
        self.color = color

    def copy(self,other):
        self.event = other.event
        self.tool_type = other.tool_type
        self.modifiyers = other.modifiyers
        self.item_name = other.item_name
        self.max = other.max
        self.color = other.color

class lootable:
    def __init__(self, loot_data, count=1, chance=1.0):
        self.loot_data = loot_data
        self.count = count
        self.chance = chance
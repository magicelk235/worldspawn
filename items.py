import pygame,default,textwrap

import objects
from modifiers import modifier


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

    def __eq__(self, other):
        if isinstance(other,inventory_item):
            if other.count == self.count and other.item_data == self.item_data:
                return True
        return False


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

    def apply_modifiers(self, right_click=False):
        self.updator()
        if self.has_modifiers:
            self.owner.reset_modifiers()
            try:
                modifier.set(self.owner.hand.item_data.modifiers, self.owner, right_click, True)
            except:pass
            item_name_list = []
            for row in self.inventory:
                for item in row:
                    if item.item_data.item_name not in item_name_list:
                        item_name_list.append(item.item_data.item_name)
                        modifier.set(item.item_data.modifiers, self.owner, right_click, False)
            used_modifiers_list = []
            for temp_modifier in self.owner.temporary_modifiers:
                if not temp_modifier.modifier in used_modifiers_list:
                    modifier.set([temp_modifier.modifier],self.owner)
                    used_modifiers_list.append(temp_modifier.modifier)

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

    def convert_to_drops(self, game):
        lootable_list = []
        for row in self.inventory:
            for items in row:
                if items.item_data.item_name != None:
                    lootable_list.append(lootable(items.item_data,items.count))
        if lootable_list != []:
            default.create_object(game.objects,objects.object(game,self.owner.rect.rect.center,self.owner.rect.dimension,objects.object_data("grave",lootable_list)))
        self.clear_inventory()

    def drop(self,x,y,game):
        if self.inventory[y][x].item_data.item_name != None:
            default.create_object(game.drops,item(game, (self.owner.rect.rect.x + 30, self.owner.rect.rect.y + 30),self.owner.rect.dimension, self.inventory[y][x].count,self.inventory[y][x].item_data))
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
    def __init__(self, game, pos,dimension, count, itemdata):
        super().__init__(game.camera_group)
        self.count = count
        self.path = f'assets/items/{itemdata.item_name}'
        self.image = default.image(self.path)
        self.item_data = item_data(None)
        self.cooldown = 0
        self.item_data.copy(itemdata)
        self.rect = self.image.get_rect(dimension,topleft=pos)

    def to_dict_client(self):
        return {
            "rect":self.rect.copy(),
            "image_data":self.image.to_dict(),
        }

    def remove(self):
        self.rect = None

    def updator(self, game):
        for player in list(game.players.values()):
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
        for player in list(players.values()):
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

class item_data:
    def __init__(self, item_name, max=32, modifiers=[modifier("damage", 1), modifier("attack_cooldown", 0.5)], tool_type=None, color=None, event=None):
        self.tool_type = tool_type
        self.event = event
        if self.event != None:
            self.event = textwrap.dedent(self.event)
        self.modifiers = modifiers
        self.item_name = item_name
        self.max = max
        self.color = color

    def copy(self,other):
        self.event = other.event
        self.tool_type = other.tool_type
        self.modifiers = other.modifiers
        self.item_name = other.item_name
        self.max = other.max
        self.color = other.color

    def __eq__(self, other):
        return self.tool_type == other.tool_type and self.event == other.event and self.modifiers == other.modifiers and self.item_name == other.item_name and self.max == other.max and self.color == other.color

class lootable:
    def __init__(self, loot_data, count=1, chance=1.0):
        self.loot_data = loot_data
        self.count = count
        self.chance = chance
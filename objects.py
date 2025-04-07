import random,items,default,entities,pygame,gui

class plant:
    def __init__(self,max_stage,drop,grow_time,harvest_to_stage=-1):
        self.max_stage = max_stage
        self.drop = drop
        self.grow_time = grow_time
        self.harvest_to_stage = harvest_to_stage

class portal:
    def __init__(self,dimension = None,location=None,one_way=False):
        self.one_way = one_way
        self.dimension = dimension
        self.location = location

class object_data:
    def __init__(self, name, lootable_list=None, health=1, needed_item=None, type_range=None, is_solid=False, hitbox=None, plant_data=None, recipe_list=None, door=False, store=False, floor=False, dyeable=False,summoner=None,thrower=None,custom_code=None,portal_data=None):
        self.name = name
        self.custom_code = custom_code
        self.lootable_list = lootable_list
        self.health = health
        self.needed_item = needed_item
        self.type_range = type_range
        self.is_solid = is_solid
        self.door = door
        self.portal_data = portal_data

        self.dyeable = dyeable
        self.hitbox = hitbox
        self.plant_data = plant_data
        self.recipe_list = recipe_list
        self.floor = floor
        self.store = store
        self.summoner = summoner
        self.thrower = thrower

class object(pygame.sprite.Sprite):
    def __init__(self, game, pos,dimension, data, tag=None,client=False,object_data=None):
        super().__init__(game.camera_group)
        self.data = data #
        self.name = data.name #
        self.stage = 1 #
        self.timers = {"plant": 0}
        self.attacker = None
        self.tag = tag #
        self.id = hash(self) #
        self.color = (255,255,255) #
        if data.type_range:
            type = str(random.randint(data.type_range.min_value, data.type_range.max_value))
            self.path = f'assets/objects/{self.name}{type}'

        elif data.plant_data != None:
            self.path = f'assets/objects/{self.name}{self.stage}'

        elif data.door:
            self.path = f'assets/objects/{self.name}_close'

        else:
            self.path = f'assets/objects/{self.name}'
        self.image = default.image(self.path)
        self.is_solid = data.is_solid #
        self.rect = self.image.get_rect(dimension,topleft=pos)
        try:
            len(data.lootable_list)
            self.lootable_list = data.lootable_list
        except:
            self.lootable_list = [data.lootable_list]
        if data.hitbox == None:
            self.hitbox = default.hitbox(self.rect.rect.w,self.rect.rect.h)
        else:
            self.hitbox = data.hitbox

        self.health = data.health
        self.rect_hitbox = default.rect(pygame.Rect(self.rect.rect.x+self.hitbox.offset_x,self.rect.rect.y+self.hitbox.offset_y,self.hitbox.hitbox_x,self.hitbox.hitbox_y),"world")
        self.portal_origin_pos = self.rect.rect.topleft + (self.rect.dimension,)
        self.timers["summon"] = 0
        self.timers["projectile"] = 0
        self.portal_open = False
        if object_data:
            if client:
                self.from_dict_client(object_data)
            else:
                self.from_dict(object_data)


    def to_dict_client(self):
        return {
            "data":self.data,
            "rect":self.rect.copy(),
            "name":self.name,
            "image_data":self.image.to_dict(),
            "stage":self.stage,
        }

    def from_dict_client(self,object_dict):
        self.data = object_dict["data"]
        self.rect = object_dict["rect"]
        self.name = object_dict["name"]
        self.stage = object_dict["stage"]
        self.image.from_dict(object_dict["image_data"])
        self.path = self.image.path
        self.apply_color(self.color)

    def to_dict(self):
        return {
        "data":self.data,
        "health":self.health,
        "rect":self.rect.copy(),
        "path":self.path,
        "name":self.name,
        "stage":self.stage,
        "hitbox":self.hitbox,
        "rect_hitbox":self.rect_hitbox,
        "timers":self.timers,
        "is_solid":self.is_solid,
        "tag":self.tag,
        "id":self.id,
        "color":self.color,
        "portal_origin_pos":self.portal_origin_pos,
        "lootable_list":self.lootable_list
        }

    def from_dict(self,object_dict):
        self.data = object_dict["data"]

        self.health = object_dict["health"]
        self.rect = object_dict["rect"]
        self.path = object_dict["path"]
        self.timers = object_dict["timers"]
        self.name = object_dict["name"]
        self.portal_origin_pos = object_dict["portal_origin_pos"]
        self.lootable_list = object_dict["lootable_list"]
        self.stage = object_dict["stage"]
        self.hitbox = object_dict["hitbox"]
        self.rect_hitbox = object_dict["rect_hitbox"]
        self.is_solid = object_dict["is_solid"]
        self.tag = object_dict["tag"]
        self.id = object_dict["id"]
        self.color = object_dict["color"]
        self.image.replace_path(self.path)
        self.apply_color(self.color)

    def updator(self, game):
        if self.timers.get("damage",None) != None:
            if self.timers["damage"] > 0.2:
                image = self.image.to_dict()
                image["color"] = self.color + (255,)
                self.image.from_dict(image)
                del self.timers["damage"]
        if self.data.recipe_list != None and isinstance(self.data.recipe_list[-1].result.item_data,str):
            for recipe in self.data.recipe_list:
                recipe.get_items_data()
        if self.is_solid:
            self.rect_hitbox.dimension = self.rect.dimension
            self.rect_hitbox.rect = pygame.Rect(self.rect.rect.x + self.hitbox.offset_x, self.rect.rect.y + self.hitbox.offset_y,self.hitbox.hitbox_x, self.hitbox.hitbox_y)
            for player in (game.players.values()):
                if player.rect.colliderect(self.rect_hitbox):
                    player.rect.rect.topleft -= player.direction * player.speed

        if self.attacker != None and self.attacker.rect == None:
            self.attacker = None
        if self.data.summoner != None:
            self.data.summoner.updator(game,self)
        if self.data.thrower != None:
            self.data.thrower.updator(game,self)
        if self.name not in self.path:
            self.path = f'assets/objects/{self.name}'
            self.apply_color(self.color)
        if self.data.plant_data != None and str(self.stage) not in self.path:
            self.path = f'assets/objects/{self.name}{self.stage}'
            self.apply_color(self.color)

        for event in game.event_list:
            if event.type == game.TIMER_EVENT:
                for key in self.timers.keys():
                    self.timers[key] += 0.1
            if self.data.plant_data != None and self.stage < self.data.plant_data.max_stage:
                if self.timers["plant"] >= self.data.plant_data.grow_time:
                    self.stage += 1
                    self.timers["plant"] = 0
        for player in (game.players.values()):
            for event in player.events:
                if self.data.custom_code != None:
                    exec(self.data.custom_code, {}, {"game": game, "self": self, "event": event,"player":player})
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if player.block_selector.rect != None and self.rect.colliderect(player.block_selector.rect):
                        if self.health != None:
                            if self.data.needed_item == None or (f"_{self.data.needed_item.item_name}" in str(player.hand.item_data.tool_type) and player.damage >= self.data.needed_item.min_damage) and player.timers["attack"] >= player.attack_cooldown:
                                if not self.health <= 0:
                                    if "_sword" in str(player.hand.item_data.tool_type):
                                        player.set_action("attack")
                                    if "_shovel" in str(player.hand.item_data.tool_type):
                                        player.set_action("shovel")
                                    if "_axe" in str(player.hand.item_data.tool_type):
                                        player.set_action("axe")
                                    if "_pickaxe" in str(player.hand.item_data.tool_type):
                                        player.set_action("pickaxe")
                                    player.timers["attack"] = 0
                                    self.apply_damage(player.damage,game,player)
                                    break

                        if not self.portal_open:
                            if self.data.portal_data != None:
                                if self.data.portal_data.location != None:
                                    player.rect.rect.x = self.data.portal_data.loaction[0]
                                    player.rect.rect.y = self.data.portal_data.loaction[1]

                                    if not self.data.portal_data.one_way:
                                        self.rect.rect.x = self.data.portal_data.loaction[0]
                                        self.rect.rect.x = self.data.portal_data.loaction[1]
                                        self.portal_open = True
                                else:

                                    player.rect.dimension = self.data.portal_data.dimension
                                    if not self.data.portal_data.one_way:
                                        self.rect.dimension = self.data.portal_data.dimension
                                        self.portal_open = True
                        else:
                            player.rect.rect.x = self.portal_origin_pos[0]
                            player.rect.rect.y = self.portal_origin_pos[1]
                            player.rect.dimension = self.portal_origin_pos[2]
                            self.rect.rect.x = self.portal_origin_pos[0]
                            self.rect.rect.y = self.portal_origin_pos[1]
                            self.rect.dimension = self.portal_origin_pos[2]
                            self.portal_open = False


                elif event.type == pygame.MOUSEBUTTONUP and event.button == 3 and self.rect.colliderect(player.block_selector.rect) and player.can_move:
                    if self.data.dyeable:
                        if player.hand.item_data.color != None:
                            self.apply_color(player.hand.item_data.color)
                            player.hand.count -= 1
                            player.inventory.apply_modifiers()
                    if self.data.store:
                        if player.hand.item_data.item_name != None:
                            self.lootable_list.append(items.lootable(default.get_material(player.hand.item_data.item_name), 1))
                            player.hand.count -= 1
                            player.inventory.apply_modifiers()
                    if self.data.recipe_list != None and player.trade_entity_id == player.craft_object_id == None:
                        player.craft_object_id = self.id
                        player.gui_open = True

                    if self.data.door:

                        if "close" in self.path:
                            self.path = f'assets/objects/{self.name}_open'
                            self.apply_color(self.color)
                            self.is_solid = False
                        else:
                            self.path = f'assets/objects/{self.name}_close'
                            self.apply_color(self.color)
                            self.is_solid = True
        if self.health != None and self.health <= 0:
            if self.data.plant_data != None and self.data.plant_data.max_stage == self.stage:
                try:
                    len(self.data.plant_data.drop)
                    self.lootable_list = self.data.plant_data.drop
                except:
                    self.lootable_list = [self.data.plant_data.drop]

            if self.lootable_list != [None]:
                for i in range(len(self.lootable_list)):
                    try:
                        self.lootable_list[i].loot_data.item_name = self.lootable_list[i].loot_data.item_name
                    except:
                        self.lootable_list[i].loot_data = default.get_material(self.lootable_list[i].loot_data)
                    if random.random() < self.lootable_list[i].chance:
                        default.create_object(game.drops,items.item(game, self.rect.rect.center,self.rect.dimension, self.lootable_list[i].count,self.lootable_list[i].loot_data))
            if self.data.plant_data != None and self.data.plant_data.harvest_to_stage != -1 and self.stage == self.data.plant_data.max_stage:
                self.stage = self.data.plant_data.harvest_to_stage
                try:
                    len(self.data.lootable_list)
                    self.lootable_list = self.data.lootable_list
                except:
                    self.lootable_list = [self.data.lootable_list]
                self.health = self.data.health
                self.path = f'assets/objects/{self.name}{self.stage}'
                self.timers["plant"] = 0
                self.apply_color(self.color)
            else:
                return True

    def apply_color(self,color):
        self.image.replace_path(self.path)
        self.color = default.mix_colors(self.color,color)
        color = (self.color[0],self.color[1],self.color[2],255)
        self.image.color_image(color)
        self.rect = self.image.get_rect(self.rect.dimension,topleft=self.rect.rect.topleft)

    def close(self):
        self.image = None
        self.attacker = None

    def apply_damage(self,damage,game,attacker=None):
        self.health -= damage
        if self.health < 0:
            self.health = 0
        if self.timers.get("damage",None) == None:
            self.timers["damage"] = 0

            self.image.color_image((255,255,255,(self.health/self.data.health)*255))

        if attacker != None and not default.has_one_tag(self,attacker):
            self.attacker = attacker
            for entity in default.double_tag_list(game.entities,self.id,self.tag):
                entity.attacker = attacker
            for Object in default.double_tag_list(game.objects,self.id,self.tag):
                Object.attacker = attacker



    def render(self,players):
        if self.data.plant_data != None and self.stage != self.data.plant_data.max_stage:
            return True
        for player in list(players.values()):
            if self.rect.colliderect(player.render):
                return True
import gif_pygame, pygame, random,items,gui,default,math,objects,projectiles,pickle,textwrap

import modifiers

class Player(pygame.sprite.Sprite):
    def close(self):
        self.health_display.close()
        self.hotbar.close()
        self.block_selector.close()
        self.crafting_gui.remove()
        self.attack_c_text.delete()
        self.inventory_display.close()

        self.image = None

    def to_dict_main_client(self):
        return {
            "rect": self.rect,
            "image_data": self.image.to_dict(),
            "inventory.inventory": self.inventory.inventory,
            "health": self.health,
            "color": self.color,
            "ride_target_id": self.ride_target_id,
            "max_health": self.max_health,
            "default_speed": self.default_speed,
            "attack_cooldown": self.attack_cooldown,
            "timers": self.timers,
            "action": self.action,
            "speed": self.speed,
            "gui_open": self.gui_open,

            "craft_object_id": self.craft_object_id,
            "trade_entity_id": self.trade_entity_id,
            "crafting_gui.x": self.crafting_gui.x,
            "hotbar.selector.x": self.hotbar.selector.x,
            "inventory_display.selector.x": self.inventory_display.selector.x,
            "inventory_display.selector.y": self.inventory_display.selector.y,

            "animation_direction": self.animation_direction,
        }

    def from_dict_main_client(self,player_dict):
        self.rect = player_dict["rect"]
        self.health = player_dict["health"]
        self.color = player_dict["color"]
        self.speed = player_dict["speed"]
        self.ride_target_id = player_dict["ride_target_id"]
        self.default_speed = player_dict["default_speed"]
        self.max_health = player_dict["max_health"]
        self.inventory.inventory = player_dict["inventory.inventory"]
        self.animation_direction = player_dict["animation_direction"]
        self.timers = player_dict["timers"]
        self.attack_cooldown = player_dict["attack_cooldown"]

        self.craft_object_id = player_dict["craft_object_id"]
        self.trade_entity_id = player_dict["trade_entity_id"]
        self.crafting_gui.x = player_dict["crafting_gui.x"]
        self.hotbar.selector.x = player_dict["hotbar.selector.x"]
        self.inventory_display.selector.x = player_dict["inventory_display.selector.x"]
        self.inventory_display.selector.y = player_dict["inventory_display.selector.y"]
        self.action = player_dict["action"]

        self.image.from_dict(player_dict["image_data"])

    def to_dict_client(self):
        return {
            "rect":self.rect.copy(),
            "image_data":self.image.to_dict()
        }

    def from_dict_client(self,player_dict):
        self.rect = player_dict["rect"]
        self.image.from_dict(player_dict["image_data"])

    def set_action(self,action):
        if self.actions[action]["value"] >= self.actions[self.action]["value"]:
            self.action = action

    def __init__(self, pos,dimension, game,main_client=False,player_dict=None):
        super().__init__(game.camera_group)
        self.keys = []
        self.events = []
        self.mouse = pygame.mouse.get_pos()
        self.can_move = True
        self.actions = {
            "idle":{"can_move":True,"value":1,"display_type_left":"topleft","display_type_right":"topleft"},
            "walk":{"can_move":True,"value":1,"display_type_left":"topleft","display_type_right":"topleft"},
            "dead":{"can_move":False,"value":10,"display_type_left":"topleft","display_type_right":"topleft"},
            "roll":{"can_move":False,"value":10,"display_type_left":"topleft","display_type_right":"topleft"},
            "ride":{"can_move":True,"value":10,"display_type_left":"topleft","display_type_right":"topleft"},
            "axe":{"can_move":True,"value":2,"display_type_left":"bottomright","display_type_right":"bottomleft","once":True},
            "attack":{"can_move":True,"value":2,"display_type_left":"bottomright","display_type_right":"bottomleft","once":True},
            "pickaxe":{"can_move":True,"value":2,"display_type_left":"bottomright","display_type_right":"bottomleft","once":True},
            "shovel":{"can_move":True,"value":2,"display_type_left":"bottomright","display_type_right":"bottomleft","once":True},

        }
        self.path = 'assets/entities/player_idle'
        self.image = default.image(self.path)
        self.rect = self.image.get_rect(dimension,bottomleft=pos)
        self.direction = pygame.math.Vector2()
        self.face_direction = "left"
        self.block_selector = gui.block_selector(pos,dimension,game,self)
        self.crafting_gui = gui.crafting_gui(game,self)
        self.timers = {}
        self.speed = 1
        self.health = 10
        self.max_health = 10
        self.damage = 1
        self.id = hash(self)
        self.timers["roll"] = 3
        self.ride_target_id = None
        self.health_display = gui.heart_display(game, self)
        self.hand = None
        self.shield = 0.0
        self.animation_direction = "left"
        self.default_speed = 1
        self.range = 1
        self.attack_cooldown = 0.0
        self.timers["attack"] = 0
        self.timers["roll"] = 0
        self.timers["dead"] = 0
        self.timers["damage"] = 0
        self.timers["eat"] = 0
        self.spawn = (0,0,"world")
        self.roll_c = 0
        self.action = "idle"
        self.temporary_modifiers = []
        self.render = default.rect(pygame.Rect(100,100,1200,800),dimension)
        self.trade_entity_id = None
        self.craft_object_id = None
        self.inventory = items.inventory(5,5,self,True)
        self.hotbar = gui.hotbar(self,game)
        self.color = (255,255,255,255)
        self.attacker = None
        self.gui_open = False
        self.inventory.clear_inventory()
        self.inventory_display = gui.inventory(game,player=self)
        self.attack_c_text = gui.text(self.hotbar.rect.rect.center+pygame.math.Vector2(100,0),dimension,24,"0",game.camera_group,player=self)
        self.inventory.add_item(default.get_material("iron_sword"),1)
        self.inventory.add_item(default.get_material("iron_shovel"),1)
        self.inventory.add_item(default.get_material("iron_pickaxe"),1)
        self.inventory.add_item(default.get_material("wooden_axe"),1)
        self.inventory.add_item(default.get_material("flower_blue"),1)
        self.inventory.add_item(default.get_material("flower_red"),1)
        self.inventory.add_item(default.get_material("wood_cube"),1)
        self.inventory.add_item(default.get_material("cauldron"),1)
        self.inventory.add_item(default.get_material("iron_horse"),1)
        self.inventory.add_item(default.get_material("iron_horse"),1)
        self.inventory.add_item(default.get_material("iron_horse"),1)
        self.inventory.add_item(default.get_material("magic_lantern"),64)
        if player_dict:
            if main_client:
                self.from_dict_main_client(player_dict)
            else:
                self.from_dict(player_dict)

    def from_dict(self,player_dict):
        self.rect = player_dict["rect"]
        self.id = player_dict["id"]
        self.health = player_dict["health"]
        self.inventory.inventory = player_dict["inventory"]

    def to_dict(self):
        return {"id": self.id,"rect":self.rect.copy(),"inventory":self.inventory.inventory,"health":self.health}

    def reset_modifiers(self):
        self.max_health = 10
        self.shield = 0.0
        self.speed = self.default_speed
        self.damage = 1

    def apply_damage(self,damage,game,attacker=None):
        if self.timers.get("damage",None) == None:
            self.timers["damage"] = 0
            self.color = (228,58,58,255)
            self.image.color_image((228,58,58,255))
        if attacker != None and not default.has_one_tag(self,attacker):
            self.attacker = attacker
            for object in list(game.objects.values()):
                if object.tag == self.id:
                    object.attacker = attacker
        self.health -= round(damage*(1.00-self.shield))

    def input(self, game,client=False):
        if self.timers.get("damage",None) != None:
            if self.timers["damage"] > 0.2:
                frame = self.image.image.frame
                frame_time = self.image.image.frame_time
                image = self.image.to_dict()

                image["color"] = (255,255,255,255)
                self.color = image["color"]
                self.image.from_dict(image)
                self.image.image.frame = frame
                self.image.image.frame_time = frame_time
                del self.timers["damage"]
        # animation updator

        if self.action not in self.path:
            self.path = f'assets/entities/player_{self.action}'
            self.image.replace_path(self.path)
            self.image.color_image(self.color)

        self.can_move = self.actions[self.action]["can_move"]
        self.rect.display_type = self.actions[self.action][f"display_type_{self.animation_direction}"]
        if self.image.flip_x != (True if self.animation_direction == "right" else False):

            self.image.flip(True)
        if self.actions[self.action].get("once") != None and self.image.image.frame==len(self.image.image.frames)-1:
            self.action = "idle"
        # render
        self.render.rect.x = self.rect.rect.x - 600
        self.render.rect.y = self.rect.rect.y - 400
        self.render.dimension = self.rect.dimension
        # inventory check
        self.hotbar.updator()
        for modifier in self.temporary_modifiers:
            if modifier.updator(game):
                self.temporary_modifiers.remove(modifier)
                del modifier
                self.inventory.apply_modifiers()

        # death check
        if self.health <= 0:
            if self.inventory.has_item("heart"):
                self.health = 10
                self.inventory.remove_item_amount("heart",1)
            else:
                self.direction.x = 0
                self.direction.y = 0
                self.action = "dead"
            if self.image.image.frame == 12:
                try:
                    game.entities[self.ride_target_id].ridden = False
                    game.entities[self.ride_target_id].rider = None
                except: pass
                self.default_speed = 1
                if self.inventory.has_item("totem"):
                    self.inventory.remove_item_amount("totem", 1)
                else:
                    self.inventory.convert_to_drops(game)
                self.inventory_display.close_inventory()
                self.crafting_gui.close()
                self.ride_target_id = None

                self.rect.rect.x = 0
                self.rect.rect.y = 0
                self.rect.dimension = "world"
                self.health = 10
                self.action = "idle"
                self.inventory.apply_modifiers()
                self.speed = 1

        if self.action == "roll":
            if self.face_direction == "down":
                self.direction.y = 1
            elif self.face_direction == "up":
                self.direction.y = -1
            elif self.face_direction == "left":
                self.direction.x = -1
            elif self.face_direction == "right":
                self.direction.x = 1
            self.block_selector.moving()
            if self.image.image.frame >= 9:
                self.action = "idle"
                self.default_speed -= 3
                self.inventory.apply_modifiers(False)
        # walk
                # inventory update
        if self.gui_open:
            self.can_move = False
            self.block_selector.rect.dimension = "null"
            if game.entities.get(self.trade_entity_id, None) != None:
                if not self.crafting_gui.is_open:
                    self.crafting_gui.open()
                self.crafting_gui.updator(game.entities[self.trade_entity_id].entity_data.trade_list, game)
            if game.objects.get(self.craft_object_id, None) != None:
                if not self.crafting_gui.is_open:
                    self.crafting_gui.open()
                self.crafting_gui.updator(game.objects[self.craft_object_id].data.recipe_list, game)
            self.inventory_display.updator(game, self.inventory)
            self.direction.x = 0
            self.direction.y = 0

        if self.can_move:
            self.direction.x = 0
            self.direction.y = 0
            if "s" in self.keys:
                self.direction.y = 1
                self.set_action("walk")
                self.face_direction = "down"
            elif "w" in self.keys:
                self.direction.y = -1
                self.set_action("walk")
                self.face_direction = "up"
            else:
                self.direction.y = 0
            if "d" in self.keys:
                self.direction.x = 1
                self.set_action("walk")
                self.face_direction = "right"
                self.animation_direction = "right"
            elif "a" in self.keys:
                self.direction.x = -1
                self.set_action("walk")
                self.face_direction = "left"
                self.animation_direction = "left"
            else:
                self.direction.x = 0
            if self.direction == (0,0):
                self.set_action("idle")
            if "left shift" in self.keys and self.action != "ride":
                if self.timers["roll"] >= 3:
                    self.timers["roll"] = 0
                    self.roll_c = 0
                    self.action = "roll"

                    self.default_speed += 3
                    self.inventory.apply_modifiers(False)
            self.block_selector.moving()
        # event listener

        if not self.action == "dead":

            for event in self.events:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.timers["attack"] >= self.attack_cooldown and not self.gui_open:
                    if "_sword" in str(self.hand.item_data.tool_type):
                        self.set_action("attack")
                    if "_axe" in str(self.hand.item_data.tool_type):
                        self.set_action("axe")
                    if "_pickaxe" in str(self.hand.item_data.tool_type):
                        self.set_action("pickaxe")
                    if "_shovel" in str(self.hand.item_data.tool_type):
                        self.set_action("shovel")
                if not client:
                    if self.hand.item_data.event != None:
                        exec(self.hand.item_data.event,{},{"self":self,"game":game,"event":event})

                    if "_sword" in str(self.hand.item_data.tool_type) and self.timers["attack"] >= self.attack_cooldown and event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:
                            for player in list(game.players.values()):
                                if player == self:
                                    continue
                                if self.block_selector.rect != None and player.rect.colliderect(self.block_selector.rect):
                                    player.apply_damage(self.damage, game, self)
                                    self.timers["attack"] = 0
                                    break
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_e and self.action != "roll":
                        self.direction.x = 0
                        self.direction.y = 0
                        self.gui_open = not self.gui_open
                        if self.gui_open:
                            self.inventory_display.open_inventory(game,self,self.inventory.inventory)
                        else:
                            self.inventory_display.close_inventory()
                        if self.trade_entity_id != None:
                            self.trade_entity_id = None
                            self.crafting_gui.close()
                        elif self.craft_object_id != None:
                            self.craft_object_id = None
                            self.crafting_gui.close()

            for event in game.event_list:
                if event.type == game.TIMER_EVENT:
                    for key in self.timers.keys():
                        self.timers[key] += 0.1
                    if self.timers["attack"] < self.attack_cooldown:
                        self.attack_c_text.set_text(default.round_dec(self.attack_cooldown-self.timers["attack"]))
                    else:
                        self.attack_c_text.set_text(0)


    def updator(self,game,client=False):
        self.input(game,client)
        self.rect.rect.topleft += self.direction * self.speed
        if self.health < 0:
            self.health = 0
        if self.health > self.max_health:
            self.health = self.max_health
        self.health_display.updator(self)
        if self.ride_target_id != None and self.action == "ride":
            try:
                game.entities[self.ride_target_id].rect.rect.topleft = (self.rect.rect.x, self.rect.rect.y + 4)
                game.entities[self.ride_target_id].rect.dimension = self.rect.dimension
                if game.entities[self.ride_target_id].direction == "left" and not client:
                    game.entities[self.ride_target_id].rect.rect.x -= 5
            except:
                self.ride_target_id = None
                self.action = "idle"
        self.attack_c_text.rect.rect.center = self.hotbar.rect.rect.center + pygame.math.Vector2(100, 0)
        self.attack_c_text.rect.dimension = self.rect.dimension

        self.hotbar.selector.rect.dimension = self.rect.dimension
        if not self.gui_open:
            self.block_selector.rect.dimension = self.rect.dimension
            if self.direction != [0,0]:
                self.block_selector.rect.rect.topleft += self.speed * self.direction
                self.hotbar.rect.rect.topleft += self.speed * self.direction
                self.attack_c_text.rect.rect.topleft += self.speed * self.direction
                if self.hotbar.selector != None and self.hotbar.selector.rect != None:
                    self.hotbar.selector.rect.rect.topleft += self.speed * self.direction


        for x in range(5):
            self.hotbar.display_array[x].text.rect.dimension = self.rect.dimension
            self.hotbar.display_array[x].rect.rect.topleft += self.speed * self.direction
            self.hotbar.display_array[x].rect.dimension = self.rect.dimension
            self.hotbar.display_array[x].text.rect.rect.topleft += self.speed * self.direction

class breed:
    def __init__(self,item_name,duplicate=False,cooldown=60*2,amount=1):
        self.item_name = item_name
        self.duplicate = duplicate
        self.cooldown = cooldown
        self.amount = amount

class ride:
    def __init__(self,needed_item="saddle",y_offset=0):
        self.needed_item = needed_item
        self.y_offset = y_offset

class tame:
    def __init__(self,needed_item,amount):
        self.needed_item = needed_item
        self.amount = amount
    
    def updator(self,mob,game):
        if mob.mob_type != "L":
            for player in list(game.players.values()):
                for event in player.events:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 3:
                            if player.hand.item_data.item_name == mob.entity_data.tame.needed_item and player.hand.count >= mob.entity_data.tame.amount:
                                player.hand.count -= mob.entity_data.tame.amount
                                player.inventory.apply_modifiers()
                                mob.mob_type = "L"
                                mob.tag = player.id

class entity_data:
    def __init__(self, name, health, lootable_list=[], mob_type="P", attack_damage=0, attack_cooldown=0,
                 despawn_time=-1, knockback=1, vision=600, speed=3, shield=0.0, trade_list=None, summoner=None,
                 suicide=False, thrower=None, breed=None, kill_spawn=None, ride_data=None, ignore_solid=False,tame=None,custom_event=None):
        self.vision = vision
        self.name = name
        self.health = health
        try:
            len(lootable_list)
            self.lootable_list = lootable_list
        except:
            self.lootable_list = [lootable_list]

        self.mob_type = mob_type
        self.attack_damage = attack_damage
        self.attack_cooldown = attack_cooldown
        self.despawn_time = despawn_time
        self.tame = tame
        self.ignore_solid = ignore_solid
        self.trade_list = trade_list
        self.speed = speed
        self.suicide = suicide
        self.shield = shield
        self.knockback = knockback
        self.summoner = summoner
        self.custom_event = custom_event
        if self.custom_event != None:
            self.custom_event = textwrap.dedent(self.custom_event)
        self.thrower = thrower
        self.breed = breed
        self.kill_spawn = kill_spawn
        self.ride_data = ride_data

class kill_spawn:
    def __init__(self,name,amount):
        self.name = name
        self.amount = amount

class entity(pygame.sprite.Sprite):
    def __init__(self, game, entity_data, pos,dimension, tag=None,client=False,entity_dict=None):
        super().__init__(game.camera_group)
        # entity info
        self.entity_data = entity_data #
        self.health = entity_data.health #
        self.timers = {}
        self.direction = "left"
        self.id = hash(self) #
        self.tag = tag #
        self.mob_type = entity_data.mob_type  #
        # P not attack
        # H attack
        # N attack when attacked
        # L loyal
        self.vision_rect = default.rect(pygame.Rect(pos[0],pos[1],self.entity_data.vision,self.entity_data.vision),dimension)
        self.timers["regeneration"] = 0
        self.max_health = self.entity_data.health
        self.damage = self.entity_data.attack_damage
        self.timers["attack"] = 0
        self.timers["despawn"] = 0

        self.attack_cooldown = self.entity_data.attack_cooldown
        self.shield = entity_data.shield #
        self.ridden = False
        self.rider = None
        if self.mob_type == "H":
            self.attacker = random.choice(list(game.players.values()))
        else:
            self.attacker = None

        self.saddled = False #
        if self.entity_data.ride_data != None and self.entity_data.ride_data.needed_item == None:
            self.saddled = True

        self.speed = entity_data.speed #



        self.path = f'assets/entities/{self.entity_data.name}'
        self.image = default.image(self.path)
        self.rect = self.image.get_rect(dimension,topleft=pos) #
        self.flipped = False
        # move
        self.created_path = False
        self.cant_walk = False
        self.timers["walk"] = 40

        self.walking_path = False
        self.path_point = 0
        self.max_path_point = 0

        self.temporary_modifiers = []
        
        self.way_x = 0
        self.way_y = 0
        self.angle = 0
        self.walk_direction = pygame.math.Vector2()
        
        self.random_x = 0 
        self.random_y = 0
        self.random_path = False
        # summoner
        self.timers["summon"] = 0

        self.timers["projectile"] = 0
        # thrower
        # breed
        try:
            self.timers["breed"] = self.entity_data.breed.cooldown
        except:
            self.timers["breed"] = 0
        self.fed = False
        self.breed_target = None
        if entity_dict:
            if client:
                self.from_dict_client(entity_dict)
            else:
                self.from_dict(entity_dict)

    def reset_modifiers(self):
        self.max_health = self.entity_data.health
        self.damage = self.entity_data.attack_damage
        self.attack_cooldown = self.entity_data.attack_cooldown
        self.shield = self.entity_data.shield
        self.speed = self.entity_data.speed

    def apply_modifiers(self):
        self.reset_modifiers()
        for temp_modifier in self.temporary_modifiers:
            modifiers.modifier.set([temp_modifier.modifier],self,False,False)

    def to_dict_client(self):
        return {
            "rect":self.rect.copy(),
            "entity_data":self.entity_data,
            "image_data":self.image.to_dict(),
        }

    def from_dict_client(self,entity_dict):
        self.rect = entity_dict["rect"]
        self.entity_data = entity_dict["entity_data"]
        self.image.from_dict(entity_dict["image_data"])

    def to_dict(self):
        return {
            'id': self.id,
            'tag': self.tag,
            'health': self.health,
            'vision_rect': self.vision_rect,
           'mob_type': self.mob_type,
           'timers': self.timers,
           'rect': self.rect,
           'path': self.path,
           'saddled': self.saddled,
            "entity_data":self.entity_data
        }

    def from_dict(self,entity_dict):
        self.id = entity_dict["id"]
        self.timers = entity_dict["timers"]
        self.tag = entity_dict["tag"]
        self.health = entity_dict["health"]
        self.vision_rect = entity_dict["vision_rect"]
        self.mob_type = entity_dict["mob_type"]
        self.rect = entity_dict["rect"]
        self.path = entity_dict["path"]
        self.image.replace_path(self.path)
        self.saddled = entity_dict["saddled"]
        self.entity_data = entity_dict["entity_data"]
        self.reset_modifiers()

    def damageTint(self):
        if self.timers.get("damage",None) != None:
            if self.timers["damage"] > 0.2:
                image = self.image.to_dict()
                image["color"] = (255,255,255,255)
                self.image.from_dict(image)
                del self.timers["damage"]
    def modifiersUpdate(self,game):
        for modifier in self.temporary_modifiers:
            if modifier.updator(game):
                self.temporary_modifiers.remove(modifier)
                del modifier
                self.apply_modifiers()
    def breedTargetFinder(self,game):
        if self.entity_data.breed != None:
            if self.fed and self.breed_target == None:
                if self.entity_data.breed.duplicate:
                    for i in range(self.entity_data.breed.amount):
                        default.create_object(game.entities,entity(game.camera_group, default.get_entity(self.entity_data.name), self.rect.rect.center,self.rect.dimension))
                    self.fed = False
                else:
                    closest = 10000000000000000
                    for Entity in list(game.entities.values()):
                        if Entity != self:
                            if Entity.fed and Entity.entity_data.name == self.entity_data.name:
                                if closest > math.sqrt(2**(self.rect.rect.x-Entity.rect.rect.x) + (self.rect.rect.y-Entity.rect.rect.y) ** 2):
                                    closest = math.sqrt(2**(self.rect.rect.x-Entity.rect.rect.x) + (self.rect.rect.y-Entity.rect.rect.y) ** 2)
                                    self.breed_target = Entity

    def deathCheck(self,game):
        if self.health <= 0:
            if self.entity_data.kill_spawn != None:
                for i in range(self.entity_data.kill_spawn.amount):
                    id = default.create_object(game.entities,entity(game, default.get_entity(self.entity_data.kill_spawn.name),(self.rect.rect.x + random.randint(-50, 50), self.rect.rect.y + random.randint(-50, 50)),self.rect.dimension))
                    game.entities[id].attacker = self.attacker
            if self.entity_data.lootable_list != [] and self.entity_data.lootable_list != [None]:
                for i in range(len(self.entity_data.lootable_list)):
                    if random.random() < self.entity_data.lootable_list[i].chance:
                        default.create_object(game.drops,items.item(game, self.rect.rect.center,self.rect.dimension, self.entity_data.lootable_list[i].count,self.entity_data.lootable_list[i].loot_data))
            if self.ridden:
                self.stop_riding()
            # soul drop check
            if isinstance(self.attacker,Player) and "_soul" in str(self.attacker.hand.item_data.tool_type):
                default.create_object(game.drops,items.item(game, self.rect.rect.center,self.rect.dimension, 1, default.get_material("soul")))
            return True
        return False

    def attackerUpdate(self,game):
        try:
            if self.attacker != None:
                if self.attacker.rect == None:
                    if self.mob_type == "H":
                        self.attacker = random.choice(list(game.players.values()))
                    else:
                        self.attacker = None
        except:
            if self.mob_type == "H":
                self.attacker = random.choice(list(game.players.values()))
            else:
                self.attacker = None

    def solidCheck(self,game):
        if not self.entity_data.ignore_solid:
            for block in list(game.objects.values()):
                if block.is_solid and self.rect.colliderect(block.rect_hitbox):
                    self.rect.rect.topleft -= self.walk_direction
                    self.created_path = False
                    self.path_point = self.max_path_point

    def visionRectUpdate(self):
        self.vision_rect.rect.center = self.rect.rect.center
        self.vision_rect.dimension = self.rect.dimension

    def attack(self,game):
        # attack check
        if self.rect.colliderect(self.attacker.rect):
            if self.timers["attack"] >= self.attack_cooldown:
                self.timers["attack"] = 0
                self.attacker.apply_damage(self.entity_data.attack_damage, game, self)
                default.post_event(game.event_list, game.ATTACK_EVENT, attacker=self, attacked=self.attacker)
                if self.entity_data.suicide:
                    return True

    def updator(self, game):
        self.damageTint()
        self.modifiersUpdate(game)
        self.breedTargetFinder(game)

        # death check
        if self.deathCheck(game):
            return True
        self.attackerUpdate(game)
        self.solidCheck(game)
        self.visionRectUpdate()

        # tame
        if self.entity_data.tame != None:
            self.entity_data.tame.updator(self,game)
        if self.attacker != None and self.attacker.rect != None:
            # thrower
            if self.entity_data.thrower != None and self.vision_rect.colliderect(self.attacker.rect):
                self.entity_data.thrower.updator(game, self)
            # summoner
            if self.entity_data.summoner != None:
                self.entity_data.summoner.updator(game,self)
            if self.attack(game):
                return True
        for event in game.event_list:
            for modifier in self.temporary_modifiers:
                if modifier.updator(game):
                    self.temporary_modifiers.remove(modifier)
                    del modifier
                    self.apply_modifiers()
            if event.type == game.TIMER_EVENT:
                for key in self.timers.keys():
                    self.timers[key] += 0.1

                if self.entity_data.despawn_time != -1 and self.timers["despawn"] >= self.entity_data.despawn_time:
                    return True
                if self.timers["regeneration"] == 10:
                    if self.health < self.max_health:
                        self.health += 1
        if self.entity_data.custom_event:
            exec(self.entity_data.custom_event, {}, {"game": game, "self": self})
        for player in list(game.players.values()):
            for event in player.events:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        # attack check
                        if player.block_selector.rect != None and self.rect.colliderect(player.block_selector.rect):
                            if self.saddled == True and self.entity_data.ride_data.needed_item != None:
                                default.create_object(game.drops,items.item(game, self.rect.rect.center,self.rect.dimension, 1,default.get_material(self.entity_data.ride_data.needed_item)))
                                self.saddled = False
                            if "_sword" in str(player.hand.item_data.tool_type) and player.timers["attack"] >= player.attack_cooldown:
                                player.timers["attack"] = 0
                                player.set_action("attack")
                                self.apply_damage(player.damage,game,player)
                    elif event.button == 3 and player.block_selector.rect != None and self.rect.colliderect(player.block_selector.rect) and player.can_move:
                        # trade menu check
                        if self.entity_data.trade_list != None and player.trade_entity_id == player.craft_object_id == None:
                            player.trade_entity_id = self.id
                            player.gui_open = True
                        # feed check
                        if self.entity_data.breed != None and player.hand.item_data.item_name == self.entity_data.breed.item_name and not self.fed and self.timers["breed"] > self.entity_data.breed.cooldown:
                            self.fed = True
                            player.hand.count -= 1
                            player.inventory.apply_modifiers()
                        if self.entity_data.ride_data:
                            if self.saddled:
                                if not self.ridden:
                                    self.ridden = True
                                    self.rider = player
                                    self.rider.ride_target_id = self.id
                                    self.rider.speed += self.speed
                                    self.rider.default_speed += self.speed
                            elif player.hand.item_data.item_name == self.entity_data.ride_data.needed_item:
                                self.saddled = True
                                player.hand.count -= 1
                                player.inventory.apply_modifiers()

        if self.ridden:
            self.rider.action = "ride"
            if "d" in self.rider.keys:
                self.direction = "right"
                if not self.image.flip_x:
                    self.image.flip(True)
            elif "a" in self.rider.keys:
                self.direction = "left"
                if self.image.flip_x:
                    self.image.flip(True)

            if "space" in self.rider.keys or self.rider.ride_target_id != self.id:
                self.stop_riding()

        elif not self.breed_target != None:
            holding_item = False
            player_holder = None
            for player in list(game.players.values()):
                if self.entity_data.breed != None and player.hand != None and player.hand.item_data.item_name == self.entity_data.breed.item_name:
                    holding_item = True
                    player_holder = player
                    break
            if holding_item:
                self.walk_location(game,player_holder.rect.rect.x,player_holder.rect.rect.y,player_holder.rect.dimension)
            elif self.attacker != None and self.attacker.rect != None and self.vision_rect.colliderect(self.attacker.rect):
                self.walk_location(game,self.attacker.rect.rect.centerx,self.attacker.rect.rect.centery,self.attacker.rect.dimension)
            elif self.mob_type == "L":
                player_loyal = game.players.get(self.tag)
                if player_loyal != None:
                    if player_loyal.attacker != None and player_loyal.attacker.rect != None:
                        self.attacker = player_loyal.attacker
                    else:
                        self.walk_location(game,player_loyal.rect.rect.centerx,player_loyal.rect.rect.centery,player_loyal.rect.dimension)
            else:
                self.random_walking(game)
            # breed system
        else:
            try:
                self.walk_location(game, self.breed_target.rect.rect.x, self.breed_target.rect.rect.y,self.breed_target.rect.dimension)
                if self.rect.colliderect(self.breed_target.rect):
                    self.fed = False
                    self.breed_target.fed = False
                    self.timers["breed"] = 0
                    self.breed_target.timers["breed"] = 0
                    self.breed_target.breed_target = None
                    self.breed_target = None
                    for i in range(self.entity_data.breed.amount):
                        default.create_object(game.entities,entity(game.camera_group, default.get_entity(self.entity_data.name), self.rect.rect.center,self.rect.dimension))
            except:
                self.breed_target = None

    def walking_solid(self, game, x,y,dimension):
        if not self.created_path and not self.rect.collidepoint(x,y,dimension) and not self.cant_walk:
            if self.vision_rect.collidepoint(x,y,dimension):
                if not (self.path_point < self.max_path_point):
                    self.walking_path = default.calculate_path(self.rect.rect.topleft, (x,y), game.objects, self.rect.rect.width, self.rect.rect.height, 200,self.speed*2)
                    if not self.walking_path:
                        self.cant_walk = True
                    else:
                        self.path_point = 0
                        self.max_path_point = len(self.walking_path) - 1
                        self.angle = (math.degrees(math.atan2(-(self.rect.rect.y - self.walking_path[self.path_point][1]),self.rect.rect.x - self.walking_path[self.path_point][0])) + 180) % 360


                else:
                    self.created_path = True
        elif not self.rect.collidepoint(x,y,dimension) and not self.cant_walk:
            radians = abs(math.radians(self.angle))
            self.walk_direction.x = self.speed * math.cos(radians)
            self.walk_direction.y = - (self.speed * math.sin(radians))
            self.rect.rect.topleft += self.walk_direction

            if 90 < self.angle < 270:
                if self.image.flip_x:
                    self.image.flip(True)
            elif not self.image.flip_x:
                self.image.flip(True)

            if self.path_point < self.max_path_point and default.almost(self.rect.rect.topleft,self.walking_path[self.path_point],self.speed*0.5):
                if not self.walking_path:
                    self.cant_walk = True
                else:
                    self.path_point += 1
                    self.angle = (math.degrees(math.atan2(-(self.rect.rect.y-self.walking_path[self.path_point][1]),self.rect.rect.x-self.walking_path[self.path_point][0]))+180) % 360


            else:
                self.timers["walk"] = 0
                self.created_path = False

    def walk_location(self,game,x,y,dimension):
        if not self.cant_walk:
            collide = False
            if not self.entity_data.ignore_solid:

                for object in list(game.objects.values()):
                    if object.is_solid and self.vision_rect.colliderect(object.rect):
                        collide = True
            if collide:
                self.walking_solid(game, x, y,dimension)
            else:
                self.walking_ignore_solid(x,y,dimension)
        elif self.timers["walk"] > 20:
            self.timers["walk"] = 0
            self.cant_walk = False

    def walking_ignore_solid(self, x, y,dimension):
        if not self.created_path:
            self.angle = (math.degrees(math.atan2(-(self.rect.rect.y-y),self.rect.rect.x-x))+180) % 360
            self.created_path = True
        else:
            if self.vision_rect.collidepoint(x, y,dimension):
                radians = abs(math.radians(self.angle))
                self.walk_direction.x = self.speed * math.cos(radians)
                self.walk_direction.y = -(self.speed * math.sin(radians))
                self.rect.rect.topleft += self.walk_direction
                if 90 < self.angle < 270:
                    if self.image.flip_x:
                        self.image.flip(True)
                elif not self.image.flip_x:
                    self.image.flip(True)
                del radians
            location_check = default.rect(pygame.Rect(x,y,10,10),dimension)
            
            if not location_check.collidepoint(self.way_x * self.walk_direction.x,self.way_y * self.walk_direction.y,dimension) or default.is_point_on_line(self.rect.rect.x,self.rect.rect.y,self.angle,x,y):
                self.created_path = False
                self.timers["walk"] = 0
            del location_check

    def random_walking(self,game):
        if not self.random_path:
            if self.timers["walk"] > 20:
                self.random_x = random.randint(self.vision_rect.rect.left+(self.vision_rect.rect.width//4),self.vision_rect.rect.right-(self.vision_rect.rect.width//4))
                self.random_y = random.randint(self.vision_rect.rect.top+(self.vision_rect.rect.height//4),self.vision_rect.rect.bottom-(self.vision_rect.rect.height//4))
                self.random_path = True
        else:
            self.walk_location(game,self.random_x,self.random_y,self.rect.dimension)
            if self.random_x - 10 < self.rect.rect.x < self.random_x + 10 and self.random_y - 10 < self.rect.rect.y < self.random_y + 10:
                self.random_path = False

    def render(self,players):
        for player in list(players.values()):
            if self.rect.colliderect(player.render):
                return True

    def apply_damage(self,damage,game,attacker=None):
        if self.timers.get("damage",None) == None:
            self.timers["damage"] = 0
            self.image.color_image((228,58,58,255))
        self.health -= round(damage*(1.0-self.shield))
        if attacker != None and not default.has_one_tag(self,attacker):
            if self.mob_type != "P":
                self.attacker = attacker
                for block in default.double_tag_list(game.objects,self.tag,self.id):
                    block.attacker = attacker
                for Entity in default.double_tag_list(game.entities,self.tag,self.id):
                    Entity.attacker = attacker
        if self.direction == "left":
            self.rect.rect.x += self.entity_data.knockback + self.speed
            self.direction = "right"
        elif self.direction == "right":
            self.rect.rect.x -= self.entity_data.knockback + self.speed
            self.direction = "left"
        if self.direction == "up":
            self.rect.rect.y += self.entity_data.knockback + self.speed
            self.direction = "down"
        elif self.direction == "down":
            self.rect.rect.y -= self.entity_data.knockback + self.speed
            self.direction = "up"
        self.timers["walk"] = 21

    def stop_riding(self):
        self.rider.action = "idle"
        self.rider.default_speed -= self.speed
        self.rider.ride_target_id = None
        self.rider.reset_modifiers()
        self.rider = None
        self.ridden = False

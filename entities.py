import gif_pygame, pygame, random,items,gui,default,math,objects,projectiles,pickle

import modifiers


class Player(pygame.sprite.Sprite):
    def close(self):
        self.health_display.close()
        self.hotbar.close()
        self.block_selector.close()
        self.crafting_gui.remove()
        self.inventory_display.close()

        self.image = None

    def __init__(self, pos,dimension, game):
        super().__init__(game.camera_group)
        self.keys = ()
        self.events = []
        self.mouse = pygame.mouse.get_pos()
        self.path = 'assets/entities/player_left_idle'
        self.image = default.image(self.path)
        self.rect = self.image.get_rect(pos,dimension)
        self.direction = pygame.math.Vector2()
        self.face_direction = "left"
        self.block_selector = gui.block_selector(pos,dimension,game,self)
        self.crafting_gui = gui.crafting_gui(game,self)

        self.speed = 4
        self.health = 10
        self.max_health = 10
        self.damage = 1
        self.id = hash(self)
        self.roll_cooldown = 3
        self.ride_target = None
        self.health_display = gui.heart_display(game, self)
        self.hand = None
        self.shield = 0.0
        self.animation_direction = "left"
        self.default_speed = 4
        self.range = 1
        self.attack_cooldown = 0.0
        self.attack_c = 0.0
        self.roll_c = 0
        self.action = "idle"
        self.temporary_modifiers = []
        self.render = default.rect(pygame.Rect(100,100,1200,800),dimension)

        self.inventory = items.inventory(5,5,self,True)
        self.hotbar = gui.hotbar(self,game)

        self.attacker = None
        self.gui_open = False
        self.inventory.clear_inventory()
        self.inventory.add_item(default.get_material('health_potion'), 16)
        self.inventory.add_item(default.get_material('stick1'), 1)
        self.inventory.add_item(default.get_material('wood_cube'), 32)
        self.inventory.add_item(default.get_material('phoenix_feather'), 1)
        self.inventory.add_item(default.get_material('iron_horse'), 1)
        self.inventory.add_item(default.get_material('mega_shield'), 1)
        self.inventory.add_item(default.get_material('door'), 1)
        self.inventory_display = gui.inventory(game,player=self)
        self.attack_c_text = gui.text(self.hotbar.rect.rect.center+pygame.math.Vector2(100,0),dimension,24,self.attack_c,game.camera_group,player=self)

    def from_dict(self,path,id):
        with open(f"{path}/players/{id}.pkl","rb") as f:
            player_dict = pickle.load(f)
            self.rect = player_dict["rect"]
            self.id = id
            self.health = player_dict["health"]
            self.inventory.inventory = player_dict["inventory"]

    def to_dict(self):
        return {"id": self.id,"rect":self.rect,"inventory":self.inventory.inventory,"health":self.health}

    def reset_modifiers(self):
        self.max_health = 10
        self.shield = 0.0
        self.speed = self.default_speed
        self.damage = 1

    def apply_damage(self,damage,game,attacker=None):
        if attacker != None and not default.has_one_tag(self,attacker):
            self.attacker = attacker
            for object in game.objects:
                if object.tag == self.id:
                    object.attacker = attacker
        self.health -= round(damage*(1.00-self.shield))

    def input(self, game):

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
                    self.ride_target.ridden = False
                    self.ride_target.rider = None
                except: pass
                self.default_speed = 4
                if self.inventory.has_item("totem"):
                    self.inventory.remove_item_amount("totem", 1)
                else:
                    self.inventory.convert_to_drops(game)
                self.inventory_display.close_inventory()
                self.crafting_gui.close()
                self.ride_target = None

                self.rect.rect.x = 3001
                self.rect.rect.y = 3008
                self.rect.dimension = "world"
                self.health = 10
                self.action = "idle"
                self.inventory.apply_modifiers()
                self.speed = 4



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
        elif not self.gui_open and self.action != "dead":
            self.direction.x = 0
            self.direction.y = 0
            if "s" in self.keys:
                self.direction.y = 1
                if self.action != "ride":
                    self.action = "walk"
                self.face_direction = "down"
            elif "w" in self.keys:
                self.direction.y = -1
                if self.action != "ride":
                    self.action = "walk"
                self.face_direction = "up"
            else:
                self.direction.y = 0
            if "d" in self.keys:
                self.direction.x = 1
                if self.action != "ride":
                    self.action = "walk"
                self.face_direction = "right"
                self.animation_direction = "right"
            elif "a" in self.keys:
                self.direction.x = -1
                if self.action != "ride":
                    self.action = "walk"
                self.face_direction = "left"
                self.animation_direction = "left"
            else:
                self.direction.x = 0
            if self.direction == (0,0):
                if self.action == "walk":
                    self.action = "idle"
            if "left shift" in self.keys and self.action != "ride":
                if self.roll_cooldown >= 3:
                    self.roll_cooldown = 0
                    self.roll_c = 0
                    self.action = "roll"

                    self.default_speed += 3
                    self.inventory.apply_modifiers(False)
            self.block_selector.moving()
        # inventory update
        elif self.gui_open:
            self.block_selector.rect.rect.y = 1204567890
            self.block_selector.rect.rect.x = 1204567890
            self.inventory_display.updator(game,self.inventory)
            self.direction.x = 0
            self.direction.y = 0
        # animation updator
        if self.action not in self.path or self.animation_direction not in self.path:

            self.path = f'assets/entities/player_{self.animation_direction}_{self.action}'
            self.image.replace_path(self.path)

        # event listener

        if not self.action == "dead":

            for event in self.events:
                if self.hand.item_data.event != None:
                    exec(self.hand.item_data.event,{},{"self":self,"game":game,"event":event})

                if "_sword" in str(self.hand.item_data.tool_type) and self.attack_c == self.attack_cooldown and event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        for player in game.players:
                            if player == self:
                                continue
                            if self.block_selector.rect != None and player.rect.colliderect(self.block_selector.rect):
                                player.apply_damage(self.damage, game, self)
                                self.attack_c = 0
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

            for event in game.event_list:
                if event.type == pygame.USEREVENT:
                    if self.roll_cooldown < 3:
                        self.roll_cooldown += 1
                    if self.roll_c < 1:
                        self.roll_c += 1
                if event.type == game.TIMER_EVENT:
                    if self.attack_cooldown != self.attack_c:
                        self.attack_cooldown = default.round_dec(self.attack_cooldown)
                        self.attack_c += 0.1
                        self.attack_c_text.set_text(default.round_dec(self.attack_cooldown-self.attack_c))


    def updator(self,game):
        self.input(game)

        self.rect.rect.topleft += self.direction * self.speed



        if self.health < 0:
            self.health = 0
        if self.health > self.max_health:
            self.health = self.max_health
        self.health_display.updator(self)
        if self.ride_target != None and self.action == "ride":
            try:
                self.ride_target.rect.rect.topleft = (self.rect.rect.x, self.rect.rect.y + 4)
                self.ride_target.rect.dimension = self.rect.dimension
                if self.ride_target.direction == "left":
                    self.ride_target.rect.rect.x -= 5
            except:
                self.ride_target = None
                self.action = "idle"
        self.attack_c_text.rect.rect.center = self.hotbar.rect.rect.center + pygame.math.Vector2(100, 0)
        self.attack_c_text.rect.dimension = self.rect.dimension
        self.block_selector.rect.dimension = self.rect.dimension
        self.hotbar.selector.rect.dimension = self.rect.dimension
        if not self.gui_open and self.direction != [0,0]:
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
            for player in game.players:
                for event in player.events:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 3:
                            if player.hand.item_data.item_name == mob.entity_data.tame.needed_item and player.hand.count >= mob.entity_data.tame.amount:
                                player.hand.count -= mob.entity_data.tame.amount
                                mob.mob_type = "L"
                                mob.tag = player.id

class entity_data:
    def __init__(self, name, health, lootable_list=[], mob_type="P", attack_damage=0, attack_cooldown=0,
                 despawn_time=-1, knockback=1, vision=600, speed=3, shield=0.0, trade_list=None, summoner=None,
                 suicide=False, thrower=None, breed=None, kill_spawn=None, ride_data=None, ignore_solid=False,tame=None):
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
        self.thrower = thrower
        self.breed = breed
        self.kill_spawn = kill_spawn
        self.ride_data = ride_data

class kill_spawn:
    def __init__(self,name,amount):
        self.name = name
        self.amount = amount

class entity(pygame.sprite.Sprite):
    def __init__(self, game, entity_data, pos,dimension, tag=None):
        super().__init__(game.camera_group)
        # entity info
        self.entity_data = entity_data #
        self.health = entity_data.health #
        self.direction = "left"
        self.id = hash(self) #
        self.tag = tag #
        self.mob_type = entity_data.mob_type  #
        # P not attack
        # H attack
        # N attack when attacked
        # L loyal
        self.vision_rect = default.rect(pygame.Rect(pos[0],pos[1],self.entity_data.vision,self.entity_data.vision),dimension)

        self.regeneration_time = 0


        self.despawn_time = entity_data.despawn_time #
        self.max_health = self.entity_data.health
        self.damage = self.entity_data.attack_damage
        self.attack_c = 0
        self.attack_cooldown = self.entity_data.attack_cooldown
        self.shield = entity_data.shield #
        self.ridden = False
        self.rider = None
        if self.mob_type == "H":
            self.attacker = random.choice(game.players)
        else:
            self.attacker = None

        self.saddled = False #
        if self.entity_data.ride_data != None and self.entity_data.ride_data.needed_item == None:
            self.saddled = True

        self.speed = entity_data.speed #

        self.trade_menu_user = None
        self.crafting_menu_open = False
        spawn_kill = False
        if self.mob_type == "B":
            for e in game.entities:
                if e.mob_type == "B" and e.entity_data.name == self.entity_data.name:
                    self.despawn_time = 1
                    spawn_kill = True

            # sprite
        if spawn_kill:
            self.path = f'assets/entities/None'
        else:
            self.path = f'assets/entities/{self.entity_data.name}'
        self.image = default.image(self.path)
        self.rect = self.image.get_rect(pos,dimension) #
        self.flipped = False
        # move
        self.created_path = False
        self.cant_walk = False
        self.cooldown = 40
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
        self.summon_c = 0
        # thrower
        self.projectile_c = 0
        # breed
        try:
            self.breed_cooldown = self.entity_data.breed.cooldown
        except:
            self.breed_cooldown = 0
        self.fed = False
        self.breed_target = None

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

    def to_dict(self):
        return {
            'id': self.id,
            'tag': self.tag,
            'health': self.health,
            'vision_rect': self.vision_rect,
           'mob_type': self.mob_type,
            'despawn_time': self.despawn_time,
            'cooldown': self.cooldown,
           'rect': self.rect,
           'path': self.path,
           'saddled': self.saddled,
            "entity_data":self.entity_data
        }

    def from_dict(self,entity_dict):
        self.id = entity_dict["id"]
        self.tag = entity_dict["tag"]
        self.health = entity_dict["health"]
        self.vision_rect = entity_dict["vision_rect"]
        self.mob_type = entity_dict["mob_type"]
        self.despawn_time = entity_dict["despawn_time"]
        self.rect = entity_dict["rect"]
        self.path = entity_dict["path"]
        self.image.replace_path(self.path)
        self.saddled = entity_dict["saddled"]
        self.cooldown = entity_dict["cooldown"]
        self.entity_data = entity_dict["entity_data"]
        self.reset_modifiers()

    def updator(self, game):
        for modifier in self.temporary_modifiers:
            if modifier.updator(game):
                self.temporary_modifiers.remove(modifier)
                del modifier
                self.apply_modifiers()
        # breed target finder
        if self.entity_data.breed != None:
            if self.fed and self.breed_target == None:
                if self.entity_data.breed.duplicate:
                    for i in range(self.entity_data.breed.amount):
                        game.entities.append(
                            entity(game.camera_group, default.get_entity(self.entity_data.name), self.rect.rect.center,self.rect.dimension))
                    self.fed = False
                else:
                    closest = 10000000000000000
                    for Entity in game.entities:
                        if Entity != self:
                            if Entity.fed and Entity.entity_data.name == self.entity_data.name:
                                if closest > math.sqrt(2**(self.rect.rect.x-Entity.rect.rect.x) + (self.rect.rect.y-Entity.rect.rect.y) ** 2):
                                    closest = math.sqrt(2**(self.rect.rect.x-Entity.rect.rect.x) + (self.rect.rect.y-Entity.rect.rect.y) ** 2)
                                    self.breed_target = Entity
        # death check
        if self.health <= 0:
            if self.entity_data.kill_spawn != None:
                for i in range(self.entity_data.kill_spawn.amount):
                    game.entities.append(entity(game, default.get_entity(self.entity_data.kill_spawn.name),(self.rect.rect.x + random.randint(-50, 50), self.rect.rect.y + random.randint(-50, 50)),self.rect.dimension))
                    game.entities[-1].attacker = self.attacker
            if self.entity_data.lootable_list != [] and self.entity_data.lootable_list != [None]:
                for i in range(len(self.entity_data.lootable_list)):
                    if random.random() < self.entity_data.lootable_list[i].chance:
                        game.drops.append(
                            items.item(game, self.rect.rect.center,self.rect.dimension, self.entity_data.lootable_list[i].count,
                                        self.entity_data.lootable_list[i].loot_data))
            if self.ridden:
                self.stop_riding()   
            # soul drop check
            if isinstance(self.attacker,Player) and "_soul" in str(self.attacker.hand.item_data.tool_type):
                game.drops.append(items.item(game, self.rect.rect.center,self.rect.dimension, 1, default.get_material("soul")))
            return True
        try:
            if self.attacker != None:
                if self.attacker.rect == None:
                    if self.mob_type == "H":
                        self.attacker = random.choice(game.players)
                    else:
                        self.attacker = None
        except:
            if self.mob_type == "H":
                self.attacker = random.choice(game.players)
            else:
                self.attacker = None
        if not self.entity_data.ignore_solid:
            for block in game.objects:
                if block.is_solid and self.rect.colliderect(block.rect_hitbox):
                    self.rect.rect.topleft -= self.walk_direction
                    self.created_path = False
                    self.path_point = self.max_path_point
                    if "border" in block.name:
                        self.rect.rect.x = random.randint(10, 178) * 26
                        self.rect.rect.y = random.randint(10, 151) * 20
        # vision rect updator
        self.vision_rect.rect.center = self.rect.rect.center
        self.vision_rect.dimension = self.rect.dimension
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
            # attack check
            if self.rect.colliderect(self.attacker.rect):
                if self.attack_c >= self.attack_cooldown:
                    self.attack_c = 0
                    self.attacker.apply_damage(self.entity_data.attack_damage,game,self)
                    if self.entity_data.suicide:
                        return True
        for event in game.event_list:
            for modifier in self.temporary_modifiers:
                if modifier.updator(game):
                    self.temporary_modifiers.remove(modifier)
                    del modifier
                    self.apply_modifiers()
            if event.type == pygame.USEREVENT:
                # cooldowns
                self.cooldown += 1
                if self.entity_data.breed != None and self.breed_cooldown <= self.entity_data.breed.cooldown:
                    self.breed_cooldown += 1
                self.attack_c += 1
                if self.health < self.entity_data.health:
                    self.regeneration_time += 1
                if self.despawn_time != -1:
                    self.despawn_time -= 1
                    # despawn time check
                    if self.despawn_time == 0:
                        return True
                if self.regeneration_time == 10:
                    self.health += 1
                    self.regeneration_time = 0
        for player in game.players:
            for event in player.events:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        # attack check
                        if player.block_selector.rect != None and self.rect.colliderect(player.block_selector.rect):
                            if self.saddled == True and self.entity_data.ride_data.needed_item != None:
                                game.drops.append(items.item(game, self.rect.rect.center,self.rect.dimension, 1,default.get_material(self.entity_data.ride_data.needed_item)))
                                self.saddled = False
                            if "_sword" in str(player.hand.item_data.tool_type) and player.attack_c == player.attack_c:
                                player.attack_c = 0
                                self.apply_damage(player.damage,game,player)
                    elif event.button == 3 and player.block_selector.rect != None and self.rect.colliderect(player.block_selector.rect):
                        # trade menu check
                        if self.entity_data.trade_list != None:
                            self.crafting_menu_open = True
                            self.trade_menu_user = player
                            self.trade_menu_user.inventory_display.open_inventory(game,player,player.inventory.inventory)
                            self.trade_menu_user.crafting_gui.open()
                        # feed check
                        if self.entity_data.breed != None and player.hand.item_data.item_name == self.entity_data.breed.item_name and not self.fed and self.breed_cooldown > self.entity_data.breed.cooldown:
                            self.fed = True
                            player.hand.count -= 1
                        if self.entity_data.ride_data:
                            if self.saddled:
                                if not self.ridden:
                                    self.ridden = True
                                    self.rider = player
                                    self.rider.ride_target = self
                                    self.rider.speed += self.speed
                                    self.rider.default_speed += self.speed
                            elif player.hand.item_data.item_name == self.entity_data.ride_data.needed_item:
                                self.saddled = True
                                player.hand.count -= 1
        if self.ridden:
            self.rider.action = "ride"
            if "d" in self.rider.keys:
                self.direction = "right"
                if not self.flipped:
                    self.image.flip( True)
                    self.flipped = True
            elif "a" in self.rider.keys:
                self.direction = "left"
                if self.flipped:
                    self.image.flip(True)
                    self.flipped = False
            if "space" in self.rider.keys or self.rider.ride_target != self:
                self.stop_riding()

        elif not self.breed_target != None:
            for player in game.players:
                # random walking/waking to player
                if self.entity_data.breed != None and player.hand != None and player.hand.item_data.item_name == self.entity_data.breed.item_name:
                    self.walk_location(game,player.rect.rect.x,player.rect.rect.y,player.rect.dimension)
                elif self.attacker != None and self.attacker.rect != None and self.vision_rect.colliderect(self.attacker.rect):
                    self.walk_location(game,self.attacker.rect.rect.centerx,self.attacker.rect.rect.centery,self.attacker.rect.dimension)
                elif self.mob_type == "L":
                    player_loyal = default.get_player(game.players,self.tag)
                    if player_loyal != None and player_loyal.attacker != None and player_loyal.attacker.rect != None:
                        self.attacker = player_loyal.attacker
                    else:
                        self.walk_location(game,player_loyal.rect.rect.x,player_loyal.rect.rect.y,player_loyal.rect.dimension)
                else:
                    self.random_walking(game)
            # breed system
        else:
            try:
                self.walk_location(game, self.breed_target.rect.rect.x, self.breed_target.rect.rect.y,self.breed_target.rect.dimension)
                if self.rect.colliderect(self.breed_target.rect):
                    self.fed = False
                    self.breed_target.fed = False
                    self.breed_cooldown = 0
                    self.breed_target.breed_cooldown = 0
                    self.breed_target.breed_target = None
                    self.breed_target = None
                    for i in range(self.entity_data.breed.amount):
                        game.entities.append(
                            entity(game.camera_group, default.get_entity(self.entity_data.name), self.rect.rect.center,self.rect.dimension))
            except:
                self.breed_target = None
        # trade menu
        
        if self.crafting_menu_open:
            if not self.trade_menu_user.crafting_gui.is_open:
                self.crafting_menu_open = False
                self.trade_menu_user = None
            else:
                
                self.trade_menu_user.crafting_gui.updator(self.entity_data.trade_list, game)
                for event in self.trade_menu_user.events:
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                        self.trade_menu_user.crafting_gui.close()
                        self.crafting_menu_open = False
                        self.trade_menu_user = None

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
                if self.flipped:
                    self.image.flip(True)
                    self.flipped = False
            elif not self.flipped:
                self.image.flip(True)
                self.flipped = True
            if self.path_point < self.max_path_point and default.almost(self.rect.rect.topleft,self.walking_path[self.path_point],self.speed*1.5):
                if not self.walking_path:
                    self.cant_walk = True
                else:
                    self.path_point += 1
                    self.angle = (math.degrees(math.atan2(-(self.rect.rect.y-self.walking_path[self.path_point][1]),self.rect.rect.x-self.walking_path[self.path_point][0]))+180) % 360


            else:
                self.cooldown = 0
                self.created_path = False

    def walk_location(self,game,x,y,dimension):
        if not self.cant_walk:
            collide = False
            if not self.entity_data.ignore_solid:

                for object in game.objects:
                    if object.is_solid and self.vision_rect.colliderect(object.rect):
                        collide = True
            if collide:
                self.walking_solid(game, x, y,dimension)
            else:
                self.walking_ignore_solid(x,y,dimension)
        elif self.cooldown > 20:
            self.cooldown = 0
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
                    if self.flipped:
                        self.image.flip(True)
                        self.flipped = False
                elif not self.flipped:
                    self.image.flip(True)
                    self.flipped = True
                del radians
            location_check = default.rect(pygame.Rect(x,y,10,10),dimension)
            
            if not location_check.collidepoint(self.way_x * self.walk_direction.x,self.way_y * self.walk_direction.y,dimension) or default.is_point_on_line(self.path[self.path_point][0],self.path[self.path_point][0],self.angle,x,y):
                self.created_path = False
                self.cooldown = 0
            del location_check

    def random_walking(self,game):
        if not self.random_path:
            if self.cooldown > 20:
                attempts = 0
                while True:
                    self.random_x = random.randint(self.vision_rect.rect.left+(self.vision_rect.rect.width//4),self.vision_rect.rect.right-(self.vision_rect.rect.width//4))
                    self.random_y = random.randint(self.vision_rect.rect.top+(self.vision_rect.rect.height//4),self.vision_rect.rect.bottom-(self.vision_rect.rect.height//4))
                    self.random_path = True
                    attempts += 1
                    if self.random_y > 0 and self.random_x > 0:
                        break
                    if attempts > 10:
                        self.cooldown = 0
                        break
        else:
            self.walk_location(game,self.random_x,self.random_y,self.rect.dimension)
            if self.random_x - 10 < self.rect.rect.x < self.random_x + 10 and self.random_y - 10 < self.rect.rect.y < self.random_y + 10:
                self.random_path = False

    def render(self,players):
        for player in players:
            if self.rect.colliderect(player.render):
                return True

    def apply_damage(self,damage,game,attacker=None):
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
            self.cooldown = 40
        elif self.direction == "right":
            self.rect.rect.x -= self.entity_data.knockback + self.speed
            self.direction = "left"
            self.cooldown = 40
        if self.direction == "up":
            self.rect.rect.y += self.entity_data.knockback + self.speed
            self.direction = "down"
            self.cooldown = 40
        elif self.direction == "down":
            self.rect.rect.y -= self.entity_data.knockback + self.speed
            self.direction = "up"
            self.cooldown = 40

    def stop_riding(self):
        self.rider.action = "idle"
        self.rider.default_speed -= self.speed
        self.rider.reset_modifiers()
        self.rider = None
        self.ridden = False
import gif_pygame, pygame, random,items,gui,default,math,objects,projectiles,numpy

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, game):
        super().__init__(game.camera_group)
        self.keys = ()
        self.events = []
        self.mouse = pygame.mouse.get_pos()
        self.path = 'assets/entities/player_left_idle'
        self.image = default.load_image(self.path)
        self.rect = self.image.get_rect(topleft=pos)
        self.direction = pygame.math.Vector2()
        self.face_direction = "left"
        self.block_selector = gui.block_selector(pos,game,self)
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
        self.render = pygame.Rect(100,100,1200,800)

        self.inventory = items.inventory(5,5,self,True)
        self.hotbar = gui.hotbar(self,game)

        self.attacker = None
        self.gui_open = False
        self.inventory.clear_inventory()
        self.inventory.add_item(default.get_material('iron_horse'), 1)
        self.inventory.add_item(default.get_material('phoenix_feather'), 1)
        self.inventory_display = gui.inventory(game,player=self)

    def load_form_file(self,path,id):
        new_player = numpy.load(f"{path}/players/{id}.npy", None, True)
        new_player = new_player[0]
        self.path = new_player[0].path
        self.rect = new_player[0].rect
        self.id = id
        self.direction = new_player[0].direction
        self.face_direction = new_player[0].face_direction
        self.speed = new_player[0].speed
        self.inventory.inventory = new_player[0].inventory.inventory
        self.gui_open = new_player[0].gui_open
        self.hand = new_player[0].hand
        self.health = new_player[0].health


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
        self.render.x = self.rect.x - 600
        self.render.y = self.rect.y - 400

        # inventory check
        self.hotbar.updator()

        # death check
        if self.health <= 0:
            if self.inventory.has_item("heart"):
                self.health = 10
                self.inventory.remove_item_amount("heart",1)
            else:
                self.direction.x = 0
                self.direction.y = 0
                self.action = "dead"
            if self.image.frame == 12:
                try: self.ride_target.stop_riding(self)
                except: pass
                self.default_speed = 4
                if self.inventory.has_item("totem"):
                    self.inventory.remove_item_amount("totem", 1)
                else:
                    self.inventory.conver_to_drops(game)
                self.inventory_display.close_inventory()
                self.crafting_gui.close()
                self.ride_target = None
                self.inventory.apply_modifiers()
                self.rect.x = 3001
                self.rect.y = 3008
                self.health = 10
                self.action = "idle"


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
            if self.image.frame >= 9:
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
            self.block_selector.rect.y = 1204567890
            self.block_selector.rect.x = 1204567890
            self.inventory_display.updator(game,self.inventory)
            self.direction.x = 0
            self.direction.y = 0
        # animation updator
        if self.action not in self.path or self.animation_direction not in self.path:
            
            self.path = f'assets/entities/player_{self.animation_direction}_{self.action}'
            self.image = default.load_image(self.path)

        # event listener

        if not self.action == "dead":

            for event in self.events:
                if self.hand.item_data.event != None:
                    exec(self.hand.item_data.event,{},{"self":self,"game":game,"event":event})
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
                    if self.attack_cooldown >= self.attack_c:
                        self.attack_c += 0.1


    def updator(self,game):
        self.input(game)

        self.rect.topleft += self.direction * self.speed

        if self.health < 0:
            self.health = 0
        if self.health > self.max_health:
            self.health = self.max_health
        self.health_display.updator(self)
        if self.ride_target != None and self.action == "ride":
            try:
                self.ride_target.rect.topleft = (self.rect.x, self.rect.y + 4)
                if self.ride_target.direction == "left":
                    self.ride_target.rect.x -= 5
            except:
                self.ride_target = None
                self.action = "idle"

        if not self.gui_open and self.direction != [0,0]:
            self.block_selector.rect.x += self.speed * self.direction.x
            self.block_selector.rect.y += self.speed * self.direction.y

            self.hotbar.rect.y += self.speed * self.direction.y
            self.hotbar.rect.x += self.speed * self.direction.x
            if self.hotbar.selector != None and self.hotbar.selector.rect != None:
                self.hotbar.selector.rect.y += self.speed * self.direction.y
                self.hotbar.selector.rect.x += self.speed * self.direction.x
            for x in range(5):
                self.hotbar.display_array[x].rect.x += self.speed * self.direction.x
                self.hotbar.display_array[x].rect.y += self.speed * self.direction.y
                self.hotbar.display_array[x].text.rect.topleft += self.speed * self.direction


    def close(self):
        self.health_display.close()
        self.hotbar.close()
        self.block_selector.close()
        self.crafting_gui.remove()
        del self.inventory_display

        self.image = None

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
    def __init__(self, name, health, lootable_list=None, mob_type="P", attack_damage=0, attack_cooldown=0,
                 despawn_time=-1, knockback=1, vision=600, speed=3, shield=0.0, trade_list=None, summoner=None,
                 suicide=False, thrower=None, breed=None, kill_spawn=None, ride_data=None, ignore_solid=False,tame=None):
        self.vision = vision
        self.name = name
        self.health = health
        self.lootable_list = lootable_list
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


# noinspection PyBroadException
class entity(pygame.sprite.Sprite):
    def __init__(self, game, entity_data, pos, tag=None):
        super().__init__(game.camera_group)
        # entity info
        self.entity_data = entity_data
        self.name = entity_data.name
        self.health = entity_data.health
        self.direction = "left"
        self.id = hash(self)
        self.tag = tag
        # P not attack
        # H attack
        # N attack when attacked
        # L loyal
        self.vision_rect = pygame.Rect(pos[0],pos[1],self.entity_data.vision,self.entity_data.vision)
        self.max_health = self.health
        self.regeneration_time = 0
        self.ignore_solid = entity_data.ignore_solid
        self.mob_type = entity_data.mob_type
        self.despawn_time = entity_data.despawn_time
        self.attack_damage = entity_data.attack_damage
        self.attack_delay = entity_data.attack_cooldown
        self.attack_cooldown = 0
        self.shield = entity_data.shield
        self.ridden = False
        self.rider = None
        if self.mob_type == "H":
            self.attacker = random.choice(game.players)
        else:
            self.attacker = None

        self.saddled = False
        if self.entity_data.ride_data != None and self.entity_data.ride_data.needed_item == None:
            self.saddled = True
        self.knockback = entity_data.knockback
        self.speed = entity_data.speed
        # loot data
        try:
            len(entity_data.lootable_list)
            self.lootable_list = entity_data.lootable_list
        except:
            self.lootable_list = [entity_data.lootable_list]
        # trade data
        self.trade_list = entity_data.trade_list

        

        self.trade_menu_user = None
        self.crafting_menu_open = False
        spawn_kill = False
        if self.mob_type == "B":
            for e in game.entities:
                if e.mob_type == "B" and e.name == self.name:
                    self.despawn_time = 1
                    spawn_kill = True

            # sprite
        if spawn_kill:
            self.path = f'assets/entities/None'
        else:
            self.path = f'assets/entities/{self.name}'
        self.image = default.load_image(self.path)
        self.rect = self.image.get_rect(midbottom=pos)
        self.flipped = False
        # move
        self.created_path = False
        self.cant_walk = False
        self.cooldown = 40
        self.walking_path = False
        self.path_point = 0
        self.max_path_point = 0
        
        
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


    def remove(self):
        self.path = f'assets/entities/None'
        self.image = default.load_image(self.path)
        self.rect.x = 9999999
        self.rect.y = 9999999
        self.rect = None
        self.image = None

    def updator(self, game):
        # breed target finder
        if self.entity_data.breed != None:
            if self.fed and self.breed_target == None:
                if self.entity_data.breed.duplicate:
                    for i in range(self.entity_data.breed.amount):
                        game.entities.append(
                            entity(game.camera_group, default.get_entity(self.name), self.rect.center))
                    self.fed = False
                else:
                    closest = 10000000000000000
                    for Entity in game.entities:
                        if Entity != self:
                            if Entity.fed and Entity.name == self.name:
                                if closest > math.sqrt(2**(self.rect.x-Entity.rect.x) + (self.rect.y-Entity.rect.y) ** 2):
                                    closest = math.sqrt(2**(self.rect.x-Entity.rect.x) + (self.rect.y-Entity.rect.y) ** 2)
                                    self.breed_target = Entity
        # death check
        if self.health <= 0:
            if self.entity_data.kill_spawn != None:
                for i in range(self.entity_data.kill_spawn.amount):
                    game.entities.append(entity(game, default.get_entity(self.entity_data.kill_spawn.name),(self.rect.x + random.randint(-50, 50), self.rect.y + random.randint(-50, 50))))
                    game.entities[-1].attacker = self.attacker
            if self.lootable_list != [None]:
                for i in range(len(self.lootable_list)):
                    if random.random() < self.lootable_list[i].chance:
                        game.drops.append(
                            items.item(game, self.rect.center, self.lootable_list[i].count,
                                        self.lootable_list[i].loot_data))
            if self.ridden:
                self.stop_riding()   
            # soul drop check
            
            if isinstance(self.attacker,Player) and self.attacker.hand.item_data.item_name == "scythe":
                game.drops.append(items.item(game, self.rect.center, 1, default.get_material("soul")))
            self.remove()
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
                    self.rect.topleft -= self.walk_direction
                    self.created_path = False
                    self.path_point = self.max_path_point
                    if "border" in block.name:
                        self.rect.x = random.randint(10, 178) * 26
                        self.rect.y = random.randint(10, 151) * 20
        # vision rect updator
        self.vision_rect.center = self.rect.center

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
                if self.attack_cooldown >= self.attack_delay:
                    self.attack_cooldown = 0
                    self.attacker.apply_damage(self.attack_damage,game,self)
                    if self.entity_data.suicide:
                        self.remove()
                        return True
        # events

        for event in game.event_list:
            if event.type == pygame.USEREVENT:
                # cooldowns
                self.cooldown += 1
                if self.entity_data.breed != None and self.breed_cooldown <= self.entity_data.breed.cooldown:
                    self.breed_cooldown += 1

                self.attack_cooldown += 1

                if self.health < self.max_health:
                    self.regeneration_time += 1
                if self.despawn_time != -1:
                    self.despawn_time -= 1
                    # despawn time check
                    if self.despawn_time == 0:
                        self.remove()
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
                                game.drops.append(items.item(game, self.rect.center, 1,default.get_material(self.entity_data.ride_data.needed_item)))
                                self.saddled = False
                            if "_sword" in str(player.hand.item_data.tool_type) and player.attack_c > player.attack_cooldown:
                                player.attack_c = 0
                                self.apply_damage(player.damage,game,player)
                    elif event.button == 3 and player.block_selector.rect != None and self.rect.colliderect(player.block_selector.rect):
                        # trade menu check
                        if self.trade_list != None:
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
            if "space" in self.rider.keys or self.rider.ride_target != self:
                self.stop_riding()

            if "d" in self.rider.keys:
                self.direction = "right"
                if not self.flipped:
                    self.image = default.flip(self.image, True)
                    self.flipped = True
            elif "a" in self.rider.keys:
                self.direction = "left"
                if self.flipped:
                    self.image = default.flip(self.image,True)
                    self.flipped = False
        elif not self.breed_target != None:
            # random walking/waking to player
            if self.entity_data.breed != None and player.hand != None and player.hand.item_data.item_name == self.entity_data.breed.item_name:
                self.walk_location(game,player.rect.x,player.rect.y)
            elif self.attacker != None and self.attacker.rect != None and self.vision_rect.colliderect(self.attacker.rect):
                self.walk_location(game,self.attacker.rect.centerx,self.attacker.rect.centery)
            elif self.mob_type == "L":
                player_loyal = default.get_player(game.players,self.tag)

                if player_loyal != None and player_loyal.attacker != None and player_loyal.attacker.rect != None:
                    self.attacker = player_loyal.attacker
                else:
                    self.walk_location(game,player_loyal.rect.x,player_loyal.rect.y)
            else:
                self.random_walking(game)
            # breed system
        else:
            try:
                self.walk_location(game, self.breed_target.rect.x, self.breed_target.rect.y)
                if self.rect.colliderect(self.breed_target.rect):
                    self.fed = False
                    self.breed_target.fed = False
                    self.breed_cooldown = 0
                    self.breed_target.breed_cooldown = 0
                    self.breed_target.breed_target = None
                    self.breed_target = None
                    for i in range(self.entity_data.breed.amount):
                        game.entities.append(
                            entity(game.camera_group, default.get_entity(self.name), self.rect.center))
            except:
                self.breed_target = None
        # trade menu
        
        if self.crafting_menu_open:
            if not self.trade_menu_user.crafting_gui.is_open:
                self.crafting_menu_open = False
                self.trade_menu_user = None
            else:
                print(self.trade_list)
                self.trade_menu_user.crafting_gui.updator(self.trade_list, game)
                for event in self.trade_menu_user.events:
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                        self.trade_menu_user.crafting_gui.close()
                        self.crafting_menu_open = False
                        self.trade_menu_user = None


    def close(self):
        
        self.image = None

    def walking_solid(self, game, x,y):
        if not self.created_path and not self.rect.collidepoint(x,y) and not self.cant_walk:
            if self.vision_rect.collidepoint(x,y):
                if not (self.path_point < self.max_path_point):
                    self.walking_path = default.calculate_path(self.rect.topleft, (x,y), game.objects, self.rect.width, self.rect.height, 500,self.speed)
                    if not self.walking_path:
                        self.cant_walk = True
                    else:

                        self.path_point = 0
                        self.max_path_point = len(self.walking_path) - 1
                        self.angle = (math.degrees(math.atan2(-(self.rect.y - self.walking_path[self.path_point][1]),self.rect.x - self.walking_path[self.path_point][0])) + 180) % 360


                else:
                    self.created_path = True
        elif not self.rect.collidepoint(x,y) and not self.cant_walk:
            radians = abs(math.radians(self.angle))
            self.walk_direction.x = self.speed * math.cos(radians)
            self.walk_direction.y = - (self.speed * math.sin(radians))
            self.rect.topleft += self.walk_direction

            if 90 < self.angle < 270:
                if self.flipped:
                    self.image = default.flip(self.image,True)
                    self.flipped = False
            elif not self.flipped:
                self.image = default.flip(self.image,True)
                self.flipped = True
            if self.path_point < self.max_path_point and default.almost(self.rect.topleft,self.walking_path[self.path_point],self.speed*1.5):
                if not self.walking_path:
                    self.cant_walk = True
                else:
                    self.path_point += 1
                    self.angle = (math.degrees(math.atan2(-(self.rect.y-self.walking_path[self.path_point][1]),self.rect.x-self.walking_path[self.path_point][0]))+180) % 360


            else:
                self.cooldown = 0
                self.created_path = False

    def walk_location(self,game,x,y):
        if not self.cant_walk:
            collide = False
            if not self.entity_data.ignore_solid:

                for object in game.objects:
                    if object.is_solid and self.vision_rect.colliderect(object.rect):
                        collide = True
            if collide:
                self.walking_solid(game, x, y)
            else:
                self.walking_ignore_solid(x,y)
        elif self.cooldown > 20:
            self.cooldown = 0
            self.cant_walk = False

    def walking_ignore_solid(self, x, y):
        if not self.created_path:
            self.angle = (math.degrees(math.atan2(-(self.rect.y-y),self.rect.x-x))+180) % 360
            self.created_path = True
        else:
            if self.vision_rect.collidepoint(x, y):
                radians = abs(math.radians(self.angle))
                self.walk_direction.x = self.speed * math.cos(radians)
                self.walk_direction.y = -(self.speed * math.sin(radians))
                self.rect.topleft += self.walk_direction
                if 90 < self.angle < 270:
                    if self.flipped:
                        self.image = default.flip(self.image,True)
                        self.flipped = False
                elif not self.flipped:
                    self.image = default.flip(self.image,True)
                    self.flipped = True
                del radians
            location_check = pygame.Rect(x,y,10,10)
            
            if not location_check.collidepoint(self.way_x * self.walk_direction.x,self.way_y * self.walk_direction.y) or default.is_point_on_line(self.path[self.path_point][0],self.path[self.path_point][0],self.angle,x,y):
                self.created_path = False
                self.cooldown = 0
            del location_check

    def random_walking(self,game):
        if not self.random_path:
            if self.cooldown > 20:
                attempts = 0
                while True:
                    self.random_x = random.randint(self.vision_rect.left+(self.vision_rect.width//4),self.vision_rect.right-(self.vision_rect.width//4))
                    self.random_y = random.randint(self.vision_rect.top+(self.vision_rect.height//4),self.vision_rect.bottom-(self.vision_rect.height//4))
                    self.random_path = True
                    attempts += 1
                    if self.random_y > 0 and self.random_x > 0:
                        break
                    if attempts > 10:
                        self.cooldown = 0
                        break
        else:
            self.walk_location(game,self.random_x,self.random_y)
            if self.random_x - 10 < self.rect.x < self.random_x + 10 and self.random_y - 10 < self.rect.y < self.random_y + 10:
                self.random_path = False

    def render(self,players):
        for player in players:
            if self.rect.colliderect(player.render):
                return True

    def copy(self, other):
        self.entity_data = other.entity_data

        self.despawn_time = other.despawn_time
        self.name = other.name
        self.health = other.health
        self.direction = other.direction
        self.saddled = other.saddled
        self.cooldown = other.cooldown
        self.mob_type = other.mob_type
        self.attack_damage = other.attack_damage
        self.id = other.id
        self.tag = other.tag
        self.attack_delay = other.attack_delay
        self.regeneration_time = other.regeneration_time
        self.max_health = other.max_health
        self.attack_cooldown = other.attack_cooldown
        self.ignore_solid = other.ignore_solid
        self.trade_list = other.trade_list

        self.lootable_list = other.lootable_list
        self.path = other.path
        self.image = default.load_image(self.path)
        self.rect = other.rect
        self.vision_rect = other.vision_rect
        self.created_path = other.created_path
        self.cant_walk = other.cant_walk
        self.walking_path = other.walking_path
        self.path_point = other.path_point
        self.max_path_point = other.max_path_point
        self.walk_direction.y = other.walk_direction.y
        self.walk_direction.x = other.walk_direction.x
        self.way_x = other.way_x
        self.way_y = other.way_y

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
            self.rect.x += self.knockback + self.speed
            self.direction = "right"
            self.cooldown = 40
        elif self.direction == "right":
            self.rect.x -= self.knockback + self.speed
            self.direction = "left"
            self.cooldown = 40
        if self.direction == "up":
            self.rect.y += self.knockback + self.speed
            self.direction = "down"
            self.cooldown = 40
        elif self.direction == "down":
            self.rect.y -= self.knockback + self.speed
            self.direction = "up"
            self.cooldown = 40

    def stop_riding(self):
        self.rider.action = "idle"
        self.rider.default_speed -= self.speed
        self.rider.reset_modifiers()
        self.ridden = False
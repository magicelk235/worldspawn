import random,items,default,entities,pygame,gui

class plant:
    def __init__(self,max_stage,drop,grow_time,harvest_to_stage=-1):
        self.max_stage = max_stage
        self.drop = drop
        self.grow_time = grow_time
        self.harvest_to_stage = harvest_to_stage

class object_data:
    def __init__(self, name, lootable_list=None, health=1, needed_item=None, type_range=None, is_solid=False, hitbox=None, plant_data=None, recipe_list=None, door=False, store=False, floor=False, dyeable=False,summoner=None,thrower=None,custom_code=None):
        self.name = name
        self.custom_code = custom_code
        self.lootable_list = lootable_list
        self.health = health
        self.needed_item = needed_item
        self.type_range = type_range
        self.is_solid = is_solid
        self.door = door
        self.dyeable = dyeable
        self.hitbox = hitbox
        self.plant_data = plant_data
        self.recipe_list = recipe_list
        self.floor = floor
        self.store = store
        self.summoner = summoner
        self.thrower = thrower

class object(pygame.sprite.Sprite):
    def __init__(self, game, pos, data, tag=None):
        super().__init__(game.camera_group)
        self.name = data.name
        self.stage = 1
        self.plant_timer = 0
        self.attacker = None
        self.tag = tag
        self.id = hash(self)
        self.color = (255,255,255)
        if data.type_range:
            type = str(random.randint(data.type_range.min_value, data.type_range.max_value))
            self.path = f'assets/objects/{self.name}{type}'
            self.image = default.load_image(self.path)
        elif data.plant_data != None:
            self.path = f'assets/objects/{self.name}{self.stage}'
            self.image = default.load_image(self.path)
        elif data.door:
            self.path = f'assets/objects/{self.name}_close'
            self.image = default.load_image(self.path)
        else:
            self.path = f'assets/objects/{self.name}'
            self.image = default.load_image(self.path)
        self.is_solid = data.is_solid
        self.rect = self.image.get_rect(topleft=pos)
        try:
            len(data.lootable_list)
            self.lootable_list = data.lootable_list
        except:
            self.lootable_list = [data.lootable_list]
        if data.hitbox == None:
            self.hitbox = default.hitbox(self.rect.w,self.rect.h)
        else:
            self.hitbox = data.hitbox
        self.returner = None
        self.health = data.health
        self.crafting_gui_user = None
        self.crafting_gui_open = False
        self.rect_hitbox = pygame.Rect(self.rect.x+self.hitbox.offset_x,self.rect.y+self.hitbox.offset_y,self.hitbox.hitbox_x,self.hitbox.hitbox_y)
        self.recipe_list = data.recipe_list
        self.summon_c = 0
        self.projectile_c = 0
        self.data = data

    def updator(self, game):
        if self.is_solid:
            self.rect_hitbox = pygame.Rect(self.rect.x + self.hitbox.offset_x, self.rect.y + self.hitbox.offset_y,self.hitbox.hitbox_x, self.hitbox.hitbox_y)
            for player in game.players:
                if player.rect.colliderect(self.rect_hitbox):
                    player.rect.topleft -= player.direction * player.speed

        if self.attacker != None and self.attacker.rect == None:
            self.attacker == None
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

            if self.data.plant_data != None and self.stage < self.data.plant_data.max_stage and event.type == pygame.USEREVENT:
                self.plant_timer += 1
                if self.plant_timer >= self.data.plant_data.grow_time:
                    self.stage += 1
                    self.plant_timer = 0
        for player in game.players:
            for event in player.events:
                if self.data.custom_code != None:
                    exec(self.data.custom_code, {}, {"game": game, "self": self, "event": event,"player":player})
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.health != None:
                        if player.block_selector.rect != None and self.rect.colliderect(player.block_selector.rect):
                            if self.data.needed_item == None or (f"_{self.data.needed_item.item_name}" in str(player.hand.item_data.tool_type) and player.damage >= self.data.needed_item.min_damage) and player.attack_c > player.attack_cooldown:
                                if not self.health <= 0:
                                    player.attack_c = 0
                                    self.apply_damage(player.damage,game,player)
                                    break
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 3 and self.rect.colliderect(player.block_selector.rect) and player.action != "roll":
                    if self.data.dyeable:
                        if player.hand.item_data.color != None:
                            self.apply_color(player.hand.item_data.color)
                            player.hand.count -= 1
                    if self.data.store == True:
                        if player.hand.item_data.item_name != None:
                            self.lootable_list.append(items.lootable(default.get_material(player.hand.item_data.item_name), 1))
                            player.hand.count -= 1
                    if self.data.recipe_list != None and not self.crafting_gui_open:
                        for recipe in self.recipe_list:
                            recipe.get_items_data()
                        player.inventory_display.open_inventory(game,player,player.inventory.inventory)
                        self.crafting_gui_user = player
                        player.crafting_gui.open()
                        self.crafting_gui_open = True

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
                        game.drops.append(items.item(game, self.rect.center, self.lootable_list[i].count,self.lootable_list[i].loot_data))
            if self.data.plant_data != None and self.data.plant_data.harvest_to_stage != -1 and self.stage == self.data.plant_data.max_stage:
                self.stage = self.data.plant_data.harvest_to_stage
                try:
                    len(self.data.lootable_list)
                    self.lootable_list = self.data.lootable_list
                except:
                    self.lootable_list = [self.data.lootable_list]
                self.health = self.data.health
                self.path = f'assets/objects/{self.name}{self.stage}'
                self.apply_color(self.color)
            else:
                self.path = f'assets/objects/None'
                self.image = default.load_image(self.path)
                self.rect.y = 1234567890
                self.rect.x = 1234567890
                self.rect = None
                self.returner = False
                self.rect_hitbox.x = 1234567890
                self.rect_hitbox.y = 1234567890
                self.rect_hitbox = None
                return True
        if self.crafting_gui_open:
            if not self.crafting_gui_user.crafting_gui.is_open:
                self.crafting_gui_open = False
                self.crafting_gui_user = None
            else:
                self.crafting_gui_user.crafting_gui.updator(self.recipe_list, game)
                for event in self.crafting_gui_user.events:
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                        self.crafting_gui_user.crafting_gui.close()
                        self.crafting_gui_open = False

    def apply_color(self,color):
        self.image = default.load_image(self.path)
        self.color = default.mix_colors(self.color,color)
        color = (self.color[0],self.color[1],self.color[2],255)
        default.color_image(self.image,color)
        self.rect = self.image.get_rect(topleft=self.rect.topleft)

    def copy(self,other,game):
        self.path = other.path
        self.is_solid = other.is_solid
        self.rect = other.rect
        self.name = other.name
        self.plant_timer = other.plant_timer
        self.stage = other.stage
        self.lootable_list = other.lootable_list
        self.returner = other.returner
        self.health = other.health
        self.hitbox = other.hitbox
        self.tag = other.tag
        self.color = other.color
        self.id = other.id

        self.rect_hitbox = other.rect_hitbox
        self.data = other.data
        self.recipe_list = other.recipe_list
        self.apply_color(self.color)

    def close(self):
        self.image = None
        self.attacker = None


    def apply_damage(self,damage,game,attacker=None):
        if attacker != None and not default.has_one_tag(self,attacker):
            self.attacker = attacker
            for entity in default.double_tag_list(game.entities,self.id,self.tag):
                entity.attacker = attacker
            for Object in default.double_tag_list(game.objects,self.id,self.tag):
                Object.attacker = attacker
        self.health -= damage


    def render(self,players):
        
        if self.data.plant_data != None and self.stage != self.data.plant_data.max_stage:
            return True
        for player in players:
            if self.rect.colliderect(player.render):
                return True

class cave(pygame.sprite.Sprite):
    def __init__(self,pos,game,ore_name,max_ores,objects):
        super().__init__(game.camera_group)
        self.path = 'assets/objects/cave_entering'
        self.image = default.load_image(self.path)
        self.rect = self.image.get_rect(topleft=pos)
        self.cave_pos = (512,7510)
        self.org_pos = pos
        self.id = hash(self)
        self.ore_name = ore_name
        self.max_ores = max_ores
        self.caves_cooldown = 0
        for i in range(self.max_ores):
            objects.append(object(game, (99999, 99999), default.get_object(self.ore_name), self.id))
        self.player_in = False


    def updator(self,game):
        for player in game.players:
            for event in player.events:
                if self.rect.colliderect(player.rect) and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if not self.player_in:
                        self.path = 'assets/objects/cave_entering1'
                        self.image = default.load_image(self.path)
                        self.rect = self.image.get_rect(topleft=self.rect.topleft)
                        player.rect.x = self.cave_pos[0]
                        player.rect.y = self.cave_pos[1]
                        self.rect.x = self.cave_pos[0]
                        self.rect.y = self.cave_pos[1]
                        for block in game.objects:
                            if block.tag == self.id:
                                block.rect.x = random.randint(62, 908)
                                block.rect.y = random.randint(7100, 7904)
                        self.player_in = True
                    else:
                        self.path = 'assets/objects/cave_entering'
                        self.image = default.load_image(self.path)
                        self.rect = self.image.get_rect(topleft=self.rect.topleft)
                        player.rect.x = self.org_pos[0]
                        player.rect.y = self.org_pos[1]
                        for block in game.objects:
                            if block.tag == self.id:
                                block.rect.x = 9999999
                                block.rect.y = 9999999
                        self.rect.x = self.org_pos[0]
                        self.rect.y = self.org_pos[1]
                        self.player_in = False

    def restock(self, game):
        new_ores_needed = self.max_ores - default.tag_counter(game.objects,self.id)
        if new_ores_needed != 0:
            for i in range(new_ores_needed):
                game.objects.append(object(game, (99999, 99999), default.get_object(self.ore_name), self.id))
        if self.player_in:
            for block in game.objects:
                if block.tag == self.id:
                    block.rect.x = random.randint(62, 908)
                    block.rect.y = random.randint(7100, 7904)


    def close(self):
        self.image = None

    def copy(self,other,group):
        self.path = other.path
        self.image = default.load_image(self.path)
        self.rect = other.rect
        self.cave_pos = other.cave_pos
        self.org_pos = other.org_pos
        self.player_in = other.player_in
        self.id = other.id
        self.max_ores = other.max_ores

    def render(self,players):
        for player in players:
            if self.rect.colliderect(player.render):
                return True
        return False
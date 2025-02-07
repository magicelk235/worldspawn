import default,objects,items,math,pygame,os,copy,gif_pygame,shutil

class display_sprite(pygame.sprite.Sprite):
    def __init__(self,camera_group,rect,image,image_in_bytes):
        super().__init__(camera_group)
        self.rect = rect
        self.image = image
        self.image_in_bytes = image_in_bytes

class fake_player(pygame.sprite.Sprite):
    def __init__(self,camera_group,rect,image,image_in_bytes):
        super().__init__(camera_group)
        self.rect = rect
        self.image = image
        self.image_in_bytes = image_in_bytes
        self.render = pygame.Rect(100,100,1200,800)
        self.render.x = self.rect.x - 600
        self.render.y = self.rect.y - 400

class selected(pygame.sprite.Sprite):
    def __init__(self,pos,x,y,game,player):
        super().__init__(game.camera_group)
        self.x = x
        self.y = y
        self.player = player
        self.path = "assets/gui/selected"
        self.image = default.load_image(self.path)
        self.rect = self.image.get_rect(topleft=pos)

    def delete(self):
        self.image = None
        self.rect = None
        self.player = None

    def close(self):
        self.image = None

class inventory_selector(pygame.sprite.Sprite):
    def __init__(self,pos,game,max_x,max_y,player):
        super().__init__(game.camera_group)
        self.x = max_x//2
        self.y = max_y//2
        self.player = player
        self.max_x = max_x
        self.max_y = max_y
        self.is_ready = None
        self.is_selected = False
        self.inventory_pos = pos
        self.selected = None
        self.path = "assets/gui/None"
        self.image = default.load_image(self.path)
        self.rect = self.image.get_rect(topleft=(self.inventory_pos[0] + self.x * 36,self.inventory_pos[1] + self.y * 36))

    def moving(self,game):
        self.path = "assets/gui/selector"
        self.image = default.load_image(self.path)
        self.rect = self.image.get_rect(topleft=(self.inventory_pos[0] + self.x * 36, self.inventory_pos[1] + self.y * 36))
        for event in self.player.events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.is_ready == None:
                        self.selected = selected((self.rect.x, self.rect.y),self.x, self.y, game,self.player)
                        self.is_ready = False
                    elif not self.is_ready:
                        self.is_ready = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    if self.y > 0:
                        self.y -= 1
                if event.key == pygame.K_s:
                    if self.y < (self.max_y - 1):
                        self.y += 1
                elif event.key == pygame.K_a:
                    if self.x > 0:
                        self.x -= 1
                elif event.key == pygame.K_d:
                    if self.x < (self.max_x - 1):
                        self.x += 1
        if self.is_ready:
            return True
        return False


    def delete(self):
        self.image = None
        self.rect = None
        if self.selected != None:
            self.selected.delete()

    def close(self):
        self.image = None

class hotbar_selector(pygame.sprite.Sprite):
    def __init__(self, pos, game, x, player):
        super().__init__(game.camera_group)
        self.x = x
        self.y = 0
        self.player = player
        self.is_selected = False
        self.inventory_pos = pos
        self.path = "assets/gui/None"
        self.image = default.load_image(self.path)
        self.rect = self.image.get_rect(topleft=(self.inventory_pos[0] + self.x * 36,self.inventory_pos[1] + self.y * 36))

    def moving(self, hotbar):
        self.path = "assets/gui/selector"
        self.image = default.load_image(self.path)
        self.rect = self.image.get_rect(topleft=(hotbar.rect.x + self.x * 36, hotbar.rect.y + self.y * 36))

        


        for event in self.player.events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    self.x = 0
                elif event.key == pygame.K_2:
                    self.x = 1
                elif event.key == pygame.K_3:
                    self.x = 2
                elif event.key == pygame.K_4:
                    self.x = 3
                elif event.key == pygame.K_5:
                    self.x = 4
        return self.player.inventory.inventory[self.y + 4][self.x]


    def delete(self):
        self.image = None
        self.rect = None

    def close(self):
        self.image = None

class block_selector(pygame.sprite.Sprite):
    def __init__(self,pos,game,player):
        super().__init__(game.camera_group)
        self.x = 0
        self.y = 0
        self.player = player
        self.inventory_pos = pos
        self.path = "assets/gui/block_selector"
        self.image = default.load_image(self.path)
        self.rect = self.image.get_rect(topleft=(self.x * 32+5,self.y * 23+5))

    def moving(self):
        if self.image != None:
            self.path = "assets/gui/block_selector"
            self.image = default.load_image(self.path)
            self.rect = self.image.get_rect(topleft=(1, 1))



        mouse_pos = self.player.mouse
        x = mouse_pos[0] + self.player.rect.centerx - 400
        y = mouse_pos[1] + self.player.rect.centery - 200

        if x > self.player.rect.x + 26*self.player.range:
            x = self.player.rect.x + 26*self.player.range
        elif x < self.player.rect.x - 26*self.player.range:
            x = self.player.rect.x - 26*self.player.range
        if y > self.player.rect.y + 20*self.player.range:
            y = self.player.rect.y + 20*self.player.range
        elif y < self.player.rect.y - 20*self.player.range:
            y = self.player.rect.y - 20*self.player.range



        self.rect.topleft = (x,y)
        self.y = self.rect.y // 20
        self.x = self.rect.x // 26

    def delete(self):
        self.image = None
        self.rect = None
        del self

    def close(self):
        self.image = None
        self.rect = None
        del self

class gui_item(pygame.sprite.Sprite):
    def __init__(self,pos, count, name, game,player):
        super().__init__(game.camera_group)
        self.name = name
        self.player = player
        if count == 0:
            self.count = ""
        self.path = f'assets/items/{name}'
        self.image = default.load_image(self.path)
        self.rect = self.image.get_rect(topleft=(pos[0],pos[1]))
        self.text = text((self.rect.x+18,self.rect.y+18),10,str(count),game.camera_group,player=player)


    def close(self):
        self.image = default.load_image(self.path)
        self.text.delete()
        self.image = None
        self.rect = None
        del self

    def reset(self,name,count,pos):
        if pos != self.rect.topleft:
            self.rect.y = pos[1]
            self.rect.x = pos[0]

        if name != self.name or count != self.count:
            if count == 0:
                self.count = ""
            else:
                self.count = count
            self.name = name
            self.path = f'assets/items/{name}'
            self.image = default.load_image(self.path)
            self.text.set_text(self.count)
        if self.text.rect.topleft != (pos[0] + 18,pos[1] + 18):
            self.text.rect.x = pos[0] + 18
            self.text.rect.y = pos[1] + 18

class crafting_gui(pygame.sprite.Sprite):
    def __init__(self, game,player):
        super().__init__(game.camera_group)
        self.player = player
        self.path = "assets/gui/crafting_gui"
        self.image = default.load_image(self.path)
        self.rect = self.image.get_rect(topleft=(-1000,-1000))
        self.needed_items = None
        self.needed_items_gui = inventory(game,-240,10,1,1,True,player)
        self.is_open = False
        self.item = self.item = gui_item((999999,999999),0, None, game,player)
        self.x = 0
        self.is_created = False

    def updator(self,recipes,game):
        if not self.is_created:
            self.item.reset(recipes[self.x].result.item_data.item_name,recipes[self.x].result.count,(self.rect.x+6,self.rect.y+24))


            if self.needed_items_gui != None:
                self.needed_items_gui.close_inventory()
                self.needed_items_gui.close()
            self.needed_items = [[items.inventory_item(default.get_material(None),0) for _ in range(3)] for _ in range(math.ceil(len(recipes[self.x].items) / 3))]
            i = 0
            for row in self.needed_items:
                for item in row:
                    try:
                        item.copy(recipes[self.x].items[i])
                    except:
                        pass
                    i += 1
            self.needed_items_gui.open_inventory(game,self.player,self.needed_items,3,math.ceil(len(recipes[self.x].items)/3))

            self.is_created = True
        else:
            self.needed_items_gui.updator(game,self.needed_items)
        for event in self.player.events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w and self.x < len(recipes) - 1:
                    self.x += 1
                    self.is_created = False
                elif event.key == pygame.K_s and self.x != 0:
                    self.x -= 1
                    self.is_created = False

                elif event.key == pygame.K_RETURN:


                    has_items = True
                    for item in recipes[self.x].items:
                        if not self.player.inventory.has_item(item.item_data.item_name,item.count):
                            has_items = False
                    if has_items and self.player.inventory.add_item(recipes[self.x].result.item_data, recipes[self.x].result.count):
                        for item in recipes[self.x].items:
                            self.player.inventory.remove_item_amount(item.item_data.item_name,item.count)


    def close(self):
        self.player.gui_open = False
        self.player.inventory_display.close_inventory()
        self.is_created = False
        self.path = "assets/gui/None"
        self.image = default.load_image(self.path)
        self.needed_items_gui.close_inventory()
        self.item.remove()
        self.item.reset(None,0,(999999,999999))
        self.is_open = False


    def remove(self):
        self.is_open = False
        self.is_created = False
        self.image = None
        self.needed_items_gui.close()
        if self.item != None:
            self.item.remove()
        self.item = None
        self.rect = None

    def open(self):
        self.x = 0
        self.path = "assets/gui/crafting_gui"
        self.image = default.load_image(self.path)
        self.rect = self.image.get_rect(center=(self.player.rect.x-150, self.player.rect.y + 50))
        self.is_open = True
        self.player.gui_open = True

class CameraGroup(pygame.sprite.Group):
    def __init__(self):

        super().__init__()
        self.screen = pygame.display.set_mode((800, 400), pygame.SCALED | pygame.RESIZABLE)
        self.display_surface = pygame.display.get_surface()

        # camera offset
        self.offset = pygame.math.Vector2()
        self.half_w = 800 // 2
        self.half_h = 400 // 2


        # ground
        self.ground_surf_path = 'assets/objects/ground.png'
        self.ground_surf = pygame.image.load(default.resource_path(self.ground_surf_path)).convert_alpha()
        self.ground_rect = self.ground_surf.get_rect(topleft=(0, 0))


        self.cave_ground_surf1_path = 'assets/objects/cave_ground.png'
        self.cave_ground_surf1 = pygame.image.load(default.resource_path(self.cave_ground_surf1_path)).convert_alpha()
        self.cave_ground_rect1 = self.ground_surf.get_rect(topleft=(0, 7061))


        # cave dark
        self.cave_surf_path = 'assets/objects/night.png'
        self.cave_surf = pygame.image.load(default.resource_path(self.cave_surf_path)).convert_alpha()
        self.cave_rect = self.cave_surf.get_rect(topleft=(-500, 6500))
        # zoom
        self.zoom_scale = 1
        self.internal_surf_size = (2500, 2500)
        self.internal_surf = pygame.Surface(self.internal_surf_size, pygame.SRCALPHA)
        self.internal_rect = self.internal_surf.get_rect(center=(self.half_w, self.half_h))
        self.internal_surface_size_vector = pygame.math.Vector2(self.internal_surf_size)
        self.internal_offset = pygame.math.Vector2()
        self.internal_offset.x = self.internal_surf_size[0] // 2 - self.half_w
        self.internal_offset.y = self.internal_surf_size[1] // 2 - self.half_h

    def center_target_camera(self, target):
        self.offset.x = target.rect.centerx - self.half_w
        self.offset.y = target.rect.centery - self.half_h

    def close(self):
        
        del self.screen
        del self.display_surface

        del self.offset
        del self.half_w
        del self.half_h


        # ground
        del self.ground_surf_path
        del self.ground_surf
        del self.ground_rect


        del self.cave_ground_surf1_path
        del self.cave_ground_surf1
        del self.cave_ground_rect1


        # cave dark
        del self.cave_surf_path
        del self.cave_surf
        del self.cave_rect
        # zoom
        del self.zoom_scale
        del self.internal_surf_size
        del self.internal_surf
        del self.internal_rect
        del self.internal_surface_size_vector
        del self.internal_offset

        
        for sprite in self.sprites():    
            sprite.image = default.to_bytes(sprite.image)

    def player_load(self,player,client,ignore_render=False,clear_trash=True,always_update=False):
        sprite_list = []
        load_object_start = [
            "wooden_floor",
            "rock_floor",
            "lake",
            "cliff",
            "mini_cliff",
            "spawn0",
            "spawn1",
            "spawn2",
            "spawn3",
            "spawn4",

        ]
        load_middle = [

            "<hotbar Sprite(in 1 groups)>",
            "<inventory Sprite(in 1 groups)>",
            "<crafting_gui Sprite(in 1 groups)>",
            "<world_menu Sprite(in 1 groups)>",
            "<gui_item Sprite(in 1 groups)>",

        ]
        one_player_load = [
            "<gui_item Sprite(in 1 groups)>",
            "<hotbar Sprite(in 1 groups)>",
            "<inventory Sprite(in 1 groups)>",
            "<crafting_gui Sprite(in 1 groups)>",
            "<text Sprite(in 1 groups)>",
            "<death_heart Sprite(in 1 groups)>",
            "<alive_heart Sprite(in 1 groups)>",
            "<inventory_selector Sprite(in 1 groups)>",
            "<hotbar_selector Sprite(in 1 groups)>",
            "<block_selector Sprite(in 1 groups)>",
            "<selected Sprite(in 1 groups)>",
        ]
        load_end = [
            "<world_icon Sprite(in 1 groups)>",
            "<selected Sprite(in 1 groups)>",
            "<text Sprite(in 1 groups)>",
            "<death_heart Sprite(in 1 groups)>",
            "<alive_heart Sprite(in 1 groups)>",
            "<inventory_selector Sprite(in 1 groups)>",
            "<hotbar_selector Sprite(in 1 groups)>",
            "<block_selector Sprite(in 1 groups)>",
            "<world_menu_selector Sprite(in 1 groups)>",
        ]
        load_theme = [
            "<theme Sprite(in 1 groups)>"
        ]

        # ground
        player_offset = pygame.math.Vector2()
        player_offset.x = player.rect.centerx - self.half_w
        player_offset.y = player.rect.centery - self.half_h

        for sprite in self.sprites():
            if sprite.rect is not None:

                if isinstance(sprite.image,gif_pygame.GIFPygame) and always_update:
                    sprite.image._animate()
                if ignore_render or player.render.colliderect(sprite.rect) :
                    if (str(sprite) == "<object Sprite(in 1 groups)>" and sprite.name in load_object_start) or isinstance(sprite, objects.cave):
                        offset = sprite.rect.topleft - player_offset + self.internal_offset
                        sprite_list.append({"sprite":sprite,"location":offset})

            elif clear_trash:
                self.remove(sprite)
                del sprite

        for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.centery if sprite.rect else float('-inf')):
            if sprite.rect != None and (ignore_render or player.render.colliderect(sprite.rect)):
                load_object_check = False
                if str(sprite) == "<object Sprite(in 1 groups)>" and sprite.name in load_object_start:
                    load_object_check = True
                if not (str(sprite) in load_end or str(sprite) in load_middle or str(
                        sprite) in load_theme or load_object_check or isinstance(sprite, objects.cave)):
                    offset = sprite.rect.topleft - player_offset + self.internal_offset
                    sprite_list.append({"sprite": sprite, "location": offset})
        for sprite in self.sprites():
            if sprite.rect != None and (ignore_render or player.render.colliderect(sprite.rect)):
                if str(sprite) in load_middle:
                    if str(sprite) in one_player_load and client:
                        if sprite.player == player:
                            offset = sprite.rect.topleft - player_offset + self.internal_offset
                            sprite_list.append({"sprite": sprite, "location": offset})
                    elif not client:
                        offset = sprite.rect.topleft - player_offset + self.internal_offset
                        sprite_list.append({"sprite": sprite, "location": offset})

        for sprite in self.sprites():
            if sprite.rect != None and (ignore_render or player.render.colliderect(sprite.rect)):
                if str(sprite) in load_end:
                    if str(sprite) in one_player_load and client:
                        if sprite.player == player:
                            offset = sprite.rect.topleft - player_offset + self.internal_offset
                            sprite_list.append({"sprite": sprite, "location": offset})
                    elif not client:
                        offset = sprite.rect.topleft - player_offset + self.internal_offset
                        sprite_list.append({"sprite": sprite, "location": offset})


        for sprite in self.sprites():
            if str(sprite) in load_theme:
                sprite_list.append({"sprite": sprite, "location": self.internal_offset})
        return sprite_list

    def to_dict(self,player):
        sprite_list = []
        for sprite in self.player_load(player,True,clear_trash=False):
            if sprite["sprite"].rect == None or sprite["sprite"].image == None:
                continue
            image_size = sprite["sprite"].image.get_size()
            image = default.to_bytes(copy.copy(sprite["sprite"].image))
            sprite_list.append({"rect":copy.deepcopy(sprite["sprite"].rect),"image":image,"size":image_size})
            sprite_list[-1]["rect"].topleft = sprite["location"]


        return sprite_list

    def from_dict(self, sprite_list):
        self.empty()
        for sprite in sprite_list:
            sprite_rect = pygame.Rect(sprite["rect"])
            sprite_image = default.from_bytes(sprite["image"], sprite["size"])
            display_sprite(self, sprite_rect, sprite_image, sprite["image"])

    def normal_draw(self,player):
        self.internal_surf.fill('#191716')

        self.center_target_camera(player)

        ground_offset = self.ground_rect.topleft - self.offset + self.internal_offset
        self.internal_surf.blit(self.ground_surf, ground_offset)

        cave_ground_offset1 = self.cave_ground_rect1.topleft - self.offset + self.internal_offset
        self.internal_surf.blit(self.cave_ground_surf1, cave_ground_offset1)
        for sprite in self.sprites():
            default.display_image(sprite.image, self.internal_surf, sprite.rect)


        cave_offset = self.cave_rect.topleft - self.offset + self.internal_offset
        self.internal_surf.blit(self.cave_surf, cave_offset)
        scaled_surf = pygame.transform.scale(self.internal_surf, self.internal_surface_size_vector * self.zoom_scale)
        scaled_rect = scaled_surf.get_rect(center=(self.half_w, self.half_h))
        self.internal_surf.fill('#191716')

        self.display_surface.blit(scaled_surf, scaled_rect)

    def custom_draw(self, player,client=True,ignore_render=False):
        self.internal_surf.fill('#191716')

        self.center_target_camera(player)

        ground_offset = self.ground_rect.topleft - self.offset + self.internal_offset
        self.internal_surf.blit(self.ground_surf,  ground_offset)

        cave_ground_offset1 = self.cave_ground_rect1.topleft - self.offset + self.internal_offset
        self.internal_surf.blit(self.cave_ground_surf1, cave_ground_offset1)


        for sprite in self.player_load(player,client,ignore_render,always_update=True):

            default.display_image(sprite["sprite"].image, self.internal_surf, sprite["location"])


        cave_offset = self.cave_rect.topleft - self.offset + self.internal_offset
        self.internal_surf.blit(self.cave_surf, cave_offset)
        scaled_surf = pygame.transform.scale(self.internal_surf, self.internal_surface_size_vector * self.zoom_scale)
        scaled_rect = scaled_surf.get_rect(center=(self.half_w, self.half_h))
        self.internal_surf.fill('#191716')
        self.display_surface.blit(scaled_surf, scaled_rect)

class world_menu_selector(pygame.sprite.Sprite):
    def __init__(self,pos,camera_group):
        super().__init__(camera_group)
        self.image = default.load_image('assets/gui/world_selector')
        self.rect = self.image.get_rect(topleft=pos)
        self.offset = 0
        self.keyboard = None
        self.y = 0

    def updator(self,event_list,world_menu,camera_group):
        if self.keyboard == None:
            for event in event_list:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DOWN:
                        if self.y < 3:
                            self.y += 1
                        else:
                            self.offset += 4
                            self.y = 0
                            world_menu.reset(self.offset,camera_group)
                    elif event.key == pygame.K_UP:
                        if self.y > 0:
                            self.y -= 1
                        elif self.offset != 0:
                            self.offset -= 4
                            self.y = 3
                            world_menu.reset(self.offset, camera_group)
                    elif event.key == pygame.K_x:
                        try:
                            shutil.rmtree(f"{world_menu.path}/{world_menu.worlds_list[self.y]}")
                            world_menu.worlds_list.remove(world_menu.worlds_list[self.y])
                            world_menu.reset(self.offset,camera_group)

                        except:
                            pass
                    elif event.key == pygame.K_RETURN:
                        try:
                            return f"{world_menu.path}/{world_menu.worlds_list[self.y+self.offset]}"
                        except:
                            if "host" in world_menu.path:
                                self.keyboard = keyboard(camera_group,world_menu.rect.bottomleft+pygame.math.Vector2(0,0),"enter world name")
                            else:
                                self.keyboard = keyboard(camera_group, world_menu.rect.bottomleft+pygame.math.Vector2(0,0), "enter joining code")
        else:
            entered_text = self.keyboard.update(event_list)
            try:
                if entered_text != None:
                    os.mkdir(f"{world_menu.path}/{entered_text}")
                    return f"{world_menu.path}/{entered_text}"
            except:
                self.keyboard.set_text("name/code already used")
        self.rect = self.image.get_rect(topleft=(world_menu.rect.x + 14,world_menu.rect.y + 13 + (self.y * 42)))

    def delete(self):
        self.rect = None
        self.image = None

class world_menu(pygame.sprite.Sprite):
    def __init__(self, pos, camera_group, extension):
        super().__init__(camera_group)
        if not os.path.exists("data"):
            os.mkdir("data")
            os.mkdir("data/host")
            os.mkdir("data/join")

        self.image = default.load_image("assets/gui/world_list")
        self.rect = self.image.get_rect(topleft=pos)
        self.render = pygame.Rect(self.rect.x, self.rect.y, 780, 400)

        self.path = f"data/{extension}"
        self.worlds_list = os.listdir(self.path)

        self.world_icons_list = [None,None,None,None]
        self.world_names_list = [None,None,None,None]
        self.reset(0,camera_group)

    def reset(self,offset,camera_group):
        for i in range(1, 5):
            try:
                if self.world_names_list[i-1] != None:
                    camera_group.remove(self.world_names_list[i-1])
                if self.world_icons_list[i-1] != None:
                    camera_group.remove(self.world_icons_list[i-1])
                self.world_names_list[i - 1] = text((self.rect.x + 56, self.rect.y + 18 + i * 42 - 42), 15,self.worlds_list[offset+i-1], camera_group)
                self.world_icons_list[i - 1] = world_icon((self.rect.x + 20, self.rect.y + 16 + i * 42 - 42),camera_group)
            except:
                pass

class world_icon(pygame.sprite.Sprite):
    def __init__(self, pos, camera_group):
        super().__init__(camera_group)
        self.image = default.load_image("assets/gui/world_icon")
        self.rect = self.image.get_rect(topleft=pos)

    def delete(self):
        self.rect = None
        self.image = None

class textbox(pygame.sprite.Sprite):
    def __init__(self,pos,camera_group):
        super().__init__(camera_group)
        self.image = default.load_image("assets/gui/textbox")
        self.rect = self.image.get_rect(topleft=pos)

class keyboard:
    def __init__(self,camera_group,pos,default_text=""):
        self.text = default_text
        self.textbox = textbox(pos,camera_group)
        self.text_object = text(pos+pygame.math.Vector2(20,28),13,self.text,camera_group)

    def set_text(self,text):
        self.text_object.set_text(text)

    def update(self,event_list):
        for event in event_list:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return self.text
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                elif event.key == pygame.K_SPACE:
                    self.text = self.text + " "
                else:
                    key_name = pygame.key.name(event.key)
                    self.text = self.text + key_name
                self.text_object.set_text(self.text)
        return None

class button:
    def __init__(self,x,y,w,h):
        self.rect = pygame.Rect(x,y,w,h)

    def check(self,event_list):
        for event in event_list:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.rect.collidepoint(pygame.mouse.get_pos()+pygame.math.Vector2(1678,1855)):
                    return True
        return False
    
class game_type_gui(pygame.sprite.Sprite):
    def __init__(self,pos,camera_group):
        super().__init__(camera_group)
        self.image = default.load_image("assets/gui/game_type")
        self.rect = self.image.get_rect(topleft=pos)
        self.host_button = button(self.rect.x+15,self.rect.y+13,130,40)
        self.join_button = button(self.rect.x+15,self.rect.y+59,130,40)

    def updator(self,events):
        if self.host_button.check(events):
            return "host"
        elif self.join_button.check(events):
            return "join"
        else:
            return None

class text(pygame.sprite.Sprite):
    def __init__(self,pos,size,text,camera_group,color=(0,0,0),normal_font=False,player=None):
        super().__init__(camera_group)
        self.color = color
        self.text = text
        self.player = player
        self.normal_font = normal_font
        self.size = size
        if normal_font:
            font = pygame.font.Font(None, size)
        else:
            font = pygame.font.Font(default.resource_path('assets/fonts/font.ttf'), size)
        self.image = font.render(str(self.text), normal_font, self.color)
        self.rect = self.image.get_rect(topleft=pos)

    def updator(self):
        if self.normal_font:
            font = pygame.font.Font(None, self.size)
        else:
            font = pygame.font.Font(default.resource_path('assets/fonts/font.ttf'), self.size)

        self.image = font.render(str(self.text), False, self.color)

    def set_text(self,text):
        self.text = text
        if self.normal_font:
            font = pygame.font.Font(None, self.size)
        else:
            font = pygame.font.Font(default.resource_path('assets/fonts/font.ttf'), self.size)
        self.image = font.render(str(self.text),False,self.color)

    def delete(self):
        self.rect = None
        self.image = None

class heart_display:
    def __init__(self, group, player):
        self.death_hearts = death_heart(group, player)
        self.alive_hearts = alive_heart(group, player)


    def updator(self, player):
        self.death_hearts.updator(player)
        self.alive_hearts.updator(player)


    def close(self):
        self.alive_hearts.close()
        self.death_hearts.close()

class death_heart(pygame.sprite.Sprite):
    def __init__(self, game, player):
        super().__init__(game.camera_group)
        self.player = player
        self.path = default.resource_path('assets/gui/death_hearts')
        self.image = default.load_image(self.path)
        self.hearts = 10
        self.rect = pygame.Rect(0,0,self.hearts*16,14)
        self.image = self.image.subsurface(self.rect)

    def updator(self,player):
        if player.max_health != self.hearts:
            self.path = default.resource_path('assets/gui/death_hearts')
            self.image = default.load_image(self.path)
            self.hearts = player.max_health
            self.rect = pygame.Rect(0, 0, self.hearts * 16, 14)
            self.image = self.image.subsurface(self.rect)
        self.rect.x = player.rect.x - 392
        self.rect.y = player.rect.y - 190

    def close(self):
        self.image = None

class alive_heart(pygame.sprite.Sprite):
    def __init__(self, game, player):
        super().__init__(game.camera_group)
        self.player = player
        self.path = default.resource_path('assets/gui/alive_hearts')
        self.image = default.load_image(self.path)
        self.hearts = 10
        self.rect = pygame.Rect(0, 0, self.hearts * 16, 14)
        self.image = self.image.subsurface(self.rect)

    def updator(self, player):
        if player.health != self.hearts:
            self.path = default.resource_path('assets/gui/alive_hearts')
            self.image = default.load_image(self.path)
            self.hearts = player.health
            self.rect = pygame.Rect(0, 0, self.hearts * 16, 14)
            self.image = self.image.subsurface(self.rect)
        self.rect.x = player.rect.x - 392
        self.rect.y = player.rect.y - 190

    def close(self):
        self.image = None

class inventory(pygame.sprite.Sprite):
    def __init__(self,game,offset_x=0,offset_y=0,max_x=5,max_y=5,display_only=False,player=None):
        super().__init__(game.camera_group)
        self.path = 'assets/gui/None'
        self.image = default.load_image(self.path)
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.player = player
        self.display_only = display_only
        self.max_x = max_x
        self.max_y = max_y
        self.rect = self.image.get_rect(topleft=(0, 0))
        self.opened = False
        self.selector = None
        self.display_array = [[gui_item((-3000,-3000),0,None,game,player) for _ in range(max_x)] for _ in range(max_y)]


    def open_inventory(self,game,player,inventory,max_x=None,max_y=None):
        self.path = 'assets/gui/inventory'
        if max_x != None:
            self.max_x = max_x
        if max_y != None:
            self.max_y = max_y
        if max_y != None or max_x != None:
            self.display_array = [[gui_item((99999,99999),0,None,game,self.player) for _ in range(self.max_x)] for _ in range(self.max_y)]
        self.image = default.load_image(self.path)
        self.image = default.cut_image(self.image,36*self.max_x+4,36*self.max_y+4)
        self.rect = self.image.get_rect()
        self.rect.x = player.rect.x + self.offset_x - ((36 * self.max_x) // 2)
        self.rect.y = player.rect.y + self.offset_y - ((36 * self.max_y) // 2)
        self.reset(inventory)
        if not self.display_only:
            self.selector = inventory_selector((self.rect.x, self.rect.y), game, self.max_x, self.max_y,player)
        self.opened = True

    def reset(self,inventory):
        for x in range(self.max_x):
            for y in range(self.max_y):
                self.display_array[y][x].reset(inventory[y][x].item_data.item_name,inventory[y][x].count,(self.rect.x + x * 36+5,self.rect.y + y * 36+5))


    def updator(self,game,inventory):

        if self.display_only:
            self.reset(inventory)
        else:
            self.reset(inventory.inventory)
            if self.selector.moving(game):
                inventory.interact(self.selector.x,self.selector.y,self.selector.selected.x,self.selector.selected.y)
                self.selector.selected.delete()
                self.selector.is_ready = None

            if "x" in self.player.keys:
                inventory.remove_at(self.selector.x,self.selector.y)
            if "y" in self.player.keys:
                inventory.drop(self.selector.x,self.selector.y,game)


    def close_inventory(self):
        self.path = 'assets/gui/None'
        self.image = default.load_image(self.path)
        self.rect = self.image.get_rect(topleft=(99999,99999))
        if self.selector != None:
            self.selector.delete()
            if self.selector.selected != None:
                self.selector.selected.delete()
        for x in range(self.max_x):
            for y in range(self.max_y):
                self.display_array[y][x].reset(None,0,(99999,999999))
        self.opened = False


    def close(self):
        if self.selector != None:
            self.selector.close()
            if self.selector.selected != None:
                self.selector.selected.close()
        self.image = None
        for x in range(self.max_x):
            for y in range(self.max_y):
                if self.display_array[y][x] != None:
                    self.display_array[y][x].close()

class hotbar(pygame.sprite.Sprite):
    def __init__(self,player,game):
        super().__init__(game.camera_group)
        self.path = 'assets/gui/hotbar'
        self.image = default.load_image(self.path)
        self.player = player
        self.rect = self.image.get_rect(topleft=(player.rect.x - 90, player.rect.y + 170))
        self.selector = hotbar_selector((self.rect.x, self.rect.y), game, 0, player)
        self.display_array = [gui_item((999999,999999),0,None,game,self.player) for _ in range(5)]

    def close(self):
        for x in range(5):
            self.display_array[x].close()
        self.selector.close()
        self.image = None

    def updator(self):
        self.rect.x = self.player.rect.x - 90
        self.rect.y = self.player.rect.y + 170
        temp = self.selector.moving(self)
        for x in range(5):
            self.display_array[x].reset(self.player.inventory.inventory[4][x].item_data.item_name,self.player.inventory.inventory[4][x].count,(self.rect.x + x * 36 + 5,self.rect.y+5))

        if self.player.hand != temp:
            self.player.hand = temp
            self.player.inventory.apply_modifiers()
            self.player.attack_c = 0.0

    def open_hotbar(self,game):
        if self.selector != None:
            self.selector.delete()
        self.selector = hotbar_selector((self.rect.x, self.rect.y), game, 0, self.player)
        self.path = 'assets/gui/hotbar'
        self.image = default.load_image(self.path)
        self.rect = self.image.get_rect(topleft=(game.player.rect.x - 90, game.player.rect.y + 170))


    def close_hotbar(self):
        self.path = 'assets/gui/None'
        self.image = default.load_image(self.path)
        for x in range(5):
            self.display_array[x].reset(None,0,(9999999,9999999))
        self.selector.delete()
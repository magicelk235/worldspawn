import sys,random,pygame,os,items,entities,objects,math,gif_pygame,projectiles,pickle,struct,copy,gif_pygame,zlib,cv2,numpy,socket,particles
from heapq import heappush, heappop

import modifiers


class rect:
    def __init__(self, rect, dimension):
        self.rect = rect
        self.dimension = dimension

    def colliderect(self,other):
        if self.rect.colliderect(other) and other.dimension == self.dimension:
            return True
        return False
    def collidepoint(self,x,y,dimension):
        if self.rect.collidepoint(x,y) and dimension == self.dimension:
            return True
        return False


class image:
    def __init__(self,path):
        self.path = path
        self.image = None
        self.is_gif = False
        self.size = None
        self.flip_x = False
        self.flip_y = False
        self.color = (255,255,255)
        self.angle = 0
        self.load_image()


    def load_image(self):

        if os.path.exists(resource_path(f"{self.path}.png")):
            self.is_gif = False
            self.image = pygame.image.load(resource_path(f"{self.path}.png")).convert_alpha()
        else:
            self.is_gif = True
            self.image = gif_pygame.load(resource_path(resource_path(f"{self.path}.gif")))
        self.size = self.image.get_size()

    def replace_path(self,path):
        self.path = path
        self.load_image()

    def save(self):
        self.image = None

    def display_image(self, floor, pos):
        try:
            floor.blit(self.image.blit_ready(), pos)
        except:
            floor.blit(self.image, pos)

    def to_dict(self):
        return {
            "path":self.path,
            "size":self.size,
            "angle":self.angle,
            "flip_x":self.flip_x,
            "flip_y":self.flip_y,
            "color":self.color,
        }

    def from_dict(self,image_dict):
        self.path = image_dict["path"]
        self.size = image_dict["size"]
        self.angle = image_dict["angle"]
        self.color = image_dict["color"]
        self.flip(image_dict["flip_x"],image_dict["flip_y"])
        self.rotate(self.angle)




    def cut_image(self, w, h):
        rect = pygame.Rect(0, 0, w, h)
        if self.is_gif:
            for frame in self.image.frames:
                frame[0] = frame[0].subsurface(rect)
        else:
            self.image = self.image.subsurface(rect)
        self.size = self.image.get_size()


    def color_image(self, color):
        if self.is_gif:
            for frame in self.image.frames:
                frame[0] = frame[0].convert_alpha()
                frame[0].fill(color, special_flags=pygame.BLEND_RGBA_MULT)
        else:
            self.image.fill(color, special_flags=pygame.BLEND_RGBA_MULT)
        self.color = color
        self.size = self.image.get_size()

    def flip(self, x=False, y=False):
        if self.is_gif:
            gif_pygame.transform.flip(self.image, x, y)
        else:
            self.image = pygame.transform.flip(self.image, x, y)
        if x:
            self.flip_x = not self.flip_x
        if y:
            self.flip_y = not self.flip_y
        self.size = self.image.get_size()

    def rotate(self, angle):
        if self.is_gif:
            gif_pygame.transform.rotate(self.image, angle)
        else:
            self.image = pygame.transform.rotate(self.image, angle)
        self.angle = angle
        self.size = self.image.get_size()

    def get_rect(self,pos,dimension):
        return rect(self.image.get_rect(topleft=pos),dimension)

def display_image(image,floor,pos):
    try:
        floor.blit(image, pos)
    except:
        floor.blit(image,pos)

def get_pressed_key_names(key_states):

    modifier_keys = {
        pygame.K_LSHIFT: "left shift",
        pygame.K_RSHIFT: "right shift",
        pygame.K_LCTRL: "left ctrl",
        pygame.K_RCTRL: "right ctrl",
        pygame.K_LALT: "left alt",
        pygame.K_RALT: "right alt",
    }
    key_names = []
    for index in range(len(key_states)):
        if key_states[index]:
            if index in modifier_keys:
                key_names.append(modifier_keys[index])
            else:
                key_names.append(pygame.key.name(index))
    mods = pygame.key.get_mods()
    if mods & pygame.KMOD_LSHIFT:
        if "left shift" not in key_names:
            key_names.append("left shift")
    if mods & pygame.KMOD_RSHIFT:
        if "right shift" not in key_names:
            key_names.append("right shift")
    if mods & pygame.KMOD_LCTRL:
        if "left ctrl" not in key_names:
            key_names.append("left ctrl")
    if mods & pygame.KMOD_RCTRL:
        if "right ctrl" not in key_names:
            key_names.append("right ctrl")
    if mods & pygame.KMOD_LALT:
        if "left alt" not in key_names:
            key_names.append("left alt")
    if mods & pygame.KMOD_RALT:
        if "right alt" not in key_names:
            key_names.append("right alt")
    return key_names

def serialize_pygame_inputs(pygame_events,keys,mouse_pos):
    events = []
    for event in pygame_events:
        event_dict = {
            'type': event.type,
            'dict': {k: v for k, v in event.__dict__.items() if isinstance(v, (int, str, float, bool))}
        }
        events.append(event_dict)

    key_states = get_pressed_key_names(keys)

    mouse_pos = list(mouse_pos)

    return [events, key_states, mouse_pos]

def send_msg(sock, msg):
    msg = pickle.dumps(msg)
    msg = struct.pack('>I', len(msg)) + msg
    sock.sendall(msg)

def recv_msg(sock):
    raw_msglen = recvall(sock, 4)
    if not raw_msglen:
        return None
    msglen = struct.unpack('>I', raw_msglen)[0]
    data = pickle.loads(recvall(sock, msglen))
    return data

def recvall(sock, n):
    data = bytearray()
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data.extend(packet)
    return data

def unserialize_pygame_inputs(serialized_inputs):

    events, key_states, mouse_pos = serialized_inputs
    reconstructed_events = []
    for event_info in events:
        pygame_event = pygame.event.Event(event_info['type'])
        for k, v in event_info['dict'].items():
            setattr(pygame_event, k, v)
        reconstructed_events.append(pygame_event)
    return [reconstructed_events, key_states, mouse_pos]

def from_bytes(image,size):
    try:
        return pygame.image.frombytes(image,size, "RGBA")
    except:
        try:
            for i in range(len(image.frames)):
                image.frames[i] = (
                pygame.image.frombytes(image.frames[i][0], size, "RGBA"), image.frames[i][1])
            for i in range(len(image.orig_frames)):
                image.orig_frames[i] = (
                pygame.image.frombytes(image.orig_frames[i][0], size, "RGBA"), image.frames[i][1])
            return image
        except:
            return pygame.image.load(resource_path("assets/gui/failed.png"))


def send_surface(conn, surface):
    """Send a Pygame Surface over a TCP socket using JPEG compression."""
    width, height = surface.get_size()

    # Convert Pygame surface to OpenCV format
    frame = pygame.surfarray.array3d(surface)
    frame = numpy.rot90(frame)  # Convert Pygame's format to OpenCV's

    # Encode as JPEG (quality=80 for speed + size balance)
    _, encoded_frame = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
    frame_bytes = encoded_frame.tobytes()

    # Pack width, height, and pixel data length
    header = struct.pack(">III", width, height, len(frame_bytes))
    conn.sendall(header)

    # Send entire frame
    conn.sendall(frame_bytes)


def recv_surface(sock):
    """Receive a Pygame Surface over a TCP socket using JPEG decoding."""
    try:
        # Receive width, height, and pixel data length (12 bytes)
        header = sock.recv(12)
        if not header:
            return None

        width, height, pixel_data_size = struct.unpack(">III", header)

        # Receive all pixel data
        pixel_data = b""
        while len(pixel_data) < pixel_data_size:
            chunk = sock.recv(pixel_data_size - len(pixel_data))
            if not chunk:
                raise ConnectionError("Connection lost while receiving image data.")
            pixel_data += chunk

        # Convert JPEG back to RGB
        jpg_frame = numpy.frombuffer(pixel_data, dtype=numpy.uint8)
        rgb_frame = cv2.imdecode(jpg_frame, cv2.IMREAD_COLOR)

        # Convert OpenCV image to Pygame surface
        surface = pygame.surfarray.make_surface(numpy.rot90(rgb_frame, k=3))  # Rotate back
        return surface

    except Exception as e:
        print("❌ Error receiving frame:", e)
        return None

def get_player(players,id):
    for player in players:
        if player.id == id:
            return player
    return None

def encrypt(ip):
    encrypted_ip = ""
    crypt_dic = {"0":"h","1":"g","2":"y","3":"a","4":"j","5":"m","6":"c","7":"t","8":"x","9":"s",".":"f"}
    for char in ip:
        encrypted_ip += crypt_dic[char]
    return encrypted_ip

def decrypt(ip):
    decrypted_ip = ""
    decrypt_dic = {'h': '0','g': '1','y': '2','a': '3','j': '4','m': '5','c': '6','t': '7','x': '8','s': '9','f': '.'}
    for char in ip:
        decrypted_ip += decrypt_dic[char]
    return decrypted_ip

def is_point_on_line(x0, y0, angle, x, y, tolerance=1e-6):

    # Convert angle to radians
    theta = math.radians(angle)
    
    # Line direction (dx, dy)
    dx = math.cos(theta)
    dy = -math.sin(theta)  # Minus because y decreases upward

    # Check if the point satisfies the parametric equations
    if dx != 0:  # Avoid division by zero
        t_x = (x - x0) / dx
    else:
        t_x = None  # Line is vertical

    if dy != 0:  # Avoid division by zero
        t_y = (y - y0) / dy
    else:
        t_y = None  # Line is horizontal

    # Compare t_x and t_y within the tolerance
    if t_x is not None and t_y is not None:
        return abs(t_x - t_y) < tolerance
    elif t_x is None:  # Vertical line
        return abs(x - x0) < tolerance
    elif t_y is None:  # Horizontal line
        return abs(y - y0) < tolerance
    return False

class need_item:
    def __init__(self,item_name,min_damage=1):
        self.item_name = item_name
        self.min_damage = min_damage

class summoner:
    def __init__(self,moblist,summon_cooldown,max,summon_count=1,range=40):
        self.moblist = moblist
        self.summon_cooldown = summon_cooldown
        self.max = max
        self.summon_count = summon_count
        self.range = range

    def spawn(self,amount,game,object):
        for i in range(amount):
            random_x = random.randint(object.rect.rect.x - self.range, object.rect.rect.x + self.range)
            random_y = random.randint(object.rect.rect.y - self.range, object.rect.rect.y + self.range)
            game.entities.append(entities.entity(game, get_entity(random.choice(self.moblist)), (random_x, random_y),object.rect.dimension,object.id))
            if object.attacker != None:
                game.entities[-1].attacker = object.attacker
        object.summon_c = 0

    def updator(self,game,object):
        if object.summon_c >= self.summon_cooldown and tag_counter(game.entities,object.id) < self.max:
            if tag_counter(game.entities,object.id) + self.summon_count > self.max:
                self.spawn(self.max - tag_counter(game.entities,object.id),game,object)
            else:
                self.spawn(self.summon_count,game,object)
        for event in game.event_list:
            if event.type == pygame.USEREVENT:
                object.summon_c += 1

class thrower:
    def __init__(self,projectile_list,projectile_cooldown,projectile_count=1,range=10):
        self.projectile_list = projectile_list
        self.projectile_cooldown = projectile_cooldown
        self.projectile_count = projectile_count
        self.range = range

    def spawn(self,amount,game,object):
        for i in range(amount):
            random_x = random.randint(object.rect.rect.x - self.range, object.rect.rect.x + self.range)
            random_y = random.randint(object.rect.rect.y - self.range, object.rect.rect.y + self.range)
            choicen_projectile = get_projectile(random.choice(self.projectile_list))

            if object.attacker != None and object.attacker.rect != None and abs(object.attacker.rect.rect.x-random_x) + abs(object.attacker.rect.rect.y-random_y) <= choicen_projectile.max_distance:
                game.projectiles.append(projectiles.projectile(game,object.rect.dimension, (random_x,random_y), object.attacker.rect.rect.center,choicen_projectile,object))
                object.projectile_c = 0

    def updator(self,game,object):
        if object.projectile_c >= self.projectile_cooldown:
            self.spawn(self.projectile_count,game,object)
        for event in game.event_list:
            if event.type == pygame.USEREVENT:
                object.projectile_c += 1

def calculate_path(start, end, blocks, width, height, max_steps=None,speed=20):

    def is_walkable(pos):
        x, y = pos
        object_rect = pygame.Rect(x, y, width, height)
        for sprite in blocks:
            if sprite.is_solid and object_rect.colliderect(sprite.rect_hitbox):
                return False
        return True

    def heuristic(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def adjust_position(pos, target):    
        x, y = pos
        tx, ty = target
        if abs(tx - x) < speed:
            x = tx
        if abs(ty - y) < speed:
            y = ty
        return x, y

    
    open_set = []
    heappush(open_set, (0, start))
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, end)}

    step_count = 0

    while open_set:
        if max_steps is not None and step_count >= max_steps:
            # Exceeded max steps, terminate and return empty path
            return False

        _, current = heappop(open_set)

        # If the goal is reached, reconstruct the path
        if current == end:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.reverse()
            return path

        # Explore neighboring positions
        neighbors = [
            adjust_position((current[0] + speed, current[1]), end),  # Right
            adjust_position((current[0] - speed, current[1]), end),  # Left
            adjust_position((current[0], current[1] + speed), end),  # Down
            adjust_position((current[0], current[1] - speed), end),  # Up
            adjust_position((current[0] - speed, current[1] - speed), end),  # up left
            adjust_position((current[0] - speed, current[1] + speed), end),  # down left
            adjust_position((current[0] + speed, current[1] - speed), end),  # up right
            adjust_position((current[0] + speed, current[1] + speed), end),  # down right
        ]

        for neighbor in neighbors:
            if not is_walkable(neighbor):
                continue

            # Calculate tentative g_score for the neighbor
            tentative_g_score = g_score[current] + speed

            if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = tentative_g_score + heuristic(neighbor, end)
                heappush(open_set, (f_score[neighbor], neighbor))

        step_count += 1

    # If no path is found, return an empty list
    return False

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

def has_one_tag(object1,object2):
    try:
        if object1.tag == object2.id != None:
            return True
    except:
        pass
    try:
        if object1.id == object2.tag != None:
            return True
    except:
        pass
    try:
        if object1.tag == object2.tag != None:
            return True
    except:
        pass
    return False

def collide(list,rect):
    for object in list:
        if object.rect.colliderect(rect):
            return True
    return False

def tag_counter(list,tag):
    count = 0
    for object in list:
        if object.tag == tag:
            count += 1
    return count

def tag_list(list,tag):
    list_tag = []
    for object in list:

        if tag != None and object.tag == tag or object.id == tag:
            list_tag.append(object)
    return list_tag

def double_tag_list(list,tag1,tag2):
    list1 = tag_list(list,tag1)
    list2 = tag_list(list,tag2)
    return list1 + list2

class hitbox:
    def __init__(self,hitbox_x,hitbox_y,offset_x=0,offset_y=0):
        self.hitbox_x = hitbox_x
        self.hitbox_y = hitbox_y
        self.offset_x = offset_x
        self.offset_y = offset_y

def set_attr(obj, attr_path, value):
    attributes = attr_path.split(".")
    for attr in attributes[:-1]:
        obj = getattr(obj, attr)
    setattr(obj, attributes[-1], value)

def get_attr(obj, attr_path):
    attributes = attr_path.split(".")
    for attr in attributes:  # Navigate through the path
        obj = getattr(obj, attr)
    return obj

def projectile_item_template(names,amount,needed_items,needed_item_amount):
    code = f"""
    import sys,random,pygame,os,items,entities,objects,math,gif_pygame,default,projectiles
    names = {names}
    amount = {amount}
    needed_items = {needed_items}
    needed_item_amount = {needed_item_amount}
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
        if not self.gui_open and self.attack_c == self.attack_cooldown:
            n = 0
            for name in needed_items:
                item = self.inventory.get_item(name)
                if item != None:
                    for i in range(amount):
                        random_aim = random.choice([self.block_selector.rect.rect.center,self.block_selector.rect.rect.topleft,self.block_selector.rect.rect.topright,self.block_selector.rect.rect.bottomleft,self.block_selector.rect.rect.bottomright])
                        game.projectiles.append(projectiles.projectile(game,self.rect.dimension, self.rect.rect.center, random_aim,default.get_projectile(names[n]), self))
                    self.attack_c = 0
                    item.count -= needed_item_amount
                    self.inventory.apply_modifiers()
                    break
                n += 1
    
    """
    return code

def object_item_template(name):
    code = f"""
    
    import sys,random,pygame,os,items,entities,objects,math,gif_pygame,default,projectiles
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
        same_pos = False
        item_object = default.get_object('{name}')
        for block in game.objects:
            if block.is_solid:
                if "border" in block.name and block.rect.colliderect(self.block_selector.rect):
                    same_pos = True
            if item_object.is_solid:
                if block.rect.rect.x == self.block_selector.x * 26 and block.rect.rect.y == self.block_selector.y * 20 and not block.data.floor:
                    same_pos = True
            elif block.rect.rect.x == self.block_selector.x * 26 and block.rect.rect.y == self.block_selector.y * 20 and (
                    not block.data.floor or (block.data.floor and item_object.floor)):
                same_pos = True
        if default.collide(game.entities, self.block_selector.rect):
            same_pos = True
        if not same_pos:
            game.objects.append(objects.object(game, (self.block_selector.x * 26, self.block_selector.y * 20),self.rect.dimension,item_object, self.id))
            self.hand.count -= 1
            self.inventory.apply_modifiers()
    
    """
    return code

def entity_item_template(name):
    code = f"""
    import sys,random,pygame,os,items,entities,objects,math,gif_pygame,default,projectiles
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
        if not default.collide(game.objects, self.block_selector.rect):
            game.entities.append(entities.entity(game, default.get_entity('{name}'),self.block_selector.rect.rect.center,self.rect.dimension, self.id))
            self.hand.count -= 1
            self.inventory.apply_modifiers()
        """
    return code

def food_item_template(health):
    code = f"""
    import sys,random,pygame,os,items,entities,objects,math,gif_pygame,default,projectiles
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3 and self.health != self.max_health:
        if {health} + self.health > self.max_health:
            self.hand.count -= 1
            self.inventory.apply_modifiers()
            self.health = self.max_health
        else:
            self.hand.count -= 1
            self.health += {health}
            self.inventory.apply_modifiers()
    
    """
    return code

def potion_cloud_template(modifier_cooldown, modifier_type, modifier_amount, modifier_set=True, modifier_percent=False,only_players=False):
    code = f"""
    import pygame,modifiers
    modifier = modifiers.modifier('{modifier_type}',{modifier_amount},{modifier_set},hand_needed=False,percent={modifier_percent})
    if not {only_players}:
        for entity in game.entities:
            if self.rect.colliderect(entity.rect):
                has_modifier = False
                for temp_modifier in entity.temporary_modifiers:
                    if temp_modifier.modifier == modifier:
                        has_modifier = True
                        break
                if not has_modifier:
                    entity.temporary_modifiers.append(modifiers.temporary_modifier(modifier, {modifier_cooldown}))
                    entity.apply_modifiers()
    for player in game.players:
        if self.rect.colliderect(player.rect):
            has_modifier = False
            for temp_modifier in player.temporary_modifiers:
                if temp_modifier.modifier == modifier:
                    has_modifier = True
                    break
            if not has_modifier:
                player.temporary_modifiers.append(modifiers.temporary_modifier(modifier, {modifier_cooldown}))
                player.inventory.apply_modifiers()
    """
    return code


def potion_item_template(color, cooldown,modifier_cooldown, modifier_type, modifier_amount, modifier_set=True, modifier_percent=False, only_players=False):

    code = f"""
    
    import sys, random, pygame, os, items, entities, objects, math, gif_pygame, default, modifiers,particles
    
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
        self.hand.count -= 1
        self.inventory.apply_modifiers()
        game.particles.append(particles.particle(particles.particle_data('potion_cloud',{cooldown},{color},default.potion_cloud_template({modifier_cooldown},'{modifier_type}',{modifier_amount},{modifier_set},{modifier_percent},{only_players})),self.rect.rect.topleft,self.rect.dimension,game))

        
    """
    return code


def event_item_template(name,set):
    code = f"""
    import sys, random, pygame, os, items, entities, objects, math, gif_pygame, default, projectiles
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
        for Event in game.events:
            if Event.data.name == '{name}':
                if Event.currently != {set}:
                    if {set}:
                        Event.start()
                    else:
                        Event.end()
                    break
            
    """
    return code
materials = []
entity_list = []
object_list = []
projectiles_list = []
def get_material(name):
    global materials
    if not materials:
        materials = {

        "stick":items.item_data("stick"),
        "stick1":items.item_data("stick1",
        event="""
        import pygame
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.dimension == "world":
                self.rect.dimension = "cave"
            else:
                self.rect.dimension = "world"            
        """),
        "crystal":items.item_data("crystal"),

        "golden_chain":items.item_data("golden_chain", 1, [modifiers.modifier("max_health", 14, True, False)]),
        "mega_shield":items.item_data("mega_shield", 1, [modifiers.modifier("speed", -1.0, set=True,choose_bigger=False,percent=True), modifiers.modifier("shield", 1.5, True)]),
        "magick_book":items.item_data("magic_book", 1, [modifiers.modifier("attack_cooldown", 1.3)], event=projectile_item_template(["soul"], 3, ["magic_book"], 0)),
        "scythe":items.item_data("scythe", 1, [modifiers.modifier("damage", 3)], tool_type="_sword_soul"),
        "wings":items.item_data("wings", 1, modifiers=[modifiers.modifier("speed", 3, False, False)]),
        "genie_lamp":items.item_data("genie_lamp", 1, event=entity_item_template("genie_friendly")),
        "trident":items.item_data("trident", 1, modifiers=[modifiers.modifier("damage", 3),modifiers.modifier("attack_cooldown", 0.5)], event=projectile_item_template(["trident"], 1, ["trident"], 1), tool_type="_sword"),

        "spawn_potion":items.item_data("spawn_potion", 32, [modifiers.modifier("rect.rect.topleft", (3001, 3008), True, True, True)]),
        "beer":items.item_data("beer", 32,event=food_item_template(2)),

        "health_potion":items.item_data("health_potion", 32,event=potion_item_template((255,139,208),6,60*5,"max_health",0.25,False,True)),
        "speed_potion":items.item_data("speed_potion", 32,event=potion_item_template((100,231,255),6,60*5,"speed",0.25,False,True)),
        "strength_potion":items.item_data("strength_potion", 32,event=potion_item_template((209,0,7),6,60*5,"damage",0.25,False,True)),

        "bush":items.item_data("bush"),

        "coal":items.item_data("coal"),
        "copper_raw":items.item_data("copper_raw"),
        "copper_bar":items.item_data("copper_bar"),
        "iron_raw":items.item_data("iron_raw"),
        "iron_bar":items.item_data("iron_bar"),
        "silver_raw":items.item_data("silver_raw"),
        "silver_bar":items.item_data("silver_bar"),
        "gold_raw":items.item_data("gold_raw"),
        "gold_bar":items.item_data("gold_bar"),

        "silk":items.item_data("silk"),
        "string":items.item_data("string"),

        "carrot":items.item_data("carrot", 32,event=food_item_template(2)),
        "pumpkin":items.item_data("pumpkin", 32,event=food_item_template(2)),
        "tomato":items.item_data("tomato", 32,event=food_item_template(2)),
        "potato":items.item_data("potato", 32,event=food_item_template(2)),
        "wheat":items.item_data("wheat"),
        "saddle":items.item_data("saddle"),

        "iron_horse":items.item_data("iron_horse", 1, event=entity_item_template('iron_horse')),
        "phoenix_egg":items.item_data("phoenix_egg", 1),

        "carrot_seeds":items.item_data("carrot_seeds", event=object_item_template("carrot")),
        "pumpkin_seeds":items.item_data("pumpkin_seeds", event=object_item_template("pumpkin")),
        "tomato_seeds":items.item_data("tomato_seeds", event=object_item_template("tomato")),
        "potato_seeds":items.item_data("potato_seeds", event=object_item_template("potato")),
        "wheat_seeds":items.item_data("wheat_seeds", event=object_item_template("wheat")),

        "sheep_raw":items.item_data("sheep_raw", 32,event=food_item_template(1)),
        "cow_raw":items.item_data("cow_raw", 32, event=food_item_template(1)),
        "chick_raw":items.item_data("chick_raw", 32, event=food_item_template(1)),
        "pig_raw":items.item_data("pig_raw", 32, event=food_item_template(1)),
        "sheep_cooked":items.item_data("sheep_cooked", 32, event=food_item_template(2)),
        "cow_cooked":items.item_data("cow_cooked", 32, event=food_item_template(4)),
        "chick_cooked":items.item_data("chick_cooked", 32, event=food_item_template(2)),
        "pig_cooked":items.item_data("pig_cooked", 32, event=food_item_template(3)),
        "bread":items.item_data("bread", 32, event=food_item_template(3)),
        "apple":items.item_data("apple", 32, event=food_item_template(2)),

        "wooden_sword":items.item_data("wooden_sword", 1, tool_type="_sword"),
        "wooden_pickaxe":items.item_data("wooden_pickaxe", 1, tool_type="_pickaxe"),
        "wooden_axe":items.item_data("wooden_axe", 1, tool_type="_axe"),
        "wooden_hoe":items.item_data("wooden_hoe", 1, tool_type="_hoe"),
        "wooden_chestplate":items.item_data("wooden_chestplate", 1, [modifiers.modifier("shield", 0.05, True, False)]),
        "wooden_dagger":items.item_data("wooden_dagger", 1, [modifiers.modifier("damage", 2),
                                             modifiers.modifier("attack_cooldown", 0.3),
                                             modifiers.modifier("range", 0.3)], tool_type="_sword"),
        "wooden_spear":items.item_data("wooden_spear", 1, [modifiers.modifier("damage", 1),
                                            modifiers.modifier("attack_cooldown", 0.6),
                                            modifiers.modifier("range", 2)], tool_type="_sword"),

        "wooden_hammer":items.item_data("wooden_hammer", 1, [modifiers.modifier("damage", 3),
                                             modifiers.modifier("attack_cooldown", 1.0)], tool_type="_sword"),


        "copper_sword":items.item_data("copper_sword", 1, [modifiers.modifier("damage", 2),
                                            modifiers.modifier("attack_cooldown", 0.5)], tool_type="_sword"),
        "copper_pickaxe":items.item_data("copper_pickaxe", 1, [modifiers.modifier("damage", 2),
                                              modifiers.modifier("attack_cooldown", 0.5)], tool_type="_pickaxe"),
        "copper_axe":items.item_data("copper_axe", 1, [modifiers.modifier("damage", 2),
                                          modifiers.modifier("attack_cooldown", 0.5)], tool_type="_axe"),
        "copper_hoe":items.item_data("copper_hoe", 1, [modifiers.modifier("damage", 2),
                                          modifiers.modifier("attack_cooldown", 0.5)], tool_type="_hoe"),
        "copper_chestplate":items.item_data("copper_chestplate", 1, [modifiers.modifier("shield", 0.1, True, False)]),
        "copper_dagger":items.item_data("copper_dagger", 1, [modifiers.modifier("damage", 3),
                                             modifiers.modifier("attack_cooldown", 0.3),
                                             modifiers.modifier("range", 0.3)], tool_type="_sword"),
        "copper_spear":items.item_data("copper_spear", 1, [modifiers.modifier("damage", 2),
                                            modifiers.modifier("attack_cooldown", 0.6),
                                            modifiers.modifier("range", 2)], tool_type="_sword"),
        "copper_hammer":items.item_data("copper_hammer", 1, [modifiers.modifier("damage", 4),
                                             modifiers.modifier("attack_cooldown", 1.0)], tool_type="_sword"),

        "iron_sword":items.item_data("iron_sword", 1, [modifiers.modifier("damage", 3),
                                          modifiers.modifier("attack_cooldown", 0.5)], tool_type="_sword"),
        "iron_pickaxe":items.item_data("iron_pickaxe", 1, [modifiers.modifier("damage", 3),
                                            modifiers.modifier("attack_cooldown", 0.5)], tool_type="_pickaxe"),
        "iron_axe":items.item_data("iron_axe", 1, [modifiers.modifier("damage", 3),
                                        modifiers.modifier("attack_cooldown", 0.5)], tool_type="_axe"),
        "iron_hoe":items.item_data("iron_hoe", 1, [modifiers.modifier("damage", 3),
                                        modifiers.modifier("attack_cooldown", 0.5)], tool_type="_hoe"),
        "iron_chestplate":items.item_data("iron_chestplate", 1, [modifiers.modifier("shield", 0.15, True, False)]),
        "iron_dagger":items.item_data("iron_dagger", 1, [modifiers.modifier("damage", 4),
                                           modifiers.modifier("attack_cooldown", 0.3),
                                           modifiers.modifier("range", 0.3)], tool_type="_sword"),
        "iron_spear":items.item_data("iron_spear", 1, [modifiers.modifier("damage", 3),
                                          modifiers.modifier("attack_cooldown", 0.6),
                                          modifiers.modifier("range", 2)], tool_type="_sword"),
        "iron_hammer":items.item_data("iron_hammer", 1, [modifiers.modifier("damage", 5),
                                           modifiers.modifier("attack_cooldown", 1.0)], tool_type="_sword"),

        "silver_sword":items.item_data("silver_sword", 1, [modifiers.modifier("damage", 4),
                                            modifiers.modifier("attack_cooldown", 0.5)], tool_type="_sword"),
        "silver_pickaxe":items.item_data("silver_pickaxe", 1, [modifiers.modifier("damage", 4),
                                              modifiers.modifier("attack_cooldown", 0.5)], tool_type="_pickaxe"),
        "silver_axe":items.item_data("silver_axe", 1, [modifiers.modifier("damage", 4),
                                          modifiers.modifier("attack_cooldown", 0.5)], tool_type="_axe"),
        "silver_hoe":items.item_data("silver_hoe", 1, [modifiers.modifier("damage", 4),
                                          modifiers.modifier("attack_cooldown", 0.5)], tool_type="_hoe"),
        "silver_chestplate":items.item_data("silver_chestplate", 1, [modifiers.modifier("shield", 0.2, True, False)]),
        "silver_dagger":items.item_data("silver_dagger", 1, [modifiers.modifier("damage", 5),
                                             modifiers.modifier("attack_cooldown", 0.3),
                                             modifiers.modifier("range", 0.3)], tool_type="_sword"),
        "silver_spear":items.item_data("silver_spear", 1, [modifiers.modifier("damage", 4),
                                            modifiers.modifier("attack_cooldown", 0.6),
                                            modifiers.modifier("range", 2)], tool_type="_sword"),
        "silver_hammer":items.item_data("silver_hammer", 1, [modifiers.modifier("damage", 6),
                                             modifiers.modifier("attack_cooldown", 1.0)], tool_type="_sword"),

        "gold_sword":items.item_data("gold_sword", 1, [modifiers.modifier("damage", 5),
                                          modifiers.modifier("attack_cooldown", 0.5)], tool_type="_sword"),
        "gold_pickaxe":items.item_data("gold_pickaxe", 1, [modifiers.modifier("damage", 5),
                                            modifiers.modifier("attack_cooldown", 0.5)], tool_type="_pickaxe"),
        "gold_axe":items.item_data("gold_axe", 1, [modifiers.modifier("damage", 5),
                                        modifiers.modifier("attack_cooldown", 0.5)], tool_type="_axe"),
        "gold_hoe":items.item_data("gold_hoe", 1, [modifiers.modifier("damage", 5),
                                        modifiers.modifier("attack_cooldown", 0.5)], tool_type="_hoe"),
        "gold_chestplate":items.item_data("gold_chestplate", 1, [modifiers.modifier("shield", 0.25, True, False)]),
        "gold_dagger":items.item_data("gold_dagger", 1, [modifiers.modifier("damage", 6),
                                           modifiers.modifier("attack_cooldown", 0.3),
                                           modifiers.modifier("range", 0.3)], tool_type="_sword"),
        "gold_spear":items.item_data("gold_spear", 1, [modifiers.modifier("damage", 5),
                                          modifiers.modifier("attack_cooldown", 0.6),
                                          modifiers.modifier("range", 2)], tool_type="_sword"),
        "gold_hammer":items.item_data("gold_hammer", 1, [modifiers.modifier("damage", 7),
                                           modifiers.modifier("attack_cooldown", 1.0)], tool_type="_sword"),

        "phoenix_feather":items.item_data("phoenix_feather", 1,
                        [modifiers.modifier("damage", 20, hand_needed=False), modifiers.modifier("speed", 2, False)],
                        tool_type="_hoe_pickaxe_axe_sword"),

        "shield":items.item_data("shield", 1, [modifiers.modifier("speed", -1, False, choose_bigger=False), modifiers.modifier("shield", 0.40, True)]),

        "fire":items.item_data("fire", 32),
        "fire_wand":items.item_data("fire_wand",event=projectile_item_template(["fire"],1,["fire"],1)),

        "arrow":items.item_data("arrow", 32),
        "bow":items.item_data("bow", 1,event=projectile_item_template(["arrow"],1,["arrow"],1)),


        "rock":items.item_data("rock"),
        "door":items.item_data("door", 32,event=object_item_template("door")),
        "sapling_cherry":items.item_data("sapling_cherry", 32,event=object_item_template("tree_cherry")),
        "sapling_oak":items.item_data("sapling_oak", 32, event=object_item_template("tree_oak")),
        "sapling_spruce":items.item_data("sapling_spruce", 32, event=object_item_template("tree_spruce")),
        "wood":items.item_data("wood"),
        "work_bench":items.item_data("work_bench", 1, event=object_item_template("work_bench")),
        "oven":items.item_data("oven", 1, event=object_item_template("oven")),
        "anvil":items.item_data("anvil", 1, event=object_item_template("anvil")),

        "pot":items.item_data("pot", event=object_item_template("pot")),

        "soul":items.item_data("soul"),
        "energy1":items.item_data("energy1"),
        "energy2":items.item_data("energy2"),
        "energy3":items.item_data("energy3"),
        "energy4":items.item_data("energy4"),

        "flower_red":items.item_data("flower_red", color=(255, 0, 0),event=object_item_template("flower_red")),
        "flower_green":items.item_data("flower_green", color=(0, 255, 0),event=object_item_template("flower_green")),
        "flower_blue":items.item_data("flower_blue", color=(0, 0, 255),event=object_item_template("flower_blue")),
        "flower_white":items.item_data("flower_white", color=(255, 255, 255),event=object_item_template("flower_white")),
        "flower_black":items.item_data("flower_black", color=(0, 0, 0),event=object_item_template("flower_black")),

        "totem":items.item_data("totem", 1),
        "heart":items.item_data("heart", 1),
        "None":items.item_data(None),

        "wood_cube":items.item_data("wood_cube", event=object_item_template("wood_cube")),
        "cauldron":items.item_data("cauldron", event=object_item_template("cauldron")),
        "rock_cube":items.item_data("rock_cube", event=object_item_template("rock_cube")),
        "magic_lantern":items.item_data("magic_lantern", event=object_item_template("magic_lantern")),
        "wooden_floor":items.item_data("wooden_floor", event=object_item_template("wooden_floor")),
        "rock_floor":items.item_data("rock_floor", event=object_item_template("rock_floor")),

        }
    return copy.deepcopy(materials.get(str(name),None))

def get_entity(name):
    global entity_list
    if not entity_list:
        entity_list = {

        "goat":entities.entity_data("goat", 16,
                             [items.lootable(get_material("sheep_raw"), 2), items.lootable(get_material("silk"), 1)],
                             "N", 1, 5, breed=entities.breed("apple"), ride_data=entities.ride()),
        "cow":entities.entity_data("cow", 16, items.lootable(get_material("cow_raw"), 2), breed=entities.breed("carrot")),
        "pig":entities.entity_data("pig", 10, items.lootable(get_material("pig_raw"), 2),breed=entities.breed("potato", amount=2)),
        "dog":entities.entity_data("dog", 20, items.lootable(get_material("sheep_raw"), 2),"N",breed=entities.breed("cow_raw"),tame=entities.tame("stick",1)),
        "sheep":entities.entity_data("sheep", 10,
                             [items.lootable(get_material("sheep_raw"), 2), items.lootable(get_material("silk"), 1)],
                             breed=entities.breed("pumpkin")),
        "chicken":entities.entity_data("chicken", 6, items.lootable(get_material("chick_raw"), 2),
                             breed=entities.breed("potato_seeds")),
        "duck":entities.entity_data("duck", 6, items.lootable(get_material("chick_raw"), 2),
                             breed=entities.breed("carrot_seeds")),
        "deer":entities.entity_data("deer", 16, items.lootable(get_material("cow_raw"), 2), "N", 2, 5,
                             breed=entities.breed("tomato"), ride_data=entities.ride()),
        "horse":entities.entity_data("horse", 16, items.lootable(get_material("cow_raw"), 2), speed=5,
                             breed=entities.breed("wheat"), ride_data=entities.ride()),
        "wolf":entities.entity_data("wolf", 14, items.lootable(get_material("cow_raw"), 2), "N", attack_damage=2,
                             attack_cooldown=3, speed=3, breed=entities.breed("cow_raw"), ride_data=entities.ride()),
        "lion":entities.entity_data("lion", 16, items.lootable(get_material("sheep_raw"), 2), "N", attack_damage=2,
                             attack_cooldown=3, speed=4, breed=entities.breed("sheep_raw"), ride_data=entities.ride()),



        "iron_horse":entities.entity_data("iron_horse", 1, items.lootable(get_material("iron_horse")), mob_type="L", speed=6,
                             ride_data=entities.ride(None),attack_damage=3, attack_cooldown=2),

        "zombie":entities.entity_data("zombie", 10, items.lootable(get_material("coal"), 2, 0.75), "H", 1, 3, 60),
        "skeleton":entities.entity_data("skeleton", 8, items.lootable(get_material("coal")), "H", 1, 2, 60, speed=3),
        "skeleton_bow":entities.entity_data("skeleton_bow", 8, items.lootable(get_material("bow")), "H", 1, 2, 60, speed=2,
                             thrower=thrower(["arrow"],3,1)),
        "caveman":entities.entity_data("caveman", 8, items.lootable(get_material("iron_raw")), "H", 2, 3, 60, speed=2,
                             thrower=thrower(["bone"], 4)),
        "stone_golem":entities.entity_data("stone_golem", 20, items.lootable(get_material("rock")), "H", 3, 4, 60, speed=2,
                             thrower=thrower(["rock"],5)),


        "troll":entities.entity_data("troll", 16, [items.lootable(get_material("gold_raw"), 1, 0.25),
                                           items.lootable(get_material("silver_raw"), 1, 0.25),
                                           items.lootable(get_material("iron_raw"), 1, 0.25)], "H", 2, 5, 60),

        "ogre":entities.entity_data("ogre", 18, items.lootable(get_material("pig_raw"), 5), "H", 3, 8, 60),
        "fungal":entities.entity_data("fungal", 6, None, "H", 1, 1, 60, speed=4),
        "cyclops":entities.entity_data("cyclops", 16, None, "H", 3, 8, 60),
        "knight":entities.entity_data("knight", 16, [items.lootable(get_material("copper_sword"), 1, 0.25),
                                            items.lootable(get_material("iron_chestplate"), 1, 0.15)], "N", 1, 2,
                             shield=0.3),
        "brave_knight":entities.entity_data("brave_knight", 16, [items.lootable(get_material("silver_sword"), 1, 0.25),
                                                  items.lootable(get_material("shield"), 1, 0.25)], "N", 2, 3,
                             shield=0.35),
        "knight_spear":entities.entity_data("knight_spear", 16, items.lootable(get_material("silver_spear"), 1, 0.15), "N", 3, 2,
                             shield=0.2),
        "ghost":entities.entity_data("ghost", 8, [items.lootable(get_material("crystal"), 2, 0.50),
                                          items.lootable(get_material("iron_sword"), 1, 0.25)], "N", 2, 2, -1, 2,
                             speed=3, trade_list=None, ignore_solid=True),
        "angle":entities.entity_data("angle", 8, [items.lootable(get_material("crystal"), 2, 0.50),
                                          items.lootable(get_material("iron_sword"), 1, 0.25)], "N", 2, 2, -1, 2,
                             speed=3, trade_list=None, ignore_solid=True),
        "mummy":entities.entity_data("mummy", 12, items.lootable(get_material("gold_raw"), 2, 0.50), "N", 1, 2),

        "sand_golem":entities.entity_data("sand_golem", 16, items.lootable(get_material("gold_raw"), 3, 0.75), "N", 3, 4, -1, 0,
                             speed=1,
                             trade_list=None, thrower=thrower(["sandball"],5,2), ignore_solid=False),
        "swordman":entities.entity_data("swordman", 14, items.lootable(get_material("iron_sword"), 1, 0.75), "N", 1, 2),
        "lumberjack":entities.entity_data("lumberjack", 14, items.lootable(get_material("iron_axe"), 1, 0.75), "N", 3, 4),
        "farmer":entities.entity_data("farmer", 10, items.lootable(get_material("iron_axe"), 1, 0.75), "N", 2, 3, -1,
                             trade_list=[recipe(items.inventory_item(get_material("bread"), 5),items.inventory_item(get_material("crystal"), 3)),recipe(items.inventory_item(get_material("crystal"), 5), items.inventory_item(get_material(random.choice(["carrot", "pumpkin", "potato", "tomato"])),10))], ignore_solid=False),
        "blacksmith":entities.entity_data("blacksmith", 10, items.lootable(get_material("iron_hammer"), 1, 0.75), "N", 1, 2, -1,
                             trade_list=[recipe(items.inventory_item(get_material("silver_sword"), 1),
                                                items.inventory_item(get_material("crystal"), 5))], ignore_solid=False),
        "miner":entities.entity_data("miner", 10, items.lootable(get_material("iron_pickaxe"), 1, 0.75), "N", 2, 4, -1,
                             trade_list=[recipe(items.inventory_item(get_material("coal"), 2),
                                                items.inventory_item(get_material("crystal"), 3))], ignore_solid=False),

        "drunk":entities.entity_data("drunk", 10, items.lootable(get_material("beer"), 3, 0.75), "N", 2, 4, -1,
                             trade_list=[recipe(items.inventory_item(get_material("beer"), 1),
                                                items.inventory_item(get_material("crystal"), 3))],thrower=thrower(["beer"],3)),

        "butcher":entities.entity_data("butcher", 10, items.lootable(get_material("pig_raw"), 2, 0.50), "N", 2, 4, -1, trade_list=[
            recipe(items.inventory_item(get_material("chick_cooked"), 2),
                   items.inventory_item(get_material("crystal"), 4))], ignore_solid=False),


        "phoenix":entities.entity_data("phoenix", 500, [items.lootable(get_material("phoenix_egg")),
                                              items.lootable(get_material("phoenix_feather"))], "H", 5, 3, -1,
                             vision=1000, speed=5, summoner=summoner(["fire_golem"], 10, 3),
                             thrower=thrower(["phoenix_spirit"],6), ignore_solid=False),

        "tornado":entities.entity_data("tornado", 16, None, "H", 2, 3, -1, speed=4, trade_list=None,
                             kill_spawn=entities.kill_spawn("tornado_mini", 2), ignore_solid=True),
        "tornado_mini":entities.entity_data("tornado_mini", 8, None, "H", 2, 3, -1, speed=6, trade_list=None, ignore_solid=True),
        "water_golem":entities.entity_data("water_golem", 16, None, "H", 3, 4, -1, speed=3, trade_list=None,
                             kill_spawn=entities.kill_spawn("water_golem_mini", 2), ignore_solid=False),
        "water_golem_mini":entities.entity_data("water_golem_mini", 8, None, "H", 2, 3, -1, speed=6, trade_list=None, ignore_solid=False),

        "fire_golem":entities.entity_data("fire_golem", 16, items.lootable(get_material("fire")), "H", 3, 4, -1, speed=4,
                             trade_list=None, kill_spawn=entities.kill_spawn("fire_golem_mini", 2), ignore_solid=False),
        "fire_golem_mini":entities.entity_data("fire_golem_mini", 8, items.lootable(get_material("fire")), "H", 2, 3, -1, speed=6,
                             trade_list=None, ignore_solid=False),

        "magic":entities.entity_data("magic", 1, None, "H", 1, 0, -1, -6, vision=1000, speed=6, trade_list=None, suicide=True,
                             ignore_solid=True),
        "posionball":entities.entity_data("poisonball", 1, None, "H", 1, 0, -1, -6, vision=1000, speed=6, trade_list=None,
                             suicide=True, ignore_solid=True),

        "automatic_bomb":entities.entity_data("automatic_bomb", 1, None, "H", 3, 0, -1, -6, vision=1000, speed=6, trade_list=None,
                             suicide=True, ignore_solid=True),
        "bat":entities.entity_data("bat", 5, None, "H", 1, 2, -1, speed=3, trade_list=None, ignore_solid=True),
        "witch":entities.entity_data("witch", 10, None, "H", 2, 4, -1, summoner=summoner(["bat"], 6, 2)),

        "demon":entities.entity_data("demon", 12, [items.lootable(get_material("gold_raw"), 2, chance=0.5),
                                           items.lootable(get_material("coal"), 2, chance=0.5)], "N", 1, 2, -1,
                             speed=3),
        "demon_big":entities.entity_data("demon_big", 16, [items.lootable(get_material("gold_raw"), 3, chance=0.7),
                                               items.lootable(get_material("coal"), 3, chance=0.7)], "N", 2, 3, -1,
                             speed=2),
        "demon_spider":entities.entity_data("demon_spider", 8, [items.lootable(get_material("gold_raw"), 1, chance=0.4),
                                                 items.lootable(get_material("coal"), 1, chance=0.4)], "N", 1, 1, -1,
                             speed=4),

        "goblin_witch":entities.entity_data("goblin_witch", 8, items.lootable(get_material("crystal")), "H", 1, 4, -1,
                             summoner=summoner(["poisonball"], 6, 2)),

        "goblin":entities.entity_data("goblin", 12, items.lootable(get_material("iron_sword"), chance=0.5), "H", 1, 1, -1,
                             speed=3),

        "goblin_spikeball":entities.entity_data("goblin_spikeball", 14, items.lootable(get_material("silver_sword"), chance=0.3), "H", 3,
                             2, -1, speed=2),

        "goblin_archer":entities.entity_data("goblin_archer", 8, items.lootable(get_material("bow"), chance=0.3), "H", 1, 3, -1,thrower=thrower(["arrow"], 4, 2)),

        "walrus_bubbles":entities.entity_data("walrus_bubbles", 12, items.lootable(get_material("crystal"),3, 0.5), "N", 1, 3, -1,thrower=thrower(["bubble"], 4, 2)),
        "walrus_spear":entities.entity_data("walrus_spear", 16, items.lootable(get_material("iron_spear"), chance=0.3), "N", 4, 2),

        "goblin_wolf_rider":entities.entity_data("goblin_wolf_rider", 12, items.lootable(get_material("silver_sword"), chance=0.5), "H", 3,
                             3, -1, speed=4, kill_spawn=entities.kill_spawn("wolf", 1)),

        "death":entities.entity_data("death", 100, items.lootable(get_material("scythe"), 1), "B", 8, 6, -1, 3, speed=4,
                             trade_list=None, summoner=summoner(["demon","demon_spider","demon_big"], 8, 4), ignore_solid=True),

        "golem":entities.entity_data("golem", 100, items.lootable(get_material("mega_shield"), 1), "B", 5, 4, -1, 0,speed=5,trade_list=None, summoner=summoner(["automatic_bomb"], 6, 2, 2)),

        "genie":entities.entity_data("genie", 100, [items.lootable(get_material("genie_lamp"), 1)], "B", 3, 2,speed=4,ignore_solid=True,thrower=thrower(["genie_knife"],3,2),summoner=summoner(["magic"],6,1)),
        "genie_friendly":entities.entity_data("genie_friendly", 10, [items.lootable(get_material("genie_lamp"), 1)], "L", 3, 2,speed=4,ignore_solid=True,thrower=thrower(["genie_knife"],3,2)),

        "mega_angle":entities.entity_data("mega_angle", 100, [items.lootable(get_material("wings"), 1)], "B", 5, 2,speed=6,thrower=thrower(["holy_spirit"],6,2)),

        "crusher":entities.entity_data("crusher", 100, [items.lootable(get_material("golden_chain"), 1)], "B", 5, 2,speed=6,thrower=thrower(["mega_hammer"],4)),

        "nebtune":entities.entity_data("nebtune", 100, [items.lootable(get_material("trident"), 1)], "B", 5, 2,speed=6,thrower=thrower(["nebtune_trident"],4)),

        "wizard":entities.entity_data("wizard", 100, items.lootable(get_material("magic_book")), "B", 3, 2, -1, trade_list=[recipe(items.inventory_item(get_material("spawn_potion"), 2),items.inventory_item(get_material("crystal"), 6))], summoner=summoner(["magic"], 3, 2),thrower=thrower(["crystal"],4,2),ignore_solid=False,speed=5),
        }
    return entity_list.get(name,None)

def get_object(name):
    global work_bench_recipes,oven_recipes,anvil_recipes,cauldron_recipes,object_list
    if not object_list:
        work_bench_recipes = [
        recipe(items.inventory_item("stick", 4), [items.inventory_item("wood", 2)]),
        recipe(items.inventory_item("door", 1), [items.inventory_item("wood")]),
        recipe(items.inventory_item("work_bench", 1), [items.inventory_item("wood", 8)]),

        recipe(items.inventory_item("pot", 1), [items.inventory_item("rock", 4)]),

        recipe(items.inventory_item("saddle", 1), [items.inventory_item("wood", 2), items.inventory_item("string", 1)]),

        recipe(items.inventory_item("shield", 1),
               [items.inventory_item("wood", 8), items.inventory_item("silver_bar", 8)]),

        recipe(items.inventory_item("wooden_pickaxe", 1),
               [items.inventory_item("stick", 2), items.inventory_item("wood", 3)]),
        recipe(items.inventory_item("wooden_axe", 1),
               [items.inventory_item("stick", 2), items.inventory_item("wood", 3)]),
        recipe(items.inventory_item("wooden_hoe", 1),
               [items.inventory_item("stick", 2), items.inventory_item("wood", 2)]),
        recipe(items.inventory_item("wooden_sword", 1),
               [items.inventory_item("stick", 2), items.inventory_item("wood", 2)]),
        recipe(items.inventory_item("wooden_dagger", 1),
               [items.inventory_item("stick", 1), items.inventory_item("wood", 2)]),
        recipe(items.inventory_item("wooden_spear", 1),
               [items.inventory_item("stick", 3), items.inventory_item("wood", 2)]),
        recipe(items.inventory_item("wooden_hammer", 1),
               [items.inventory_item("stick", 2), items.inventory_item("wood", 5)]),

        recipe(items.inventory_item("wooden_chestplate", 1), [items.inventory_item("wood", 6)]),

        recipe(items.inventory_item("wooden_floor", 4), [items.inventory_item("wood", 4)]),
        recipe(items.inventory_item("rock_floor", 4), [items.inventory_item("rock", 4)]),

        recipe(items.inventory_item("oven", 1), [items.inventory_item("rock", 8),items.inventory_item("coal", 4)]),
        recipe(items.inventory_item("string", 4), [items.inventory_item("silk", 1)]),
        recipe(items.inventory_item("anvil", 1),
               [items.inventory_item("copper_bar", 3), items.inventory_item("rock", 4)]),
        recipe(items.inventory_item("arrow", 3), [items.inventory_item("stick", 1), items.inventory_item("rock", 1)]),
        recipe(items.inventory_item("bow", 1), [items.inventory_item("stick", 3), items.inventory_item("string")]),



        recipe(items.inventory_item("fire_wand", 1),
               [items.inventory_item("fire", 10), items.inventory_item("soul", 5), items.inventory_item("crystal", 5)]),
        recipe(items.inventory_item("wood_cube", 4), [items.inventory_item("wood", 4)]),
        recipe(items.inventory_item("rock_cube", 4), [items.inventory_item("rock", 4)]),
        recipe(items.inventory_item("totem"), [items.inventory_item("soul"), items.inventory_item("crystal", 2)]),
        recipe(items.inventory_item("heart"), [items.inventory_item("soul", 5), items.inventory_item("crystal", 5)]),
        recipe(items.inventory_item("magic_lantern"), [items.inventory_item("soul", 2), items.inventory_item("rock", 5)]),
        recipe(items.inventory_item("iron_horse"),
               [items.inventory_item("soul", 1), items.inventory_item("crystal", 2),
                items.inventory_item("iron_bar", 16),
                items.inventory_item("gold_bar", 4)]),

        recipe(items.inventory_item("pumpkin_seeds", 2), [items.inventory_item("pumpkin", 1)]),
        recipe(items.inventory_item("potato_seeds", 2), [items.inventory_item("potato", 1)]),
        recipe(items.inventory_item("tomato_seeds", 2), [items.inventory_item("tomato", 1)]),
        recipe(items.inventory_item("carrot_seeds", 2), [items.inventory_item("carrot", 1)]),
        recipe(items.inventory_item("wheat_seeds", 2), [items.inventory_item("wheat", 1)]),

        recipe(items.inventory_item("bread", 3), [items.inventory_item("wheat", 3)]),

        recipe(items.inventory_item("energy1"),
               [items.inventory_item("pumpkin", 32), items.inventory_item("apple", 32),
                items.inventory_item("wheat", 32),
                items.inventory_item("carrot", 32), items.inventory_item("tomato", 32),
                items.inventory_item("potato", 32)]),
        recipe(items.inventory_item("energy2"),
               [items.inventory_item("copper_bar", 32), items.inventory_item("iron_bar", 32),
                items.inventory_item("silver_bar", 32), items.inventory_item("gold_bar", 32),
                items.inventory_item("crystal", 32), items.inventory_item("coal", 32)]),
        recipe(items.inventory_item("energy3"), [items.inventory_item("trident", 1),items.inventory_item("wings", 1),items.inventory_item("golden_chain", 1),items.inventory_item("scythe", 1),items.inventory_item("mega_shield", 1),items.inventory_item("magic_book", 1),items.inventory_item("genie_lamp", 1)]),
        recipe(items.inventory_item("energy4"),[items.inventory_item("soul", 32), items.inventory_item("soul", 32)])

    ]
        oven_recipes = [
        recipe(items.inventory_item("copper_bar", 2),
               [items.inventory_item("copper_raw", 2), items.inventory_item("coal", 1)]),
        recipe(items.inventory_item("gold_bar", 2),
               [items.inventory_item("gold_raw", 2), items.inventory_item("coal", 1)]),
        recipe(items.inventory_item("silver_bar", 2),
               [items.inventory_item("silver_raw", 2), items.inventory_item("coal", 1)]),
        recipe(items.inventory_item("iron_bar", 2),
               [items.inventory_item("iron_raw", 2), items.inventory_item("coal", 1)]),
        recipe(items.inventory_item("cow_cooked", 2),
               [items.inventory_item("cow_raw", 2), items.inventory_item("coal", 1)]),
        recipe(items.inventory_item("sheep_cooked", 2),
               [items.inventory_item("sheep_raw", 2), items.inventory_item("coal", 1)]),
        recipe(items.inventory_item("chick_cooked", 2),
               [items.inventory_item("chick_raw", 2), items.inventory_item("coal", 1)]),
        recipe(items.inventory_item("pig_cooked", 2),
               [items.inventory_item("pig_raw", 2), items.inventory_item("coal", 1)]),
        recipe(items.inventory_item("fire", 2), [items.inventory_item("bush", 1), items.inventory_item("coal", 1)]),
    ]
        anvil_recipes = [

        recipe(items.inventory_item("copper_pickaxe", 1),
               [items.inventory_item("stick", 2), items.inventory_item("copper_bar", 3),
                items.inventory_item("wooden_pickaxe")]),
        recipe(items.inventory_item("copper_axe", 1),
               [items.inventory_item("stick", 2), items.inventory_item("copper_bar", 3),
                items.inventory_item("wooden_axe")]),
        recipe(items.inventory_item("copper_hoe", 1),
               [items.inventory_item("stick", 2), items.inventory_item("copper_bar", 2),
                items.inventory_item("wooden_hoe")]),
        recipe(items.inventory_item("copper_sword", 1),
               [items.inventory_item("stick", 2), items.inventory_item("copper_bar", 2),
                items.inventory_item("wooden_sword")]),
        recipe(items.inventory_item("copper_dagger", 1),
               [items.inventory_item("stick", 1), items.inventory_item("copper_bar", 2),
                items.inventory_item("wooden_dagger")]),
        recipe(items.inventory_item("copper_spear", 1),
               [items.inventory_item("stick", 3), items.inventory_item("copper_bar", 2),
                items.inventory_item("wooden_spear")]),
        recipe(items.inventory_item("copper_hammer", 1),
               [items.inventory_item("stick", 2), items.inventory_item("copper_bar", 5),
                items.inventory_item("wooden_hammer")]),
        recipe(items.inventory_item("copper_chestplate", 1),
               [items.inventory_item("copper_bar", 6), items.inventory_item("wooden_chestplate")]),

        recipe(items.inventory_item("iron_pickaxe", 1),
               [items.inventory_item("stick", 2), items.inventory_item("iron_bar", 3),
                items.inventory_item("copper_pickaxe")]),
        recipe(items.inventory_item("iron_axe", 1),
               [items.inventory_item("stick", 2), items.inventory_item("iron_bar", 3),
                items.inventory_item("copper_axe")]),
        recipe(items.inventory_item("iron_hoe", 1),
               [items.inventory_item("stick", 2), items.inventory_item("iron_bar", 2),
                items.inventory_item("copper_hoe")]),
        recipe(items.inventory_item("iron_sword", 1),
               [items.inventory_item("stick", 2), items.inventory_item("iron_bar", 2),
                items.inventory_item("copper_sword")]),

        recipe(items.inventory_item("iron_dagger", 1),
               [items.inventory_item("stick", 1), items.inventory_item("iron_bar", 2),
                items.inventory_item("copper_dagger")]),
        recipe(items.inventory_item("iron_spear", 1),
               [items.inventory_item("stick", 3), items.inventory_item("iron_bar", 2),
                items.inventory_item("copper_spear")]),
        recipe(items.inventory_item("iron_hammer", 1),
               [items.inventory_item("stick", 2), items.inventory_item("iron_bar", 5),
                items.inventory_item("copper_hammer")]),

        recipe(items.inventory_item("iron_chestplate", 1),
               [items.inventory_item("iron_bar", 6), items.inventory_item("copper_chestplate")]),

        recipe(items.inventory_item("silver_pickaxe", 1),
               [items.inventory_item("stick", 2), items.inventory_item("silver_bar", 3),
                items.inventory_item("iron_pickaxe")]),
        recipe(items.inventory_item("silver_axe", 1),
               [items.inventory_item("stick", 2), items.inventory_item("silver_bar", 3),
                items.inventory_item("iron_axe")]),
        recipe(items.inventory_item("silver_hoe", 1),
               [items.inventory_item("stick", 2), items.inventory_item("silver_bar", 2),
                items.inventory_item("iron_hoe")]),
        recipe(items.inventory_item("silver_sword", 1),
               [items.inventory_item("stick", 2), items.inventory_item("silver_bar", 2),
                items.inventory_item("iron_sword")]),

        recipe(items.inventory_item("silver_dagger", 1),
               [items.inventory_item("stick", 1), items.inventory_item("silver_bar", 2),
                items.inventory_item("iron_dagger")]),
        recipe(items.inventory_item("silver_spear", 1),
               [items.inventory_item("stick", 3), items.inventory_item("silver_bar", 2),
                items.inventory_item("iron_spear")]),
        recipe(items.inventory_item("silver_hammer", 1),
               [items.inventory_item("stick", 2), items.inventory_item("silver_bar", 5),
                items.inventory_item("silver_hammer")]),

        recipe(items.inventory_item("silver_chestplate", 1),
               [items.inventory_item("silver_bar", 6), items.inventory_item("iron_chestplate")]),

        recipe(items.inventory_item("gold_pickaxe", 1),
               [items.inventory_item("stick", 2), items.inventory_item("gold_bar", 3),
                items.inventory_item("silver_pickaxe")]),
        recipe(items.inventory_item("gold_axe", 1),
               [items.inventory_item("stick", 2), items.inventory_item("gold_bar", 3),
                items.inventory_item("silver_axe")]),
        recipe(items.inventory_item("gold_hoe", 1),
               [items.inventory_item("stick", 2), items.inventory_item("gold_bar", 2),
                items.inventory_item("silver_hoe")]),
        recipe(items.inventory_item("gold_sword", 1),
               [items.inventory_item("stick", 2), items.inventory_item("gold_bar", 2),
                items.inventory_item("silver_sword")]),

        recipe(items.inventory_item("gold_dagger", 1),
               [items.inventory_item("stick", 1), items.inventory_item("gold_bar", 2),
                items.inventory_item("silver_dagger")]),
        recipe(items.inventory_item("gold_spear", 1),
               [items.inventory_item("stick", 3), items.inventory_item("gold_bar", 2),
                items.inventory_item("silver_spear")]),
        recipe(items.inventory_item("gold_hammer", 1),
               [items.inventory_item("stick", 2), items.inventory_item("gold_bar", 5),
                items.inventory_item("silver_hammer")]),

        recipe(items.inventory_item("gold_chestplate", 1),
               [items.inventory_item("gold_bar", 6), items.inventory_item("silver_chestplate")]),
    ]
        cauldron_recipes = [
        recipe(items.inventory_item("copper_pickaxe", 1),
               [items.inventory_item("stick", 2), items.inventory_item("copper_bar", 3),
                items.inventory_item("wooden_pickaxe")]),
    ]
        object_list = {
        "tomato":objects.object_data("tomato", items.lootable("tomato_seeds"), 3, need_item("hoe", 1), None, False, None,objects.plant(5, items.lootable("tomato",2), 50, 3)),
        "flower_red":objects.object_data("flower_red", None, 3, need_item("hoe", 1), None, False, None,objects.plant(3, items.lootable("flower_red",2), 50)),
        "flower_black":objects.object_data("flower_black", None, 3, need_item("hoe", 1), None, False, None,objects.plant(3, items.lootable("flower_black",2), 50)),
        "flower_white":objects.object_data("flower_white", None, 3, need_item("hoe", 1), None, False, None,objects.plant(3, items.lootable("flower_white",2), 50)),
        "flower_blue":objects.object_data("flower_blue", None, 3, need_item("hoe", 1), None, False, None,objects.plant(3, items.lootable("flower_blue",2), 50)),
        "flower_green":objects.object_data("flower_green", None, 3, need_item("hoe", 1), None, False, None,objects.plant(3, items.lootable("flower_green",2), 50)),
        "pumpkin":objects.object_data("pumpkin", items.lootable("pumpkin_seeds"), 3, need_item("hoe", 1), None, False, None,
                            objects.plant(4, items.lootable("pumpkin",2), 50, )),
        "potato":objects.object_data("potato", items.lootable("potato_seeds"), 3, need_item("hoe", 1), None, False, None,
                            objects.plant(4, items.lootable("potato",2), 50, )),
        "carrot":objects.object_data("carrot", items.lootable("carrot_seeds"), 3, need_item("hoe", 1), None, False, None,
                            objects.plant(4, items.lootable("carrot",2), 50, )),
        "wheat":objects.object_data("wheat", items.lootable("wheat_seeds"), 3, need_item("hoe", 1), None, False, None,
                            objects.plant(4, items.lootable("wheat",2), 50, )),

        "wooden_floor":objects.object_data("wooden_floor", items.lootable("wooden_floor"), 5, need_item("axe", 1), floor=True),
        "rock_floor":objects.object_data("rock_floor", items.lootable("rock_floor"), 5, need_item("pickaxe", 1), floor=True),

        "tree_cherry":objects.object_data("tree_cherry", items.lootable("sapling_cherry", 1), 3, need_item("axe", 1),plant_data=objects.plant(3,[items.lootable("wood", 4),items.lootable("sapling_cherry", 2, 0.75)],40)),
        "tree_oak":objects.object_data("tree_oak", [items.lootable("sapling_oak"), items.lootable("wood", 2)], 3,
                            need_item("axe", 1),
                            plant_data=objects.plant(4, [items.lootable("apple", 2), items.lootable("wood", 2),
                                                         items.lootable("sapling_oak", 2, 0.75)], 40, 3)),
        "tree_spruce":objects.object_data("tree_spruce", items.lootable("sapling_spruce"), 3, need_item("axe", 1),
                            plant_data=objects.plant(3,
                                                     [items.lootable("wood", 4),
                                                      items.lootable("sapling_spruce", 2, 0.75)],
                                                     40)),
        "twig":objects.object_data("twig", items.lootable("wood", 2), 2, None, type_range(1, 7)),
        "rock":objects.object_data("rock", items.lootable("rock", 2), 3, need_item("pickaxe", 1), type_range(1, 6)),
        "bush":objects.object_data("bush", items.lootable("bush"), 3, need_item("hoe", 1), type_range(1, 4)),

        "cave_rock":objects.object_data("cave_rock", items.lootable("rock", 2), 4, need_item("pickaxe", 1)),
        "copper_ore":objects.object_data("copper_ore", items.lootable("copper_raw", 2), 4, need_item("pickaxe", 1)),
        "coal_ore":objects.object_data("coal_ore", items.lootable("coal", 2), 4, need_item("pickaxe", 1)),
        "iron_ore":objects.object_data("iron_ore", items.lootable("iron_raw", 2), 4, need_item("pickaxe", 2)),
        "silver_ore":objects.object_data("silver_ore", items.lootable("silver_raw", 2), 4, need_item("pickaxe", 3)),
        "gold_ore":objects.object_data("gold_ore", items.lootable("gold_raw", 2), 4, need_item("pickaxe", 4)),
        "pot":objects.object_data("pot", items.lootable("pot", 1), 3, None, store=True),
        "crystal":objects.object_data("crystal", items.lootable("crystal", 2), 1, need_item("pickaxe", 2), type_range(1, 9)),
        "grass":objects.object_data("grass"),
        "cave_ground":objects.object_data("cave_ground"),
        "cave":objects.object_data("cave",portal_data=objects.portal("cave"),health=None),

        "rock_cube":objects.object_data("rock_cube", items.lootable("rock_cube"), 3, need_item("pickaxe", 1), None, True,
                            hitbox(24, 18, 4, 5), dyeable=True),
        "wood_cube":objects.object_data("wood_cube", items.lootable("wood_cube"), 1, need_item("axe", 1), None, True,
                            hitbox(24, 18, 4, 5), dyeable=True),
        "door":objects.object_data("door", items.lootable("door"), 1, need_item("axe", 1), None, True, hitbox(24, 18, 4, 5),
                            door=True, dyeable=True),
        "work_bench":objects.object_data("work_bench", items.lootable("work_bench"), 1, need_item("axe", 1), None, True,hitbox(24, 18, 4, 5), None, work_bench_recipes),
        "cauldron":objects.object_data("cauldron", items.lootable("cauldron"), 1, need_item("pickaxe", 1), None, recipe_list=cauldron_recipes),
        "oven":objects.object_data("oven", items.lootable("oven"), 3, need_item("pickaxe", 1), None, True,
                            hitbox(24, 18, 4, 5),
                            None, oven_recipes),
        "anvil":objects.object_data("anvil", items.lootable("anvil"), 5, need_item("pickaxe", 1), None, True,hitbox(24, 18, 4, 5),None, anvil_recipes),
        "magic_lantern":objects.object_data("magic_lantern", items.lootable("magic_lantern"), 5, need_item("pickaxe", 1), None, True,hitbox(24, 20, 4, 18),None, thrower=thrower(["soul"],3,1)),

        "spawn0":objects.object_data("spawn0", None, None,
                            recipe_list=[
                                recipe(items.inventory_item("work_bench"), [items.inventory_item("wood", 4)])],custom_code=f"""
import sys, random, pygame, os, items, entities, objects, math, gif_pygame, default, projectiles
if event.type == pygame.MOUSEBUTTONDOWN:
    if event.button == 3:
        if not player.gui_open:
            if self.rect.colliderect(player.block_selector.rect):
                if self.name == "spawn4":
                    game.entities.append(entities.entity(self.camera_group, get_entity("phoenix"), self.rect.center))
                    block.name = "spawn0"
                if "energy" in str(player.hand.item_data.item_name):
                    for i in range(1, 5):
                        if str(i) in str(player.hand.item_data.item_name) and str(i - 1) in self.name:
                            self.name = f"spawn"+str(i)
                            player.hand.count -= 1
"""),


        "lake":objects.object_data("lake", None, None, False, None, True),
        "cliff":objects.object_data("cliff", None, None, False, None, True),
        "cave_wall_x":objects.object_data("cave_wall_x", None, None, False, None, True),
        "cave_wall_y":objects.object_data("cave_wall_y", None, None, False, None, True),
        "mini_cliff":objects.object_data("mini_cliff", None, None, False, None, False),

        "sand_temple":objects.object_data("sand_temple", None, 50, need_item("pickaxe"),
                            summoner=summoner(["mummy", "genie", "sand_golem"], 10, 5)),
        "olympos":objects.object_data("olympos", None, 50, need_item("pickaxe"),
                            summoner=summoner(["angle", "ghost","mega_angle"], 10, 5)),
        "defence_tower":objects.object_data("defence_tower", None, 50, need_item("pickaxe"),
                            summoner=summoner(["lumberjack", "swordman","golem"], 10, 5),thrower=thrower(["arrow"],3)),
        "ruined_village":objects.object_data("ruined_village", None, 50, need_item("pickaxe"),
                            summoner=summoner(["blacksmith", "miner","drunk", "farmer", "wizard", "butcher"], 10, 6)),
        "knight_tower":objects.object_data("knight_tower", None, 50, need_item("pickaxe"),
                            summoner=summoner(["knight", "brave_knight", "knight_spear","crusher"], 10, 5)),
        "cursed_olympos":objects.object_data("cursed_olympos", None, 50, need_item("pickaxe"),
                            summoner=summoner(["death", "demon", "demon_big", "demon_spider"], 10, 5)),
        "ship":objects.object_data("ship", None, 50, need_item("pickaxe"),
                            summoner=summoner(["nebtune", "walrus_bubbles", "walrus_spear"], 10, 5)),
        }
    return copy.deepcopy(object_list.get(name,None))

def get_projectile(name):
    global projectiles_list
    if not projectiles_list:
        projectiles_list = {
        "arrow":projectiles.projectile_data("arrow", 400, 7, 2),
        "fire":projectiles.projectile_data("fire", 400, 8, 3),
        "soul":projectiles.projectile_data("soul", 400, 9, 2),
        "bone":projectiles.projectile_data("bone", 400, 6, 1),
        "beer":projectiles.projectile_data("beer", 400, 6, 2),
        "trident":projectiles.projectile_data("trident", 400, 20, 3,True),
        "nebtune_trident":projectiles.projectile_data("nebtune_trident", 400, 10, 4),
        "phoenix_spirit":projectiles.projectile_data("phoenix_spirit", 500, 9, 5),
        "sandball":projectiles.projectile_data("sandball", 300, 6, 2),
        "rock":projectiles.projectile_data("rock", 300, 6, 2),
        "bubble":projectiles.projectile_data("bubble", 300, 6, 2),
        "genie_knife":projectiles.projectile_data("genie_knife", 500, 6, 4),
        "crystal":projectiles.projectile_data("crystal", 500, 6, 4),
        "mega_hammer":projectiles.projectile_data("mega_hammer", 600, 8, 4),
        "holy_spirit":projectiles.projectile_data("holy_spirit", 600, 10, 2),
        }
    return projectiles_list.get(name,None)

def nearest(object,list):
    closest_object = None
    closest = 10000000000000000
    for item in list:
        if item != object:
            if closest > math.sqrt(2 ** (object.rect.rect.x - item.rect.rect.x) + (object.rect.rect.y - item.rect.rect.y) ** 2):
                closest = math.sqrt(2 ** (object.rect.rect.x - item.rect.rect.x) + (object.rect.rect.y - item.rect.rect.y) ** 2)
                closest_object = item
    return closest_object

def mix_colors(color1, color2, ratio=0.5):

    def hex_to_rgb(hex_color):
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def rgb_to_hex(rgb_color):
        return "#{:02x}{:02x}{:02x}".format(*rgb_color)

    # Convert colors to RGB if they are hex strings
    if isinstance(color1, str):
        color1 = hex_to_rgb(color1)
    if isinstance(color2, str):
        color2 = hex_to_rgb(color2)

    # Ensure ratio is within bounds
    ratio = max(0, min(ratio, 1))

    # Mix the colors
    mixed_color = tuple(
        round((1 - ratio) * c1 + ratio * c2) for c1, c2 in zip(color1, color2)
    )
    return mixed_color

def round_dec(dec,max_place=10):
    return int(dec*max_place)/max_place

class recipe:
    def __init__(self,result,items):
        try:
            items[-1]
            self.items = items

        except:
            self.items = [items]
        self.result = result

    def get_items_data(self):
        if type(self.result.item_data) is str:
            self.result.item_data = get_material(self.result.item_data)
        for item in self.items:
            if type(item.item_data) is str:
                item.item_data = get_material(item.item_data)

class trade:
    def __init__(self,main_item,result):
        self.main_item = main_item
        self.result = result
        
class type_range:
    def __init__(self, min_value, max_value):
        self.min_value = min_value
        self.max_value = max_value

def almost(location1,location2,step):
    if location2[0] - step > location1[0] or location1[0] > location2[0] - step:
        if location2[1] - step > location1[1] or location1[1] > location2[1] - step:
            return True
    return False
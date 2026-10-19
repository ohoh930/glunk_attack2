import pygame
import math
import random
import time
import asyncio

async def main():
    pygame.init()
    width = 800
    height = 800
    screen = pygame.display.set_mode((800, 800))
    clock = pygame.time.Clock()
    fontSettings = pygame.font.SysFont(None, 30)
    smallFontSettings = pygame.font.SysFont(None, 25)


    pygame.font.init()
    font = pygame.font.SysFont('arial', 30)


    running = True
    wave = 1
    wave_just_started = False
    on_wave_screen = True
    on_upgrade_screen = False
    shoot_waterdrop = False
    clicked_sword = False
    clicked_upgrade = False
    wave_text = "Click when your sword is on the enemy to kill them!"
    intro_text = "Click to start."
    clicked_pos = pygame.math.Vector2(0, 0)
    win = False
    ending_screen = False

    kills = 0
    state = "start"
    health = 5 #BRIANNA

    #PLAYER / UPGRADE STATS
    sword_length = 90
    max_health = 5
    unlocked_watergun = False
    maximum_ammo = 8

    healthBar_behind_rect = pygame.Rect(20, 20, 200, 25)



    #for the sprite sheet, this function extracts like each single of the image thing from the sheet
    #SAGE
    class SpriteSheet:
        def __init__(self, image):
            self.sheet = image
        def get_image(self, frame, width, height,scale, color):
                image = pygame.Surface((width, height)).convert_alpha()
                image.blit(self.sheet, (0,0), ((frame * width), 0, width, height))
                image = pygame.transform.scale(image, (width* scale, height*scale))
                image.set_colorkey(color)
                return image



    glook_sheet = SpriteSheet(pygame.image.load("assets/glook.png").convert_alpha())
    glunk1_sheet = SpriteSheet(pygame.image.load("assets/glunk1.png").convert_alpha())
    glunk2_sheet = SpriteSheet(pygame.image.load("assets/glunk2.png").convert_alpha())
    glunk3_sheet = SpriteSheet(pygame.image.load("assets/glunk3.png").convert_alpha())

    glook_sheet = SpriteSheet(pygame.image.load("assets/glook.png").convert_alpha())
    glunk1_sheet = SpriteSheet(pygame.image.load("assets/glunk1.png").convert_alpha())
    glunk2_sheet = SpriteSheet(pygame.image.load("assets/glunk2.png").convert_alpha())
    glunk3_sheet = SpriteSheet(pygame.image.load("assets/glunk3.png").convert_alpha())


    def frames_load(sheet, num, w, h, scale):
        frames = []
        for frame in range(num):
            image = sheet.get_image(frame, w, h, scale, (0,0,0))
            frames.append(image)
        return frames
    



    glook_frame = frames_load(glook_sheet, 6, 100,100, 1.3)
    glunk1_frame = frames_load(glunk1_sheet,3, 100, 100, 1)
    glunk2_frame = frames_load(glunk2_sheet, 5, 100, 100,1)
    glunk3_frame = frames_load(glunk3_sheet,3, 100,100,1.3)


    #glunk for each wave
    glunk_level_sprites = {
    1: glunk1_frame, 2: glunk2_frame, 3: glunk3_frame }


    #might need to transform it if its not fully 800x800

    background = pygame.image.load("assets/background.png").convert_alpha()
    background = pygame.transform.scale(background, (800,800))
    glook_ending = pygame.image.load("assets/glookending.png").convert_alpha()
    glook_ending = pygame.transform.scale(glook_ending, (800,800))
    glunk_ending = pygame.image.load("assets/glunkending.png").convert_alpha()
    glunk_ending  = pygame.transform.scale(glunk_ending , (800,800))


    #controls which animation frame is being shown
    frame_index =0
    #how fast we change frame
    animation_spd = 15
    #checks how many frame of sprite we went through, like this would change when u gone through them all
    time_glook = 0#SAGE

    class Glook:
        def __init__(self):
            self.rect = pygame.Rect(20, height/2, 20, 20)


    default_angle = pygame.math.Vector2(0, 360)
    def randomize_direction(x_low, x_high, y_low, y_high):
        forward = pygame.Vector2(
            math.cos(math.radians(random.randint(x_low, x_high))),
            math.sin(math.radians(random.randint(y_low, y_high)))
        )
        return forward


    def default_randomize_direction():
        forward = pygame.Vector2(
            math.cos(math.radians(random.randint(-360, 360))),
            math.sin(math.radians(random.randint(-360, 360)))
        )
        return forward


    # UPGRADE STUFF
    upgrade_background_rect = pygame.Rect(0, 0, 700, 700)
    upgrade_background_rect.center = (400, 400)

    # num is defined as the order it'll show up in the upgrade menu. NEVER DOUBLE UP
    class Upgrade:
        text = "template"

        def __init__(self, num, upgrade_num):
            self.pos = (0, 0)
            self.upgrade_num = upgrade_num
            match num:
                case 0:
                    pos = pygame.math.Vector2(100, 100)
                case 1:
                    pos = pygame.math.Vector2(100, 317)
                case 2:
                    pos = pygame.math.Vector2(100, 534)
            self.rect = pygame.Rect(pos.x, pos.y, 600, 167)
            match upgrade_num:
                case 0: 
                    self.text = "Increase max health by 5."
                case 1: 
                    self.text = "Increase sword length by 20."
                case 2:
                    self.text = "Unlock water gun. Collect ammo to refill."
                case 3:
                    self.text = "Double maximum ammo."
        
        def choose_upgrade(self):
            return self.upgrade_num
            
            


    #def get_upgrades():
        #randoms = random.sample(range(0, 5), 3)
        #match 


    def outside_bounds(rect):
        edge = False
        if rect.right >= 800:
            rect.right = 800
            edge = True
        if rect.x < 0:
            rect.x = 0
            edge = True
        if rect.bottom >= 800:
            rect.bottom = 800
            edge = True
        if rect.y < 0:
            rect.y = 0
            edge = True
        return edge



    #ENEMY
    #SUBCLASSES: melee, ranged, boss
    #PARAMETERS: vector, int, string (melee, ranged, boss), vector
    class Glunk:
        movement_decision_ticks = random.randint(200, 400)
        current_tick = 0


        time_since_hit_player = 0
        hit_cooldown = 180
        on_hit_cooldown = False


        def __init__(self, forward, speed, subclass, pos, frames):
            self.subclass = subclass
            self.forward = forward
            self.speed = speed
            self.pos = pos
            self.state = "patrol"
            self.frames = frames #SAGE
            self.frame_index =0
            self.animation_spd =0
        # self.rect = pygame.Rect(int(pos.x), int(pos.y),21,21)
            self.current_tick =0

        def which_glunk(curr_wave):
            frames = glunk_level_sprites[curr_wave]
            return Glunk(default_randomize_direction(), 1, "melee", pygame.math.Vector2(random.randint(0, 800), random.randint(0, 800)), frames)




    # SUBCLASS TYPES: fireball (from glunks AKA the enemy) OR water (from glooks)
    class Projectile:
        def __init__(self, forward, speed, subclass, pos):
            self.subclass = subclass
            self.forward = forward
            self.speed = speed
            self.pos = pos
            self.radius = 5


    # AMMO STUFF
    ammo_gain = 4
    current_ammo = 8
    class Ammo: 
        def __init__(self, pos):
            self.pos = pos
            self.text = smallFontSettings.render(f"AMMO", True, (255, 255, 255))


    glunks = []
    waterdrops = []
    ammos = []
    upgrades = []
    wave2_upgrades = [0, 1, 3]
    fireballs = []

    glook = Glook()

    while running:

        if ending_screen == False:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if on_wave_screen and not on_upgrade_screen:
                        on_wave_screen = False
                        wave_just_started = True
                    elif on_wave_screen and on_upgrade_screen: 
                        clicked_upgrade = True
                        clicked_pos = event.pos
                    else:
                        clicked_sword = True
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3 and unlocked_watergun and current_ammo != 0 and not on_wave_screen:
                    shoot_waterdrop = True
        
            keys = pygame.key.get_pressed()
        
            if not on_wave_screen:
                if keys[pygame.K_LEFT]:
                    glook.rect.move_ip(-3, 0)
                if keys[pygame.K_RIGHT]:
                    glook.rect.move_ip(3, 0)
                if keys[pygame.K_DOWN]:
                    glook.rect.move_ip(0, 3)
                if keys[pygame.K_UP]:
                    glook.rect.move_ip(0, -3)


        mouse_pos = pygame.mouse.get_pos()
        glook_center = pygame.math.Vector2(glook.rect.centerx, glook.rect.centery)
        mouse_to_player = (mouse_pos - glook_center).normalize()


        glook_pos = pygame.math.Vector2(glook.rect.x, glook.rect.y)
        outside_bounds(glook.rect)

        screen.fill((0, 0, 0))
        screen.blit(background, (0,0))#SAGE
        topleft = pygame.math.Vector2(glook.rect.topleft)
        screen.blit((glook_frame[frame_index]), (topleft.x - 50, topleft.y - 50))
        text_surface = font.render("Health: " + str(health), False, (255, 255, 255))



    
        # WAVE SYSTEMS
        if on_wave_screen:
            if wave == 1:
                wave_text_surface = font.render(wave_text, False, (255, 255, 255))
                intro_surface = font.render(intro_text, False, (255, 237, 77))
                screen.blit(wave_text_surface, (10, 20))
                screen.blit(intro_surface, (10, 60))
    
        if wave_just_started:
            wave_just_started = False
            glook.rect.topleft = (20, height/2)
            health = max_health
            ammo = maximum_ammo
            
            match wave:
                case 1:
                    for _ in range(5):
                        glunk = Glunk(default_randomize_direction(), 1, "melee", pygame.math.Vector2(random.randint(600, 800), random.randint(0, 800)), glunk_level_sprites[1])
                        glunks.append(glunk)

                    if unlocked_watergun: 
                        for _ in range(2):
                            ammo = Ammo(pygame.math.Vector2(random.randint(100, 700), random.randint(100, 700)))
                            ammos.append(ammo)
                case 2:
                    for _ in range(10):
                        glunk = Glunk(default_randomize_direction(), 1, "melee", pygame.math.Vector2(random.randint(0, 800), random.randint(0, 800)), glunk_level_sprites[1])
                        glunks.append(glunk)       

                    if unlocked_watergun: 
                        for _ in range(2):
                            ammo = Ammo(pygame.math.Vector2(random.randint(600, 800), random.randint(0, 800)))
                            ammos.append(ammo)

                    for _ in range(2):
                        glunk = Glunk(default_randomize_direction(), 0, "ranged", pygame.math.Vector2(random.randint(100, 700), random.randint(100, 700)), glunk_level_sprites[2])
                        glunk.angle = random.randint(0, 360)
                        glunks.append(glunk)    
                case 3:
                    for _ in range(10):
                        glunk = Glunk(default_randomize_direction(), 4, "melee", pygame.math.Vector2(random.randint(600, 800), random.randint(0, 800)), glunk_level_sprites[wave])
                        glunks.append(glunk)

                    if unlocked_watergun: 
                        for _ in range(2):
                            ammo = Ammo(pygame.math.Vector2(random.randint(600, 800), random.randint(0, 800)))
                            ammos.append(ammo)

                    for _ in range(2):
                        glunk = Glunk(default_randomize_direction(), 0, "ranged", pygame.math.Vector2(random.randint(100, 700), random.randint(100, 700)), glunk_level_sprites[2])
                        glunk.angle = random.randint(0, 360)
                        glunks.append(glunk)    




        
        # UPGRADE SYSTEMS
        if on_upgrade_screen: 
            upgrade_top_text = font.render(f"CHOOSE UPGRADE", False, (0, 0, 0))
            pygame.draw.rect(screen, (150, 150, 150), upgrade_background_rect)
            screen.blit(upgrade_top_text, (280, 55))
            if len(upgrades) == 0:
                if unlocked_watergun == False:
                    for i in range(3):
                        upgrade = Upgrade(i, i)
                        upgrades.append(upgrade)
                else:
                    for i in range(3):
                        upgrade = Upgrade(i, wave2_upgrades[i])
                        upgrades.append(upgrade)

            for upgrade in upgrades:
                pygame.draw.rect(screen, (255, 255, 255), upgrade.rect)
                upgrade_text = fontSettings.render(upgrade.text, True, (0, 0, 0)) 
                topleft = pygame.math.Vector2(upgrade.rect.topleft)
                screen.blit(upgrade_text, (topleft.x + 25, topleft.y + 25))
            
            if clicked_upgrade:
                for upgrade in upgrades:
                    if upgrade.rect.collidepoint(clicked_pos):
                        num = upgrade.choose_upgrade()
                        match num:
                            case 0: 
                                max_health += 5
                            case 1: 
                                sword_length += 20
                            case 2: 
                                unlocked_watergun = True
                            case 3: 
                                maximum_ammo = 16
                        on_upgrade_screen = False
                        on_wave_screen = False
                        wave_just_started = True
                        upgrades = []
                        

        if shoot_waterdrop and current_ammo > 0:
            current_ammo -= 1
            waterdrop = Projectile(mouse_to_player, 5, "waterdrop", glook_pos)
            waterdrop.rect = pygame.Rect(0, 0, 10, 10)
            waterdrop.rect.center = waterdrop.pos
            waterdrops.append(waterdrop)
            shoot_waterdrop = False

        # line for the mouse aiming thing
        if not on_wave_screen:
            health_text = fontSettings.render("HEALTH: " + str(health) + "/" + str(max_health), True, (255, 255, 255)) #BRIANNA
    
            cWave_text = fontSettings.render(f"Wave: {wave}/3", True, (255, 161, 60)) #BRIANNA

            healthBar_rect = pygame.Rect(20, 20, (health/max_health) * 200, 25)
            add_red = min((max_health - health) * 60, 197)
            subtract_green = min((max_health - health) * 30, 191)

            sword = pygame.draw.line(screen, (230, 230, 230), glook_center, mouse_to_player * sword_length + glook_center, 10)
            #glook = pygame.draw.rect(screen, (255, 255, 255), glook_rect)

            pygame.draw.rect(screen, (180, 180, 180), healthBar_behind_rect)
            pygame.draw.rect(screen, (58 + add_red, 191 - subtract_green, 2), healthBar_rect) #Brianna
            screen.blit(health_text, (25, 22)) #BRIANNA
            screen.blit(cWave_text, (20, 60)) #BRIANNA

            if unlocked_watergun:
                ammo_bar_text = fontSettings.render(f"Ammo: {current_ammo}/{maximum_ammo}", True, (48, 221, 255)) #BRIANNA
                screen.blit(ammo_bar_text, (20, 100))

        



        for waterdrop in waterdrops:
            waterdrop.rect.center += waterdrop.forward * waterdrop.speed
            waterdrop.speed *= 0.995 # DRAG
            if waterdrop.speed < 0.01:
                waterdrops.remove(waterdrop) 
            pygame.draw.rect(screen, (48, 221, 255), waterdrop.rect, border_radius=5)

        for fireball in fireballs: 
            fireball.rect.center += fireball.forward * fireball.speed
            fireball.speed *= 0.995 # DRAG
            if fireball.speed < 0.01:
                fireballs.remove(fireball)
            pygame.draw.rect(screen, (252, 127, 3), fireball.rect, border_radius=5)

            if fireball.rect.colliderect(glook.rect):
                health -= 1
                fireballs.remove(fireball)

        for ammo in ammos: 
            ammo.rect = pygame.Rect(ammo.pos.x, ammo.pos.y, 55, 17)
            ammo_box = pygame.draw.rect(screen, (28, 34, 199), ammo.rect)
            screen.blit(ammo.text, pygame.math.Vector2(ammo.pos))

            if ammo.rect.colliderect(glook.rect):
                current_ammo += ammo_gain
                current_ammo = min(current_ammo, maximum_ammo)
                ammos.remove(ammo)


        for glunk in glunks:
            # PATROL
            if glunk.subclass == "melee" or glunk.subclass == "ranged":
                glunk.rect = pygame.Rect(glunk.pos.x, glunk.pos.y, 40, 40)
            else: 
                glunk.rect = pygame.Rect(glunk.pos.x, glunk.pos.y, 60, 60)
        
            glunk.current_tick +=1
            if glunk.current_tick >= animation_spd:
                glunk.frame_index +=1
                glunk.current_tick =0
                if glunk.frame_index >= len(glunk.frames):
                    glunk.frame_index=0

            glook_fight = False


            if glunk.state == "patrol":
                if glunk.subclass == "melee":
                    glunk.speed = 1 * wave
                    glunk.current_tick += 1
                    if glunk.current_tick == glunk.movement_decision_ticks:
                        current_tick = 0
                        choice = random.randint(0, 1)
                        if choice == 1:
                            glunk.forward = pygame.math.Vector2(0, 0)
                        else:
                            glunk.forward = default_randomize_direction()
                elif glunk.subclass == "ranged":
                    radians = math.radians(glunk.angle)
                    glunk.forward = pygame.math.Vector2(
                        math.cos(radians),
                        math.sin(radians)
                    )
                    glunk.angle += 0.5
                    


            check_bounds = outside_bounds(glunk.rect)
            if check_bounds == True:
                glunk.forward = default_randomize_direction()
            
            distance = glunk.pos.distance_to(glook_pos)
            to_player = (glook_pos - glunk.pos).normalize()
            dot = glunk.forward.dot(to_player)
            if glunk.subclass == "ranged":
                if glunk.state == "patrol":
                    pygame.draw.circle(screen, (128, 128, 128), glunk.rect.center, 250, 2)
                else: 
                    pygame.draw.circle(screen, (255, 0, 0), glunk.rect.center, 250, 2)
                pygame.draw.line(screen, (255, 255, 255), glunk.rect.center, glunk.rect.center + glunk.forward * 125, 2)
                if dot > 0.75 and distance < 250:
                    glunk.forward = to_player
                    glunk.state = "attacking"
                    glook_fight = True
                else:
                    glunk.forward = default_randomize_direction()
                    glunk.state = "patrol"
                    glook_fight = False

            if glook_fight:
                time_glook +=1
            
                if time_glook >= animation_spd:
                    frame_index += 1
                    time_glook =0
            
                    if frame_index >= len(glook_frame):
                        frame_index =0
                    else:
                        frame_index =0
                        time_glook = 0

            if glunk.subclass == "melee" and distance < 150 and glunk.on_hit_cooldown == False:
                glunk.state = "attacking"
                glunk.forward = to_player
                glunk.speed = 1 * wave
        
            glunk.pos += glunk.forward * glunk.speed


            # collision
            if glunk.on_hit_cooldown == True:
                glunk.time_since_hit_player += 1
                if glunk.hit_cooldown == glunk.time_since_hit_player:
                    if glunk.subclass == "melee":
                        glunk.speed = 1 * wave
                    glunk.on_hit_cooldown = False
                    glunk.time_since_hit_player = 0

            if glunk.on_hit_cooldown == False and glunk.subclass == "ranged" and glunk.state == "attacking":
                fireball = Projectile(to_player, 5, "fireball", glunk.pos)
                fireball.rect = pygame.Rect(0, 0, 10, 10)
                fireball.rect.center = fireball.pos
                fireballs.append(fireball)
                glunk.on_hit_cooldown = True

            if glunk.rect.colliderect(glook.rect) and glunk.on_hit_cooldown == False:
                health -= 1
                health = max(health, 0)
                glunk.on_hit_cooldown = True
                glunk.speed = 0

            for waterdrop in waterdrops:
                if glunk.rect.colliderect(waterdrop.rect):
                    glunks.remove(glunk)
                    kills += 1
                    waterdrops.remove(waterdrop)
            
            sword_collide = glunk.rect.clipline(glook_center, mouse_to_player * sword_length + glook_center)
            if sword_collide and clicked_sword:
                try: 
                    glunks.remove(glunk)
                except Exception:
                    pass
                kills += 1
                clicked_sword = False

        
            glunk_image = glunk.frames[glunk.frame_index]
            topleft = pygame.math.Vector2(glunk.rect.topleft)
            screen.blit(glunk_image, (topleft.x - 25, topleft.y - 25))


        if len(glunks) == 0 and kills > 0:
            on_wave_screen = True
            on_upgrade_screen = True
            wave += 1
            kills = 0
            health = min(health, max_health)
            ammos = []
            # put upgrades here
        
        clicked_sword = False
        clicked_upgrade = False

        if wave > 3:
            ending_screen = True
            on_wave_screen = True
            on_upgrade_screen = False
            screen.blit(glook_ending, (0,0))
            text = font.render(f"You win! The glunks were defeated!", False, (255, 255, 255))
            screen.blit(text, (50, 50))

        if health == 0: 
            ending_screen = True
            on_wave_screen = True
            on_upgrade_screen = False
            screen.blit(glunk_ending, (0,0))
            text = font.render(f"You lose!", False, (255, 255, 255))
            screen.blit(text, (50, 50))


        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)

    pygame.quit()

asyncio.run(main())

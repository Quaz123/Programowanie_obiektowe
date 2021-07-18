import pygame, os, random
import game_module as gm

os.environ['SDL_VIDEO_CENTERED'] = '1'          # centrowanie okna
pygame.init()


## ustawienia ekranu i gry
screen = pygame.display.set_mode(gm.SIZESCREEN)
pygame.display.set_caption('Prosta gra platformowa...')
clock = pygame.time.Clock()


# klasa gracza
class Player(pygame.sprite.Sprite):
    def __init__(self, file_image):
        super().__init__()
        self.image = file_image
        self.rect = self.image.get_rect()
        self.movement_x = 0
        self.movement_y = 0
        self.press_left = False
        self.press_right = False
        self.rotate_left = False
        self._count = 0
        self.level = None
        self.lifes = 3
        self.items = {}


    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def turn_left(self):
        self.rotate_left = True
        self.movement_x = -6


    def turn_right(self):
        self.rotate_left = False
        self.movement_x = 6

    def stop(self):
        self.movement_x = 0

    def jump(self):
        self.rect.y += 2
        colliding_platforms = pygame.sprite.spritecollide(self, self.level.set_of_platforms, False)
        self.rect.y -= 2
        if colliding_platforms:
            self.movement_y = -15

    def shoot(self):
        if self.items.get("shotgun", False):
            b = Bullet(gm.BULLET_LIST, self.rotate_left,
                       self.rect.centerx, self.rect.centery + 20)
            self.level.set_of_bullets.add(b)


    def update(self):
        self._gravitation()

        # -------ruch w poziomie--------
        self.rect.x += self.movement_x

        # animacje
        if self.movement_x > 0:
            self._move(gm.PLAYER_WALK_LIST_R)
        if self.movement_x < 0:
            self._move(gm.PLAYER_WALK_LIST_L)


        # kolizje z platformami
        colliding_platforms = pygame.sprite.spritecollide(self, self.level.set_of_platforms, False)

        for p in colliding_platforms:
            if self.movement_x > 0:
                self.rect.right = p.rect.left
            if self.movement_x < 0:
                self.rect.left = p.rect.right

        # -------ruch w pionie--------
        self.rect.y += self.movement_y

        # kolizje z platformami
        colliding_platforms = pygame.sprite.spritecollide(self, self.level.set_of_platforms, False)

        for p in colliding_platforms:
            if self.movement_y > 0:
                self.rect.bottom = p.rect.top
                if self.rotate_left and self.movement_x == 0:
                    self.image = gm.PLAYER_STAND_L
                if not self.rotate_left and self.movement_x == 0:
                    self.image = gm.PLAYER_STAND_R
            if self.movement_y < 0:
                self.rect.top = p.rect.bottom

            self.movement_y = 0

        # zmiana grafik gdy spadamy i skaczemy
        if self.movement_y > 0:
            if self.rotate_left:
                self.image = gm.PLAYER_FALL_L
            else:
                self.image = gm.PLAYER_FALL_R
        if self.movement_y < 0:
            if self.rotate_left:
                self.image = gm.PLAYER_JUMP_L
            else:
                self.image = gm.PLAYER_JUMP_R

        # wykrywamy kolizje z przedmiotami
        colliding_items = pygame.sprite.spritecollide(self, self.level.set_of_items, False)

        for item in colliding_items:
            if item.name == "life":
                self.lifes += 1
                item.kill()

            if item.name == "shotgun":
                self.items[item.name] = 1
                item.kill()

    def _gravitation(self):
        if self.movement_y == 0:
            self.movement_y = 2
        else:
            self.movement_y += 0.35

    def get_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.press_left = True
                self.turn_left()
            if event.key == pygame.K_RIGHT:
                self.press_right = True
                self.turn_right()
            if event.key == pygame.K_UP:
                self.jump()
            if event.key == pygame.K_SPACE:
                self.shoot()
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                if self.press_right:
                    self.turn_right()
                else:
                    self.stop()
                    self.image = gm.PLAYER_STAND_L
                self.press_left = False

            if event.key == pygame.K_RIGHT:
                if self.press_left:
                    self.turn_left()
                else:
                    self.stop()
                    self.image = gm.PLAYER_STAND_R
                self.press_right = False

    def _move(self, image_list):
        if self._count < 3:
            self.image = image_list[0]
        elif self._count < 6:
            self.image = image_list[1]
        elif self._count < 9:
            self.image = image_list[2]
        elif self._count < 12:
            self.image = image_list[3]
        elif self._count < 15:
            self.image = image_list[4]
        elif self._count < 18:
            self.image = image_list[5]
        elif self._count < 21:
            self.image = image_list[6]

        if self._count < 21:
            self._count += 1
        else:
            self._count = 0


class Platform(pygame.sprite.Sprite):
    def __init__(self, image_list, width, height, pos_x, pos_y):
        super().__init__()
        self.image_list = image_list
        self.width = width
        self.height = height
        self.image = pygame.Surface([self.width, self.height])
        self.rect = self.image.get_rect()
        self.rect.x = pos_x
        self.rect.y = pos_y

    def draw(self, surface):
        # self.image.fill(gm.DARKGREEN)
        # surface.blit(self.image, self.rect)
        if self.width == 70:
            surface.blit(self.image_list[0], self.rect)
        else:
            surface.blit(self.image_list[1], self.rect)
            for i in range(70, self.width - 70, 70):
                surface.blit(self.image_list[2], [self.rect.x + i, self.rect.y])
            surface.blit(self.image_list[3], [self.rect.x + self.width - 70, self.rect.y])

# klasa przedmiotu
class Item(pygame.sprite.Sprite):
    def __init__(self, image, name, pos_center_x, pos_center_y):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.name = name
        self.rect.center = [pos_center_x, pos_center_y]

class Bullet(pygame.sprite.Sprite):
    def __init__(self, image_list, rotate_left, pos_center_x, pos_center_y):
        super().__init__()
        self.image = image_list[0] if rotate_left else image_list[1]
        self.rect = self.image.get_rect()
        self.movement_x = -15 if rotate_left else 15
        self.rect.center = [pos_center_x, pos_center_y]

    def update(self):
        self.rect.x += self.movement_x


#ogólna klasa wroga
class Enemy(pygame.sprite.Sprite):
    def __init__(self, start_image, image_list_left, image_list_right, image_list_dead_left,
                 image_list_dead_right, movement_x = 0, movement_y = 0):
        super().__init__()
        self.image = start_image
        self.rect = self.image.get_rect()
        self.image_list_left = image_list_left
        self.image_list_right = image_list_right
        self.image_list_dead_left = image_list_dead_left
        self.image_list_dead_right = image_list_dead_right
        self.movement_x = movement_x
        self.movement_y = movement_y
        self.lifes = 1
        self.rotate_left = True
        self.count = 0

    def update(self):
        if not self.lifes and self.count > 7:
            self.kill()

        self.rect.x += self.movement_x


        if self.movement_x > 0 and self.rotate_left:
            self.rotate_left = False
        if self.movement_x < 0 and not self.rotate_left:
            self.rotate_left = True

        #animacja
        if self.lifes:
            if self.movement_x > 0:
                self._move(self.image_list_right)
            if self.movement_x < 0:
                self._move(self.image_list_left)
        else:
            self.movement_x = 0
            self.movement_y = 0
            if self.rotate_left:
                self._move(self.image_list_dead_left)
            if not self.rotate_left:
                self._move(self.image_list_dead_right)


    def _move(self, image_list):
        if self.count < 4:
            self.image = image_list[0]
        elif self.count < 8:
            self.image = image_list[1]


        if self.count < 8:
            self.count += 1
        else:
            self.count = 0


class PlatformEnemy(Enemy):
    def __init__(self, start_image, image_list_left, image_list_right, image_list_dead_left,
                 image_list_dead_right, platform, movement_x = 0, movement_y = 0):

        super().__init__(start_image, image_list_left, image_list_right, image_list_dead_left,
                 image_list_dead_right, movement_x, movement_y)

        self.platform = platform
        self.rect.bottom = self.platform.rect.top
        self.rect.centerx = random.randint(self.platform.rect.left + self.rect.width//2,
                                           self.platform.rect.right - self.rect.width//2)

    def update(self):
        super().update()
        if (self.rect.left < self.platform.rect.left or self.rect.right > self.platform.rect.right):
            self.movement_x *= -1

class BatEnemy(Enemy):
    def __init__(self, start_image, image_list_left, image_list_right, image_list_dead_left,
                 image_list_dead_right, level, movement_x = 0, movement_y = 0, boundary_right = 0,
                 boundary_left = 0, boundary_top = 0, boundary_bottom = 0):

        super().__init__(start_image, image_list_left, image_list_right, image_list_dead_left,
                 image_list_dead_right, movement_x, movement_y)

        self.level = level
        self.boundary_right = boundary_right
        self.boundary_left = boundary_left
        self.boundary_top = boundary_top
        self.boundary_bottom = boundary_bottom
        self.sleep = True

    def update(self):
        if self.sleep:
            if self.rect.left - self.level.player.rect.right < 300:
                self.sleep = False
        else:
            super().update()
            self.rect.y += self.movement_y
            pos_x = self.rect.left - self.level.world_shift
            if (pos_x < self.boundary_left or pos_x + self.rect.width > self.boundary_right):
                self.movement_x *= -1
            if (self.rect.top < self.boundary_top or self.rect.bottom > self.boundary_bottom):
                self.movement_y *= -1

# ogólna klasa planszy
class Level:
    def __init__(self, player):
        self.player = player
        self.set_of_platforms = set()
        self.set_of_items = pygame.sprite.Group()
        self.set_of_bullets = pygame.sprite.Group()
        self.set_of_enemies = pygame.sprite.Group()
        self.world_shift = 0

    def update(self):
        self._delete_bullets()
        self.set_of_bullets.update()
        self.set_of_enemies.update()

        if self.player.rect.right >= 500:
            diff = self.player.rect.right - 500
            self.player.rect.right = 500
            self._shift_world(-diff)

        if self.player.rect.left <= 100:
            diff = 100 - self.player.rect.left
            self.player.rect.left = 100
            self._shift_world(diff)


    def draw(self, surface):
        for p in self.set_of_platforms:
            p.draw(surface)

        self.set_of_items.draw(surface)
        self.set_of_bullets.draw(surface)
        self.set_of_enemies.draw(surface)


        # rysowanie żyć
        for i in range(self.player.lifes - 1):
           surface.blit(gm.HEART, [20 + 40 * i, 15])

    def _shift_world(self, shift_x):
        self.world_shift += shift_x

        for p in self.set_of_platforms:
            p.rect.x += shift_x

        for item in self.set_of_items:
            item.rect.x += shift_x

        for b in self.set_of_bullets:
            b.rect.x += shift_x

        for e in self.set_of_enemies:
            e.rect.x += shift_x

    def _delete_bullets(self):
        pygame.sprite.groupcollide(self.set_of_bullets, self.set_of_platforms, True, False)

        for b in self.set_of_bullets:
            if b.rect.left > gm.WIDTH or b.rect.right < 0:
                b.kill()

            colliding_enemies = pygame.sprite.spritecollide(b, self.set_of_enemies, False)
            for enemy in colliding_enemies:
                b.kill()
                if enemy.lifes:
                    enemy.lifes -= 1
                    if enemy.lifes == 0:
                        enemy.count = 0


class Level_1(Level):
    def __init__(self, player = None):
        super().__init__(player)
        self._create_platforms()
        self._create_itmes()
        self._create_platform_enemies()
        self._create_bat_enemies()


    def _create_platforms(self):
        ws_static_platforms = [[70, 70, 200, 350],[48*70, 70, 0, gm.HEIGHT - 70],[6*70, 70, 800, 350],
                               [70, 70, 800,  gm.HEIGHT -140]]
        for ws in ws_static_platforms:
            p = Platform(gm.GRASS_LIST, *ws)
            self.set_of_platforms.add(p)

    def _create_itmes(self):
        life = Item(gm.HEART, 'life', 1000, 300)
        self.set_of_items.add(life)

        shotgun = Item(gm.SHOTGUN, 'shotgun', 1400, 620)
        self.set_of_items.add(shotgun)

    def _create_platform_enemies(self):
        ws_static_platforms = [[8*70, 70, 1400, 350], [6*70, 70, 2200, 350]]
        for ws in ws_static_platforms:
            p = Platform(gm.GRASS_LIST, *ws)
            self.set_of_platforms.add(p)

            pe = PlatformEnemy(gm.ZOMBIE_STAND_L, gm.ZOMBIE_WALK_LIST_L, gm.ZOMBIE_WALK_LIST_R,
                               gm.ZOMBIE_DEAD_LIST_L, gm.ZOMBIE_DEAD_LIST_R, p,
                               random.choice([-5,-4,-3,-2,2,3,4,5]))

            self.set_of_enemies.add(pe)

    def _create_bat_enemies(self):
        bat = BatEnemy(gm.BAT_HANG, gm.BAT_FLY_LIST_L, gm.BAT_FLY_LIST_R, gm.BAT_DEAD_LIST_L,
                       gm.BAT_DEAD_LIST_R, self, random.choice([-5,-4,-3,-2,2,3,4,5]),
                       random.choice([-4,-3,-2,2,3,4]),2400, 1200,0,300)

        bat.rect.left = 1600
        bat.rect.top = 0
        self.set_of_enemies.add(bat)



# konkretyzacja obiektów
player = Player(gm.PLAYER_STAND_R)
player.rect.center = screen.get_rect().center
current_level = Level_1(player)
player.level = current_level


# głowna pętla gry
window_open = True
while window_open:
    # screen.fill(gm.LIGHTBLUE)
    screen.blit(gm.BACKGROUND, (0,-340))
    # pętla zdarzeń
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                window_open = False
        elif event.type == pygame.QUIT:
            window_open = False
        player.get_event(event)


    # rysowanie i aktualizacja obiektów
    current_level.update()
    player.update()
    current_level.draw(screen)
    player.draw(screen)


    # aktualizacja okna pygame
    pygame.display.flip()
    clock.tick(30)

pygame.quit()

import sys

import os
import random
import math

import pygame

from scripts.entities import Player, Enemy
from scripts.utils import load_image, load_images, Animation
from scripts.tilemap import Tilemap
from scripts.clouds import Clouds
from scripts.particle import Particle
from scripts.spark import Spark
from scripts.edit import Score


class Game:
    def __init__(self):
        pygame.init()
        # tiêu đề cửa sổ
        pygame.display.set_caption("Ninja game")
        # cửa sổ game
        self.screen = pygame.display.set_mode((1280, 960))
        # màn hình game
        self.display = pygame.Surface((640, 480), pygame.SRCALPHA)
        # màn hình game 2
        self.display_2 = pygame.Surface((640, 480))
        # đồng hồ game
        self.clock = pygame.time.Clock()
        # di chuyển
        self.movement = [False, False]
        # tải hình ảnh
        self.assets = {
            'decor': load_images('tiles/decor'),
            'grass': load_images('tiles/grass'),
            'large_decor': load_images('tiles/large_decor'),
            'stone': load_images('tiles/stone'),
            'player' : load_image('entities/player.png'),
            'background' :pygame.transform.scale(load_image('background.png'), (1280, 960)),
            'clouds' : load_images('clouds'),
            'enemy/idle': Animation(load_images('entities/enemy/idle'), img_dur=6),
            'enemy/run': Animation(load_images('entities/enemy/run'), img_dur=4),
            'player/idle': Animation(load_images('entities/player/idle'), img_dur = 6),
            'player/run': Animation(load_images('entities/player/run'), img_dur = 4),
            'player/jump': Animation(load_images('entities/player/jump')),
            'player/slide': Animation(load_images('entities/player/slide')),
            'player/wall_slide': Animation(load_images('entities/player/wall_slide')),
            'particle/leaf': Animation(load_images('particles/leaf'), img_dur = 20, loop= False),
            'particle/particle': Animation(load_images('particles/leaf'), img_dur = 6, loop= False),
            'gun': load_image('gun.png'),
            'projectile': load_image('projectile.png'),
        }
        # tải âm thanh
        self.sfx ={
            'jump' : pygame.mixer.Sound('data/sfx/jump.wav'),
            'dash': pygame.mixer.Sound('data/sfx/dash.wav'),
            'hit': pygame.mixer.Sound('data/sfx/hit.wav'),
            'shoot': pygame.mixer.Sound('data/sfx/shoot.wav'),
            'ambience': pygame.mixer.Sound('data/sfx/ambience.wav'),
        }
        # âm lượng âm thanh
        self.sfx['ambience'].set_volume(0.2)
        self.sfx['shoot'].set_volume(0.4)
        self.sfx['dash'].set_volume(0.8)
        self.sfx['hit'].set_volume(0.3)
        self.sfx['jump'].set_volume(0.7)
        # mây
        self.clouds = Clouds(self.assets['clouds'], count = 16)
        # người chơi
        self.player = Player(self,(100,45),(8, 15)) #tạo người chơi ở vị trí x=80, y=50, kích thước 8x15
        # tilemap
        self.tilemap = Tilemap(self, tile_size=32) #tạo tilemap với kích thước tile 16x16
        # Load level
        self.level = 0
        self.load_level(self.level) #load level hiện tại được thiết lặp sẵn là 0
        # rung màn hình
        self.screenshake = 0  # màn hình không rung
    
    def load_level(self, map_id): # tạo hàm load level với thông số truyền vào là map_id
        #load map từ file json trong thư mục data/maps str(map_id) là tên file json được chuyển từ số thành chuỗi
        map_file = 'data/maps/' + str(map_id) + '.json'
        if not os.path.exists(map_file):
            self.end_game()
            return
        self.tilemap.load(map_file) 
        # note: variant là biến định danh cho từng loại tile
        self.leaf_spawners = []
        for tree in self.tilemap.extract([('large_decor', 2)], keep=True):
            self.leaf_spawners.append(pygame.Rect(4 + tree['pos'][0], 4 + tree['pos'][1], 23, 13))

        self.enemies = []
        for spawner in self.tilemap.extract([('spawners', 0), ('spawners', 1)]):
            if spawner['variant'] == 0:
                self.player.pos = spawner['pos']
                self.player.air_time = 0
            else:
                self.enemies.append(Enemy(self, spawner['pos'], (8, 15)))

        self.projectiles = []
        self.particles = []

        self.sparks = []
        self.scroll = [0, 0]
        self.dead = 0
        self.transition = -30
        self.score = 0
        self.score_display = Score(self.score)

    def run(self):
        pygame.mixer.music.load('data/music.wav')
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)

        self.sfx['ambience'].play(-1)

        while True:
            self.display.fill((0,0,0, 0))
            self.display_2.blit(self.assets['background'], (0,0))

            self.screenshake = max(0, self.screenshake - 1)

            if not len(self.enemies):
                self.transition += 1
                if self.transition >= 30:
                    if self.level >= len(os.listdir('data/maps')) - 1:
                        
                        self.end_game()
                    else:
                        self.level += 1
                        self.load_level(self.level)
            if self.transition < 0:
                self.transition += 1

            if self.dead:
                self.dead += 1
                if self.dead >= 10:
                    self.transition += min(30, self.transition + 1)
                if self.dead == 40:
                    self.load_level(self.level)

            self.scroll[0] += (self.player.rect().centerx - self.display.get_width() /2 - self.scroll[0]) / 30
            self.scroll[1] += (self.player.rect().centery - self.display.get_width() /2 - self.scroll[1]) / 30
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

            for rect in self.leaf_spawners:
                if random.random() * 49999 < rect.width * rect.height:
                    pos = (rect.x + random.random() * rect.width, rect.y + random.random() * rect.height)
                    self.particles.append(Particle(self, 'leaf', pos, velocity=[-0.1, 0.3], frame= random.randint(0, 20)))

            self.clouds.update()
            self.clouds.render(self.display, offset=render_scroll)

            self.tilemap.render(self.display, offset =render_scroll)
            self.score_display.render(self.display)
            
            for enemy in self.enemies.copy():
                kill = enemy.update(self.tilemap, (0, 0))
                enemy.render(self.display, offset = render_scroll)
                if kill:
                    self.enemies.remove((enemy))
                    self.score += 1
                    self.score_display.update(self.score)

            if not self.dead:
                self.player.update(self.tilemap, (self.movement[1] - self.movement[0], 0))
                self.player.render(self.display, offset = render_scroll)

            for projectile in self.projectiles.copy():
                projectile[0][0] += projectile[1]
                projectile[2] += 1
                img = self.assets['projectile']
                self.display.blit(img,(projectile[0][0] - img.get_width() / 2 - render_scroll[0], projectile[0][1] - img.get_height() /2 - render_scroll[1]))
                if self.tilemap.solid_check(projectile[0]):
                    self.projectiles.remove(projectile)
                    for i in range (4):
                        self.sparks.append(Spark(projectile[0], random.random() - 0.5 + (math.pi if projectile[1] > 0 else 0), 2 + random.random()))
                elif projectile[2] > 360:
                    self.projectiles.remove(projectile)
                elif abs(self.player.dashing) < 50:
                    if self.player.rect().collidepoint(projectile[0]):
                        self.projectiles.remove(projectile)
                        self.dead += 1
                        self.sfx['hit'].play()
                        self.screenshake = max(16, self.screenshake)
                        for i in range (30):
                            angle = random.random() * math.pi * 2
                            speed = random .random() * 5
                            self.sparks.append(Spark(self.player.rect().center, angle, 2 + random.random()))
                            self.particles.append(Particle(self, 'particle', self.player.rect().center, velocity=[math.cos(angle + math.pi) * speed * 0.5, math.sin(angle + math.pi) * speed *0.5], frame = random.randint(0 , 7)))

            for spark in self.sparks.copy():
                kill = spark.update()
                spark.render(self.display, offset =render_scroll)
                if kill:
                    self.sparks.remove(spark)

            display_mask = pygame.mask.from_surface(self.display)
            display_sillhouette = display_mask.to_surface(setcolor=(0, 0, 0 ,180), unsetcolor= (0, 0, 0,0))
            for offset in [(-1,0), (1, 0), (0, -1), (0, 1), (-1, 0)]:
                self.display_2.blit(display_sillhouette, offset)

            for particle in self.particles.copy():
                kill = particle.update()
                if particle.type =='leaf':
                    particle.pos[0] += math.sin(particle.animation.frame * 0.035) * 0.3
                particle.render(self.display, offset= render_scroll)
                if kill:
                    self.particles.remove(particle)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a:
                        self.movement[0] = True
                    if event.key == pygame.K_d:
                        self.movement[1] = True
                    if event.key == pygame.K_SPACE or event.key == pygame.K_w:
                        if self.player.jump():
                         self.sfx['jump'].play()
                    if event.key == pygame.K_LSHIFT:
                        self.player.dash()
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_a:
                        self.movement[0] = False
                    if event.key == pygame.K_d:
                        self.movement[1] = False

            if self.transition:
                transition_surf = pygame.Surface(self.display.get_size())
                radius = max(0, (30 - abs(self.transition)) * 8)
                pygame.draw.circle(transition_surf, (255, 255, 255), (self.display.get_width() // 2 , self.display.get_height() // 2), radius)
                transition_surf.set_colorkey((255, 255, 255))
                self.display.blit(transition_surf, (0,0))

            self.display_2.blit(self.display, (0,0))

            screenshake_offset = (random.random() * self.screenshake - self.screenshake /2,random.random() * self.screenshake - self.screenshake /2)
            self.screen.blit(pygame.transform.scale(self.display_2,self.screen.get_size()),screenshake_offset)
            pygame.display.update()
            self.clock.tick(60)
    def end_game(self):
        # Tạo một surface đen với kích thước giống như màn hình hiển thị
        end_screen = pygame.Surface(self.screen.get_size())
        end_screen.fill((0,0,0)) # Điền màu đen
        # Tạo font
        font = pygame.font.Font(None, 36)
        # Tạo surface chứa văn bản
        text = font.render("Congratulations! You have completed the game.", True, (255, 255, 255))
        text2 = font.render("Press C to play again or Q to quit.", True, (255, 255, 255))
        # Hiển thị văn bản lên màn hình
        self.screen.blit(text, (0, 0))
        self.screen.blit(text2, (0, 36))
        pygame.display.update()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        pygame.quit()
                        sys.exit()
                    if event.key == pygame.K_c:
                        self.level = 0
                        self.load_level(self.level)
                        return
Game().run()
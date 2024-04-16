import random

import pygame

import math

from scripts.particle import Particle
from scripts.spark import Spark

class PhysicsEntity:
    def __init__(self, game, e_type, pos, size):
        self.game = game
        self.type = e_type
        self.pos = list(pos)
        self.size = size
        self.velocity = [0, 0]
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}

        self.action = ''
        self.anim_offset = (-3, -3)
        self.flip = False
        self.set_action('idle')

        self.last_movement = [0, 0]

    def rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])

    def set_action(self, action):
        if action != self.action:
            self.action = action
            self.animation = self.game.assets[self.type + '/' + self.action].copy()

    def update(self, tilemap, movement=(0, 0)):
        # khởi tạo 1 danh sách để lưu trữ các giá trị va chạm
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}
        # tính toán vị trí mà thực thể sẽ di chuyển tới
        frame_movement = (movement[0] + self.velocity[0], movement[1] + self.velocity[1])

        # Cập nhật vị trí theo trục x của đối tượng
        self.pos[0] += frame_movement[0]
        # Lấy hình chữ nhật đại diện cho đối tượng
        entity_rect = self.rect()
        # Kiểm tra va chạm với các hình chữ nhật trong tilemap xung quanh vị trí hiện tại của đối tượng
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                # Nếu có va chạm và đối tượng đang di chuyển về phía bên phải
                if frame_movement[0] > 0:
                    # Đặt cạnh phải của hình chữ nhật đối tượng bằng cạnh trái của hình chữ nhật va chạm
                    entity_rect.right = rect.left
                    # Đánh dấu rằng có va chạm ở bên phải
                    self.collisions['right'] = True
                # Nếu có va chạm và đối tượng đang di chuyển về phía bên trái
                if frame_movement[0] < 0:
                    # Đặt cạnh trái của hình chữ nhật đối tượng bằng cạnh phải của hình chữ nhật va chạm
                    entity_rect.left = rect.right
                    # Đánh dấu rằng có va chạm ở bên trái
                    self.collisions['left'] = True
                # Cập nhật vị trí x của đối tượng dựa trên hình chữ nhật đối tượng sau khi xử lý va chạm
                self.pos[0] = entity_rect.x

         # Cập nhật vị trí theo trục y của đối tượng
        self.pos[1] += frame_movement[1]
        # Lấy hình chữ nhật đại diện cho đối tượng
        entity_rect = self.rect()
        # Kiểm tra va chạm với các hình chữ nhật trong tilemap xung quanh vị trí hiện tại của đối tượng
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                # Nếu có va chạm và đối tượng đang di chuyển xuống
                if frame_movement[1] > 0:
                    # Đặt cạnh dưới của hình chữ nhật đối tượng bằng cạnh trên của hình chữ nhật va chạm
                    entity_rect.bottom = rect.top
                    # Đánh dấu rằng có va chạm ở phía dưới
                    self.collisions['down'] = True
                # Nếu có va chạm và đối tượng đang di chuyển lên
                if frame_movement[1] < 0:
                    # Đặt cạnh trên của hình chữ nhật đối tượng bằng cạnh dưới của hình chữ nhật va chạm
                    entity_rect.top = rect.bottom
                    # Đánh dấu rằng có va chạm ở phía trên
                    self.collisions['up'] = True
                # Cập nhật vị trí y của đối tượng dựa trên hình chữ nhật đối tượng sau khi xử lý va chạm
                self.pos[1] = entity_rect.y

        if movement[0] > 0:
            self.flip = False
        if movement[0] < 0:
            self.flip = True

        self.last_movement = movement

        self.velocity[1] = min(5, self.velocity[1] + 0.1)

        if self.collisions['down'] or self.collisions['up']:
            self.velocity[1] = 0

        self.animation.update()

    def render(self, surf, offset=(0, 0)):
        surf.blit(pygame.transform.flip(self.animation.img(), self.flip, False), (self.pos[0] - offset[0] + self.anim_offset[0], self.pos[1] - offset[1] + self.anim_offset[1]))

class Enemy(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, 'enemy', pos, size)

        self.walking = 0

    def update(self, tilemap, movement =(0, 0)):
        # Nếu kẻ thù đang di chuyển
        if self.walking:
            # Kiểm tra xem nếu có va chạm với một đối tượng cứng ở vị trí mà kẻ thù sẽ di chuyển tới
            if tilemap.solid_check((self.rect().centerx +(-7 if self.flip else 7), self.pos[1] +23)):
                # Nếu có va chạm ở bên phải hoặc bên trái kẻ thù
                if (self.collisions['right'] or self.collisions['left']):
                    # Đảo ngược hướng di chuyển của kẻ thù
                    self.flip = not self.flip
                else:
                    # Thay đổi hướng di chuyển của kẻ thù dựa trên giá trị hiện tại của self.flip
                    movement = (movement[0] - 0.5 if self.flip else 0.5 , movement[1])
            else:
                # Nếu không có va chạm, đảo ngược hướng di chuyển của kẻ thù
                self.flip = not self.flip
            # Giảm giá trị self.walking xuống 1 đơn vị, nhưng không để nó nhỏ hơn 0
            self.walking = max(0, self.walking - 1)
            # Nếu kẻ thù không di chuyển
            if not self.walking:
                # Tính toán khoảng cách từ kẻ thù tới người chơi
                dis = (self.game.player.pos[0] - self.pos[0], self.game.player.pos[1] - self.pos[1])
                # Nếu khoảng cách theo trục y nhỏ hơn 16, và kẻ thù đang nhìn về phía người chơi
                if (abs(dis[1]) < 16):
                    if (self.flip and dis[0] < 0):
                        # Kẻ thù bắn một viên đạn và tạo ra một số tia lửa
                        self.game.sfx['shoot'].play()
                        self.game.projectiles.append([[self.rect().centerx - 7, self.rect().centery],-1.5 , 0])
                        for i in range(4):
                            self.game.sparks.append(Spark(self.game.projectiles[-1][0], random.random() - 0.5 + math.pi, 2 + random.random()))
                    if (not self.flip and dis[0] > 0):
                        # Kẻ thù bắn một viên đạn và tạo ra một số tia lửa
                        self.game.sfx['shoot'].play()
                        self.game.projectiles.append([[self.rect().centerx + 7, self.rect().centery], 1.5 , 0])
                        for i in range(4):
                            self.game.sparks.append(Spark(self.game.projectiles[-1][0], random.random() - 0.5, 2 + random.random()))
        # Nếu kẻ thù không di chuyển, có một xác suất nhỏ (0.01) để bắt đầu di chuyển lại, với số lượng bước di chuyển ngẫu nhiên từ 30 đến 120
        elif random.random() < 0.01:
            self.walking = random.randint(30, 120)
        # Gọi phương thức update của lớp cha với tilemap và movement là đối số
        super().update(tilemap, movement= movement)

        if movement[0] != 0:
            self.set_action('run')
        else:
            self.set_action('idle')

        if abs(self.game.player.dashing) >= 50:
            if self.rect().colliderect((self.game.player.rect())):
                self.game.screenshake = max(16, self.game.screenshake)
                # Nếu người chơi đang dashing với mức độ tối thiểu là 50 và đối tượng này va chạm với người chơi,
                # đặt mức độ rung màn hình (screenshake) tối thiểu là 16
                self.game.sfx['hit'].play()
                for i in range(30):
                    angle = random.random() * math.pi * 2
                    speed = random.random() * 5
                     # Tạo 30 tia lửa với góc và tốc độ ngẫu nhiên từ vị trí trung tâm của người chơi
                    self.game.sparks.append(Spark(self.game.player.rect().center, angle, 2 + random.random()))
                    # Tạo các hạt với tốc độ và hình dạng ngẫu nhiên từ vị trí trung tâm của người chơi
                    self.game.particles.append(Particle(self.game, 'particle', self.game.player.rect().center, velocity=[math.cos(angle + math.pi) * speed * 0.5, math.sin(angle + math.pi) * speed * 0.5], frame=random.randint(0, 7)))
                self.game.sparks.append(Spark(self.rect().center, 0, 5 + random.random()))
                self.game.sparks.append(Spark(self.rect().center, math.pi, 5 + random.random()))
                # Tạo thêm 2 tia lửa từ vị trí trung tâm của đối tượng này với góc cố định và tốc độ ngẫu nhiên

                return True
                # Trả về True, có thể để biểu thị rằng một sự kiện va chạm đã xảy ra

    def render(self, surf, offset=(0, 0)):
        super().render(surf, offset = offset)
        # Gọi phương thức render của lớp cha với surf và offset là đối số

        if self.flip:
            surf.blit(pygame.transform.flip(self.game.assets['gun'], True, False), (self.rect().centerx - 4 - self.game.assets['gun'].get_width() - offset[0], self.rect().centery - offset[1]))
            # Nếu thuộc tính flip là True, vẽ hình ảnh của 'gun' đã được lật ngược lên surf tại vị trí đã tính toán
        else:
            surf.blit(self.game.assets['gun'], (self.rect().centerx +4 - offset[0], self.rect().centery - offset[1]))
             # Nếu thuộc tính flip là False, vẽ hình ảnh của 'gun' lên surf tại vị trí đã tính toán
class Player(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, 'player', pos, size)
        self.air_time = 0
        self.jumps = 1
        self.wall_slide = False
        # Khởi tạo thuộc tính wall_slide (trượt tường) bằng False
        self.dashing = 0

    def update(self, tilemap, movement=(0, 0)):
        super().update(tilemap, movement=movement)

        self.air_time += 1
        # Tăng thời gian trong không khí lên 1
        if self.air_time > 120:
            if not self.game.dead:
                self.game.screenshake = max(16, self.game.screenshake)
             # Nếu thời gian trong không khí lớn hơn 120 và người chơi không chết, đặt mức độ rung màn hình (screenshake) tối thiểu là 16
            self.game.dead += 1
            # Tăng số lần chết của game lên 1

        if self.collisions['down']:
            self.air_time = 0
            self.jumps = 1
             # Nếu người chơi va chạm với mặt đất, đặt lại thời gian trong không khí và số lần nhảy

        self.wall_slide = False
        if (self.collisions['right'] or self.collisions['left']) and self.air_time > 4:
            self.wall_slide = True
            self.velocity[1] = min(self.velocity[1], 0.5)
        # Nếu người chơi va chạm với tường và thời gian trong không khí lớn hơn 4, cho phép trượt tường và giới hạn tốc độ rơi xuống
            if self.collisions['right']:
                self.flip = False
            else:
                self.flip = True
            self.set_action('wall_slide')

        if not self.wall_slide:
            if self.air_time > 4:
                self.set_action('jump')
            elif movement[0] != 0:
                self.set_action('run')
            else:
                self.set_action('idle')

        if self.dashing > 0:
            self.dashing = max(0, self.dashing - 1)
        if self.dashing < 0:
            self.dashing = min(0, self.dashing + 1)
        if abs(self.dashing) > 50:
            self.velocity[0] = abs(self.dashing) / self.dashing * 8
            # Nếu giá trị tuyệt đối của dashing lớn hơn 50, đặt tốc độ theo chiều x của người chơi dựa trên giá trị của dashing
            if abs (self.dashing) == 51:
                self.velocity[0] *= 0.1
            # Nếu giá trị tuyệt đối của dashing bằng 51, giảm tốc độ theo chiều x của người chơi xuống 10%

            pvelocity = [abs(self.dashing) / self.dashing * random.random() * 3, 0]
            # Tạo một vector tốc độ ngẫu nhiên cho hạt
            self.game.particles.append(Particle(self.game, 'particle', self.rect().center, velocity=pvelocity, frame=random.randint(0, 7)))
            # Thêm một hạt mới vào danh sách hạt của game với tốc độ và khung hình ngẫu nhiên

        if abs(self.dashing) in {60, 50}:
            for i  in range(20):
                angle = random.random() *  math.pi * 2
                speed= random.random() * 0.5 +0.5
                pvelocity = [math.cos(angle)* speed, math.sin(angle) * speed]
                self.game.particles.append(Particle(self.game, 'particle', self.rect().center, velocity=pvelocity, frame = random.randint(0,7)))
                # Nếu giá trị tuyệt đối của dashing là 60 hoặc 50, tạo 20 góc ngẫu nhiên trong khoảng từ 0 đến 2π
        if self.velocity[0] > 0:
            self.velocity[0] = max(self.velocity[0] - 0.1, 0)
        else:
            self.velocity[0] = min(self.velocity[0] + 0.1, 0)
            # Giảm tốc độ theo chiều x của người chơi về 0 nếu tốc độ dương, tăng tốc độ theo chiều x của người chơi về 0 nếu tốc độ âm

    def render(self, surf, offset = (0, 0)):
        if abs(self.dashing) <= 50:
            super().render(surf, offset=offset)
        # Nếu giá trị tuyệt đối của dashing nhỏ hơn hoặc bằng 50, gọi phương thức render của lớp cha

    def jump(self):
        if self.wall_slide:
            if self.flip and self.last_movement[0] < 0:
                self.velocity[0] = 3.5
                self.velocity[1] = -2.5
                self.air_time = 5
                self.jumps = max(0, self.jumps - 1)
                return True
                # Nếu người chơi đang trượt tường và di chuyển về phía trái, thay đổi tốc độ và thời gian trong không khí của người chơi, giảm số lần nhảy xuống 1 và trả về True
            elif not self.flip and self.last_movement[0] > 0:
                self.velocity[0] = -3.5
                self.velocity[1] = -2.5
                self.air_time = 5
                self.jumps = max(0, self.jumps - 1)
                return True
                # Nếu người chơi đang trượt tường và di chuyển về phía phải, thay đổi tốc độ và thời gian trong không khí của người chơi, giảm số lần nhảy xuống 1 và trả về True
        elif self.jumps:
            self.velocity[1] = -3
            self.jumps -= 1
            self.air_time = 5
            return True
            # Nếu người chơi không trượt tường và còn số lần nhảy, thay đổi tốc độ và thời gian trong không khí của người chơi, giảm số lần nhảy xuống 1 và trả về True

    def dash(self):
        if not self.dashing:
            self.game.sfx['dash'].play()
        # Nếu người chơi không đang dash, phát hiệu ứng âm thanh 'dash'
            if self.flip:
                self.dashing = -60
            else:
                self.dashing = 60
        # Nếu thuộc tính flip là True, đặt giá trị của dashing là -60. Nếu không, đặt giá trị của dashing là 60
        
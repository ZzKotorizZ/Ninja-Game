import random

class Cloud:
    # khởi tạo phương thức init với các tham số truyền vào là pos, img, speed, depth
    def __init__(self, pos, img, speed, depth):
        self.pos = list(pos) # tạo list pos
        self.img = img  # gán img cho biến img
        self.speed = speed  # gán speed cho biến speed
        self.depth = depth  # gán depth cho biến depth
    # tạo phương thức update
    def update(self):
        # tăng pos[0] lên speed
        self.pos[0] += self.speed
    # tạo phương thức render với tham số truyền vào là surf, offset
    def render(self, surf, offset =(0,0)):
        # tạo biến render_pos 
        render_pos = (self.pos[0] - offset[0] * self.depth, self.pos[1] - offset[1] * self.depth)
        # vẽ img lên surf
        surf.blit(self.img, (render_pos[0] % (surf.get_width() + self.img.get_width()) -self.img.get_width(),render_pos[1] % (surf.get_height() + self.img.get_height()) -self.img.get_height()))

class Clouds:
    # tạo phương thức init với các tham số truyền vào là cloud_images, count = 16
    def __init__(self, cloud_images, count = 16):
        # tạo clouds là list rỗng
        self.clouds =[]
        # tạo vòng lặp for 
        for i in range(count):
            self.clouds.append(Cloud((random.random()* 99999, random.random() * 99999), random.choice(cloud_images), random.random() *0.05 + 0.05, random.random() * 0.6 +0.2))
        # Tạo một đối tượng Cloud mới với vị trí ngẫu nhiên, hình ảnh ngẫu nhiên từ cloud_images, tốc độ ngẫu nhiên, và độ sâu ngẫu nhiên.
        self.clouds.sort(key=lambda x:x.depth)  # sắp xếp clouds theo depth  
    
    def update(self):
        # tạo vòng lặp for
        for cloud in self.clouds:
            cloud.update()
        #  tạo phương thhức render với tham số truyền vào là surf (đối tượng Surface để vẽ lên) và offset (sự dịch chuyển của camera).
    def render(self, surf, offset =(0,0)):
        for cloud in self.clouds:
            cloud.render(surf, offset = offset)

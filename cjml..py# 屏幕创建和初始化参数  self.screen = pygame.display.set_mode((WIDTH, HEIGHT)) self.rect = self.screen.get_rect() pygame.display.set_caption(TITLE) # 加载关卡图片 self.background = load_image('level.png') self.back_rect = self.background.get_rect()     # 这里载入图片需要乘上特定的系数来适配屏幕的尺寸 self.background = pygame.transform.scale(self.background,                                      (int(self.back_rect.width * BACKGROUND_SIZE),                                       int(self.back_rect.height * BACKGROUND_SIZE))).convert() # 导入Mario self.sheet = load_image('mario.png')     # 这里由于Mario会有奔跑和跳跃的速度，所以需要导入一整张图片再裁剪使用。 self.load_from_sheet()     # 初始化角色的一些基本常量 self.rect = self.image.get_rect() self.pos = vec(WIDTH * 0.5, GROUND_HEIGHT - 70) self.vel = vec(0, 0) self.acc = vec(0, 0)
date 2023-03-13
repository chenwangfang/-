# 屏幕创建和初始化参数 
self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
self.rect = self.screen.get_rect()
pygame.display.set_caption(TITLE)
# 加载关卡图片
self.background = load_image('level.png')
self.back_rect = self.background.get_rect()
    # 这里载入图片需要乘上特定的系数来适配屏幕的尺寸
self.background = pygame.transform.scale(self.background,
                                     (int(self.back_rect.width * BACKGROUND_SIZE),
                                      int(self.back_rect.height * BACKGROUND_SIZE))).convert()
# 导入Mario
self.sheet = load_image('mario.png')
    # 这里由于Mario会有奔跑和跳跃的速度，所以需要导入一整张图片再裁剪使用。
self.load_from_sheet()
    # 初始化角色的一些基本常量
self.rect = self.image.get_rect()
self.pos = vec(WIDTH * 0.5, GROUND_HEIGHT - 70)
self.vel = vec(0, 0)
self.acc = vec(0, 0)

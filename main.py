import pygame
import socket
import _thread
import pickle
from sys import exit
from math import acos, cos, sin, sqrt, pi, degrees


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.transform.rotozoom(pygame.image.load('graphics/player.png').convert_alpha(), 0, 0.75)
        self.image_const = self.image
        self.rect = self.image.get_rect(center=(960, 540))
        self.speed_x = 0
        self.speed_y = 0
        self.angle = -pi / 2

    def input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_z]:
            self.image = self.image_const
            mouse_pos = pygame.mouse.get_pos()
            hypotenus = sqrt((mouse_pos[0] - self.rect.x) ** 2 + (mouse_pos[1] - self.rect.y) ** 2)
            angle_cursor = acos(abs(mouse_pos[0] - self.rect.x) / hypotenus)

            if mouse_pos[0] > self.rect.x:
                if mouse_pos[1] < self.rect.y:
                    angle_cursor = -angle_cursor
            else:
                if mouse_pos[1] > self.rect.y:
                    angle_cursor = pi - angle_cursor
                else:
                    angle_cursor = -pi + angle_cursor

            if self.angle > 0 and angle_cursor > 0:
                if self.angle > angle_cursor:
                    self.move_angle(-0.05, self.angle - angle_cursor)
                else:
                    self.move_angle(0.05, angle_cursor - self.angle)
            elif self.angle < 0 and angle_cursor < 0:
                if self.angle < angle_cursor:
                    self.move_angle(0.05, angle_cursor - self.angle)
                else:
                    self.move_angle(-0.05, self.angle - angle_cursor)
            else:
                if self.angle > 0:
                    if self.angle - angle_cursor > pi:
                        self.move_angle(0.05, pi - self.angle + pi + angle_cursor)
                    else:
                        self.move_angle(-0.05, self.angle - angle_cursor)
                else:
                    if angle_cursor - self.angle > pi:
                        self.move_angle(-0.05, pi + self.angle + pi - angle_cursor)
                    else:
                        self.move_angle(0.05, angle_cursor - self.angle)

            if self.angle > pi:
                self.angle = self.angle - 2 * pi
            elif self.angle < -pi:
                self.angle = self.angle + 2 * pi

            self.speed_x = cos(self.angle) * hypotenus / 25
            self.speed_y = sin(self.angle) * hypotenus / 25

            if self.speed_x > 10:
                self.speed_x = 10
            elif self.speed_x < -10:
                self.speed_x = -10

            if self.speed_y > 10:
                self.speed_y = 10
            elif self.speed_y < -10:
                self.speed_y = -10

        if keys[pygame.K_q] and not(keys[pygame.K_z]):
            self.angle -= 0.05

            if self.angle > pi:
                self.angle = self.angle - 2 * pi
            elif self.angle < -pi:
                self.angle = self.angle + 2 * pi

        if keys[pygame.K_d] and not(keys[pygame.K_z]):
            self.angle += 0.05

            if self.angle > pi:
                self.angle = self.angle - 2 * pi
            elif self.angle < -pi:
                self.angle = self.angle + 2 * pi

        if keys[pygame.K_s] and not(keys[pygame.K_z]):
            self.speed_x = -cos(self.angle) * 2
            self.speed_y = -sin(self.angle) * 2

    def move(self):
        global camera_x_speed
        global camera_y_speed
        global camera_x
        global camera_y

        if self.speed_x > 0.1:
            self.speed_x -= 0.1
        elif self.speed_x < -0.1:
            self.speed_x += 0.1
        else:
            self.speed_x = 0

        if self.speed_y > 0.1:
            self.speed_y -= 0.1
        elif self.speed_y < -0.1:
            self.speed_y += 0.1
        else:
            self.speed_y = 0

        if self.rect.right > 2460 + camera_x and self.speed_x > 0:
            self.speed_x = 0
        elif self.rect.left < -540 + camera_x and self.speed_x < 0:
            self.speed_x = 0

        if self.rect.bottom > 2040 + camera_y and self.speed_y > 0:
            self.speed_y = 0
        elif self.rect.top < -960 + camera_y and self.speed_y < 0:
            self.speed_y = 0

        self.rect.x += self.speed_x + camera_x_speed
        self.rect.y += self.speed_y + camera_y_speed

        self.image = pygame.transform.rotozoom(self.image_const, degrees(-self.angle - pi / 2), 1)

    def move_angle(self, angle, difference):
        if difference >= 0.05:
            self.angle += angle
        else:
            self.angle += difference * angle / 0.05

    def camera(self):
        global camera_x_speed
        global camera_y_speed

        if self.rect.x > 1152:
            camera_x_speed = -abs(self.speed_x)
            self.rect.x = 1152
        elif self.rect.x < 768:
            camera_x_speed = abs(self.speed_x)
            self.rect.x = 768

        if self.rect.y > 648:
            camera_y_speed = -abs(self.speed_y)
            self.rect.y = 648
        elif self.rect.y < 432:
            camera_y_speed = abs(self.speed_y)
            self.rect.y = 432

        if camera_x_speed > 0.05:
            camera_x_speed -= 0.05
        elif camera_x_speed < -0.05:
            camera_x_speed += 0.05
        else:
            camera_x_speed = 0

        if camera_y_speed > 0.05:
            camera_y_speed -= 0.05
        elif camera_y_speed < -0.05:
            camera_y_speed += 0.05
        else:
            camera_y_speed = 0

    def shoot(self):
        missile.add(Missile(10, 0, 0, self.rect.center, self.angle))

    def update(self, shoot):
        if shoot:
            self.shoot()
        else:
            self.input()
            self.move()
            self.camera()


class Missile(pygame.sprite.Sprite):
    def __init__(self, speed, damage, image_index, pos, angle):
        super().__init__()
        self.speed_x = speed * cos(angle)
        self.speed_y = speed * sin(angle)
        self.damage = damage
        image_0 = pygame.transform.rotozoom(pygame.image.load('graphics/missile.png').convert_alpha(), 1, 0.25)
        images = [image_0]
        self.image = images[image_index]
        self.rect = self.image.get_rect(center=pos)
        self.image = pygame.transform.rotozoom(self.image, degrees(-angle - pi / 2), 1)

    def move(self):
        global camera_x
        global camera_y

        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        if self.rect.right > 2560 + camera_x:
            self.kill()
        elif self.rect.left < -640 + camera_x:
            self.kill()

        if self.rect.bottom > 2140 + camera_y:
            self.kill()
        elif self.rect.top < -1060 + camera_y:
            self.kill()

    def update(self):
        self.move()


def receive(server):
    global list_player
    global list_missile_receive

    while True:
        try:
            message = pickle.loads(server.recv(2048))
        except OSError:
            break

        while len(list_player) < message[0][4] + 1:
            list_player.append(None)

        list_player[message[0][4]] = message[0]
        list_missile_receive = message[1]


def send(server):
    global camera_x
    global camera_y
    global list_missile

    while True:
        try:
            server.send(pickle.dumps([[player.sprite.rect.center, player.sprite.angle, camera_x, camera_y], list_missile]))
            list_missile.clear()
        except OSError:
            break

        clock.tick(60)


def update_multiplayer(list_player, list_missile_receive):
    global camera_x
    global camera_y

    missile.empty()

    for k in range(len(list_player)):
        if not list_player[k] is None:
            image = pygame.transform.rotozoom(pygame.image.load('graphics/player.png'), degrees(-list_player[k][1] - pi / 2), 0.75)
            screen.blit(image, (list_player[k][0][0] - list_player[k][2] + camera_x, list_player[k][0][1] - list_player[k][3] + camera_y))

    for k in range(len(list_missile_receive)):
        missile.add(Missile(list_missile_receive[k][0], list_missile_receive[k][1], list_missile_receive[k][2], (list_missile_receive[k][3] + camera_x, list_missile_receive[k][4] + camera_y), list_missile_receive[k][5]))


pygame.init()

flag = pygame.FULLSCREEN
screen = pygame.display.set_mode((1920, 1080), flag)
pygame.display.set_caption('Projet')
clock = pygame.time.Clock()
camera_x_speed = 0
camera_y_speed = 0
camera_x = 0
camera_y = 0
game_active = False
multiplayer = False
ip = ''
port = 5555
list_player = []
list_missile = []
list_missile_receive = []

left_wall = pygame.Surface((1268, 4864))
right_wall = pygame.Surface((1268, 4864))
top_wall = pygame.Surface((5536, 932))
bottom_wall = pygame.Surface((5536, 932))

left_wall.fill((85, 91, 97))
right_wall.fill((85, 91, 97))
top_wall.fill((85, 91, 97))
bottom_wall.fill((85, 91, 97))

player = pygame.sprite.GroupSingle()
player.add(Player())

missile = pygame.sprite.Group()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            if multiplayer:
                server.close()

            pygame.quit()
            exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if multiplayer:
                    server.close()

                pygame.quit()
                exit()

        if event.type == pygame.MOUSEBUTTONDOWN and game_active:
            mouse_click = pygame.mouse.get_pressed()

            if mouse_click[0]:
                if multiplayer:
                    list_missile.append([10, 0, 0, player.sprite.rect.x - camera_x, player.sprite.rect.y - camera_y, player.sprite.angle])
                else:
                    player.update(True)

    if game_active:
        camera_x += camera_x_speed
        camera_y += camera_y_speed
        screen.fill((192, 233, 239))

        missile.draw(screen)

        if multiplayer:
            update_multiplayer(list_player, list_missile_receive)
        else:
            missile.update()

        player.update(False)
        player.draw(screen)

        screen.blit(left_wall, (-1808 + camera_x, -1892 + camera_y))
        screen.blit(top_wall, (-1808 + camera_x, -1892 + camera_y))
        screen.blit(right_wall, (2460 + camera_x, -1892 + camera_y))
        screen.blit(bottom_wall, (-1808 + camera_x, 2040 + camera_y))

    else:
        game_active = True
        multiplayer = True

        if multiplayer:
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.connect((ip, port))

            _thread.start_new_thread(receive, (server,))
            _thread.start_new_thread(send, (server,))

    pygame.display.update()
    clock.tick(60)

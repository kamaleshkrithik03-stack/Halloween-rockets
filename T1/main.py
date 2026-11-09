import os
import sys
import math
import random
import pygame 
import cv2 
from pygame.math import Vector2 
import config as cfg

pygame.init()
pygame.font.init()

screen = pygame.display.set_mode((cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT))
pygame.display.set_caption("halloween edition of the TVC rocket -it is now much harder")
clock = pygame.time.Clock()

MENU_BG = None
for ext in [".JPG"]:
    img_path = f"launch_update{ext}"
    if os.path.exists(img_path):
        MENU_BG = pygame.image.load(img_path).convert()
        MENU_BG = pygame.transform.scale(MENU_BG, (cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT))
        break

FONT_SMALL = pygame.font.SysFont("Consolas", 12)
FONT_MED = pygame.font.SysFont("Consolas", 15, bold=True)
FONT_LARGE = pygame.font.SysFont("Consolas", 20, bold=True)

class Slider:
    def __init__(self, x, y, w, h, min_val, max_val, val, label, fmt="{:.2f}"):
        self.rect = pygame.Rect(x, y, w, h)
        self.min_val = min_val
        self.max_val = max_val
        self.val = val
        self.label = label
        self.fmt = fmt
        self.dragging = False
        ratio = (val - min_val) / (max_val - min_val)
        self.handle_rect = pygame.Rect(x + int(ratio * w) - 6, y - 4, 12, h + 8)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.handle_rect.collidepoint(event.pos) or self.rect.collidepoint(event.pos):
                self.dragging = True
                self.update_val(event.pos[0])
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self.update_val(event.pos[0])

    def update_val(self, mouse_x):
        rel_x = max(self.rect.left, min(mouse_x, self.rect.right)) - self.rect.left
        ratio = rel_x / self.rect.width
        self.val = self.min_val + ratio * (self.max_val - self.min_val)
        self.handle_rect.centerx = self.rect.left + int(ratio * self.rect.width)

    def draw(self, surface):
        txt = f"{self.label}: {self.fmt.format(self.val)}"
        lbl_surf = FONT_SMALL.render(txt, True, cfg.COLOR_TEXT)
        bg_rect = pygame.Rect(self.rect.x - 3, self.rect.y - 18, lbl_surf.get_width() + 6, lbl_surf.get_height() + 4)
        pygame.draw.rect(surface, (15, 10, 25), bg_rect, border_radius=3)
        surface.blit(lbl_surf, (self.rect.x, self.rect.y - 16))
        pygame.draw.rect(surface, cfg.COLOR_SLIDER_BG, self.rect, border_radius=3)
        pygame.draw.rect(surface, cfg.COLOR_SLIDER_HANDLE, self.handle_rect, border_radius=4)

class Pumpkin:
    def __init__(self):
        self.radius = random.randint(14, 22)
        self.pos = Vector2(random.randint(40, cfg.SCREEN_WIDTH - 40), random.randint(-300, -50))
        self.vel = Vector2(random.uniform(-1.5, 1.5), random.uniform(2.0, 5.0))
    def update(self):
        self.pos += self.vel
        if self.pos.y > cfg.SCREEN_HEIGHT + 100:
                self.pos.y = random.randint(-800, -200)
                self.pos.x = random.randint(40, cfg.SCREEN_WIDTH - 40)
                self.vel.y = random.uniform(2.0, 5.0)
    def draw(self, surface, camera_y):
        x, y = int(self.pos.x), int(self.pos.y - camera_y)
        pygame.draw.circle(surface, cfg.COLOR_PUMPKIN, (x, y), self.radius)
        pygame.draw.rect(surface, (34, 139, 34), (x - 3, y - self.radius - 5, 6, 6))
        eye_offset = self.radius // 3
        pygame.draw.polygon(surface, (0, 0, 0), [(x - eye_offset, y - 3), (x - eye_offset - 4, y + 3), (x - eye_offset + 4, y + 3)])
        pygame.draw.polygon(surface, (0, 0, 0), [(x + eye_offset, y - 3), (x + eye_offset - 4, y + 3), (x + eye_offset + 4, y + 3)])
        pygame.draw.polygon(surface, (0, 0, 0), [(x, y + 4), (x - 6, y + 10), (x + 6, y + 10)])

class Cloud:
    def __init__(self):
        self.x = random.randint(0, cfg.SCREEN_WIDTH)
        self.y = random.randint(-3000, 100)
        self.width = random.randint(70, 130)
        self.height = random.randint(22, 45)
        self.speed = random.uniform(0.2, 0.6)

    def update(self):
        self.x += self.speed
        if self.x > cfg.SCREEN_WIDTH + 150:
            self.x = -150

    def draw(self, surface, camera_y):
        draw_y = int(self.y - camera_y * 0.4)
        if -60 < draw_y < cfg.SCREEN_HEIGHT + 60:
            pygame.draw.ellipse(surface, (230, 230, 240), (int(self.x), draw_y, self.width, self.height))

class Simulation:
    def play_emotional_damage_video(self, surface):
        if self.video_played:
            return

        video_path = None
        for f in os.listdir("."):
            if ("EMOTIONAL" in f.upper() or "DAMAGE" in f.upper()) and f.endswith(".mp4"):
                video_path = f
                break
        if not video_path and os.path.exists("EMOTIONALDAMAGE.mp4"):
            video_path = "EMOTIONALDAMAGE.mp4"

        if not video_path:
            return

        cap = cv2.VideoCapture(video_path)
        vid_clock = pygame.time.Clock()
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    cap.release()
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r or event.key == pygame.K_RETURN:
                        cap.release()
                        self.video_played = True
                        return

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT))
            frame_surf = pygame.surfarray.make_surface(frame.swapaxes(0, 1))

            surface.blit(frame_surf, (0, 0))
            pygame.display.flip()
            vid_clock.tick(30)

        cap.release()
        self.video_played = True
    
    def __init__(self):
        self.state = "MENU"
        self.camera_y = 0.0
        self.clouds = [Cloud() for _ in range(12)]
        self.sliders = {
            "kp": Slider(20, 40, 150, 10, 0.0, 5.0, cfg.KP_DEFAULT, "PID Kp", "{:.2f}"),   # ai copy pasted code from line 78 to line 82
            "ki": Slider(20, 80, 150, 10, 0.0, 0.5, cfg.KI_DEFAULT, "PID Ki", "{:.3f}"),
            "kd": Slider(20, 120, 150, 10, 0.0, 5.0, cfg.KD_DEFAULT, "PID Kd", "{:.2f}"),
            "wind": Slider(20, 160, 150, 10, -10.0, 10.0, 0.0, "wind speed", "{:.1f} m/s"),
            "mass": Slider(20, 200, 150, 10, 0.5, 3.0, cfg.ROCKET_DRY_MASS, "dry mass", "{:.2f} kg"),
            "fuel": Slider(20, 240, 150, 10, 0.5, 10.0, cfg.FUEL_INITIAL, "fuel mass", "{:.1f} kg"),
            "thrust": Slider(20, 280, 150, 10, 10.0, 200.0, cfg.THRUST_MAX, "max thrust", "{:.1f} N"),
        }
        self.reset_rocket()
        self.health = cfg.MAX_HEALTH
        self.pumpkins = [Pumpkin() for _ in range(7)]
        self.parachute_deployed = False
        self.game_over = False
        self.landing_success = False
        self.integral_error = 0.0
        self.prev_error = 0.0
        self.video_played = False

    def reset_rocket(self):
        self.pos = Vector2(cfg.SCREEN_WIDTH // 2, cfg.SCREEN_HEIGHT - cfg.GROUND_HEIGHT - cfg.ROCKET_HEIGHT // 2 - 15)
        self.vel = Vector2(0.0, 0.0)
        self.camera_y = 0.0
        self.angle = 0.0
        self.angular_vel = 0.0
        self.tvc_gimbal = 0.0
        self.fuel = self.sliders["fuel"].val
        self.health = cfg.MAX_HEALTH
        self.parachute_deployed = False 
        self.game_over = False
        self.landing_success = False
        self.integral_error = 0.0
        self.prev_error = 0.0
        self.video_played = False
    def calculate_com_cop(self):
        current_mass = self.sliders["mass"].val + self.fuel
        fuel_ratio = self.fuel / cfg.FUEL_INITIAL if cfg.FUEL_INITIAL > 0 else 0
        com_ratio = 0.45 + 0.10 * (1.0 - fuel_ratio)
        cop_ratio = 0.70
        com_y = com_ratio * cfg.ROCKET_HEIGHT
        cop_y = cop_ratio * cfg.ROCKET_HEIGHT
        stability_margin = (cop_y - com_y) / (cfg.ROCKET_WIDTH)
        return com_y, cop_y, stability_margin

    def update_physics(self, dt):  #now im kinda experienced enough to do this shi on my own
        for cloud in self.clouds:
            cloud.update()

        target_camera_y = self.pos.y - (cfg.SCREEN_HEIGHT * 0.4)
        self.camera_y = target_camera_y
        self.camera_y = min(0.0, self.camera_y) #basically i have to speel evrything tto py ofc not below gnd

        if self.state == "MENU" or self.game_over:
            return

        keys = pygame.key.get_pressed()
        thrusting = keys[pygame.K_SPACE] or keys[pygame.K_UP]
        if keys[pygame.K_p] and not self.parachute_deployed:
            self.parachute_deployed = True

        if self.state == "MENU" or self.game_over:
            return
        angle_error = 0.0 - self.angle
        self.integral_error += angle_error * dt
        derivative_error = (angle_error - self.prev_error) / dt if dt > 0 else 0
        self.prev_error = angle_error

        pid_out = (
            self.sliders["kp"].val * angle_error + #yeah from here to line 130 AI usage after that is kinda basic TVC knowledge
            self.sliders["ki"].val * self.integral_error +
            self.sliders["kd"].val * derivative_error
        )
        self.tvc_gimbal = max(-cfg.MAX_TVC_ANGLE, min(cfg.MAX_TVC_ANGLE, pid_out))

        if keys[pygame.K_LEFT]:
            self.tvc_gimbal = cfg.MAX_TVC_ANGLE
        elif keys[pygame.K_RIGHT]:
            self.tvc_gimbal = -cfg.MAX_TVC_ANGLE

        
        current_mass = self.sliders["mass"].val + self.fuel
        gravity_force = Vector2(0, current_mass * cfg.GRAVITY) #obviously w=mg

        thrust_force = Vector2(0, 0)
        if thrusting and self.fuel > 0:
            thrust_mag = self.sliders["thrust"].val
            thrust_angle_rad = math.radians(self.angle + self.tvc_gimbal)
            thrust_force = Vector2(-thrust_mag * math.sin(thrust_angle_rad), -thrust_mag * math.cos(thrust_angle_rad)) #yeah at this point im used to it had to google the formula for this one as cos for paralle and sin for perpendicular(My physics teachr is kinda like google at this point)
            self.fuel = max(0.0, self.fuel - cfg.FUEL_BURN_RATE * dt)

        wind_speed = self.sliders["wind"].val
        rel_vel = self.vel - Vector2(wind_speed, 0)
        cd = cfg.CD_PARACHUTE if self.parachute_deployed else cfg.CD_ROCKET

        drag_mult = 1.8 if self.parachute_deployed else 0.03
        drag_mag = 0.5 * cfg.AIR_DENSITY * rel_vel.length_squared() * cd * drag_mult
        drag_force = -rel_vel.normalize() * drag_mag if rel_vel.length() > 0 else Vector2(0, 0)
        
        net_force = gravity_force + thrust_force + drag_force #basic phy
        accel = net_force / current_mass

        self.vel += accel * dt
        self.pos += self.vel * dt

        self.angular_vel = self.tvc_gimbal * 0.1
        self.angle += self.angular_vel

        ground_y = cfg.SCREEN_HEIGHT - cfg.GROUND_HEIGHT - cfg.ROCKET_HEIGHT // 2
        if self.pos.y >= ground_y and self.vel.y > 0.5:
            self.pos.y = ground_y
            if self.vel.y < 8 and abs(self.angle) < 45.0:
                self.landing_success = True
            else:
                self.landing_success = False
            self.game_over = True
            self.vel = Vector2(0, 0)

        for pumpkin in self.pumpkins:
            pumpkin.update()
            if self.pos.distance_to(pumpkin.pos) < (pumpkin.radius + cfg.ROCKET_WIDTH):
                self.health -= 1
                pumpkin.pos.y = random.randint(-200, -40)
                pumpkin.pos.x = random.randint(40, cfg.SCREEN_WIDTH - 40)
                if self.health <= 0:
                    self.health = 0
                    self.game_over = True

    def draw(self, surface):
        surface.fill(cfg.COLOR_BG)

        for cloud in self.clouds:
            cloud.draw(surface, self.camera_y)
        
        pygame.draw.circle(surface, cfg.COLOR_MOON, (cfg.SCREEN_WIDTH - 80, int(80 - self.camera_y * 0.2)), 50)
        pygame.draw.circle(surface, (210, 210, 190), (cfg.SCREEN_WIDTH - 95, int(65 - self.camera_y * 0.2)), 10)
        pygame.draw.circle(surface, (210, 210, 190), (cfg.SCREEN_WIDTH - 80, int(80 - self.camera_y * 0.2)), 50)
        ground_draw_y = cfg.SCREEN_HEIGHT - cfg.GROUND_HEIGHT - int(self.camera_y)
        pygame.draw.rect(surface, cfg.COLOR_GRASS, (0, ground_draw_y, cfg.SCREEN_WIDTH, cfg.GROUND_HEIGHT + int(abs(self.camera_y))))

        for pumpkin in self.pumpkins:
            pumpkin.draw(surface, self.camera_y)

        if self.parachute_deployed:
            chute_x = int(self.pos.x)
            chute_y = int(self.pos.y - self.camera_y - cfg.ROCKET_HEIGHT // 2 - 40)
            pygame.draw.arc(surface, (250, 69, 0), (chute_x - 30, chute_y - 20, 60, 40), 0, math.pi, 5)
            pygame.draw.line(surface, (200, 200, 200), (chute_x - 28, chute_y), (int(self.pos.x), int(self.pos.y - cfg.ROCKET_HEIGHT // 2)), 1)
            pygame.draw.line(surface, (200, 200, 200), (chute_x + 28, chute_y), (int(self.pos.x), int(self.pos.y - cfg.ROCKET_HEIGHT // 2)), 1)

        rocket_surf = pygame.Surface((cfg.ROCKET_WIDTH + 20, cfg.ROCKET_HEIGHT + 30), pygame.SRCALPHA)
        rx, ry = 10, 0

        pygame.draw.rect(rocket_surf, cfg.COLOR_ROCKET_BODY, (rx, ry + 15, cfg.ROCKET_WIDTH, cfg.ROCKET_HEIGHT - 15), border_radius=3) 
        pygame.draw.polygon(rocket_surf, cfg.COLOR_ROCKET_NOSE, [(rx, ry + 15), (rx + cfg.ROCKET_WIDTH // 2, ry), (rx + cfg.ROCKET_WIDTH, ry + 15)])

        com_y, cop_y, stability_margin = self.calculate_com_cop()
        pygame.draw.circle(rocket_surf, (255, 255, 0), (rx + cfg.ROCKET_WIDTH // 2, int(ry + com_y)), 4)
        pygame.draw.circle(rocket_surf, (0, 255, 255), (rx + cfg.ROCKET_WIDTH // 2, int(ry + cop_y)), 4)

        keys = pygame.key.get_pressed()
        if (keys[pygame.K_SPACE] or keys[pygame.K_UP]) and self.fuel > 0 and not self.game_over:
            flame_h = random.randint(18, 30)
            flame_angle_rad = math.radians(self.tvc_gimbal) #ai coded again to line 234
            flame_x = rx + cfg.ROCKET_WIDTH // 2 + math.sin(flame_angle_rad) * flame_h * 0.5
            flame_y = ry + cfg.ROCKET_HEIGHT + math.cos(flame_angle_rad) * flame_h * 0.5
            pygame.draw.circle(rocket_surf, (255, 140, 0), (int(flame_x), int(flame_y)), 7)
            pygame.draw.circle(rocket_surf, (255, 255, 0), (int(flame_x), int(flame_y)), 4)

        rotated_surf = pygame.transform.rotate(rocket_surf, self.angle)
        new_rect = rotated_surf.get_rect(center=(int(self.pos.x), int(self.pos.y - self.camera_y)))
        surface.blit(rotated_surf, new_rect.topleft)

        for slider in self.sliders.values():
            slider.draw(surface)
        if self.state == "MENU":
            if MENU_BG:
                surface.blit(MENU_BG, (0, 0))
            else:
                surface.fill((15, 10, 25))

            title_surf = FONT_LARGE.render("Halloween style bs", True, (255, 95, 30))
            surface.blit(title_surf, (cfg.SCREEN_WIDTH // 2 - title_surf.get_width() // 2, 100))

            instr_surf = FONT_MED.render("Press SPACE or ENTER to Launch", True, (255, 255, 255))
            surface.blit(instr_surf, (cfg.SCREEN_WIDTH // 2 - instr_surf.get_width() // 2, cfg.SCREEN_HEIGHT - 150))

            for slider in self.sliders.values():
                slider.draw(surface)
            return

        telemetry_rect = pygame.Rect(cfg.SCREEN_WIDTH - 230, 20, 210, 210)
        pygame.draw.rect(surface, (15, 10, 25, 200), telemetry_rect, border_radius=8)
        pygame.draw.rect(surface, cfg.COLOR_TEXT, telemetry_rect, width=1, border_radius=8)

        tele_lines = [
            ("lets see your telemtery stats", cfg.COLOR_TEXT),
            (f"altitude: {cfg.SCREEN_HEIGHT - cfg.GROUND_HEIGHT - self.pos.y:.1f} m", (255, 255, 255)),
            (f"vertical velocity: {-self.vel.y:.1f} m/s", (255, 255, 255)),
            (f"horizontal velocity: {self.vel.x:.1f} m/s", (255, 255, 255)),
            (f"angle: {self.angle:.1f} degrees", (255, 255, 255)),
            (f"tvc gimbal: {self.tvc_gimbal:.1f}°", (255, 255, 255)),
            (f"fuel left: {self.fuel:.1f} kg", (255, 165, 0) if self.fuel < 3.0 else (255, 255, 255)),
            (f"stability margin: {stability_margin:.2f} cal", (0, 255, 255)),         
        ]
        for idx, (line, col) in enumerate(tele_lines):
            txt = FONT_SMALL.render(line, True, col)
            surface.blit(txt, (telemetry_rect.x + 10, telemetry_rect.y + 10 + idx * 24))

        health_rect = pygame.Rect(cfg.SCREEN_WIDTH - 230, 245, 210, 20)
        pygame.draw.rect(surface, (50, 20, 20), health_rect, border_radius=4)
        current_health_w = int((self.health / cfg.MAX_HEALTH) * 210)
        if current_health_w > 0:
            pygame.draw.rect(surface, (220, 50, 50), (health_rect.x, health_rect.y, current_health_w, 20), border_radius=4)
        pygame.draw.rect(surface, (255, 255, 255), health_rect, width=1, border_radius=4)
        health_txt = FONT_SMALL.render(f"lets see ur damage(hehehe): ({self.health}/{cfg.MAX_HEALTH} )* 100", True, (255, 255, 255))
        surface.blit(health_txt, (health_rect.x + 40, health_rect.y + 3))

        controls_txt = FONT_SMALL.render("space: thrust p: chute r: reset after that u figure it out(see README)", True, (180, 180, 180))
        surface.blit(controls_txt, (20, cfg.SCREEN_HEIGHT - 25))

        if self.game_over:

            if not self.landing_success or self.health <= 0:
                self.play_emotional_damage_video(surface)
            
            banner_rect = pygame.Rect(cfg.SCREEN_WIDTH // 2 - 190, cfg.SCREEN_HEIGHT // 2 - 75, 380, 150)
            pygame.draw.rect(surface, (10, 10, 15), banner_rect, border_radius=10)
            pygame.draw.rect(surface, cfg.COLOR_TEXT, banner_rect, width=2, border_radius=10)

            if self.landing_success:
                message = FONT_LARGE.render("successful landing good job to you but nxt time i will make sure this wont happen", True, (50, 255, 50))
                surface.blit(message, (banner_rect.centerx - message.get_width() // 2, banner_rect.y + 35))
            else:
                message2 = "rocket is destroyed ur mission unsuccesful but mine is all good" if self.health <= 0 else "rocket crashed,my mission is a success but urs is womp womp"
                message = FONT_LARGE.render(message2, True, (255, 50, 50))
                surface.blit(message, (banner_rect.centerx - message.get_width() // 2, banner_rect.y + 35))

            reset_message = FONT_MED.render("press r to restart(i dare ya)", True, (255, 255, 255))
            surface.blit(reset_message, (banner_rect.centerx - reset_message.get_width() // 2, banner_rect.y + 90))

def main():
    sim = Simulation()
    running = True
    while running:
        dt = clock.tick(cfg.FPS) / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    sim.reset_rocket()
                    sim.state = "MENU"
                elif event.key == pygame.K_p and sim.state == "PLAYING" and not sim.game_over: #my final hope
                    sim.parachute_deployed = True
                elif sim.state == "MENU" and (event.key == pygame.K_SPACE or event.key == pygame.K_RETURN):
                    sim.state = "PLAYING"
                    sim.reset_rocket()
            for slider in sim.sliders.values():
                slider.handle_event(event)

        sim.update_physics(dt)
        sim.draw(screen)
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
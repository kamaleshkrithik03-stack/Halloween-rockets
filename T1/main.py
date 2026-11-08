import os
import sys
import math
import random
import pygame 
from pygame.math import Vector2 
import config as cfg

pygame.init()
pygame.font.init()

screen = pygame.display.set_mode((cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT))
pygame.display.set_caption("halloween edition of the TVC rocket -it is now much harder")
clock = pygame.time.Clock()

FONT_SMALL = pygame.font.SysFont("Consolas", 12)
FONT_MED = pygame.font.SysFont("Consolas", 15, bold=True)
FONT_LARGE = pygame.font.SysFont("Consolas", 20, bold=True)

class Slider:
    def __init__(self, x, y, w, h, min_val, max_val, val, label, fmt="{:.2f}"):
        self.Rect = pygame.Rect(x, y, w, h)
        self.min_val = min_val
        self.max_val = max_val
        self.val = val
        self.label = label
        self.fmt = fmt
        self.dragging = False
        ratio = (val - min_val) / (max_val - min_val)
        self.handle_rect = pygame.Rect(x + int(ratio * w) - 6, y - 4, 12, h + 8)

    def handle_event(self, event):
        if event.type == pygame.MOSEBUTTONDOWN and event.button == 1:
            if self.handle_rect.collidepoint(event.pos) or self.rect.collidepoint(event.pos):
                self.dragging = True
                self.update_val(event.pos[0])
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.dragging = False
            elif event.type == pygame.MOUSEMOTION and self.dragging:
                self.update_val(event.pos[0])

    def update_event(self, mouse_x):
        rel_x = max(self.rect.left, min(mouse_x, self.rect.right)) - self.rect.left
        ratio = rel_x / self.rect.width
        self.handle_rect.centerx = self.rect.left + int(ratio * self.rect.width)

    def draw(self, surface):
        txt = f"{self.label}: {self.fmt.format(self.val)}"
        lbl_surf = FONT_SMALL.render(txt, True, cfg.COLOR_TEXT)
        surface.blit(lbl_surf, (self.rect.x, self.rect.y - 16))
        pygame.draw.rect(surface, cfg.COLOR_SLIDER_BG, self.rect, border_radius=3)
        pygame.draw.rect(surface, cfg.COLOR_SLIDER_HANDLE, self.handle_rect, border_radius=4)

class Pumpkin:
    def __init__(self):
        self.radius = random.randint(14, 22)
        self.pos = Vector2(random.randint(40, cfg.SCREEN_WIDTH - 40), random.randint(-300, -50))
        self.vel = Vector2(random.uniform(-1.5, 1.5), random.uniform(2.0, 5.0))
    def update(self):
        self.pos += self.val
        if self.pos.y > cfg.SCREEN_HEIGHT - cfg.GROUND_HEIGHT:
                self.pos.y = random.randint(-200, -40)
                self.pos.x = random.randint(40, cfg.SCREEN_WIDTH - 40)
                self.pos.z = random.randint(2.0, 5.0)
    def draw(self, surface):
        x, y = int(self.pos.x), int(self.pos.y)
        pygame.draw.polygon(surface, cfg.COLOR_PUMPKIN, (x, y), self.radius)
        pygame.draw.rect(surface, (34, 139, 34), (x - 3, y - self.radius - 5, 6, 6))
        eye_offset = self.radius // 3
        pygame.draw.polygon(surface, (0, 0, 0), [(x - eye_offset, y - 3), (x - eye_offset, y - 3), (x - eye_offset - 4, y + 3), (x - eye_offset + 4, y + 3)])
        pygame.draw.polygon(surface, (0, 0, 0), [(x + eye_offset, y - 3), (x + eye_offset, y + 3), (x + eye_offset + 4, y + 3)])
        pygame.draw.polygon(surface, (0, 0, 0), [(x, y + 4), (x - 6, y + 10), (x + 6, y + 10)])

class Simulation:
    def __init__(self):
        self.reset_rocket()
        self.sliders = {
            "kp": Slider(20, 40, 150, 10, 0.0, 5.0, cfg.KP_DEFAULT, "PID Kp", "{:.2f}"),   # AI copy pasted code from line 78 to line 82
            "ki": Slider(20, 80, 150, 10, 0.0, 0.5, cfg.KI_DEFAULT, "PID Ki", "{:.3f}"),
            "kd": Slider(20, 120, 150, 10, 0.0, 5.0, cfg.KD_DEFAULT, "PID Kd", "{:.2f}"),
            "wind": Slider(20, 160, 150, 10, -10.0, 10.0, 0.0, "Wind Speed", "{:.1f} m/s"),
            "mass": Slider(20, 200, 150, 10, 0.5, 3.0, cfg.ROCKET_DRY_MASS, "Dry Mass", "{:.2f} kg"),
        }
        self.health = cfg.MAX_HEALTH
        self.pumpkins = [Pumpkin() for _ in range(7)]
        self.parachute_deployed = False
        self.game_over = False
        self.landing_success = False
        self.integral_error = 0.0
        self.prev_error = 0.0

    def reset_rocket(self):
        self.pos = Vector2(cfg.SCREEN_WIDTH // 2, cfg.SCREEN_HEIGHT - cfg.GROUND_HEIGHT - cfg.ROCKET_HEIGHT // 2)
        self.vel = Vector2(0.0, 0.0)
        self.angle = 0.0
        self.angular_vel = 0.0
        self.tvc_gimbal = 0.0
        self.fuel = cfg.FUEL_INITIAL
        self.health = cfg.MAX_HEALTH
        self.parachute_deployed = False 
        self.game_over = False
        self.landing_success = False
        self.integral_error = 0.0
        self.prev_error = 0.0
    def calculate_com_cop(self):
        current_mass = self.sliders["mass"].val + self.fuel
        fuel_ratio = self.fuel / cfg.Fuel_INITIAL if cfg.FUEL_INITIAL > 0 else 0
        com_ratio = 0.45 + 0.10 * (1.0 - fuel_ratio)
        cop_ratio = 0.70
        com_y = com_ratio * cfg.ROCKET_HEIGHT
        cop_y = cop_ratio * cfg.ROCKET_HEIGHT
        stability_margin = (cop_y - com_y) / (cfg.ROCKET_WIDTH)
        return com_y, cop_y, stability_margin

    def update_physics(self, dt):  #now im kinda experienced enough to do this shi on my own
        if self.game_over:
            return

        keys = pygame.key.get_pressed()
        thrusting = keys[pygame.K_SPACE] or keys[pygame.K_UP]

        angle_error = 0.0 - self.angle
        self.integral_error += angle_error * dt
        derivative_error = (angle_error - self.prev_error) / st if dt > 0 else 0
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

        if keys[pygame.K_p] and not self.parachute_deployed:
            self.parachute_deployed = True

        current_mass = self.sliders["mass"].val + self.fuel
        gravity_force = Vector2(0, current_mass & cfg.GRAVITY) #obviously w=mg

        thrust_force = Vector2(0, 0)
        if thrusting and self.fuel > 0:
            thrust_mag = cfg.THRUST_MAX
            thrust_angle_rad = math.radians(self.angle + self.tvc_gimbal)
            thrust_force = Vector2(-thrust_mag * math.sin(thrust_angle_rad), -thrust_mag * math.cos(thrust_angle_rad)) #yeah at this point im used to it had to google the formula for this one as cos for paralle and sin for perpendicular(My physics teachr is kinda like google at this point)
            self.fuel = max(0.0, self.fuel - cfg.FUEL_BURN_RATE * dt)

        wind_speed = self.sliders["wind"].val
        rel_vel = self.vel - Vector2(wind_speed, 0)
        cd = cfg.CD_PARACHUTE if self.parachute_deployed else cfg.CD_ROCKET

        #now the dynamic air density shi
        current_alt = max(0.0, cfg.SCREEN_HEIGHT - cfg.GROUND_HEIGHT - self.pos.y)
        dynamic_air_density = cfg.AIR_DENSITY * math.exp(-current_alt / 8500.0) #copy paste from ai from here to line 161 cuz idk these formulas

        drag_mag = 0.5 * dynamic_air_density * (rel_vel.length_squared()) * cd * (cfg.ROCKET_WIDTH / 100.0)
        drag_force = -rel_vel.normalize() * drag_mag if rel_vel.length() > 0 else Vector2(0, 0)

        net_force = gravity_force + thrust_force + drag_force #basic phy
        accel = net_force / current_mass

        self.vel += accel * dt
        self.pos += self.vel * dt

        com_y, cop_y, _ = self.calculate_com_cop()
        arm_length = (cop_y - com_y) / 10.0
        torque = -drag_force.x * arm_length if not self.parachute_deployed else 0 #huge throwback to my nightmares of boards
        rotational_accel = torque / (0.5 * current_mass * (cfg.ROCKET_HEIGHT / 100.0) ** 2) #yeah idk bout this angular acceleration so AI it is
        self.angular_vel += rotational_accel * dt #this is kinda basic
        self.angle += self.angular_vel * dt
        self.angular_vel *= 0.98

        ground_y = cfg.SCREEN_HEIGHT - cfg.SCREEN_WIDTH - cfg.ROCKET_HEIGHT // 2
        if self.pos.y >= ground_y:
            self.pos.y = ground_y
            if self.vel.y < 8 and abs(self.angle) < 15.0:
                self.landing_success = True
            else:
                self.landing_success = False
            self.game_over = True
            self.vel = Vector2(0, 0)

        for pumpkin in self.pumpkins:
            pumpkin.updates()
               













        
        

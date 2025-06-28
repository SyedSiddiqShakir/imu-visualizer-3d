import math
import time
import random as rnd
from vpython import *
from config import *

class EffectsManager:
    def __init__(self):
        self.particles = []
        self.trails = []
        self.color_mode = 0  #0=normal, 1=rainbow, 2=danger
        self.total_movement = 0
        self.frame_count = 0
        
    def create_particle_burst(self, pos, count=10):
        for _ in range(count):
            particle = sphere(
                pos=pos + vector(rnd.uniform(-0.2, 0.2), rnd.uniform(-0.2, 0.2), rnd.uniform(-0.2, 0.2)),
                radius=PARTICLE_SIZE,
                color=vector(rnd.random(), rnd.random(), rnd.random()),
                velocity=vector(rnd.uniform(-2, 2), rnd.uniform(-2, 2), rnd.uniform(-2, 2)),
                lifetime=PARTICLE_LIFETIME
            )
            self.particles.append(particle)
    
    def update_particles(self):
        to_remove = []
        
        for particle in self.particles:
            #update position
            particle.pos += particle.velocity * 0.02
            particle.velocity *= 0.98  # Damping
            particle.lifetime -= 1
            
            #fade out
            alpha = particle.lifetime / PARTICLE_LIFETIME
            particle.opacity = alpha
            particle.radius *= 0.99
            
            #remove if expired
            if particle.lifetime <= 0 or particle.radius < 0.01:
                to_remove.append(particle)
        
        #clean up expired particles
        for particle in to_remove:
            particle.visible = False
            self.particles.remove(particle)
    
    def create_trail_point(self, pos):
        trail_point = sphere(
            pos=vector(pos.x, pos.y, pos.z),
            radius=0.02,
            color=color.cyan,
            opacity=0.6,
            lifetime=TRAIL_LIFETIME
        )
        self.trails.append(trail_point)
        
        #limit trail length
        if len(self.trails) > TRAIL_LENGTH:
            old_point = self.trails.pop(0)
            old_point.visible = False
    
    def update_trails(self):
        to_remove = []
        
        for i, point in enumerate(self.trails):
            point.lifetime -= 1
            point.opacity = point.lifetime / TRAIL_LIFETIME * 0.6
            point.radius *= 0.998
            
            if point.lifetime <= 0:
                to_remove.append(point)
        
        for point in to_remove:
            point.visible = False
            self.trails.remove(point)
    
    def get_dynamic_color(self, pitch, roll):
        if self.color_mode == 0:  #normal mode
            return color.orange
        elif self.color_mode == 1:  #rainbow mode
            hue = (time.time() * 2) % (2 * math.pi)
            return vector(
                0.5 + 0.5 * math.sin(hue),
                0.5 + 0.5 * math.sin(hue + 2.094),  #120 degrees
                0.5 + 0.5 * math.sin(hue + 4.188)   #240 degrees
            )
        elif self.color_mode == 2:  #danger mode
            intensity = (abs(pitch) + abs(roll)) / 180.0
            return vector(1, 1-intensity, 1-intensity)  #white to red
        
        return color.orange
    
    def cycle_color_mode(self):
        self.color_mode = (self.color_mode + 1) % 3
        modes = ["Normal", "Rainbow 🌈", "Danger ⚠️"]
        return modes[self.color_mode]
    
    def reset_effects(self):
        for p in self.particles:
            p.visible = False
        for t in self.trails:
            t.visible = False
        self.particles.clear()
        self.trails.clear()
        self.total_movement = 0
    
    def update_frame_count(self):
        self.frame_count += 1
    
    def animate_rainbow_axes(self, x_axis, y_axis, z_axis):
        if self.color_mode == 1:
            phase = self.frame_count * 0.1
            x_axis.color = vector(1, 0.5 + 0.5 * math.sin(phase), 0)
            y_axis.color = vector(0.5 + 0.5 * math.sin(phase + 2), 1, 0)
            z_axis.color = vector(0, 0.5 + 0.5 * math.sin(phase + 4), 1)
    
    def animate_ground(self, ground):
        if self.frame_count % 30 == 0:  #every half second
            ground.color = vector(0.3, 0.3, 0.3 + 0.1 * math.sin(self.frame_count * 0.05))
    
    def add_random_sparkles(self, pos, movement):
        if rnd.random() < 0.005 and movement > SIGNIFICANT_MOVEMENT:
            spark_pos = pos + vector(rnd.uniform(-1,1), rnd.uniform(-1,1), rnd.uniform(-1,1))
            self.create_particle_burst(spark_pos, 5)
    
    def get_status_text(self):
        modes = ["Normal", "Rainbow 🌈", "Danger ⚠️"]
        return f"Mode: {modes[self.color_mode]} | Movement: {self.total_movement:.1f}° | Particles: {len(self.particles)}"

def play_beep(frequency=BEEP_FREQUENCY, duration=BEEP_DURATION):
    try:
        import winsound
        winsound.Beep(int(frequency), int(duration * 1000))
    except:
        #fallback: print sound effect
        print(f"*BEEP* ({frequency}Hz)")
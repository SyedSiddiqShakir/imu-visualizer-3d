import serial
import threading
import re
import math
import time
import random as rnd
from vpython import *
from config import *
from effects_manager import EffectsManager, play_beep

#global serial communication variables
pitch = 0
roll = 0
new_data = False
data_lock = threading.Lock()
shake_detected = False
extreme_tilt_warning = False

def read_serial():
    global pitch, roll, new_data, shake_detected
    
    try:
        ser = serial.Serial(PORT, BAUD, timeout=TIMEOUT)
        print(f"Connected to {PORT}")
        ser.flushInput()
    except Exception as e:
        print(f"Serial connection failed: {e}")
        return
    
    prev_pitch, prev_roll = 0, 0
    rapid_changes = 0
    
    while True:
        try:
            line = ser.readline().decode('utf-8').strip()
            if not line:
                continue
                
            print(f"RX: {line}")
            
            #parsing the line
            if "Tilting up" in line:
                angle = int(re.search(r'(\d+)', line).group(1))
                with data_lock:
                    pitch = -angle  #negative for up
                    new_data = True
                    
            elif "Tilting down" in line:
                angle = int(re.search(r'(\d+)', line).group(1))
                with data_lock:
                    pitch = angle   #positive for down
                    new_data = True
                    
            elif "Tilting left" in line:
                angle = int(re.search(r'(\d+)', line).group(1))
                with data_lock:
                    roll = -angle   #negative for left
                    new_data = True
                    
            elif "Tilting right" in line:
                angle = int(re.search(r'(\d+)', line).group(1))
                with data_lock:
                    roll = angle    #positive for right
                    new_data = True
            
            #detect rapid movement (shake detection), right now works as extreme detection, might change the logic later 
            with data_lock:
                if abs(pitch - prev_pitch) > SHAKE_THRESHOLD or abs(roll - prev_roll) > SHAKE_THRESHOLD:
                    rapid_changes += 1
                    if rapid_changes > SHAKE_COUNT_TRIGGER:
                        shake_detected = True
                        rapid_changes = 0
                else:
                    rapid_changes = max(0, rapid_changes - 1)
                
                prev_pitch, prev_roll = pitch, roll
                    
        except Exception as e:
            print(f"Parse error: {e}")
            continue

def calculate_orientation(pitch_deg, roll_deg):
    #convert to radians
    p = math.radians(pitch_deg)
    r = math.radians(roll_deg)
    
    #calculate rotation matrix elements
    cos_p, sin_p = math.cos(p), math.sin(p)
    cos_r, sin_r = math.cos(r), math.sin(r)
    
    #box axis (length direction), X axis after rotation
    axis = vector(
        cos_r,
        sin_r * cos_p,
        sin_r * sin_p
    )
    
    #box up direction, Y axis after rotation  
    up = vector(
        -sin_r,
        cos_r * cos_p,
        cos_r * sin_p
    )
    
    return axis, up

def setup_scene():
    scene = canvas(
        title="🚀 Enhanced IMU Tilt Visualizer 🚀",
        width=WINDOW_WIDTH,
        height=WINDOW_HEIGHT,
        background=color.gray(0.05)
    )
    
    #enhanced world axes with labels
    x_axis = arrow(pos=vector(0,0,0), axis=vector(2,0,0), color=color.red, shaftwidth=0.05)
    y_axis = arrow(pos=vector(0,0,0), axis=vector(0,2,0), color=color.green, shaftwidth=0.05)
    z_axis = arrow(pos=vector(0,0,0), axis=vector(0,0,2), color=color.blue, shaftwidth=0.05)
    
    #axis labels
    label(pos=vector(2.2,0,0), text="X", color=color.red, height=10)
    label(pos=vector(0,2.2,0), text="Y", color=color.green, height=10)
    label(pos=vector(0,0,2.2), text="Z", color=color.blue, height=10)
    
    #create IMU box with glow effect
    imu = box(
        pos=vector(0,0,0),
        length=BOX_LENGTH,
        height=BOX_HEIGHT, 
        width=BOX_WIDTH,
        color=color.orange,
        opacity=0.8
    )
    
    #add a glowing outline
    imu_outline = box(
        pos=vector(0,0,0),
        length=BOX_LENGTH + 0.1,
        height=BOX_HEIGHT + 0.05, 
        width=BOX_WIDTH + 0.05,
        color=color.white,
        opacity=0.2
    )
    
    #ground plane for reference
    ground = box(
        pos=vector(0,-2,0),
        length=8,
        height=0.1,
        width=8,
        color=color.gray(0.3),
        opacity=0.3
    )
    
    #enhanced info display
    info = label(
        pos=vector(0, -3.5, 0),
        text="🔄 Waiting for data...",
        height=14,
        color=color.white
    )
    
    #status display
    status = label(
        pos=vector(0, -4, 0),
        text="Mode: Normal | Movement: 0°",
        height=10,
        color=color.cyan
    )
    
    #controls display
    controls = label(
        pos=vector(0, 3.5, 0),
        text="🎮 Controls: C=Color Mode | R=Reset | Shake device for particles!",
        height=10,
        color=color.yellow
    )
    
    return scene, (x_axis, y_axis, z_axis), imu, imu_outline, ground, info, status, controls

def main():
    global pitch, roll, new_data, shake_detected, extreme_tilt_warning
    
    #initialize effects manager
    effects = EffectsManager()
    
    #start serial reader thread
    serial_thread = threading.Thread(target=read_serial, daemon=True)
    serial_thread.start()
    
    #setup VPython scene
    scene, axes, imu, imu_outline, ground, info, status, controls = setup_scene()
    x_axis, y_axis, z_axis = axes
    
    print("🎉 Enhanced visualization started!")
    print("Features: Particle effects, color modes, trails, shake detection")
    print("Controls: Press 'c' to cycle color modes, 'r' to reset")
    
    #animation variables
    prev_pitch, prev_roll = 0, 0
    
    #keyboard controls
    def on_keydown(evt):
        key = evt.key.lower()
        if key == 'c':
            mode_name = effects.cycle_color_mode()
            status.text = effects.get_status_text()
            play_beep(MODE_CHANGE_BEEP + effects.color_mode * 200)
        elif key == 'r':
            effects.reset_effects()
            play_beep(1500)
    
    scene.bind('keydown', on_keydown)
    
    #main animation loop
    while True:
        rate(REFRESH_RATE)
        effects.update_frame_count()
        
        #update effects
        effects.update_particles()
        effects.update_trails()
        
        #check for new data
        with data_lock:
            if new_data:
                current_pitch = pitch
                current_roll = roll
                new_data = False
                
                #calculate movement
                movement = abs(current_pitch - prev_pitch) + abs(current_roll - prev_roll)
                effects.total_movement += movement
                
                #update visualization
                axis, up = calculate_orientation(current_pitch, current_roll)
                imu.axis = axis
                imu.up = up
                imu_outline.axis = axis
                imu_outline.up = up
                
                #dynamic colors
                imu.color = effects.get_dynamic_color(current_pitch, current_roll)
                
                #extreme tilt warning
                extreme_angle = max(abs(current_pitch), abs(current_roll))
                if extreme_angle > EXTREME_TILT_THRESHOLD:
                    if not extreme_tilt_warning:
                        extreme_tilt_warning = True
                        play_beep(EXTREME_TILT_BEEP, 0.2)
                        effects.create_particle_burst(imu.pos, 20)
                    #pulsing effect for extreme tilts
                    pulse = 0.8 + 0.2 * math.sin(effects.frame_count * 0.3)
                    imu.opacity = pulse
                    imu_outline.opacity = 0.4 * pulse
                else:
                    extreme_tilt_warning = False
                    imu.opacity = 0.8
                    imu_outline.opacity = 0.2
                
                #create trail
                if movement > MOVEMENT_THRESHOLD:
                    effects.create_trail_point(imu.pos)
                
                #shake detection
                if shake_detected:
                    shake_detected = False
                    effects.create_particle_burst(imu.pos, 30)
                    play_beep(SHAKE_BEEP, 0.1)
                    print("🎆 Shake detected! Particle burst!")
                
                #update displays
                tilt_icons = "📱" if extreme_angle < 15 else "📱⚠️" if extreme_angle < 45 else "📱🚨"
                info.text = f"{tilt_icons} Pitch: {current_pitch:+.0f}°   Roll: {current_roll:+.0f}°   Total Tilt: {extreme_angle:.1f}°"
                status.text = effects.get_status_text()
                
                prev_pitch, prev_roll = current_pitch, current_roll
                
                #fun random particle effects
                effects.add_random_sparkles(imu.pos, movement)
        
        #ambient animations
        effects.animate_ground(ground)
        effects.animate_rainbow_axes(x_axis, y_axis, z_axis)

if __name__ == "__main__":
    main()
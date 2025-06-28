# IMU Tilt Visualizer

A real-time 3D visualization tool for IMU tilt data with particle effects, color modes, and a bit more.

## Features

- **Real-time 3D visualization** of IMU pitch and roll data
- **Particle system** with burst effects on shake detection
- **Multiple color modes**: Normal, Rainbow, and Danger modes
- **Interactive controls** for mode switching and reset
- **Audio feedback** for various events (Windows only)

## Controls

- **C** - Cycle through color modes (Normal, Rainbow & Danger)
- **R** - Reset all effects and counters
- **Shake your IMU device** - Triggers particle burst effects!

## Requirements

**Required Python packages:**
- `pyserial` - For serial communication with IMU device (Arduino NANO 33 BLE Sense Rev 2 in this case)
- `vpython` - For 3D visualization and graphics

**Optional (Windows only):**
- `winsound` - For audio feedback (usually included with Python on Windows)


## Project File Structure

```
imu-visualizer-3d/
├── main.py              # Main application and serial communication
├── effects_manager.py   # Visual effects and particle system
├── config.py            # Configuration settings
├── arduino_pull.ino     # Arduino code file to be uploaded to flash
├── README.md            
└── .gitignore         
```

## Configuration

All settings can be modified in `config.py`:

### Serial Communication
- `PORT` - Serial port (e.g., "COM4", "/dev/ttyUSB0")
- `BAUD` - Baud rate (default: 9600)
- `TIMEOUT` - Serial timeout in seconds
- and some more

## Acknowledgments

- Built with [VPython](https://vpython.org/) for 3D visualization
- Uses [PySerial](https://pyserial.readthedocs.io/) for serial communication
- Inspired by a professor who always loves visualising data

---
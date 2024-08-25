# bottle_flip_simulation
bottle flipping simulation for the IYPT 2018 question of water bottle

# Constants
gravity = vector(0, -9.8, 0)  # Standard gravity in m/s^2
dt = 0.01
drag = 800
t = 0

# Create the hollow bottle (approximated as a cylinder with a thin wall)
bottle_radius = 0.5
bottle_height = 2
bottle_thickness = 0.01

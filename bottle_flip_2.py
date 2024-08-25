from vpython import *
import random

# Setup the scene
scene = canvas(width=1200, height=800)
scene.title = "Bottle Flipping Simulation with Water"
scene.background = color.white

# Create the floor
floor = box(pos=vector(0, -0.5, 0), size=vector(10, 1, 10), color=color.green)

# Create the hollow bottle (approximated as a cylinder with a thin wall)
bottle_radius = 0.5
bottle_height = 2
bottle_thickness = 0.01

bottle = cylinder(pos=vector(0, bottle_height / 2, 0), axis=vector(0, 1, 0),
                  radius=bottle_radius, length=bottle_height, color=color.blue,
                  opacity=0.3)

bottle_wall = cylinder(pos=bottle.pos, axis=bottle.axis, radius=bottle.radius + bottle_thickness,
                       length=bottle.length, color=color.blue, opacity=0.5)

bottle.velocity = vector(0, 0, 0)
bottle.angular_velocity = vector(0, 0, 0)

# Constants
gravity = vector(0, -9.8, 0)  # Standard gravity in m/s^2
dt = 0.01
drag = 800
t = 0

# Creating Particles
n = 0
N = 35
particles = []
q0 = 1e-4

while n < N:
    rt = vector(random.uniform(-bottle_radius, bottle_radius),
                random.uniform(0, bottle_height),
                random.uniform(-bottle_radius, bottle_radius))
    
    if mag(rt) <= bottle_radius:  # Ensure particles are within the bottle
        n += 1
        particles.append(sphere(pos=rt + bottle.pos, radius=0.05, color=color.cyan, q=q0))

# Box-Muller Transform To Create a Normal Distribution
def normal(avg, std):
    u1 = random.uniform(0, 1)
    u2 = random.uniform(0, 1)
    vt = sqrt(-2 * log(u1)) * cos(2 * pi * u2)
    vt = vt * std + avg
    return vt

# Initial Conditions for Particles
m = 0.01
K = 10000

for particle in particles:
    particle.m = m
    v = normal(0, 1)
    particle.v = v * norm(vector(2 * random.uniform(0, 1) - 1,
                                 2 * random.uniform(0, 1) - 1,
                                 2 * random.uniform(0, 1) - 1))
    particle.p = particle.v * m
    particle.F = vector(0, 0, 0)

# Function to apply a flip
def flip_bottle():
    # Random upward force and random angular velocity
    bottle.velocity = vector(0, random.uniform(5, 15), 0)
    bottle.angular_velocity = vector(random.uniform(-10, 10), 0, random.uniform(-10, 10))

    # Give the particles some initial velocity
    for particle in particles:
        particle.velocity = vector(random.uniform(-2, 2), random.uniform(-2, 2), random.uniform(-2, 2))

# Run the simulation
running = False

def toggle_running():
    global running
    running = not running
    if running:
        flip_bottle()

scene.bind('click', toggle_running)

while True:
    rate(100)

    if running:
        # Update bottle's position and rotation
        bottle.velocity += gravity * dt
        bottle.pos += bottle.velocity * dt
        bottle_wall.pos = bottle.pos
        bottle.rotate(angle=mag(bottle.angular_velocity) * dt, axis=bottle.angular_velocity, origin=bottle.pos)
        bottle_wall.rotate(angle=mag(bottle.angular_velocity) * dt, axis=bottle.angular_velocity, origin=bottle.pos)

        # Check for collision with the floor
        if bottle.pos.y - bottle_height / 2 <= floor.pos.y + floor.size.y / 2:
            # Correct the position to just above the floor
            bottle.pos.y = floor.pos.y + floor.size.y / 2 + bottle_height / 2
            # Reflect the velocity with energy loss
            bottle.velocity.y = -bottle.velocity.y * 0.5
            # Reduce angular velocity due to friction
            bottle.angular_velocity *= 0.5

            # Ensure the bottle doesn't phase into the floor
            if bottle.velocity.y > 0 and mag(bottle.velocity) < 0.1:
                bottle.velocity.y = 0
                bottle.angular_velocity *= 0.1

            # Stop the simulation if the bottle has settled
            if mag(bottle.velocity) < 0.1 and mag(bottle.angular_velocity) < 0.1:
                running = False

        # Update particles' positions
        for particle in particles:
            particle.F = -particle.p * drag + particle.m * gravity

            # Add forces due to other particles (e.g., electrostatic forces)
            for other in particles:
                if particle != other:
                    rt = other.pos - particle.pos
                    if mag(rt) > 0.01 and mag(rt) < 1.5:
                        particle.F += K * particle.q * other.q * norm(rt) / (mag(rt) ** 2)
                        particle.F += -3 * K * particle.q * other.q * norm(rt) / (mag(rt) ** 3)

            particle.p += particle.F * dt
            particle.pos += particle.p / particle.m * dt

            # Keep particles within the bottle's bounds
            if mag(particle.pos - bottle.pos) > bottle_radius:
                particle.pos = bottle.pos + norm(particle.pos - bottle.pos) * bottle_radius

    t += dt

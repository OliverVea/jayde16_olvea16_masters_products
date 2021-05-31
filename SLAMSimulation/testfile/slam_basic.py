# %% Import
import sys
import os
import json

from math import atan2, pi

import matplotlib.pyplot as plt

from tqdm import tqdm

cwd = os.path.abspath(os.path.join('.'))
cwd = 'd:\\WindowsFolders\\Code\\Master\\jayde16_olvea16_masters_2021\\robsim'

if cwd not in sys.path:
    sys.path.append(cwd)

print(f'cwd: {cwd}')

import robsim as rs

print(f'robsim module version: {rs.__version__}')

from math import sin, cos
import random

# %% Create route

landmark_positions = [
    rs.Point(0, 0.2),
    rs.Point(0.5, 1),
    rs.Point(-0.3, -0.5),
    rs.Point(0, 0)
]

n_landmarks = len(landmark_positions)
n_route = 20

n = n_landmarks + n_route

def propagate(x, y, theta, v: float = 1, omega: float = 0.1, dt: float = 0.1):
    return x + v * cos(theta) * dt, y + v * sin(theta) * dt, theta + omega * dt

x, y, theta = 0, 0, 0
route = [rs.Pose(x, y, theta)]

for i in range(n_route):
    x, y, theta = propagate(x, y, theta,
        v = 0.5,
        omega = 2 * i / (n_route - 1) + 1,
        dt=0.5    
    )
    route.append(rs.Pose(x, y, theta))

chance = 0.30

landmark_measurements = []
for pose in route:
    measurements = []
    for i, point in enumerate(landmark_positions):
        if random.random() < chance:
            measurements.append(i)
    landmark_measurements.append(measurements)

relative_route = [b.relative(a) for a, b in zip(route[:-1], route[1:])]

# %% SLAM

slam = rs.Slam(route[0], n_landmarks, None, None)

for pose, odometry, landmarks in tqdm(zip(route[1:], relative_route, landmark_measurements[1:])):
    landmark_constraints = [(i, landmark_positions[i].relative(pose)) for i in landmarks]

    slam.add_constraints(odometry, landmark_constraints)
    slam.optimize()

print(f'Printing SLAM route with {len(slam.route)} nodes and {len([pose for pose in slam.landmarks if pose != None])} landmarks.')

fig = slam.plot(plot_landmark_measurements=True)
plt.show()

plt.spy(slam.get_sparsity())

# %% State Check
route, landmarks = slam.route, slam.landmarks

state = rs.Slam._get_state(route, landmarks)

print(f'State length: {len(state)}')

_route, _landmarks = rs.Slam._from_state(state, n_landmarks)

print(f'Route: {route == _route}\nLandmarks: {landmarks == _landmarks}')

print('Route:')
for a, b in zip(route, _route):
    print(f'{a == b}: {a} - {b}')
print('')

print('Landmarks:')
for a, b in zip(landmarks, _landmarks):
    print(f'{a == b}: {a} - {b}')
# %%

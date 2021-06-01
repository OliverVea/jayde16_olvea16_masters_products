import csv
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pyproj import Transformer
from scipy.spatial.transform import Rotation as R


def dist(a, b):
    return np.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)

def nmea_to_srs(coordinate: tuple, transformer):
    coordinate_4326 = [int(x/100) + (x - int(x / 100) * 100) / 60 for x in coordinate]
    return np.array(transformer.transform(coordinate_4326[0], coordinate_4326[1]))
 
def get_scale_and_coord(filepath, img_offset, img_step):
    gnss_file = pd.read_csv(filepath)

    # GPS coordinates are transformed to 'EPSG:25832' to get distances in meters.
    srs_in = 'EPSG:4326'
    srs_out = 'EPSG:25832'
    transformer = Transformer.from_crs(srs_in, srs_out)

    timestamps = [row.time for _, row in gnss_file.iterrows()]
    coordinates = [nmea_to_srs((float(row.lat_nmea), float(row.lon_nmea)), transformer) for _, row in gnss_file.iterrows()]

    timestamps = timestamps[img_offset::img_step]
    coordinates = coordinates[img_offset::img_step]

    first_coord = coordinates[0]

    scales = []
    last_new_idx = 0
    velocity = 0
    for i, coord in enumerate(coordinates):
        if (coord[0] != coordinates[last_new_idx][0]).all():
            velocity = sum(abs(coord - coordinates[last_new_idx])) / (timestamps[i] - timestamps[last_new_idx])
            #velocity = np.linalg.norm((coord - coordinates[last_new_idx])) / (timestamps[i] - timestamps[last_new_idx])
            last_new_idx = i
        
        if i > 0:
            scales.append(velocity * (timestamps[i] - timestamps[i - 1])) 
    return scales, first_coord

def get_orientations(imu_filepath, gnss_filepath):
    imu_file = pd.read_csv(imu_filepath)
    gnss_file = pd.read_csv(gnss_filepath)

    timestamps = [row.time for _, row in gnss_file.iterrows()]
    data = np.array([[row.time, -row.yaw_pitch_roll_0 + 123, row.yaw_pitch_roll_1, row.yaw_pitch_roll_2] for _, row in imu_file.iterrows()])
    yprs = []
    for time in timestamps:
        idx = np.argmin(abs(data[:,0] - time))
        yprs.append(data[idx,1:])

    orientations = [R.from_euler('yxz', ypr, degrees=True).as_matrix() for ypr in yprs]
    return orientations

def save_route_as_csv(route, filename, first_coord):
    x = [-pose[0, 3] for pose in route]
    z = [-pose[2, 3] for pose in route]
    if filename.split('.')[-1] != 'csv': filename = filename + '.csv'
    with open(filename, mode='w') as route_file:
        file_writer = csv.writer(route_file, delimiter=',')
        file_writer.writerow(['x','y'])
        for i in range(len(x)):
            file_writer.writerow([first_coord[0] + z[i], first_coord[1] + x[i]])

def save_2droute_as_csv(route, filename, first_coord):
    x = [-pose[0] for pose in route]
    z = [-pose[1] for pose in route]
    if filename.split('.')[-1] != 'csv': filename = filename + '.csv'
    with open(filename, mode='w') as route_file:
        file_writer = csv.writer(route_file, delimiter=',')
        file_writer.writerow(['x','y'])
        for i in range(len(x)):
            file_writer.writerow([first_coord[0] + z[i], first_coord[1] + x[i]])


def plot_route(poses, plot_type = 'scatter', projection = '2d', first_coord=[0, 0, 0]):
    fig = plt.figure()
    if projection == '3d':
        ax = fig.gca(projection=projection)
    else:
        ax = fig.gca()

    ax.set_xlabel('X')
    ax.set_ylabel('Z')
    ax.ticklabel_format(useOffset=False, style='plain')

    x = [-pose[0, 3] + first_coord[2] for pose in poses]
    y = [pose[1, 3] + first_coord[1] for pose in poses]
    z = [-pose[2, 3] + first_coord[0] for pose in poses]

    if projection == '3d':
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')

        interval = max(max(x) - min(x), max(y) - min(y), max(z) - min(z))
        x_mean, y_mean, z_mean = np.mean(x), np.mean(y), np.mean(z)
        ax.set_xlim3d([x_mean - interval, x_mean + interval])
        ax.set_ylim3d([y_mean - interval, y_mean + interval])
        ax.set_zlim3d([z_mean - interval, z_mean + interval])
        
        if plot_type == 'quiver':
            orientations = [np.dot(np.array([0, 0, -1]), pose[:3,:3]) for pose in poses]
            x_rot = [rot[0] for rot in orientations]
            y_rot = [rot[1] for rot in orientations]
            z_rot = [rot[2] for rot in orientations]
            ax.quiver(x, y, z, x_rot, y_rot, z_rot, length=1, normalize=True)
        else:
            ax.scatter(x, y, z, marker='o')
    else:
        ax.set_xlabel('Z')
        ax.set_ylabel('X')
        ax.set_aspect(1)
        ax.scatter(z, x, marker='o')
    
    plt.show()

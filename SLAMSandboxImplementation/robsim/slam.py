from robsim.primitives import Point, Pose
from robsim.utility import dist_l2

import matplotlib.pyplot as plt

from scipy.optimize import least_squares
import scipy.sparse as sparse

import numpy as np

from math import pi, sin, cos, atan2

class Slam:

    def __init__(self, origin, n_landmarks, var_odometry_d, var_odometry_theta1, var_odometry_theta2, var_landmarks_d, var_landmarks_theta):
        self.origin = origin
        self.n_landmarks = n_landmarks
        self.landmarks = [Point(0, 0) for _ in range(n_landmarks)]
        self.landmark_initialized = [False for _ in range(n_landmarks)]
        self.route = [origin]

        self.var_odometry_d = var_odometry_d
        self.var_odometry_theta1 = var_odometry_theta1
        self.var_odometry_theta2 = var_odometry_theta2

        self.var_landmarks_d = var_landmarks_d
        self.var_landmarks_theta = var_landmarks_theta
                                       #    v Transformation from origin to first position in graph.
        self.odometry_constraints = [] # [(T_A, O_A), (T_AB, O_AB), (T_BC, O_BC)] <- O_ij is the information matrix of contstaint (i,j).
        self.landmark_constraints = [] # [{0: (T_A1, O_A1), 1: (T_A2, O_A2)}, {1: (T_B2, O_B2)}, {1: (T_C2, O_C2), 2: (T_C3, O_C3)}]

    @staticmethod
    def _get_state(route, landmarks):
        for i, point in enumerate(landmarks):
            if point == None:
                landmarks[i] = Point(0, 0) # Insert valid value if not measured yet.
                                                                                        #             [route, landmarks]
        state = [(p.x, p.y, p.theta) for p in route] + [(p.x, p.y) for p in landmarks]  #    [r1, r2, ..., rm-1, l1, l2, ..., ln-1]
        state = [val for t in state for val in t]                                       # [r1x, r1y, r1t, r2x, ..., l1x, l1y, l2x, ...]

        return state

    @staticmethod
    def _from_state(state, n_landmarks): 
        n_route = (len(state) - n_landmarks * 2) // 3
        n = n_route + n_landmarks

        route = state[:n_route*3]
        route = [(route[i*3], route[i*3+1], route[i*3+2]) for i in range(n_route)]
        route = [Pose(*pose) for pose in route]

        
        landmarks = state[n_route*3:]
        landmarks = [(landmarks[i*2], landmarks[i*2+1]) for i in range(n_landmarks)]
        landmarks = [Point(*pose) for pose in landmarks]

        return route, landmarks

    @staticmethod
    def _error(state, origin, n_landmarks, odometry_constraints, landmark_constraints):
        state[:3] = np.array([origin.x, origin.y, origin.theta])
        
        route, landmarks = Slam._from_state(state, n_landmarks)

        n_route = len(route)

        odometry_errors = []
        for a, b, (constraint, information_matrix) in zip(route[:-1], route[1:], odometry_constraints):
            b_ = constraint.absolute(a)
            
            error = b - b_

            error = np.array([error.x, error.y, error.theta])
            error = np.dot(error.T, np.dot(information_matrix, error))

            odometry_errors.append(error)

        landmark_errors = []
        for origin, constraints in zip(route[1:], landmark_constraints):
            for landmark in constraints:
                point = landmarks[landmark]
                point_, information_matrix = constraints[landmark]
                point_ = point_.absolute(origin)

                error = point - point_

                error = np.array([error.x, error.y])
                error = np.dot(error.T, np.dot(information_matrix, error))

                landmark_errors.append(error)

        errors = odometry_errors + landmark_errors

        return errors

    def get_sparsity(self):
        n = len(self.route) * 3 + len(self.landmarks) * 2

        sparsity = []
        
        for i in range(len(self.route) - 1):
            row = np.zeros((n,))
            
            row[i*3:(i*3+6)] = [1, 1, 1, 1, 1, 1]

            sparsity.append(row)

        for i, constraints in enumerate(self.landmark_constraints):
            for landmark in constraints:
                row = np.zeros((n,))

                row[i*3+3:i*3+6] = [1, 1, 1]

                offset = len(self.route) * 3
                j = offset + landmark * 2
                
                row[j:j+2] = [1, 1]

                sparsity.append(row)

        sparsity = np.array(sparsity)

        return sparsity

    def optimize(self, verbose: int = 0, ftol: float = 1e-5, xtol: float = 1e-5, gtol: float = 1e-5, use_sparsity: bool = True, jac: str = '3-point', loss: str = 'huber', tr_solver: str = None):
        fun = Slam._error
        state = self._get_state(self.route, [pt for pt in self.landmarks])

        sparsity = None
        if use_sparsity: 
            sparsity = self.get_sparsity()

        result = least_squares(fun, state, 
            args=(self.origin, self.n_landmarks, self.odometry_constraints, self.landmark_constraints),
            verbose=verbose,
            ftol=ftol,
            xtol=xtol,
            gtol=gtol,
            jac=jac,
            loss=loss,
            jac_sparsity=sparsity,
            tr_solver=tr_solver
        )

        self.route, self.landmarks = Slam._from_state(result.x, self.n_landmarks)

    def add_constraints(self, odometry_constraint, landmark_contraints):
        # Add pose just from odometry
        new_pose = self.route[-1]
        new_pose = odometry_constraint.absolute(new_pose)
        self.route.append(new_pose)

        d = dist_l2(Point(0, 0), odometry_constraint)
        a = new_pose.theta
        
        variance = [[self.var_odometry_d * d, 0], [0, sin(self.var_odometry_theta1) * d]]
        variance = np.array(variance)

        R = [[cos(a), -sin(a)], [sin(a), cos(a)]]
        R = np.array(R)

        information_matrix = np.zeros((3, 3))

        information_matrix[:2,:2] = np.dot(variance, R)
        information_matrix[2, 2] = self.var_odometry_theta1 + self.var_odometry_theta2

        information_matrix = np.linalg.inv(information_matrix)

        self.odometry_constraints.append((odometry_constraint, information_matrix))

        landmark_contraints_dict = {}
        for landmark, measurement in landmark_contraints:
            d = dist_l2(Point(0, 0), measurement)

            variance = [[self.var_landmarks_d * d, 0], [0, sin(self.var_landmarks_theta) * d]]
            variance = np.array(variance)

            a = atan2(measurement.y, measurement.x) + new_pose.theta

            R = [[cos(a), -sin(a)], [sin(a), cos(a)]]
            R = np.array(R)

            information_matrix = np.linalg.inv(np.dot(variance, R))

            landmark_contraints_dict[landmark] = (measurement, information_matrix)

        self.landmark_constraints.append(landmark_contraints_dict)

        # Add landmark position if first measurement
        for landmark, measurement in landmark_contraints:
            if not self.landmark_initialized[landmark]:
                self.landmarks[landmark] = measurement.absolute(new_pose)
                self.landmark_initialized[landmark] = True

    def plot(self, plot_landmark_measurements: bool = False):
        fig = plt.figure()

        plt.plot([p.x for p in self.route], [p.y for p in self.route], '-x')
        
        lms = [p for p in self.landmarks if p != None]
        plt.plot([p.x for p in lms], [p.y for p in lms], 'o', color='red')

        if plot_landmark_measurements:
            for pose, measurements in zip(self.route, self.landmark_constraints):
                for landmark in measurements:
                    plt.plot(
                        (pose.x, self.landmarks[landmark].x), 
                        (pose.y, self.landmarks[landmark].y), 
                        '--', color='black')

        ax = plt.gca()
        ax.set_aspect(1)
        
        return fig
        
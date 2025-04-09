import numpy as np
from math import pi, sin, cos


ANGLE_STEPS = 200
DIST_STEPS = 64

def hough(data, diagonal):
    # Initialize the accumulator array with zeros
    votes = np.zeros((ANGLE_STEPS, DIST_STEPS + 2), dtype=np.int32)
    
    for i in range(data.shape[1]):
        for theta_i in range(votes.shape[0]):
            # Calculate the angle and rho
            theta = theta_i / float(votes.shape[0]) * pi
            rho = data[0, i] * sin(theta) - data[1, i] * cos(theta)
            
            # Map the rho value to the appropriate index in the accumulator
            rho_i = 1 + int((rho + 0.5 * diagonal) / diagonal * (votes.shape[1] - 3))
            
            # Increment the corresponding accumulator cell
            votes[theta_i, rho_i] += 1
    
    return votes

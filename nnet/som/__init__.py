import math;
import random;
import time;

import matplotlib.pyplot as plt;
import matplotlib.lines as mlines;
from mpl_toolkits.mplot3d import Axes3D;

import scipy.spatial;

from support import read_sample;
from support import euclidean_distance;
from support import euclidean_distance_sqrt;
from support import timedcall;


# Feature SOM 0001: Predefined initial radius that depends on size of the network. 
#                   Improves results of self-organization and helps avoid tug of neurons when network is small.

# Feature SOM 0002: Uniform grid.
#                   Initial weights of neurons depends on input data set. The uniform grid represent rectangular grid 
#                   that covers input data in first two dimensions and distance between the nodes is the same in each of 
#                   the two dimensions of data. Further the uniform grid should be aligned with the center in other 
#                   dimensions of data.

# Feature SOM 0003: Autostop. Automatic termination of learining process when adaptation is not occurred.

class type_conn:
    grid_four = 0;
    grid_eight = 1;
    honeycomb = 2;
    func_neighbor = 3;
    
    
class type_init:
    random_centroid = 0;
    random_surface = 1;
    uniform_grid = 2;


class som:
    # describe network
    _rows = 0;
    _cols = 0;
    _size = 0;
    _weights = None;        # Weights of each neuron (coordinates in data dimension in other words).
    _award = None;          # Lists of indexes of won points for each neuron.
    _data = None;           # Analyzed data.
    _conn_type = None;      # Type of connections between neuron.
    
    # just for convenience (avoid excess calculation during learning)
    _location = None;           # Location in grid.
    _sqrt_distances = None;
    _capture_objects = None;    # Store indexes of input points that were captured by each neurons individually at the end.
    _neighbors = None;          # Indexes of neighbours for each neuron.
    
    # describe learning process and internal state
    _epochs = 0;                    # Iteration for learning.
    _init_radius = 0.0;             
    _init_learn_rate = 0.1;         # Rate of learning.
    _adaptation_threshold = 0.001;  # Condition when learining process should be stoped. It's used when autostop mode is used.
    
    # dynamic changes learning parameters
    _local_radius = 0.0;
    _learn_rate = 0.0;
    
    @property
    def size(self):
        return self._size;
    
    @property
    def neighbors(self):
        return self._neighbors;
    
    @property
    def weights(self):
        return self._weights;
    
    @property
    def awards(self):
        return self._award;
    
    @property
    def capture_objects(self):
        return self._capture_objects;
    
    @property
    def autostop_adaptation_threshold(self):
        return self._adaptation_threshold;
    
    @autostop_adaptation_threshold.setter
    def autostop_adaptation_threshold(self, value):
        if (value > 0):
            self._adaptation_threshold = value;
    
    
    def __init__(self, rows, cols, data, epochs, conn_type = type_conn.grid_eight, init_type = type_init.uniform_grid):
        self._cols = cols;
        self._rows = rows;        
        self._data = data;
        self._size = cols * rows;
        self._epochs = epochs;
        self._conn_type = conn_type;
        
        # Feature SOM 0001: Predefined initial radius that depends on size of the network.
        if ((cols + rows) / 4.0 > 1):
            self._init_radius = 2.0;
        elif ( (cols > 1) and (rows > 1) ):
            self._init_radius = 1.5;
        else:
            self._init_radius = 1.0;
        
        # location
        self._location = list();
        for i in range(self._rows):
            for j in range(self._cols):
                self._location.append([float(i), float(j)]);
        
        # awards
        self._award = [0] * self._size;
        self._capture_objects = [ [] for i in range(self._size) ];
        
        # distances
        self._sqrt_distances = [ [ [] for i in range(self._size) ] for j in range(self._size) ];
        for i in range(self._size):
            for j in range(i, self._size, 1):
                dist = euclidean_distance_sqrt(self._location[i], self._location[j]);
                self._sqrt_distances[i][j] = dist;
                self._sqrt_distances[j][i] = dist;
    
        # connections
        if (conn_type != type_conn.func_neighbor):
            self._create_connections(conn_type);
        
        # weights
        self._create_initial_weights(init_type);
        

    def _create_initial_weights(self, init_type):
        dimension = len(self._data[0]);
        
        maximum_dimension = [self._data[0][i] for i in range(dimension)];
        minimum_dimension = [self._data[0][i] for i in range(dimension)];
        for i in range(len(self._data)):
            for dim in range(dimension):
                if (maximum_dimension[dim] < self._data[i][dim]):
                    maximum_dimension[dim] = self._data[i][dim];
                elif (minimum_dimension[dim] > self._data[i][dim]):
                    minimum_dimension[dim] = self._data[i][dim];
                     
        # Increase border
        width_dimension = [0] * dimension;
        center_dimension = [0] * dimension;
        for dim in range(dimension):
            if (maximum_dimension[dim] > 0):
                maximum_dimension[dim] * 1.1;
            elif(maximum_dimension[dim] < 0):
                maximum_dimension * 0.9;
                  
            if (minimum_dimension[dim] > 0):
                minimum_dimension[dim] * 0.9;
            elif (minimum_dimension[dim] < 0):
                minimum_dimension[dim] * 1.1;
             
            width_dimension[dim] = maximum_dimension[dim] - minimum_dimension[dim];
            center_dimension[dim] = (maximum_dimension[dim] + minimum_dimension[dim]) / 2;
        
        step_x = center_dimension[0];
        step_y = center_dimension[1];
        if (self._rows > 1): step_x = width_dimension[0] / (self._rows - 1);
        if (self._cols > 1): step_y = width_dimension[1] / (self._cols - 1); 
                      
        # generate weights (topological coordinates)
        random.seed();
        
        # Feature SOM 0002: Uniform grid.
        if (init_type == type_init.uniform_grid):
            # Predefined weights in line with input data.
            self._weights = [ [ [] for i in range(dimension) ] for j in range(self._size)];
            for i in range(self._size):
                location = self._location[i];
                for dim in range(dimension):
                    if (dim == 0):
                        if (self._rows > 1):
                            self._weights[i][dim] = minimum_dimension[dim] + step_x * location[dim];
                        else:
                            self._weights[i][dim] = center_dimension[dim];
                    elif (dim == 1):
                        if (self._cols > 1):
                            self._weights[i][dim] = minimum_dimension[dim] + step_y * location[dim];
                        else:
                            self._weights[i][dim] = center_dimension[dim];
                    else:
                        self._weights[i][dim] = center_dimension[dim];
        
        elif (init_type == type_init.random_surface):    
            # Random weights at the full surface.
            self._weights = [ [random.uniform(minimum_dimension[i], maximum_dimension[i]) for i in range(dimension)] for j in range(self._size) ];
            
        else:
            # Random weights at the center of input data.
            self._weights = [ [(random.random() + center_dimension[i])  for i in range(dimension)] for j in range(self._size) ];        
            
    
    def _create_connections(self, conn_type):
        "Create connections in line with input rule"
        self._neighbors = [[] for index in range(self._size)];    
            
        for index in range(0, self._size, 1):
            upper_index = index - self._cols;
            upper_left_index = index - self._cols - 1;
            upper_right_index = index - self._cols + 1;
            
            lower_index = index + self._cols;
            lower_left_index = index + self._cols - 1;
            lower_right_index = index + self._cols + 1;
            
            left_index = index - 1;
            right_index = index + 1;
            
            node_row_index = math.floor(index / self._cols);
            upper_row_index = node_row_index - 1;
            lower_row_index = node_row_index + 1;
            
            if ( (conn_type == type_conn.grid_eight) or (conn_type == type_conn.grid_four) ):
                if (upper_index >= 0):
                    self._neighbors[index].append(upper_index);
                    
                
                if (lower_index < self._size):
                    self._neighbors[index].append(lower_index);
            
            if ( (conn_type == type_conn.grid_eight) or (conn_type == type_conn.grid_four) or (conn_type == type_conn.honeycomb) ):
                if ( (left_index >= 0) and (math.floor(left_index / self._cols) == node_row_index) ):
                    self._neighbors[index].append(left_index);
                
                if ( (right_index < self._size) and (math.floor(right_index / self._cols) == node_row_index) ):
                    self._neighbors[index].append(right_index);  
                
                
            if (conn_type == type_conn.grid_eight):
                if ( (upper_left_index >= 0) and (math.floor(upper_left_index / self._cols) == upper_row_index) ):
                    self._neighbors[index].append(upper_left_index);
                
                if ( (upper_right_index >= 0) and (math.floor(upper_right_index / self._cols) == upper_row_index) ):
                    self._neighbors[index].append(upper_right_index);
                    
                if ( (lower_left_index < self._size) and (math.floor(lower_left_index / self._cols) == lower_row_index) ):
                    self._neighbors[index].append(lower_left_index);
                    
                if ( (lower_right_index < self._size) and (math.floor(lower_right_index / self._cols) == lower_row_index) ):
                    self._neighbors[index].append(lower_right_index);          
                
            
            if (conn_type == type_conn.honeycomb):
                if ( (node_row_index % 2) == 0):
                    upper_left_index = index - self._cols;
                    upper_right_index = index - self._cols + 1;
                
                    lower_left_index = index + self._cols;
                    lower_right_index = index + self._cols + 1;
                else:
                    upper_left_index = index - self._cols - 1;
                    upper_right_index = index - self._cols;
                
                    lower_left_index = index + self._cols - 1;
                    lower_right_index = index + self._cols;
                
                if ( (upper_left_index >= 0) and (math.floor(upper_left_index / self._cols) == upper_row_index) ):
                    self._neighbors[index].append(upper_left_index);
                
                if ( (upper_right_index >= 0) and (math.floor(upper_right_index / self._cols) == upper_row_index) ):
                    self._neighbors[index].append(upper_right_index);
                    
                if ( (lower_left_index < self._size) and (math.floor(lower_left_index / self._cols) == lower_row_index) ):
                    self._neighbors[index].append(lower_left_index);
                    
                if ( (lower_right_index < self._size) and (math.floor(lower_right_index / self._cols) == lower_row_index) ):
                    self._neighbors[index].append(lower_right_index);                        
    
    
    def _competition(self, x):
        "Return neuron winner (distance, neuron index)"
        index = 0;
        minimum = euclidean_distance_sqrt(self._weights[0], x);
        
        for i in range(1, self._size, 1):
            candidate = euclidean_distance_sqrt(self._weights[i], x);
            if (candidate < minimum):
                index = i;
                minimum = candidate;
        
        return index;
    
    
    def _adaptation(self, index, x):
        "Change weight of neurons in line with won neuron"
        dimension = len(self._weights[0]);
        
        if (self._conn_type == type_conn.func_neighbor):
            for neuron_index in range(self._size):
                distance = self._sqrt_distances[index][neuron_index];
                #print("distance: ", distance, ", local radius: ", self._local_radius);
                if (distance < self._local_radius):
                    #influence = math.exp(-(distance / (2 * self._local_radius)));
                    influence = math.exp( -( distance / (2.0 * self._local_radius) ) );
                    
                    for i in range(dimension):
                        self._weights[neuron_index][i] = self._weights[neuron_index][i] + self._learn_rate * influence * (x[i] - self._weights[neuron_index][i]);  
                    
        else:
            for i in range(dimension):
                self._weights[index][i] = self._weights[index][i] + self._learn_rate * (x[i] - self._weights[index][i]); 
                
            for neighbor_index in self._neighbors[index]: 
                distance = self._sqrt_distances[index][neighbor_index]
                if (distance < self._local_radius):
                    influence = math.exp( -( distance / (2.0 * self._local_radius) ) );
                    #print("distance: ", distance, ", local radius: ", self._local_radius, "influence: ", influence);
                    
                    for i in range(dimension):       
                        self._weights[neighbor_index][i] = self._weights[neighbor_index][i] + self._learn_rate * influence * (x[i] - self._weights[neighbor_index][i]);  
    
                            
    def train(self, autostop = False):
        "Train SOM"
        previous_weights = None;
        
        for epoch in range(1, self._epochs + 1):
            # Depression term of coupling
            self._local_radius = ( self._init_radius * math.exp(-(epoch / self._epochs)) ) ** 2;
            self._learn_rate = self._init_learn_rate * math.exp(-(epoch / self._epochs));

            #random.shuffle(self._data);    # Random order
            
            # Feature SOM 0003: Clear statistics
            if (autostop == True):
                for i in range(self._size):
                    self._award[i] = 0;
                    self._capture_objects[i].clear();
            
            for i in range(len(self._data)):
                # Step 1: Competition:
                index = self._competition(self._data[i]);
                    
                # Step 2: Adaptation:   
                self._adaptation(index, self._data[i]);
                
                # Update statistics
                if ( (autostop == True) or (epoch == (self._epochs - 1)) ):
                    self._award[index] += 1;
                    self._capture_objects[index].append(i);
            
            # Feature SOM 0003: Check requirement of stopping
            if ( (autostop == True) and (previous_weights is not None) ):
                maximal_adaptation = self._get_maximal_adaptation(previous_weights);
                if (maximal_adaptation < self._adaptation_threshold):
                    # print("Learning process is stopped. Iteration: ", epoch);
                    return;
                
            previous_weights = [item[:] for item in self._weights];
            
    
    def _get_maximal_adaptation(self, previous_weights):
        dimension = len(self._data[0]);
        maximal_adaptation = 0.0;
        
        for neuron_index in range(self._size):
            for dim in range(dimension):
                current_adaptation = previous_weights[neuron_index][dim] - self._weights[neuron_index][dim];
                        
                if (current_adaptation < 0): current_adaptation = -current_adaptation;
                        
                if (maximal_adaptation < current_adaptation):
                    maximal_adaptation = current_adaptation;
                    
        return maximal_adaptation;
    
    
    def get_winner_number(self):
        winner_number = 0;
        for i in range(self._size):
            if (self._award[i] > 0):
                winner_number += 1;
                
        return winner_number;
    
    
    def show_award(self):
        awards = list();
        
        for index in range(self._size):
            if ((index != 0) and (index % self._cols == 0)):
                print(awards);
                awards.clear();
                
            awards.append(self._award[index]);
            
        print(awards);
            
    
    def show_network(self, awards = False, belongs = False, coupling = True, dataset = True):
        "Show neurons in the dimension of data"
        dimension = len(self._weights[0]);
        
        fig = plt.figure();
        axes = None;
        
        # Check for dimensions
        if (dimension == 2):
            axes = fig.add_subplot(111);
        elif (dimension == 3):
            axes = fig.gca(projection='3d');
        else:
            raise NameError('Dwawer supports only 2d and 3d data representation');
        
        
        # Show data
        if (dataset == True):
            for x in self._data:
                if (dimension == 2):
                    axes.plot(x[0], x[1], 'b.');
                elif (dimension == 3):
                    axes.scatter(x[0], x[1], x[2], c = 'b', marker = '.');                           
        
        # Show neurons
        for index in range(self._size):
            color = 'g';
            if (self._award[index] == 0): color = 'y';
            
            if (dimension == 2):
                axes.plot(self._weights[index][0], self._weights[index][1], color + 'o');
                
                if (awards == True):
                    location = '{0}'.format(self._award[index]);
                    axes.text(self._weights[index][0], self._weights[index][1], location, color='black', fontsize = 10);
                    
                if (belongs == True):
                    location = '{0}'.format(index);
                    axes.text(self._weights[index][0], self._weights[index][1], location, color='black', fontsize = 12);
                    for k in range(len(self._capture_objects[index])):
                        point = self._data[self._capture_objects[index][k]];
                        axes.text(point[0], point[1], location, color='blue', fontsize = 10);
                
                if ( (self._conn_type != type_conn.func_neighbor) and (coupling != False) ):
                    for neighbor in self._neighbors[index]:
                        axes.plot([self._weights[index][0], self._weights[neighbor][0]], [self._weights[index][1], self._weights[neighbor][1]], 'g', linewidth = 0.5);
            
            elif (dimension == 3):
                axes.scatter(self._weights[index][0], self._weights[index][1], self._weights[index][2], c = color, marker = 'o');
                

        plt.grid();
        plt.show();
        
        
# sample = read_sample('../../samples/SampleTwoDiamonds.txt');
# network = som(5, 5, sample, 100, type_conn.grid_four);
# network.show_network();
# 
# network.train();
# network.show_network();
"""!

@brief TSP algorithm: ant colony based
@details Based on article description:
         - M.Dorigo, L.M.Gambardella. Ant colonies for the traveling salesman problem. 1996.
         - J.Yang, X.Shi, M.Marchese, Y.Liang. An ant colony optimization method for generalized TSP problem. 2008.

@authors Alexey Kukushkin (pyclustering@yandex.ru)
@date 2014-2016
@copyright GNU Public License

@cond GNU_PUBLIC_LICENSE
    PyClustering is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    
    PyClustering is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    
    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
@endcond

"""

from pyclustering.tsp import tsp_result;

import pyclustering.core.antcolony_tsp_wrapper as wrapper;


class antcolony_parameters:
    """!
    @brief Describes parameters of ant colony based algorithm for TSP problem.
    
    @see antcolony
    
    """
    
    def __init__(self):
        ##
        self.q                   = 1.5;
        
        ##
        self.ro                  = 0.7;
        
        ##
        self.alpha               = 1.0;
        
        ##
        self.beta                = 1.0;
        
        ##
        self.gamma               = 2.0;
        
        ##
        self.qinit_pheramone     = 0.1;
        
        ## Amount of ants that is used on each iteration.
        self.ants_per_iteration  = 10;
        
        ## Amount of iterations that is used for solving TSP.
        self.iterations          = 50;


class antcolony:
    """!
    @brief Simulates ant colony to solve travelling salesman problem (TSP).
    
    @details Ants of the artificial colony are able to generate successively shorter feasible tours by using information accumulated 
             in the form of a pheromone trail deposited on the edges of the TSP graph.
    
    @warning Solution is performed only via CCORE library (C/C++ implementation of the library).
    
    Example:
    @code
        
    @endcode
    
    """  
    
    def __init__(self, parameters):
        """!
        @brief Constructor of ant colony based algorithm for travelling salesman problem.
        
        @param[in] parameters (antcolony_parameters): Parameters of the ant colony algorithm.
        
        """
        
        self.__parameters = None;
        
        if (parameters is None):
            self.__parameters = antcolony_parameters();
        else:
            self.__parameters = parameters;
    
    
    def process(self, object_locations):
        """!
        @brief Perform simulation of ant colony to solve travelling salesman problem.
        
        @param[in] object_locations (list): Coordinates of objects that should be visited.
        
        """
        
        (result_address, c_pointer_tsp_result) = wrapper.antcolony_tsp_process(object_locations, self.__parameters);
        
        result = tsp_result();
        
        result.shortest_length = c_pointer_tsp_result.path_length;
        for i in range(c_pointer_tsp_result.size):
            result.object_sequence.append(c_pointer_tsp_result.object_sequence[i]);
        
        wrapper.antcolony_tsp_destroy(result_address);
        
        return result;
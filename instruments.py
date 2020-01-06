# -*- coding: utf-8 -*-
"""
Created on Fri Jan  3 09:09:18 2020

@author: Juan Diego
"""

import math
import random as rnd

class function_generator_simulator:
    def __init__(self,frequency):
        self.current_frequency = frequency
        self.read_termination ='\n'                #this is here just for compatibility reasons
        self.write_termination='\n'                #this is heree just for compatibility reasons 
        
    def write(self,frequency_string):
        self.current_frequency=float(frequency_string.split("Q")[1])  #Split the input string and take the number
       
    def query(self,dummy_string):              #the string is just for compatibility
        
        phase = (100)*math.sin(0.005*self.current_frequency) + ((4E-6)*(self.current_frequency)**2) + rnd.uniform(0,30)
        
        return phase
  
    


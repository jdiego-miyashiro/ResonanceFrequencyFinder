# -*- coding: utf-8 -*-
"""
Created on Fri Jan  3 09:09:18 2020

@author: Juan Diego
"""

import math

class function_generator:
    def __init__(self,frequency):
        self.current_frequency = frequency
        self.read_termination ='\n'                #for compatibility reasons
        self.write_termination='\n'                #for compatibility reasons 
        
    def write(self,frequency_string):
        self.current_frequency=frequency_string.split("Q")[1]  #Split the input string and take the number


class lock_in:
    def __init__(self,function_generator):  #it will pass the function_generator instance to here
        self.current_frequency=float(function_generator.current_frequency)
        
    def query(self,dummy_string):              #the string is just for compatibility
        phase = (100)*math.sin(0.005*self.current_frequency) + (4E-6)*(self.current_frequency)^2
        return phase
# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import visa
import numpy as np
import matplotlib.pyplot as plt
import time
import datetime
from instruments import function_generator_simulator

rm = visa.ResourceManager()


def main():
    plt.style.use('seaborn-whitegrid')
    
    
    live=False
    
    if not live:
        function_generator = function_generator_simulator(0)
        lock_in = function_generator
    else:
        lock_in,function_generator = get_instruments()
            
        
        
        
    
    
    starting_frequency=50                                                                     
    upperbound_frequency=2000
    step_size = 1
    experiment=Experiment(starting_frequency,upperbound_frequency,step_size,lock_in,function_generator,live)

    
    experiment.run()
    data=open('resonance_frequencies.txt','a+')
    for i in range(len(experiment.resonances)):
        data.write(str(experiment.resonances[i]) + '\n' )
        
        
    print(experiment.resonances)
  
def get_instruments(): 
    
    lock_in = rm.open_resource(rm.list_resources()[1])
    
    function_generator = rm.open_resource(rm.list_resources()[0])
    return lock_in,function_generator

class Experiment:
    def __init__(self,starting_frequency,upperbound_frequency,step_size,lock_in,function_generator,live):
        
        self.lock_in= lock_in
        self.function_generator= function_generator
        self.upper_bound_frequency = upperbound_frequency
        self.current_frequency = starting_frequency
        self.starting_frequency=starting_frequency
        self.upperbound_frequency=upperbound_frequency
        self.stepsize = step_size
        self.smaller_stepsize = step_size // 10
        self.waiting_time = 0.0001                        
        self.current_phase = []                                                    #Holds the current_phase_value
        self.current_datapoint= []                                              
        self.phase_data= []
        self.frequency_data= [] 
        self.phase_vs_frequency=[]
        self.is_resonance=[False]
        self.resonances=[]
        self.interpolated_frequencies=[]
        self.interpolated_resonances=[]
        self.frames=0
                                                                                     #REMEMBER WE ARE KEEPING PHASE IN THE X-AXIS, FREQ IN THE Y-AXIS
    def get_starting_measurments(self):
        
        self.function_generator.read_termination='\n'
        self.function_generator.write_termination='\n'
        self.lock_in.read_termination='\n'
        self.lock_in.write_termination='\n'
        
        
        self.function_generator.write("FREQ" + str(self.current_frequency))
        
        time.sleep(self.waiting_time)            
        initial_phase = abs(float(self.lock_in.query("OUTP?4")))                             #First
        self.current_phase = initial_phase
        self.frequency_data.append(self.current_frequency)
        self.phase_data.append(initial_phase)
        self.phase_vs_frequency.append([self.phase_data,self.frequency_data])
        data=open("resonancedata.txt", "a+")
        data.write(str(self.current_frequency) + ',' + str(self.current_phase) +'\n' )
    
    def update_frequency(self,stepsize):
        
        self.function_generator.read_termination='\n'
        self.function_generator.write_termination='\n'
        frequency=str(self.current_frequency + stepsize)
        self.function_generator.write("FREQ "+ frequency)
        self.current_frequency = float(frequency)
        

    def update_phase(self):
        time.sleep(self.waiting_time)
        self.lock_in.read_termination='\n'
        self.lock_in.write_termination='\n'
        self.current_phase = abs(float(self.lock_in.query("OUTP?4")))
        
    def write_data(self):
        self.frequency_data.append(self.current_frequency)
        self.phase_data.append(self.current_phase)
        self.phase_vs_frequency.append([self.current_frequency,self.current_phase])
        #print(self.current_frequency,self.current_phase)
        file=open("data.txt", "a+")
        file.write(str(self.current_frequency) + ',' + str(self.current_phase) + ',                   ' + str(datetime.datetime.now()) + '\n' )

        
     
        
    def polynomial_regression(self,phase_array,frequency_array):
        #print('interpolating...')
        #time.sleep(0.3)
        #print('frenquencies',frequency_array)
        #print('phases', phase_array)
        interpolation_curve=np.poly1d(np.polyfit(phase_array,frequency_array,2))
        interpolation_value=interpolation_curve(90)
        #print("Interpolation Value :", interpolation_value)
        return round(interpolation_value,6)

    def update_plot(self,i):
        self.ax.clear()
        self.ax.scatter(self.frequency_data,self.phase_data)

    
    def check_range(self,phase_data):
        l=len(phase_data)
        if l>=3:
            n=phase_data[l-1]
            n2=phase_data[l-2]
            n3=phase_data[l-3]
            if 90 < max(n,n2,n3) and 90 > min(n,n2,n3):
                
                return True
            else:
                
                return False
                
        else:
            return False
    
    def compare_phases(self,phase1,phase2):                #return phase 1 is better
        error1=abs(90-phase1)
        error2=abs(90-phase2)
        if error1 <= error2:
            return True
        
    
    def check_if_resonance(self):
        if self.current_phase < 92 and self.current_phase > 88:
            self.is_resonance.append(True)
            self.resonances.append([self.current_phase,self.current_frequency])
            print('RESONANCE')
            return True
            
        else:
            self.is_resonance.append(False)
            return False

    def make_plot(self):
            
            
            plt.ylim(0,200)
            plt.xlim(self.starting_frequency,self.upperbound_frequency)
            
            plt.xticks(np.arange(self.starting_frequency,self.upperbound_frequency +18 , (self.upperbound_frequency-self.starting_frequency)//18))
            plt.yticks(np.arange(0,211,5))
            
            plt.tick_params(axis='both',labelsize=15)
            plt.plot(self.frequency_data,self.phase_data,label='Regular data points',c='blue',marker='o', alpha=0.5)
            plt.scatter([x[1] for x in self.resonances],[x[0] for x in self.resonances],label='Resonance Found', c='red',s=150, alpha=0.9)
            plt.scatter(self.interpolated_frequencies, self.interpolated_resonances,label='Polyregression Measurement ', c='green', s=150, alpha = 0.8)
            #print(self.interpolated_frequencies)
            plt.xlabel('Frequencies (Hertz)', fontsize=25)
            plt.title('Signal Phase off-set over Frequency Range', fontsize=30)
            plt.ylabel('Phase off-set (degrees)', fontsize = 25)
            plt.pause(0.1)
            
            if self.frames == 0:
                plt.legend(fontsize='25', loc='upper right', borderpad=0.5)
                self.frames = self.frames + 1
 
       
    def run(self):
        
        self.get_starting_measurments()
       
        while self.current_frequency <= self.upper_bound_frequency:
            #self.ani=animation.FuncAnimation(fig,self.animate, interval=1000)
            self.make_plot()
            self.check_if_resonance()       #and if between range append to resonances
            
            r=self.is_resonance[len(self.is_resonance) -1]
            r1=self.is_resonance[len(self.is_resonance) -2]
        
            if len(self.phase_data) >= 3:   #determine how many points you are gonna use for the regression
                p=[self.phase_data[len(self.phase_data)-1],self.phase_data[len(self.phase_data) -2],self.phase_data[len(self.phase_data) -3]]
                f=[self.frequency_data[len(self.frequency_data)-1],self.frequency_data[len(self.frequency_data) -2],self.frequency_data[len(self.frequency_data)-3]]
                
            
                if self.check_range(p)==True and r == False and r1 == False:                                                #check if a 90 degree off-set is in the range of the previous 3 data points
                       counter=0
                                                                      
                       while counter <=  10 and r != True:
                           
                            counter = counter + 1
                            print('Counter: ', counter)
                            if self.check_range(p) == True and p[0] != p[1] and p[1] != p[2] and p[2] != p[0] :         
                                fnew = self.polynomial_regression(p,f)
                                
                                if fnew <= max(f) + self.stepsize and fnew >= min(f) - self.stepsize:                        #check if interpolated frequency is in within range
                                    self.current_frequency = fnew
                                    self.update_phase()                                                                           #read the interpolated phase and making it the new current_phase
                                    print('interpolation phase: ',self.current_phase)
                                if self.check_if_resonance() == True:                                                          #CASE 1: Resonance is found,  
                                    self.is_resonance.append(True)
                                    r = True
                                    print('!!!!RESONANCE!!!!')
                                    self.write_data()                                                                          #write data doesn't make any reads
                                elif self.compare_phases(self.current_phase,p[0]) and fnew <= max(f) + self.stepsize and fnew >= min(f) - self.stepsize:                                             #CASE 2: Resonance is not found with interpolation
                                    self.write_data()                                                                             #Compare the current_phase (the interpolated phase), with the previously measure phase and if it's better write the data 
                                    p[0]=self.current_phase                                                                    
                                    f[0]=self.current_frequency
                                    self.interpolated_frequencies.append(fnew)
                                    self.interpolated_resonances.append(self.current_phase)
                                    print('BETTER THAN PREVIOUS')
                                else:
                                    min_frequency = min(f)                                                                     #CASE 3: is not resonance and is not better than previous
                                    print('Discarting interpolated phase')                                                        #Discart the interpolated phase and get the minimum frequency of the 3 previous measurments and increase by a smaller stepsize 
                                    print('min frequency', min_frequency)
                                    self.interpolated_frequencies.append(fnew)
                                    self.interpolated_resonances.append(self.current_phase)
                                    for i in range(len(f)):
                                        if min_frequency == f[i]:                                                                 #find the minimum frequency of the 3 previous measuements and increase it by a fraction of the original stepsize                                            
                                            self.update_frequency(self.smaller_stepsize)
                                            time.sleep(0.05)
                                            self.update_phase()
                                            print('updates: ',' nmin phase' ,self.current_phase,' nmin frequency', self.current_frequency)
                                            f[i]=self.current_frequency
                                            p[i]=self.current_phase             
                            else:
                                counter = 11                                                                             #The phases are not in the proper range anymore so we exit the loop
                                self.write_data()
                       self.current_frequency=max(f)
                       self.update_frequency(self.stepsize)
                       self.update_phase()
                       self.write_data()
                       print('current frequency:',self.current_frequency)
                           
                       
                    
                       

                else:
                            self.update_frequency(self.stepsize)
                            self.update_phase()
                            self.write_data()
                        
            else:
                self.update_frequency(self.stepsize)
                self.update_phase()
                self.write_data()
            
            


    
main()

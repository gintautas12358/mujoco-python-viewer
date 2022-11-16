
#
#BSD 3-Clause License
#
#
#
#Copyright 2022 fortiss, Neuromorphic Computing group
#
#
#All rights reserved.
#
#
#
#Redistribution and use in source and binary forms, with or without
#
#modification, are permitted provided that the following conditions are met:
#
#
#
#* Redistributions of source code must retain the above copyright notice, this
#
#  list of conditions and the following disclaimer.
#
#
#
#* Redistributions in binary form must reproduce the above copyright notice,
#
#  this list of conditions and the following disclaimer in the documentation
#
#  and/or other materials provided with the distribution.
#
#
#
#* Neither the name of the copyright holder nor the names of its
#
#  contributors may be used to endorse or promote products derived from
#
#  this software without specific prior written permission.
#
#
#
#THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
#
#AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#
#IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#
#DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
#
#FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
#
#DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
#
from esim import Esim_interface
import numpy as np

import timeit

# def gen_events(samples_num, res):
#     a = np.random.randn(samples_num,4)
#     np.where(a[:,-1] > 0, 1, 0) 
#     a[:,2] = np.arange(samples_num) 
#     a[:,:2] = np.abs(a[:,:2]) 
#     a[:,0] *= res[0] * 0.7
#     a[:,1] *= res[1] * 0.7
#     a[:,:2] = np.round(a[:,:2])
#     a[:,0] = np.clip(a[:,0] , 0, res[0]-1)
#     a[:,1] = np.clip(a[:,1] , 0, res[1]-1)
#     a = a.astype("int16")

#     return a


# esim = Esim_interface()

# res = (1024, 720)
# # print(gen_events(10, res))
# events = gen_events(10, res)
# print(events)
# esim.viz_events2(events, res)
# esim.viz_events(events, res)



# code snippet to be executed only once
mysetup = """
from esim import Esim_interface
import numpy as np

def gen_events(samples_num, res):
    a = np.random.randn(samples_num,4)
    np.where(a[:,-1] > 0, 1, 0) 
    a[:,2] = np.arange(samples_num) 
    a[:,:2] = np.abs(a[:,:2]) 
    a[:,0] *= res[0] * 0.7
    a[:,1] *= res[1] * 0.7
    a[:,:2] = np.round(a[:,:2])
    a[:,0] = np.clip(a[:,0] , 0, res[0]-1)
    a[:,1] = np.clip(a[:,1] , 0, res[1]-1)
    a = a.astype("int16")

    return a

esim = Esim_interface()

res = (1024, 720)
events = gen_events(int(1e6), res)
"""
 
# code snippet whose execution time
# is to be measured
mycode1 = '''
esim.viz_events(events, res)
'''

mycode2 = '''
esim.viz_events2(events, res)
'''
 
# timeit statement
print ("The time of execution of above program is :",
       timeit.timeit(setup = mysetup,
                    stmt = mycode1,
                    number = 100))

# timeit statement
print ("The time of execution of above program is :",
       timeit.timeit(setup = mysetup,
                    stmt = mycode2,
                    number = 100))
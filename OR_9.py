#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb  2 11:59:10 2020

@author: samlefkofsky
"""


# Github

import os
from gurobipy import Model, GRB
import pulp
from scipy.optimize import linprog
import pandas as pd
import numpy as np
import math
from tkinter import *
from IPython import get_ipython
import itertools
import functools


get_ipython().magic('reset -sf')


duration_HSR = pd.read_excel('duration_hsr.xlsx')
price_HSR = pd.read_excel('price_hsr.xlsx')
duration_AIR = pd.read_excel('duration_air.xlsx')
price_AIR = pd.read_excel('price_air.xlsx')

print(price_AIR)



duration_HSR = np.array(duration_HSR)
price_HSR = np.array(price_HSR)
duration_AIR = np.array(duration_AIR)
price_AIR = np.array(price_AIR)


cost_HSR = duration_HSR*100
total_passengers = duration_HSR*100

y = 1/100 #value of price in demand 
z = 2/100 #value of time in demand


spill = 100
recapture = 100 


service_limit = 10

demand = np.zeros((7,7))
actual = np.zeros((7,7))
services = np.zeros((7,7))
          
city1 = range(7)
city2 = range(7)


# Optimization
    
m = Model("HSR")

open = m.addVars(city1, city2, vtype=GRB.BINARY, name="open")
revenue = m.addVars(city1, city2, name="revenue")
demand = m.addVars(city1, city2, name="demand")
actual = m.addVars(city1, city2, name="actual")

m.addConstr((open.sum()<= service_limit), "services capacity")

m.addConstrs(  (demand[c1,c2] == 1-(math.exp(y*price_HSR[c1,c2]+z*duration_HSR[c1,c2]))/(math.exp(y*price_HSR[c1,c2]+z*duration_HSR[c1,c2])
+math.exp(y*price_AIR[c1,c2]+z*duration_AIR[c1,c2]))for c1,c2 in itertools.product(range(7), range(7))) ,"demand")
        
m.addConstrs((actual[c1,c2] == demand[c1,c2]*total_passengers[c1,c2]-spill+recapture for c1,c2 in itertools.product(range(7), range(7))), "actual")

m.addConstrs((revenue[c1,c2] == price_HSR[c1,c2]*actual[c1,c2]*open[c1,c2] for c1,c2 in itertools.product(range(7), range(7))), "revenue")

# Objective
obj = sum(revenue[c1,c2]-cost_HSR[c1,c2]*open[c1,c2] for c1,c2 in itertools.product(range(7), range(7)))
m.setObjective(obj, GRB.MAXIMIZE) # maximize profit

m.write('HSR.lp')
m.optimize()


for x in range(7):
    for y in range(7):
        if(x==y):
            print('Service %s,%s does not exist' %(x,y))
        else:
            if(open[x,y].x > 0.99):
                print('Service %s,%s is open' %(x,y))
            else:
                print('Service %s,%s is closed' %(x,y))


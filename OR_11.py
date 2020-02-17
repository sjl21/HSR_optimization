#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 14 11:50:08 2020

@author: samlefkofsky
"""

from gurobipy import Model, GRB
import pandas as pd
import numpy as np
import math
from IPython import get_ipython
import itertools
import tkinter as tk
from itertools import permutations 


get_ipython().magic('reset -sf')

#Data
distances = pd.read_excel('Distances.xlsx')
distances=np.array(distances)
total_passengers=pd.read_excel('TotalP.xlsx')
total_passengers=np.array(total_passengers)

#Parameters
cities = ['New York',	'Boston',	'Philadelphia',	'Providence',	'D.C.']
p_types = ['child', 'adult', 'senior']
#capacity_HSR = 15000*np.ones((7,7))
service_limit = 5
y = 2 #value of price in demand 
z = 1 #value of time in demand

spill = 100
recap_rate = 0.5
splitA = 0.4
splitB = 0.6
spillA = 200
spillB = 200 


#Itineraries
Itineraries2 = list(permutations(cities,2))
Itineraries3 = list(permutations(cities, 3))

Itineraries_dist2 = np.zeros(len(Itineraries2))
for x in range(len(Itineraries2)):
    Itineraries_dist2[x]=\
    distances[cities.index(Itineraries2[x][0])][cities.index(Itineraries2[x][1])]
    
Itineraries_dist3 = np.zeros(len(Itineraries3))
for x in range(len(Itineraries3)):
    Itineraries_dist3[x]=\
    distances[cities.index(Itineraries3[x][0])][cities.index(Itineraries3[x][1])]+\
    distances[cities.index(Itineraries3[x][1])][cities.index(Itineraries3[x][2])]

Itineraries = Itineraries2+Itineraries3
Itineraries_dist=[]
for i in Itineraries_dist2: 
    Itineraries_dist.append(i)
for i in Itineraries_dist3: 
    Itineraries_dist.append(i)
    
total_passengers2= np.zeros(len(Itineraries2))
for x in range(len(Itineraries2)):
    total_passengers2[x]=\
    total_passengers[cities.index(Itineraries2[x][0])][cities.index(Itineraries2[x][1])]
    
total_passengers3 = np.zeros(len(Itineraries3))
for x in range(len(Itineraries3)):
    total_passengers3[x]=\
    total_passengers[cities.index(Itineraries3[x][0])][cities.index(Itineraries3[x][2])]
    
total_passengers_I=[]
for i in total_passengers2: 
    total_passengers_I.append(i)
for i in total_passengers3: 
    total_passengers_I.append(i)
    

duration_HSR = np.zeros(len(Itineraries))
duration_AIR = np.zeros(len(Itineraries))

for x in range(len(Itineraries)):
    duration_HSR[x]=Itineraries_dist[x]
    duration_AIR[x]=Itineraries_dist[x]/2 + 60 #Adjustment
    
price_HSR = np.zeros((len(Itineraries),len(p_types)))
price_AIR = np.zeros((len(Itineraries),len(p_types)))

for x in range(len(Itineraries)):
    for y in range(len(p_types)):
        price_HSR[x][y]=Itineraries_dist[x]/5+y*30
        price_AIR[x][y]=Itineraries_dist[x]/7+ 30+y*30 #Adjustment
    
cost_HSR = np.zeros(len(Itineraries))
for x in range(len(Itineraries)):
    cost_HSR[x] = Itineraries_dist[x]*20
    
#Optimization
I = range(len(Itineraries))
Z = range(len(p_types))
    
m= Model("HSR")

open = m.addVars(I, vtype=GRB.BINARY, name="open")
revenue = m.addVars(I,Z, name="revenue")
actual=m.addVars(I,Z, name="actual")
demand = m.addVars(I,Z, name="demand")

m.addConstr((open.sum()<=service_limit),"service_limit")

m.addConstrs((demand[i,z] == 1- (math.exp((y*price_HSR[i,z]+z*duration_HSR[i])/100)) \
              /(math.exp((y*price_HSR[i,z]+z*duration_HSR[i])/100)+math.exp((y*price_AIR[i,z]+z*duration_AIR[i])/100)) \
              for i,z in itertools.product(I,Z)),"demand")

m.addConstrs((actual[i,z] == demand[i,z]*total_passengers_I[i]-spill+recap_rate*(splitA*spillA+splitB*spillB) for i,z in itertools.product(I,Z)),"actual")
m.addConstrs((revenue[i,z] == price_HSR[i,z]*actual[i,z]*open[i] for i,z in itertools.product(I,Z)),"revenue")

obj = sum(revenue[i,z]-cost_HSR[i] for i,z in itertools.product(I,Z))
m.setObjective(obj, GRB.MAXIMIZE)

m.write('HSR.lp')
m.optimize()

print()
for i in I:
    if(open[i].x > 0.99):
        print( 'Service %s %s is open.' %(i,Itineraries[i]))
        print()


# Need to differentiate between services and itineraries,
# Need to implement timing and scheduling
# We know what itinerares are the most attractive, but thats all
    
# Data
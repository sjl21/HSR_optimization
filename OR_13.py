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
import networkx as nx 


get_ipython().magic('reset -sf')

#Data
distances = pd.read_excel('Distances.xlsx')
distances=np.array(distances)
total_passengers=pd.read_excel('TotalP.xlsx')
total_passengers=np.array(total_passengers)

#Parameters
cities = ['New York',	'Boston',	'Philadelphia',	'Providence',	'D.C.']
p_types = ['child', 'adult', 'senior']
periods = ['6-10','10-2','2-6','6-10']
a = 2 #value of price in demand 
b= 1 #value of time in demand

spill = 100
recap_rate = 0.5
splitA = 0.4
splitB = 0.6
spillA = 200
spillB = 200 


#Itineraries
Itineraries2 = list(permutations(cities,2))
Itineraries3 = list(permutations(cities, 3))
Services = list(permutations(cities,2))

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
    
S_i2=list(permutations(cities,2))
    
S_i3 = list(np.zeros(len(Itineraries3), dtype = object))
for x in range(len(Itineraries3)):
    a = Itineraries3[x][0]
    b = Itineraries3[x][1]
    c = Itineraries3[x][2]
    ab = (Itineraries3[x][0],Itineraries3[x][1])
    bc = (Itineraries3[x][1],Itineraries3[x][2])
    S_i3[x]=(ab,bc)

S_i=S_i2+S_i3

I_s=list(np.empty(len(Services)))
for x in range(len(Services)):
    I_s[x]=[]

for x in range(len(Services)):
    for i in range(len(Itineraries2)):
        if Itineraries2[i]==Services[x]:
            I_s[x].append(Itineraries[i])
    for i in range(len(S_i3)):
        if S_i3[i][0]==Services[x]:
            I_s[x].append(Itineraries3[i])
        if S_i3[i][1]==Services[x]:
            I_s[x].append(Itineraries3[i])
    
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
    
cost_HSR = np.zeros(len(Services))
for x in range(len(Services)):
    cost_HSR[x] = Itineraries_dist[x]*20

service_capacity = np.zeros(len(Itineraries))
for x in range(len(Itineraries)):
    service_capacity[x]=5000
    
     

#Optimization
I = range(len(Itineraries))
Z = range(len(p_types))
T = range(len(periods))
S = range(len(Services))
X = range(len(I_s[0]))
Y = range(2)
V = range(0,20)
W = range(20,80)

m = Model("HSR")

freq_I = m.addVars(I,T, vtype=GRB.INTEGER,name="freq_I")
freq_S = m.addVars(S,T, vtype=GRB.INTEGER,name="freq_S")
revenue_I = m.addVars(I,Z,T, name="revenue_I")
revenue_S = m.addVars(S,Z,T, name="revenue_S")
actual_I =m.addVars(I,Z,T, name="actual_I")
actual_S =m.addVars(S,X,Z,T, name="actual_S")
actual_SS =m.addVars(S,Z,T, name="actual_SS")
demand= m.addVars(I,Z, name="demand_I")
demand_S=m.addVars(S,X,Z,name = "demand_S")
demand_SS=m.addVars(S,Z, name = "demand_SS")


#Itneraries.index(I_s[s][x])
#Services.index(S_i[i][y])

#Frequency
#Attempting to set flow constraints for freq_I and freq_S

m.addConstrs((freq_I[i,t]==freq_S[Services.index(S_i[i][y]),t] for i,t,y in itertools.product(W,T,Y)),"freqc")
m.addConstrs((freq_I[i,t]==freq_S[Services.index(S_i[i]),t] for i,t in itertools.product(V,T)),"freqc")

m.addConstrs((freq_S[s,t]==freq_I[Itineraries.index(I_s[s][x]),t] for s,t,x in itertools.product(S,T,X)), "freqc")

#Demand
m.addConstrs((demand[i,z] == 1- (math.exp((y*price_HSR[i,z]+z*duration_HSR[i])/100)) \
              /(math.exp((y*price_HSR[i,z]+z*duration_HSR[i])/100)+math.exp((y*price_AIR[i,z]+z*duration_AIR[i])/100)) \
              for i,z in itertools.product(I,Z)),"demand")

m.addConstrs((demand_S[s,x,z] == demand[Itineraries.index(I_s[s][x]),z] for s,z,x in itertools.product(S,Z,range(len(I_s[0])))), "demandS")
m.addConstrs((demand_SS[s,z] == demand_S.sum(s,'*',z) for s,z in itertools.product(S,Z)), "demandSS")

#Actual
m.addConstrs(actual_I[i,z,t] <= demand[i,z]*total_passengers_I[i] for i,z,t in itertools.product(I,Z,T))

m.addConstrs((actual_S[s,x,z,t] <= demand_S[s,x,z]*total_passengers_I[Itineraries.index(I_s[s][x])]-spill+recap_rate*(splitA*spillA+splitB*spillB)for s,z,x,t in itertools.product(S,Z,range(len(I_s[0])),T)), "actualS")
m.addConstrs((actual_SS[s,z,t] == actual_S.sum(s,'*',z) for s,z,t in itertools.product(S,Z,T)), "actualSS")


#Revenue
#These equations are where the quadratic error comes from
m.addConstrs((revenue_I[i,z,t]==price_HSR[i,z]*actual_I[i,z,t]*freq_I[i,t] for i,z,t in itertools.product(I,Z,T)),"rev")
m.addConstrs((revenue_S[s,z,t]==actual_SS[s,z,t]*freq_S[s,t] for s,z,t in itertools.product(S,Z,T)),"rev")


obj = sum(revenue_I[i,z,t]-cost_HSR[s] for i,z,t,s in itertools.product(I,Z,T,S))

m.setObjective(obj, GRB.MAXIMIZE)

m.write('HSR.lp')
m.optimize()


#Print
z = 0
t = 0
for i in I:
    print(revenue_I[i,z,t].x)



    
    
    
    

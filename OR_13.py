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

def round_down(n, decimals=0):
    multiplier = 10 ** decimals
    return math.floor(n * multiplier) / multiplier

#Data
distances = pd.read_excel('Distances.xlsx')
distances=np.array(distances)
total_passengers=pd.read_excel('TotalP.xlsx')
total_passengers=np.array(total_passengers)

#Parameters
cities = ['New York',	'Boston',	'Philadelphia',	'Providence',	'D.C.', 'Baltimore', 'Portland']
p_types = ['child', 'adult', 'senior']
periods = ['6-10','10-2','2-6','6-10']
v1 = 2 #value of price in demand 
v2= 1 #value of time in demand

recap_rate = 0.5
splitA = 0.5
splitB = 0.5


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
    

  
I = range(len(Itineraries))
Z = range(len(p_types))
T = range(len(periods))
S = range(len(Services))
X = range(len(I_s[0]))
Y = range(2)
V = range(0,len(Itineraries2))
W = range(len(Itineraries2),len(Itineraries))    
T2 = range(1,3)


#Demand
demand=np.empty((len(I),len(Z)))
for i in I:
    for z in Z:
        demand[i,z] = 1- (math.exp((v1*price_HSR[i,z]+v2*duration_HSR[i])/100)) \
              /(math.exp((v1*price_HSR[i,z]+v2*duration_HSR[i])/100)+math.exp((v1*price_AIR[i,z]+v2*duration_AIR[i])/100)) 


demand_S = np.zeros((len(S),len(X),len(Z)))
for s in S:
    for x in X:
        for z in Z:
            demand_S[s,x,z] = demand[Itineraries.index(I_s[s][x]),z]
            
demand_SS= np.zeros((len(S),len(Z)))
for s in S:
    for z in Z:
        summ = 0
        for x in X:
            summ = summ + demand_S[s,x,z]
        demand_SS[s,z] = summ
    

service_capacity = np.zeros(len(Itineraries))
for x in range(len(Itineraries)):
    service_capacity[x]=250
    
cost_HSR = np.zeros(len(Services))
for x in range(len(Services)):
    cost_HSR[x] = Itineraries_dist[x]
    

# #Optimization

m = Model("HSR")

I = range(len(Itineraries))
Z = range(len(p_types))
T = range(len(periods))
S = range(len(Services))
X = range(len(I_s[0]))
Y = range(2)
V = range(0,len(Itineraries2))
W = range(len(Itineraries2),len(Itineraries))  

freq_I = m.addVars(I,T, vtype=GRB.INTEGER,name="freq_I")
freq_S = m.addVars(S,T, vtype=GRB.INTEGER,name="freq_S")
freq_X = m.addVars(S,T, vtype= GRB.INTEGER, name = "freq_X")
revenue_I = m.addVars(I,Z,T, name="revenue_I")
revenue_S = m.addVars(S,Z,T, name="revenue_S")
taking_I = m.addVars(I,Z,T, vtype=GRB.INTEGER, name = "taking_I")
taking_S = m.addVars(S,Z,T, vtype=GRB.INTEGER, name = "taking_S")
spilled_I = m.addVars(I,Z,T, vtype= GRB.INTEGER, name = "spilled_I")
intend_I = m.addVars(I,Z,T, vtype= GRB.INTEGER, name ="intend_I")
intend_S = m.addVars(S,X,Z,T, vtype= GRB.INTEGER, name = "intend_S")
intend_SS = m.addVars(S,Z,T, vtype= GRB.INTEGER, name = "intend_SS")


#Frequency
m.addConstrs(freq_I[i,t] <=100 for i,t in itertools.product(I,T))
m.addConstrs(freq_S[s,t] <= 100 for s,t in itertools.product(S,T))

for s in S:
        m.addConstrs(freq_S[s,t] >= freq_I[Itineraries.index(i),t] for i,t in itertools.product(I_s[s],T))

#Actual
m.addConstrs(intend_I[i,z,0] <= demand[i,z]*total_passengers_I[i]-spilled_I[i,z,0]+recap_rate*(splitA*spilled_I[i,z,1]) for i,z in itertools.product(I,Z))
m.addConstrs(intend_I[i,z,t] <= demand[i,z]*total_passengers_I[i]-spilled_I[i,z,t]+recap_rate*(splitA*spilled_I[i,z,t-1]+splitB*spilled_I[i,z,t+1]) for i,z,t in itertools.product(I,Z,T2))
m.addConstrs(intend_I[i,z,3] <= demand[i,z]*total_passengers_I[i]-spilled_I[i,z,3]+recap_rate*(splitA*spilled_I[i,z,2]) for i,z in itertools.product(I,Z))

#m.addConstrs(intend_S[s,x,z,t] <= demand_S[s,x,z]*total_passengers_I[Itineraries.index(I_s[s][x])] for s,x,z,t in itertools.product(S,X,Z,T))
#m.addConstrs(intend_SS[s,z,t] <= intend_S.sum(s,'*',z,t) for s,z,t in itertools.product(S,Z,T))


# Taking
m.addConstrs(taking_I[i,z,t] <= intend_I[i,z,t] for i,z,t in itertools.product(I,Z,T))
m.addConstrs(taking_I[i,z,t] <= service_capacity[0]*freq_I[i,t] for i,z,t in itertools.product(I,Z,T))
#m.addConstrs(taking_S[s,z,t] <= intend_SS[s,z,t] for s,z,t in itertools.product(S,Z,T))
#m.addConstrs(taking_S[s,z,t] <= service_capacity[0]*freq_S[s,t] for s,z,t in itertools.product(S,Z,T))

# Spill
m.addConstrs(spilled_I[i,z,t] == service_capacity[0]*freq_I[i,t]-taking_I[i,z,t] for i,z,t in itertools.product(I,Z,T))

# Revenue
m.addConstrs((revenue_I[i,z,t]==price_HSR[i,z]*taking_I[i,z,t] for i,z,t in itertools.product(I,Z,T)),"rev")
#m.addConstrs((revenue_S[s,z,t]==taking_S[s,z,t]*freq_S[s,t] for s,z,t in itertools.product(S,Z,T)),"rev")


m.addConstrs(price_HSR[i,z]*taking_I[i,z,t]-freq_I[i,t]*cost_HSR[0]>=0 for i,z,t in itertools.product(I,Z,T))


obj = sum(revenue_I[i,z,t]-cost_HSR[s]*freq_S[s,t] for i,s,z,t in itertools.product(I,S,Z,T))#
m.setObjective(obj, GRB.MAXIMIZE)

m.write('HSR.lp')
m.optimize()


# #Print
z = 0
t = 0


print()
for s in S:
    print("Service %s%s frequency is %s" %(s,Services[s],abs(freq_S[s,t].x)))


    
    
    







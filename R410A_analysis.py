#R410A 물성치 계산
#몰리에르 선도 임계치를 넘어가는 엔탈피, 엔트로피 갑들은 별도 계산 필요
#R410A : 'HEOS::R32[0.697615]&R125[0.302385]'
import CoolProp.CoolProp as CP # Calling REFPROP
import scipy
import pandas as pd

T_k = 273

# "state 0 : temperature determination"
T_ev_sat = 10
P_ev_sat = CP.PropsSI('P','T',T_ev_sat+T_k,'Q',1,'HEOS::R32[0.697615]&R125[0.302385]')
T_cd_sat = 46
P_cd_sat = CP.PropsSI('P','T',T_cd_sat+T_k,'Q',1,'HEOS::R32[0.697615]&R125[0.302385]')

# print(P_ev_sat)
# print(P_cd_sat)
# raise IOError

# "state 1 : evaporator"
T_ev_o = T_ev_sat+T_k
h_ev_o = CP.PropsSI('H','T',T_ev_o,'Q',1,'HEOS::R32[0.697615]&R125[0.302385]')
p_ev_o = CP.PropsSI('P','T',T_ev_o,'Q',1,'HEOS::R32[0.697615]&R125[0.302385]')
s_ev_o = CP.PropsSI('S','T',T_ev_o,'Q',1,'HEOS::R32[0.697615]&R125[0.302385]')

# print(h_ev_o/1000)
# print(P_ev_o/1000)
# print(s_ev_o/1000)

"state 1-1 : superheating"
p_ev_spheat = p_ev_o
T_ev_spheat = T_ev_o + 5
h_ev_spheat = CP.PropsSI('H','T',T_ev_spheat,'Q',1,'HEOS::R32[0.697615]&R125[0.302385]')
s_ev_spheat = CP.PropsSI('S','T',T_ev_spheat,'P',p_ev_spheat,'HEOS::R32[0.697615]&R125[0.302385]')

# raise IOError
"state 2 : compressor"
p_comp_i = p_ev_spheat
"condenser pressure"
h_comp_i = h_ev_spheat
T_comp_i = T_ev_spheat
s_comp_i = CP.PropsSI('S','T',T_comp_i,'P',p_comp_i,'HEOS::R32[0.697615]&R125[0.302385]')

# 클래스 타입 만들기
AS = CP.AbstractState('HEOS','R32&R125')
AS.set_mole_fractions([0.697615,0.302385])
AS.update(CP.PT_INPUTS, p_comp_i, T_comp_i)
s1 = AS.smass() # s_comp_i_mod
h1 = AS.hmass() # h_comp_i_mod

def objective(T):
    AS.update(CP.PT_INPUTS, P_cd_sat, T)
    return AS.smass()-s1

print(AS.T()) # T_comp_i (kalvin)
# Solve for isentropic temperature
T2s = scipy.optimize.newton(objective, AS.T()) # T_comp_o_kalvin
print(T2s-T_k) # T_comp_o_cel
# Use isentropic temp to get h2s
AS.update(CP.PT_INPUTS, P_cd_sat, T2s)
s2 = AS.smass() # s_comp_o
h2s = AS.hmass() # h_comp_o
print(h1, h2s, s2)

"Isentropic enthalpy"
s_comp_o = s2
p_comp_o = P_cd_sat
T_comp_o_ideal = T2s
h_comp_o = h2s

"state 3 : condenser"
p_cd_i = P_cd_sat
T_cd_i = CP.PropsSI('T','P',p_cd_i,'Q',1,'HEOS::R32[0.697615]&R125[0.302385]') #kalvin
h_cd_i = CP.PropsSI('H','P',p_cd_i,'Q',1,'HEOS::R32[0.697615]&R125[0.302385]')
s_cd_i = CP.PropsSI('S','P',p_cd_i,'Q',1,'HEOS::R32[0.697615]&R125[0.302385]')

# print(p_cd_i, h_cd_i, s_cd_i, T_cd_i)

p_cd_o = P_cd_sat
h_cd_o = CP.PropsSI('H','P',p_cd_o,'Q',0,'HEOS::R32[0.697615]&R125[0.302385]')
s_cd_o = CP.PropsSI('S','P',p_cd_o,'Q',0,'HEOS::R32[0.697615]&R125[0.302385]')
T_cd_o = CP.PropsSI('T','P',p_cd_o,'Q',0,'HEOS::R32[0.697615]&R125[0.302385]') #kalvin

# print(p_cd_o, h_cd_o, s_cd_o, T_cd_o)

"state 3-1 : subcooling"
p_cd_sbcool = P_cd_sat
T_cd_sbcool = T_cd_o - 5 #kalvin
h_cd_sbcool = CP.PropsSI('H','T',T_cd_sbcool,'P',p_cd_sbcool,'HEOS::R32[0.697615]&R125[0.302385]')
s_cd_sbcool = CP.PropsSI('S','T',T_cd_sbcool,'P',p_cd_sbcool,'HEOS::R32[0.697615]&R125[0.302385]')

"state 4 : expension valve"
T_valve_i = T_cd_sbcool
h_valve_i = h_cd_sbcool
s_valve_i = s_cd_sbcool
p_valve_i = p_cd_sbcool

# print(T_valve_i, h_valve_i, s_valve_i, p_valve_i)

# 클래스 타입 만들기
AS2 = CP.AbstractState('HEOS','R32&R125')
AS2.set_mole_fractions([0.697615,0.302385])
AS2.update(CP.PT_INPUTS, p_valve_i, T_valve_i)
s3 = AS2.smass()
h3 = AS2.hmass()
print(s3, h3)

def objective(T):
    AS2.update(CP.PT_INPUTS, P_ev_sat, T)
    return AS2.smass()-s3

print(AS2.T()) # T_valve_o (kalvin)
# Solve for isentropic temperature
T4s = scipy.optimize.newton(objective, AS2.T())
print(T4s-273) # T_valve_o (cel)

# Use isentropic temp to get h2s
AS2.update(CP.PT_INPUTS, P_ev_sat, T4s)
s4 = AS2.smass()
h4s = AS2.hmass()
print(h3, h4s, s4)

p_valve_o = P_ev_sat
h_valve_o = h_valve_i
T_valve_o = T_ev_sat
s_valve_o = s4
# print(s_valve_o)

"state 5 : evaporator return"
T_ev_i = T_valve_o
p_ev_i = p_valve_o
h_ev_i = h_valve_o
s_ev_i = s_valve_o

# name :
# 1 : evap_o
# 2 : evap_sh
# 3 : comp_i
# 4 : comp_o
# 5 : cond_i
# 6 : cond_o
# 7 : cond_sc
# 8 : valve_i
# 9 : valve_o
# 10 : evap_i
# 11 : 1

df = pd.DataFrame({'point':['evap_o', 'evap_sh', 'comp_i', 'comp_o', 'cond_i', 'cond_o', 'cond_sc', 'valve_i','valve_o','evap_i','evap_o'],
                   'T':[T_ev_o-T_k,T_ev_spheat-T_k,T_comp_i-T_k,T_comp_o_ideal-T_k,T_cd_i-T_k,T_cd_o-T_k,T_cd_sbcool-T_k,T_valve_i-T_k,T_valve_o,T_ev_i,T_ev_o-T_k],
                   'P':[p_ev_o*10,p_ev_spheat*10,p_comp_i*10,p_comp_o*10,p_cd_i*10,p_cd_o*10,p_cd_sbcool*10,p_valve_i*10,p_valve_o*10,p_ev_i*10,p_ev_o*10],
                   'h':[h_ev_o,h_ev_spheat,h_comp_i,h_comp_o,h_cd_i,h_cd_o,h_cd_sbcool,h_valve_i,h_valve_o,h_ev_i,h_ev_o],
                   'h':[s_ev_o,s_ev_spheat,s_comp_i,s_comp_o,s_cd_i,s_cd_o,s_cd_sbcool,s_valve_i,s_valve_o,s_ev_i,s_ev_o]})

print(df)



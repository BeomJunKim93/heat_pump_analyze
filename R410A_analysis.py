#R410A 물성치 계산
#R410A : 'HEOS::R32[0.697615]&R125[0.302385]'
import CoolProp.CoolProp as CP # Calling REFPROP
import scipy


# "state 0 : temperature determination"
T_ev_sat = 10
P_ev_sat = CP.PropsSI('P','T',T_ev_sat+273,'Q',1,'HEOS::R32[0.697615]&R125[0.302385]')
T_cd_sat = 46
P_cd_sat = CP.PropsSI('P','T',T_cd_sat+273,'Q',1,'HEOS::R32[0.697615]&R125[0.302385]')

# print(P_ev_sat)
# print(P_cd_sat)
# raise IOError

# "state 1 : evaporator"
T_ev_o = T_ev_sat
h_ev_o = CP.PropsSI('H','T',T_ev_o+273,'Q',1,'HEOS::R32[0.697615]&R125[0.302385]')
p_ev_o = CP.PropsSI('P','T',T_ev_o+273,'Q',1,'HEOS::R32[0.697615]&R125[0.302385]')
s_ev_o = CP.PropsSI('S','T',T_ev_o+273,'Q',1,'HEOS::R32[0.697615]&R125[0.302385]')

# print(h_ev_o/1000)
# print(P_ev_o/1000)
# print(s_ev_o/1000)

"state 1-1 : superheating"
p_ev_spheat = p_ev_o
T_ev_spheat = T_ev_o + 5
h_ev_spheat = CP.PropsSI('H','T',T_ev_spheat+273,'Q',1,'HEOS::R32[0.697615]&R125[0.302385]')
s_ev_spheat = CP.PropsSI('S','T',T_ev_spheat+273,'P',p_ev_spheat,'HEOS::R32[0.697615]&R125[0.302385]')

# raise IOError
"state 2 : compressor"
p_comp_i = p_ev_spheat
"condenser pressure"
h_comp_i = h_ev_spheat
T_comp_i = T_ev_spheat
s_comp_i = CP.PropsSI('S','T',T_comp_i+273,'P',p_comp_i,'HEOS::R32[0.697615]&R125[0.302385]')

# 클래스 타입 만들기
AS = CP.AbstractState('HEOS','R32&R125')
AS.set_mole_fractions([0.697615,0.302385])
AS.update(CP.PT_INPUTS, p_comp_i, T_comp_i+273)
s1 = AS.smass()
h1 = AS.hmass()

def objective(T):
    AS.update(CP.PT_INPUTS, P_cd_sat, T)
    return AS.smass()-s1

print(AS.T())
# Solve for isentropic temperature
T2s = scipy.optimize.newton(objective, AS.T())
print(T2s-273)
# Use isentropic temp to get h2s
AS.update(CP.PT_INPUTS, P_cd_sat, T2s)
s2 = AS.smass()
h2s = AS.hmass()
print(h1, h2s, s2)
raise IOError
"Isentropic enthalpy"
s_comp_o = s_comp_i
p_comp_o = P_cd_sat
T_comp_o_ideal = CP.PropsSI('T','P',p_comp_o,'S',1000,'HEOS::R32[0.697615]&R125[0.302385]')
raise IOError



# h_comp_o =
# T_comp_o = temperature(R410A, P=p_comp_o, h=h_comp_o)



T_cd_o = 46

"state 3 : condenser"
p_cd_i = p_comp_o
T_cd_i = temperature(R410A, P=p_cd_i, x=1)
h_cd_i = enthalpy(R410A, P=p_cd_i, x=1)
s_cd_i = CP.PropsSI('S','T',T_ev_spheat+273,'P',p_ev_spheat,'HEOS::R32[0.697615]&R125[0.302385]')

p_cd_o = CP.PropsSI('P','T',T_ev_o+273,'Q',1,'HEOS::R32[0.697615]&R125[0.302385]')
h_cd_o = enthalpy(R410A, P=p_cd_o, x=0)
s_cd_o = CP.PropsSI('S','T',T_ev_spheat+273,'P',p_ev_spheat,'HEOS::R32[0.697615]&R125[0.302385]')

"state 3-1 : subcooling"
p_cd_sbcool = p_cd_o
T_cd_sbcool = T_cd_o - 5
h_cd_sbcool = enthalpy(R410A, T=T_cd_sbcool, P=p_cd_sbcool)
s_cd_sbcool = CP.PropsSI('S','T',T_ev_spheat+273,'P',p_ev_spheat,'HEOS::R32[0.697615]&R125[0.302385]')

"state 4 : expension valve"
T_valve_i = T_cd_sbcool
h_valve_i = h_cd_sbcool
s_valve_i = s_cd_sbcool
p_valve_i = pressure(R410A, T=T_valve_i, h=h_valve_i)

p_valve_o = p_ev_o
h_valve_o = h_valve_i
T_valve_o = temperature(R410A, P=p_valve_o, h=h_valve_o)
s_valve_o = CP.PropsSI('S','T',T_ev_spheat+273,'P',p_ev_spheat,'HEOS::R32[0.697615]&R125[0.302385]')

"state 5 : evaporator return"
T_ev_i = T_valve_o
p_ev_i = p_valve_o
h_ev_i = h_valve_o
"evap outlet enthalpy"
s_ev_i = s_valve_o
"evap outlet entropy"

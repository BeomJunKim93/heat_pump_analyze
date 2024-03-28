import CoolProp.CoolProp as CP # Calling REFPROP

abs_temp = 273.15

P_hc_high=218800
P_hc_low=89000
T_hc_comp_o=86
T_hc_comp_i=46.5
T_hc_eev_i=66.5
T_hc_sc_sh_measured=7.1
T_hc_cond=73.6
T_hc_evap=39.1
W_hc=14.545
P_lc_high=279400
# P_lc_low=0
T_lc_comp_o=77
T_lc_comp_i=8.2
T_lc_eev_i=45
T_lc_sc_sh_measured=2.6
T_lc_cond=47.6
T_lc_evap=5.7
W_lc=5.746


P_lc_low_2 = CP.PropsSI('P','T',T_lc_evap+abs_temp,'Q',1,'R410A')
h_lc_low_2 = CP.PropsSI('H','T',T_lc_evap+abs_temp,'Q',1,'R410A')
print(P_lc_low_2)
print(h_lc_low_2)

P_hc_low_2 = CP.PropsSI('P','T',T_hc_evap+abs_temp,'Q',1,'R134a')
h_hc_low_2 = CP.PropsSI('H','T',T_hc_evap+abs_temp,'Q',1,'R134a')

print(P_hc_low_2)
print(h_hc_low_2)

"Low-cycle"

"state 1 : compressor inlet"
P_lc_low = CP.PropsSI('P','T',T_lc_evap+abs_temp,'Q',1,'R410A')
# print(P_lc_low)

s_lc_comp_i = CP.PropsSI('S', 'T', T_lc_comp_i+abs_temp, 'P', P_lc_low, 'R410A')
# print(s_lc_comp_i)

h_lc_comp_i = CP.PropsSI('H','T',T_lc_comp_i+abs_temp,'Q',1,'R410A')
print(h_lc_comp_i)

raise IOError

p_lc_comp_i = P_lc_low # 입력값
T_lc_comp_i = T_lc_evap+abs_temp+T_lc_sc_sh_measured # 입력값
h_lc_comp_i = CP.PropsSI('H','T',T_lc_comp_i,'Q',1,'HEOS::R32[0.697615]&R125[0.302385]')
s_lc_comp_i = CP.PropsSI('S', 'T', T_lc_comp_i, 'P', p_lc_comp_i, 'HEOS::R32[0.697615]&R125[0.302385]')
lc_comp_i = status(T_lc_comp_i, h_lc_comp_i, p_lc_comp_i, s_lc_comp_i)

"state 2 : compressor outlet"
# 클래스 타입 만들기
AS = CP.AbstractState('HEOS', 'R32&R125')
AS.set_mole_fractions([0.697615, 0.302385])
AS.update(CP.PT_INPUTS, p_lc_comp_i, T_lc_comp_i)
s1 = AS.smass()  # s_comp_i_mod
h1 = AS.hmass()  # h_comp_i_mod


# AS, T2s = calc_newton_optimization(AS, P_lc_high)

def objective(T):
    AS.update(CP.PT_INPUTS, P_lc_high, T)
    return AS.smass() - s1

# print(AS.T()) # T_comp_i (kalvin)
# Solve for isentropic temperature
T2s = scipy.optimize.newton(objective, AS.T())  # T_comp_o_kalvin
# print(T2s-abs_temp) # T_comp_o_cel
# Use isentropic temp to get h2s

AS.update(CP.PT_INPUTS, P_lc_high, T2s)
s2 = AS.smass()  # s_comp_o
h2s = AS.hmass()  # h_comp_o
# print(h1, h2s, s2)

"Isentropic enthalpy"
s_lc_comp_o = s2
p_lc_comp_o = P_lc_high
T_lc_comp_o = T2s
h_lc_comp_o = h2s
lc_comp_o = status(T_lc_comp_o, h_lc_comp_o, p_lc_comp_o, s_lc_comp_o)

"state 3 : expension valve inlet"
T_lc_valve_i = T_lc_cond
p_lc_valve_i = P_lc_high
h_lc_valve_i = CP.PropsSI('H','T',T_lc_valve_i,'P',p_lc_valve_i,'HEOS::R32[0.697615]&R125[0.302385]')
s_lc_valve_i = CP.PropsSI('S','T',T_lc_valve_i,'P',p_lc_valve_i,'HEOS::R32[0.697615]&R125[0.302385]')
lc_valve_i = status(T_lc_valve_i, h_lc_valve_i, p_lc_valve_i, s_lc_valve_i)

"state 4 : expension valve outlet"
# 클래스 타입 만들기
AS2 = CP.AbstractState('HEOS','R32&R125')
AS2.set_mole_fractions([0.697615,0.302385])
AS2.update(CP.PT_INPUTS, p_lc_valve_i, T_lc_valve_i)
s3 = AS2.smass()
h3 = AS2.hmass()
# print(s3, h3)

'''def objective_lc_eev(T):
    AS2.update(CP.PT_INPUTS, P_lc_evap, T)
    return AS2.smass()-s3

# print(AS2.T()) # T_valve_o (kalvin)
# Solve for isentropic temperature
T4s = scipy.optimize.newton(objective, AS2.T())
# print(T4s-abs_temp) # T_valve_o (cel)
'''
AS2, T4s = calc_newton_optimization(AS2, P_lc_evap)
# Use isentropic temp to get h2s
AS2.update(CP.PT_INPUTS, P_lc_evap, T4s)
s4 = AS2.smass()
h4s = AS2.hmass()
# print(h3, h4s, s4)

"Isentropic enthalpy"
p_lc_valve_o = P_lc_evap
h_lc_valve_o = h_lc_valve_i
T_lc_valve_o = T_lc_evap
s_lc_valve_o = s4
lc_valve_o = status(T_lc_valve_o, h_lc_valve_o, p_lc_valve_o, s_lc_valve_o)

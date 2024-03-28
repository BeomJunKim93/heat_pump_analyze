#R410A : LC 물성치 계산
#R134a : HC 물성치 계산
#몰리에르 선도 임계치를 넘어가는 엔탈피, 엔트로피 갑들은 별도 계산 필요
#R410A : 'HEOS::R32[0.697615]&R125[0.302385]'
import CoolProp.CoolProp as CP # Calling REFPROP
import scipy
import pandas as pd

def calc_newton_optimization(AS, P):
    def temp_objective(T):
        AS.update(CP.PT_INPUTS, P, T)
        return AS.smass() - s1
    T = scipy.optimize.newton(temp_objective, AS.T())
    return AS, T

class status:
    def __init__(self, t_value, h_value, p_value, s_value): # 괄호 안의 파라미터가 입력되는 것을 표현
        self.temperature = t_value
        self.enthalpy = h_value
        self.pressure = p_value
        self.entropy = s_value
    def export(self):
        return [self.temperature, self.enthalpy, self.pressure, self.entropy]

class result_cycle_lc:
    def __init__(self, lc_comp_i_status, lc_comp_o_status, lc_valve_i_status, lc_valve_o_status):
        self.lc_comp_i = lc_comp_i_status
        self.lc_comp_o = lc_comp_o_status
        self.lc_valve_i = lc_valve_i_status
        self.lc_valve_o = lc_valve_o_status

    def export(self):
        return [self.lc_comp_i_status, self.lc_comp_o_status, self.lc_valve_i_status, self.lc_valve_o_status]


abs_temp = 273

# (P_hc_high, P_hc_low, T_hc_comp_o, T_hc_comp_i, T_hc_eev_i, T_hc_sc_sh_measured, T_hc_cond, T_hc_evap, W_hc,
#  P_lc_high, P_lc_low, T_lc_comp_o, T_lc_comp_i, T_lc_eev_i, T_lc_sc_sh_measured, T_lc_cond, T_lc_evap, W_lc)

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

"Low-cycle"

P_lc_low = CP.PropsSI('P','T',T_lc_evap+abs_temp,'Q',0,'HEOS::R32[0.697615]&R125[0.302385]')

"state 1 : compressor inlet"
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




######################################################################################################################################################

class result_cycle_hc:
    def __init__(self, hc_comp_i_status, hc_comp_o_status, hc_valve_i_status, hc_valve_o_status):
        self.hc_comp_i = hc_comp_i_status
        self.hc_comp_o = hc_comp_o_status
        self.hc_valve_i = hc_valve_i_status
        self.hc_valve_o = hc_valve_o_status

    def export(self):
        return [self.hc_comp_i_status, self.hc_comp_o_status, self.hc_valve_i_status, self.hc_valve_o_status]

"High-cycle"

"state 1 : compressor inlet"
p_hc_comp_i = P_hc_low # 입력값
T_hc_comp_i = T_hc_evap+abs_temp+T_hc_sc_sh_measured # 입력값
h_hc_comp_i = CP.PropsSI('H','T',T_hc_comp_i,'Q',1,'R134a')
s_hc_comp_i = CP.PropsSI('S', 'T', T_hc_comp_i, 'P', p_hc_comp_i, 'R134a')
hc_comp_i = status(T_hc_comp_i, h_hc_comp_i, p_hc_comp_i, s_hc_comp_i)

"state 2 : compressor outlet"
# 클래스 타입 만들기
AS = CP.AbstractState('R134a')
# AS.set_mole_fractions([0.697615, 0.302385])
AS.update(CP.PT_INPUTS, p_hc_comp_i, T_hc_comp_i)
s1 = AS.smass()  # s_comp_i_mod
h1 = AS.hmass()  # h_comp_i_mod

'''def objective(T):
    AS.update(CP.PT_INPUTS, P_hc_high, T)
    return AS.smass() - s1

# print(AS.T()) # T_comp_i (kalvin)
# Solve for isentropic temperature
T2s = scipy.optimize.newton(objective, AS.T())  # T_comp_o_kalvin'''
AS, T2s = calc_newton_optimization(AS, p_hc_high)
# print(T2s-abs_temp) # T_comp_o_cel
# Use isentropic temp to get h2s
AS.update(CP.PT_INPUTS, P_hc_high, T2s)
s2 = AS.smass()  # s_comp_o
h2s = AS.hmass()  # h_comp_o
# print(h1, h2s, s2)

"Isentropic enthalpy"
s_hc_comp_o = s2
p_hc_comp_o = P_hc_high
T_hc_comp_o = T2s
h_hc_comp_o = h2s
hc_comp_o = status(T_hc_comp_o, h_hc_comp_o, p_hc_comp_o, s_hc_comp_o)

"state 3 : expension valve inlet"
T_hc_valve_i = T_hc_cond
p_hc_valve_i = P_hc_high
h_hc_valve_i = CP.PropsSI('H','T',T_hc_valve_i,'P',p_hc_valve_i,'R134a')
s_hc_valve_i = CP.PropsSI('S','T',T_hc_valve_i,'P',p_hc_valve_i,'R134a')
hc_valve_i = status(T_hc_valve_i, h_hc_valve_i, p_hc_valve_i, s_hc_valve_i)

"state 4 : expension valve outlet"
# 클래스 타입 만들기
AS2 = CP.AbstractState('R134a')
# AS2.set_mole_fractions([0.697615,0.302385])
AS2.update(CP.PT_INPUTS, p_hc_valve_i, T_hc_valve_i)
s3 = AS2.smass()
h3 = AS2.hmass()
# print(s3, h3)

'''def objective(T):
    AS2.update(CP.PT_INPUTS, P_hc_evap, T)
    return AS2.smass()-s3

# print(AS2.T()) # T_valve_o (kalvin)
# Solve for isentropic temperature
T4s = scipy.optimize.newton(objective, AS2.T())'''
AS2, T4s = calc_newton_optimization(AS2, p_hc_evap)
# print(T4s-abs_temp) # T_valve_o (cel)

# Use isentropic temp to get h2s
AS2.update(CP.PT_INPUTS, P_hc_evap, T4s)
s4 = AS2.smass()
h4s = AS2.hmass()
# print(h3, h4s, s4)

"Isentropic enthalpy"
p_hc_valve_o = P_hc_evap
h_hc_valve_o = h_hc_valve_i
T_hc_valve_o = T_hc_evap
s_hc_valve_o = s4
hc_valve_o = status(T_hc_valve_o, h_hc_valve_o, p_hc_valve_o, s_hc_valve_o)

######################################################################################################################################################

error_lc_comp = (T_lc_comp_o_ideal - T_lc_comp_o) / (T_lc_comp_o_ideal)

delta_h_lc_evap = h_lc_comp_i - h_lc_eev_o
delta_h_lc_comp = h_lc_comp_o - h_lc_comp_i
delta_h_lc_cond = h_lc_comp_o - h_lc_eev_i

COP_lc = delta_h_lc_cond / delta_h_lc_comp

error_hc_comp = (T_hc_comp_o_ideal - T_hc_comp_o) / (T_hc_comp_o_ideal)

delta_h_hc_evap = h_hc_comp_i - h_hc_eev_o
delta_h_hc_comp = h_hc_comp_o - h_hc_comp_i
delta_h_hc_cond = h_hc_comp_o - h_hc_eev_i

COP_hc = delta_h_hc_cond / delta_h_hc_comp
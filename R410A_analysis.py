#R410A 물성치 계산
#몰리에르 선도 임계치를 넘어가는 엔탈피, 엔트로피 갑들은 별도 계산 필요
#R410A : 'HEOS::R32[0.697615]&R125[0.302385]'
import CoolProp.CoolProp as CP # Calling REFPROP
# import scipy
# import pandas as pd

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

class status:
    def __init__(self, t_value, h_value, p_value, s_value):
        self.temperature = t_value
        self.enthalpy = h_value
        self.pressure = p_value
        self.entropy = s_value
    def export(self):
        return [self.temperature, self.enthalpy, self.pressure, self.entropy]

class result_cycle:
    def __init__(self, evap_o_status, evap_sh_status, comp_i_status, comp_o_status, cond_i_status, cond_o_status, cond_sc_status, valve_i_status, valve_o_status, evap_i_status):
        self.evap_o = evap_o_status
        self.evap_sh = evap_sh_status
        self.comp_i = comp_i_status
        self.comp_o = comp_o_status
        self.cond_i = cond_i_status
        self.cond_o = cond_o_status
        self.cond_sc = cond_sc_status
        self.valve_i = valve_i_status
        self.valve_o = valve_o_status
        self.evap_i = evap_i_status

    def export(self):
        return [self.evap_o, self.evap_sh, self.comp_i, self.comp_o, self.cond_i, self.cond_o, self.cond_sc, self.valve_i, self.valve_o, self.evap_i]

# a = status(2, 3, 4, 5)
# b = status(4, 5, 6, 7)
# a.export()
# b.export()
#
# result_cycle.evap_o.export()

# data = pd.read_excel('./basedata.xlsx')

point_arr = ['evap_o', 'evap_sh', 'comp_i', 'comp_o', 'cond_i', 'cond_o', 'cond_sc', 'valve_i', 'valve_o', 'evap_i']
status_arr = ['temperature', 'enthalpy', 'pressure', 'entropy']

res_dict = {}

for point_element in point_arr:
    for status_element in status_arr:
        res_dict[point_element + '_' + status_element] = []

# for iter, row in data.iterrows():
for i in range(100):
    # 입력데이터 연결
    abs_temp = 273

    # (P_hc_high, P_hc_low, T_hc_comp_o, T_hc_comp_i, T_hc_eev_i, T_hc_subcool_superheat_measured, T_hc_cond, T_hc_evap, W_hc,
    #  P_lc_high, P_lc_low, T_lc_comp_o, T_lc_comp_i, T_lc_eev_i, T_lc_subcool_superheat_measured, T_lc_cond, T_lc_evap, W_lc)

    T_evap_sat = 10 #row['t_lc_evap']
    T_cond_sat = 30 #row['colname']

    # "state 0 : temperature determination"
    T_ev_sat = 10
    P_ev_sat = CP.PropsSI('P','T',T_evap_sat+abs_temp,'Q',1,'HEOS::R32[0.697615]&R125[0.302385]')
    T_cd_sat = 46
    P_cd_sat = CP.PropsSI('P','T',T_cond_sat+abs_temp,'Q',1,'HEOS::R32[0.697615]&R125[0.302385]')

    "state 1 : evaporator"
    T_ev_o = T_ev_sat+abs_temp
    h_ev_o = CP.PropsSI('H','T',T_ev_o,'Q',1,'HEOS::R32[0.697615]&R125[0.302385]')
    p_ev_o = CP.PropsSI('P','T',T_ev_o,'Q',1,'HEOS::R32[0.697615]&R125[0.302385]')
    s_ev_o = CP.PropsSI('S','T',T_ev_o,'Q',1,'HEOS::R32[0.697615]&R125[0.302385]')
    ev_o = status(T_ev_o, h_ev_o, p_ev_o, s_ev_o)

    "state 1-1 : superheating"
    p_hc_evap_spheat = 279100 # p_hc_low
    T_hc_evap_spheat = T_ev_o + 5
    h_hc_evap_spheat = CP.PropsSI('H','T',T_hc_evap_spheat,'Q',1,'HEOS::R32[0.697615]&R125[0.302385]')
    s_hc_evap_spheat = CP.PropsSI('S','T',T_hc_evap_spheat,'P',p_hc_evap_spheat,'HEOS::R32[0.697615]&R125[0.302385]')
    hc_evap_spheat = status(T_hc_evap_spheat, h_hc_evap_spheat, p_hc_evap_spheat, s_hc_evap_spheat)

    # raise IOError
    "state 2 : compressor"
    p_comp_i = p_ev_o
    "condenser pressure"
    h_comp_i = h_hc_evap_spheat
    T_comp_i = T_hc_evap_spheat
    s_comp_i = CP.PropsSI('S','T',T_comp_i,'P',p_comp_i,'HEOS::R32[0.697615]&R125[0.302385]')
    comp_i = status(T_comp_i, h_comp_i, p_comp_i, s_comp_i)

    T_comp_o = 46+abs_temp
    s_comp_o = CP.PropsSI('S','T',T_comp_o,'P',279100,'HEOS::R32[0.697615]&R125[0.302385]')
    print(s_comp_o)

    # from ctREFPROP.ctREFPROP import REFPROPFunctionLibrary
    # import glob
    # import pandas
    # import numpy as np
    # import matplotlib.pyplot as plt
    # import os
    # os.environ['RPPREFIX'] = r'C:/Program Files (x86)/REFPROP'
    #
    # RP = REFPROPFunctionLibrary(os.environ['RPPREFIX'])
    # RP.SETPATHdll(os.environ['RPPREFIX'])
    # MOLAR_BASE_SI = RP.GETENUMdll(0, "MOLAR BASE SI").iEnum
    # print(RP.RPVersion())


    T_comp_o_ideal = CP.PropsSI('T','S|gas',s_comp_o,'P',279100,'HEOS::R32[0.697615]&R125[0.302385]')
    print(T_comp_o_ideal)

    raise IOError
    # 클래스 타입 만들기
    AS = CP.AbstractState('HEOS','R32&R125')
    AS.set_mole_fractions([0.697615,0.302385])
    AS.update(CP.PT_INPUTS, p_comp_i, T_comp_i)
    s1 = AS.smass() # s_comp_i_mod
    h1 = AS.hmass() # h_comp_i_mod

    def objective(T):
        AS.update(CP.PT_INPUTS, P_cd_sat, T)
        return AS.smass()-s1

    # print(AS.T()) # T_comp_i (kalvin)
    # Solve for isentropic temperature
    T2s = scipy.optimize.newton(objective, AS.T()) # T_comp_o_kalvin
    # print(T2s-abs_temp) # T_comp_o_cel
    # Use isentropic temp to get h2s
    AS.update(CP.PT_INPUTS, P_cd_sat, T2s)
    s2 = AS.smass() # s_comp_o
    h2s = AS.hmass() # h_comp_o
    # print(h1, h2s, s2)

    "Isentropic enthalpy"
    s_comp_o = s2
    p_comp_o = P_cd_sat
    T_comp_o_ideal = T2s
    h_comp_o = h2s
    comp_o = status(T_comp_o_ideal, h_comp_o, p_comp_o, s_comp_o)

    "state 3 : condenser"
    p_cd_i = P_cd_sat
    T_cd_i = CP.PropsSI('T','P',p_cd_i,'Q',1,'HEOS::R32[0.697615]&R125[0.302385]') #kalvin
    h_cd_i = CP.PropsSI('H','P',p_cd_i,'Q',1,'HEOS::R32[0.697615]&R125[0.302385]')
    s_cd_i = CP.PropsSI('S','P',p_cd_i,'Q',1,'HEOS::R32[0.697615]&R125[0.302385]')
    cd_i = status(T_cd_i, h_cd_i, p_cd_i, s_cd_i)

    # print(p_cd_i, h_cd_i, s_cd_i, T_cd_i)

    p_cd_o = P_cd_sat
    h_cd_o = CP.PropsSI('H','P',p_cd_o,'Q',0,'HEOS::R32[0.697615]&R125[0.302385]')
    s_cd_o = CP.PropsSI('S','P',p_cd_o,'Q',0,'HEOS::R32[0.697615]&R125[0.302385]')
    T_cd_o = CP.PropsSI('T','P',p_cd_o,'Q',0,'HEOS::R32[0.697615]&R125[0.302385]') #kalvin
    cd_o = status(T_cd_o, h_cd_o, p_cd_o, s_cd_o)

    # print(p_cd_o, h_cd_o, s_cd_o, T_cd_o)

    # "state 3-1 : subcooling"
    # p_cd_sbcool = P_cd_sat
    # T_cd_sbcool = T_cd_o - 5 #kalvin
    # h_cd_sbcool = CP.PropsSI('H','T',T_cd_sbcool,'P',p_cd_sbcool,'HEOS::R32[0.697615]&R125[0.302385]')
    # s_cd_sbcool = CP.PropsSI('S','T',T_cd_sbcool,'P',p_cd_sbcool,'HEOS::R32[0.697615]&R125[0.302385]')
    # cd_sbcool = status(T_cd_sbcool, h_cd_sbcool, p_cd_sbcool, s_cd_sbcool)

    "state 4 : expension valve"
    T_valve_i = T_cd_sbcool
    h_valve_i = h_cd_sbcool
    s_valve_i = s_cd_sbcool
    p_valve_i = p_cd_sbcool
    valve_i = status(T_valve_i, h_valve_i, p_valve_i, s_valve_i)

    # print(T_valve_i, h_valve_i, s_valve_i, p_valve_i)

    # 클래스 타입 만들기
    AS2 = CP.AbstractState('HEOS','R32&R125')
    AS2.set_mole_fractions([0.697615,0.302385])
    AS2.update(CP.PT_INPUTS, p_valve_i, T_valve_i)
    s3 = AS2.smass()
    h3 = AS2.hmass()
    # print(s3, h3)

    def objective(T):
        AS2.update(CP.PT_INPUTS, P_ev_sat, T)
        return AS2.smass()-s3

    # print(AS2.T()) # T_valve_o (kalvin)
    # Solve for isentropic temperature
    T4s = scipy.optimize.newton(objective, AS2.T())
    # print(T4s-abs_temp) # T_valve_o (cel)

    # Use isentropic temp to get h2s
    AS2.update(CP.PT_INPUTS, P_ev_sat, T4s)
    s4 = AS2.smass()
    h4s = AS2.hmass()
    # print(h3, h4s, s4)

    p_valve_o = P_ev_sat
    h_valve_o = h_valve_i
    T_valve_o = T_evap_sat
    s_valve_o = s4
    # print(s_valve_o)
    valve_o = status(T_valve_o, h_valve_o, p_valve_o, s_valve_o)

    "state 5 : evaporator return"
    T_ev_i = T_valve_o
    p_ev_i = p_valve_o
    h_ev_i = h_valve_o
    s_ev_i = s_valve_o
    ev_i = status(T_ev_i, h_ev_i, p_ev_i, s_ev_i)

    res_cycle = result_cycle(ev_o, ev_spheat, comp_i, comp_o, cd_i, cd_o, cd_sbcool, valve_i, valve_o, ev_i)


    i = 0
    for point_element in point_arr:
        j = 0
        for status_element in status_arr:
            res_dict[point_element + '_' + status_element].append(res_cycle.export()[i].export()[j])
            j = j + 1
        i = i + 1

result_df = pd.DataFrame(res_dict)
result_df.to_csv('./result.csv', encoding='ANSI')
print(data)
print(result_df)


#
# df = pd.DataFrame({'point':['evap_o', 'evap_sh', 'comp_i', 'comp_o', 'cond_i', 'cond_o', 'cond_sc', 'valve_i','valve_o','evap_i','evap_o'],
#                    'T':[T_ev_o-abs_temp,T_ev_spheat-abs_temp,T_comp_i-abs_temp,T_comp_o_ideal-abs_temp,T_cd_i-abs_temp,T_cd_o-abs_temp,T_cd_sbcool-abs_temp,T_valve_i-abs_temp,T_valve_o,T_ev_i,T_ev_o-abs_temp], # C
#                    'P':[p_ev_o,p_ev_spheat,p_comp_i,p_comp_o,p_cd_i,p_cd_o,p_cd_sbcool,p_valve_i,p_valve_o,p_ev_i,p_ev_o], #pa
#                    'h':[h_ev_o,h_ev_spheat,h_comp_i,h_comp_o,h_cd_i,h_cd_o,h_cd_sbcool,h_valve_i,h_valve_o,h_ev_i,h_ev_o], #J/kg
#                    's':[s_ev_o,s_ev_spheat,s_comp_i,s_comp_o,s_cd_i,s_cd_o,s_cd_sbcool,s_valve_i,s_valve_o,s_ev_i,s_ev_o]})

# print(df)



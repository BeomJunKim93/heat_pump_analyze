# 컴포넌트별로 구분해서 돌릴 수 있도록 클래스화한 모듈 코드
# 실제 call 및 계산은 다른 코드에서 하도록 한다!
# from scipy.optimize import least_squares
import pandas as pd
import CoolProp.CoolProp as CP
from CoolProp.CoolProp import AbstractState
from scipy.optimize import least_squares
from scipy.optimize import minimize_scalar
from CoolProp.Plots import PropertyPlot
import math
import copy
import time
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

def print_status(liquid):
    print(liquid.T(), liquid.p(), liquid.hmass())

stefan_coefficient = 5.67 * 10**(-8)

class heat_storage():
    def __init__(self, config_dict):
        self.pressure = config_dict['pressure']             # Pa
        self.effectiveness = config_dict['effectiveness']
        self.size = config_dict['size']                     # m3
        self.temperature = config_dict['temperature']
        self.fluid_name = config_dict['fluid_name']
        if 'backend' in config_dict.keys():
            self.backend_name = config_dict['backend']
        else:
            self.backend_name = 'HEOS'
        self.fluid = AbstractState(self.backend_name, self.fluid_name)
        self.fluid.update(CP.PT_INPUTS, 101325, config_dict['temperature'])
        self.amount = self.size * self.fluid.rhomass()      # kg

    def export_fluid(self, flowrate, timestep):
        # 유체를 내보낼 때는 온도변화가 없으므로 양만 차감한다
        export_amount = flowrate * timestep     # kg/s * s = kg
        self.amount = self.amount - export_amount
        return self.fluid

    def import_fluid(self, inlet_fluid, flowrate, timestep):
        # 유체를 들여보낼 때는 온도변화가 있으므로 양과 온도를 둘다 조정한다
        # 1. 양을 증가시킴
        import_amount = flowrate * timestep     # kg/s * s = kg
        self.amount = self.amount + import_amount

        # 2. 온도를 증가시킴
        self.fluid.update(CP.HmassP_INPUTS, self.fluid.hmass() + import_amount * (inlet_fluid.T() - self.fluid.T()) * inlet_fluid.cpmass() / self.amount, 101325)

    def export_hx(self, inlet_fluid, flowrate, timestep, hx_efficiency):
        cold_capacity = inlet_fluid.cpmass() * flowrate
        if inlet_fluid.T() > self.fluid.T():
            hot_fluid = inlet_fluid
            cold_fluid = self.fluid
            hot_flowrate = flowrate
            cold_flowrate = self.amount

        else:
            hot_fluid = self.fluid
            cold_fluid = inlet_fluid
            hot_flowrate = self.amount
            cold_flowrate = flowrate

        Q_max = cold_capacity * (hot_fluid.T() - cold_fluid.T())
        Q_act = hx_efficiency * Q_max

        outlet_fluid = AbstractState(inlet_fluid.backend_name(), inlet_fluid.name())

        if inlet_fluid.T() > self.fluid.T():
            outlet_fluid.update(CP.HmassP_INPUTS, inlet_fluid.hmass() - Q_act/flowrate, inlet_fluid.p())
            self.fluid.update(CP.HmassP_INPUTS, self.fluid.hmass() + Q_act/self.amount, self.fluid.p())
        else:
            outlet_fluid.update(CP.HmassP_INPUTS, inlet_fluid.hmass() + Q_act/flowrate, inlet_fluid.p())
            self.fluid.update(CP.HmassP_INPUTS, self.fluid.hmass() - Q_act/self.amount, self.fluid.p())
        return outlet_fluid

class heat_absorber():
    def __init__(self, config_dict):
        self.absorptance = config_dict['absorptance']
        self.efficiency = config_dict['efficiency']
        self.area = config_dict['area']
        self.ground_factor = config_dict['ground_factor']   # 지면과 천공의 비율을 지정합니다 (수직의 경우 0.5, 수평(천공을 보는)의 경우 0)

    def calc_exchange(self, inlet_fluid, flowrate, insolation, sky_temperature, regolith_temperature, timestep):
        # 일사량을 기반으로 인입열량을 정의
        heat_in = insolation * self.absorptance * self.efficiency * self.area   # W

        # inlet_fluid의 온도와 판 온도가 같다고 가정하고 복사 열손실을 정의
        sky_loss = (1 - self.ground_factor) * self.area * stefan_coefficient * (inlet_fluid.T()**4 - sky_temperature**4)
        ground_loss = self.ground_factor * self.area * stefan_coefficient * (inlet_fluid.T() ** 4 - regolith_temperature ** 4)
        heat_loss = sky_loss + ground_loss

        outlet_fluid = AbstractState(inlet_fluid.backend_name(), inlet_fluid.name())
        outlet_fluid.update(CP.HmassP_INPUTS, inlet_fluid.hmass() + (heat_in - heat_loss) / flowrate, inlet_fluid.p())
        if inlet_fluid.T() <= outlet_fluid.T():
            return outlet_fluid
        else:
            return inlet_fluid


class teg_panel():
    def __init__(self, config_dict):
        self.absorptance = config_dict['absorptance']
        self.efficiency = config_dict['efficiency']
        self.area = config_dict['area']
        self.ground_factor = config_dict['ground_factor']
        self.teg_conductivity = 0.89
        self.teg_length = 0.003


    def calc_exchange(self, inlet_fluid, flowrate, sky_temperature, regolith_temperature, timestep):
        # inlet_fluid의 온도와 판 온도가 같다고 가정하고 복사 열손실을 정의
        sky_loss = (1 - self.ground_factor) * self.area * stefan_coefficient * (inlet_fluid.T()**4 - sky_temperature**4)
        ground_loss = self.ground_factor * self.area * stefan_coefficient * (inlet_fluid.T() ** 4 - regolith_temperature ** 4)
        heat_loss = sky_loss + ground_loss

        inlet_temp = inlet_fluid.T()
        print(regolith_temperature)
        def func(x):
            # x = [T_hot, T_cold, Q_in]
            return [
                x[0] - inlet_temp,
                # x[2] - 5 * cp_water * flow_rate,
                # x[2] - (inlet_temp - x[0]) * cp_water * flow_rate,
                (x[1] ** 4 - 4 ** 4 * (1 - self.ground_factor) - regolith_temperature ** 4 * (self.ground_factor)) * stefan_coefficient * self.area - 0.95 * x[2],
                self.teg_conductivity * (x[0] - x[1]) / self.teg_length - 0.95 * x[2]
            ]

        res = least_squares(func, [regolith_temperature, regolith_temperature, 5 * inlet_fluid.cpmass() * flowrate], bounds=[(0, 0, 0), (10000, 10000, 10000000)])
        res = res['x']
        T_hot = res[0]
        T_cold = res[1]
        dT = T_hot - T_cold
        P_teg = res[2] * 0.05 # * timestep
        T_drop = res[2] / (inlet_fluid.cpmass() * flowrate)

        print(res)
        print(T_drop)


        export_dict = {
            'T_hot':T_hot,
            'T_cold': T_cold,
            'dT':T_hot-T_cold,
            'P_teg':P_teg
        }

        outlet_fluid = AbstractState(inlet_fluid.backend_name(), inlet_fluid.name())
        # outlet_fluid.update(CP.HmassP_INPUTS, inlet_fluid.hmass() - res[2] * timestep / flowrate, inlet_fluid.p())
        outlet_fluid.update(CP.PT_INPUTS, inlet_fluid.p(), inlet_fluid.T() - T_drop)
        return outlet_fluid, export_dict

class compressor():
    def __init__(self, effectiveness):
        self.effectiveness = effectiveness

    def calc_compress(self, inlet_fluid, inlet_flowrate, tgt_temperature, timestep):
        ideal_fluid = AbstractState(inlet_fluid.backend_name(), inlet_fluid.name())
        ideal_fluid.update(CP.QT_INPUTS, 1, tgt_temperature)
        h_out = (ideal_fluid.hmass() - inlet_fluid.hmass()) / self.effectiveness + inlet_fluid.hmass()
        outlet_fluid = AbstractState(inlet_fluid.backend_name(), inlet_fluid.name())
        outlet_fluid.update(CP.HmassP_INPUTS, h_out, ideal_fluid.p())
        enthalphy_added = (outlet_fluid.hmass() - inlet_fluid.hmass()) * inlet_flowrate * timestep
        result_dict = {
            'q_added':enthalphy_added
        }
        return outlet_fluid, result_dict

class condenser():
    def __init(self):
        pass

    def calc_condenser_byload(self, inlet_fluid, inlet_flowrate, heat_load):
        outlet_fluid = AbstractState(inlet_fluid.backend_name(), inlet_fluid.name())
        outlet_fluid.update(CP.HmassP_INPUTS, inlet_fluid.hmass() - heat_load/inlet_flowrate, inlet_fluid.p())
        return outlet_fluid

    def calc_condenser_actual(self, inlet_fluid, inlet_flowrate):
        outlet_fluid = AbstractState(inlet_fluid.backend_name(), inlet_fluid.name())
        outlet_fluid.update(CP.PQ_INPUTS, inlet_fluid.p(), 0)
        exhausted_heat = (inlet_fluid.hmass() - outlet_fluid.hmass()) * flowrate
        return outlet_fluid, exhausted_heat

class exp_valve():
    def __init(self):
        pass

    def calc_expansion(self, inlet_fluid, tgt_pressure):
        outlet_fluid = AbstractState(inlet_fluid.backend_name(), inlet_fluid.name())
        outlet_fluid.update(CP.HmassP_INPUTS, inlet_fluid.hmass(), tgt_pressure)
        return outlet_fluid

def get_flowrate(flowrate_bound, compressed_fluid, supply_load):
    condensed_fluid = AbstractState(compressed_fluid.backend_name(), compressed_fluid.name())
    condensed_fluid.update(CP.PQ_INPUTS, compressed_fluid.p(), 0)
    req_flowrate = supply_load / (compressed_fluid.hmass() - condensed_fluid.hmass())
    print_status(compressed_fluid)
    print_status(condensed_fluid)
    raise IOError
    # return req_flowrate, 'test'
    if req_flowrate < flowrate_bound[0]:
        print('minimum boundary condition for flowrate')
        condition = 'min'
        return flowrate_bound[0], condition
    elif req_flowrate > flowrate_bound[1]:
        print('maximum boundary condition for flowrate')
        condition = 'max'
        return flowrate_bound[1], condition
    else:
        condition = 'fit'
        return req_flowrate, condition

def get_initial_expanded_fluid(base_fluid, condensed_temperature, tgt_temperature):
    void_fluid = AbstractState(base_fluid.backend_name(), base_fluid.name())
    void_fluid.update(CP.QT_INPUTS, 0, condensed_temperature)

    void_fluid.update(CP.PT_INPUTS, base_fluid.p(), tgt_temperature)
    return void_fluid


class heat_exchanger():
    def __init__(self, config_dict):
        # type 1. effectiveness값을 바로 받기
        self.effectiveness = config_dict['effectiveness']

        # type 2. 유체와 U-area값 받기
        # self.transfer_coeff = config_dict['U']
        # self.area = config_dict['area']

    def calc_exchange(self, design_fluid, exchange_fluid, design_flowrate, exchange_flowrate):
        # design fluid의 온도를 고정 온도만큼 drop시키도록 한다.
        # hot/cold로 구분
        if design_fluid.T() > exchange_fluid.T():
            hot_fluid = design_fluid
            cold_fluid = exchange_fluid
            hot_flowrate = design_flowrate
            cold_flowrate = exchange_flowrate
        else:
            hot_fluid = exchange_fluid
            cold_fluid = design_fluid
            hot_flowrate = exchange_flowrate
            cold_flowrate = design_flowrate

        hot_capacity = hot_fluid.cpmass() * hot_flowrate        # J/kg.K * Kg/s = J/s.K
        cold_capacity = cold_fluid.cpmass() * cold_flowrate     # J/kg.K * Kg/s = J/s.K
        capacity_min = min(hot_capacity, cold_capacity)         # W/K
        # capacity_max = max(hot_capacity, cold_capacity)       # W/K

        # type 1. effectiveness값을 바로 받기
        effectiveness = self.effectiveness

        # type 2. 유체 열용량과 U-area값 받기
        # # Calculate NTU
        # NTU = self.transfer_coeff * self.area / capacity_min
        #
        # # Calculate the effectiveness (ε) for a counterflow heat exchanger
        # if capacity_min == cold_capacity:
        #     C_r = cold_capacity / hot_capacity
        # else:
        #     C_r = hot_capacity / cold_capacity
        #
        # if C_r == 1:
        #     effectiveness = NTU / (1 + NTU)
        # else:
        #     effectiveness = (1 - math.exp(-NTU * (1 - C_r))) / (1 - C_r * math.exp(-NTU * (1 - C_r)))

        Q_max = capacity_min * (hot_fluid.T() - cold_fluid.T())
        Q_act = effectiveness * Q_max

        # outlet_design_fluid = copy.deepcopy(design_fluid)
        # outlet_exchange_fluid = copy.deepcopy(exchange_fluid)

        outlet_design_fluid = AbstractState(design_fluid.backend_name(), design_fluid.name())
        outlet_exchange_fluid = AbstractState(exchange_fluid.backend_name(), exchange_fluid.name())

        if design_fluid.T() > exchange_fluid.T():
            outlet_design_fluid.update(CP.HmassP_INPUTS, design_fluid.hmass() - Q_act/design_flowrate, design_fluid.p())
            outlet_exchange_fluid.update(CP.HmassP_INPUTS, exchange_fluid.hmass() + Q_act/exchange_flowrate, exchange_fluid.p())
        else:
            outlet_design_fluid.update(CP.HmassP_INPUTS, design_fluid.hmass() + Q_act/design_flowrate, design_fluid.p())
            outlet_exchange_fluid.update(CP.HmassP_INPUTS, exchange_fluid.hmass() - Q_act/exchange_flowrate, exchange_fluid.p())
        return outlet_design_fluid, outlet_exchange_fluid

    def predict_ext_air(self, design_fluid, exchange_fluid, design_flowrate, exchange_flowrate):
        # design fluid의 온도를 고정 온도만큼 drop시키도록 한다.

        design_capacity = design_fluid.cpmass() * design_flowrate        # J/kg.K * Kg/s = J/s.K
        exchange_capacity = exchange_fluid.cpmass() * exchange_flowrate     # J/kg.K * Kg/s = J/s.K
        capacity_min = min(design_capacity, exchange_capacity)         # W/K

        # type 1. effectiveness값을 바로 받기
        effectiveness = self.effectiveness

        Q_max = capacity_min * abs(design_fluid.T() - design_fluid.T())
        Q_act = effectiveness * Q_max

        outlet_design_fluid = AbstractState(design_fluid.backend_name(), design_fluid.name())
        outlet_exchange_fluid = AbstractState(exchange_fluid.backend_name(), exchange_fluid.name())

        if design_fluid.T() > exchange_fluid.T():
            outlet_design_fluid.update(CP.HmassP_INPUTS, design_fluid.hmass() - Q_act/design_flowrate, design_fluid.p())
            outlet_exchange_fluid.update(CP.HmassP_INPUTS, exchange_fluid.hmass() + Q_act/exchange_flowrate, exchange_fluid.p())
        else:
            outlet_design_fluid.update(CP.HmassP_INPUTS, design_fluid.hmass() + Q_act/design_flowrate, design_fluid.p())
            outlet_exchange_fluid.update(CP.HmassP_INPUTS, exchange_fluid.hmass() - Q_act/exchange_flowrate, exchange_fluid.p())

        return outlet_design_fluid

def plot_fluid_point(fluid, label):
    plt.plot(fluid.Hmass(), fluid.T(), label=label)

base_fluid = AbstractState("HEOS", 'R32')
base_fluid.update(CP.QT_INPUTS, 1, 273+10)
hc_base_fluid = AbstractState("HEOS", 'R134A')
hc_base_fluid.update(CP.QT_INPUTS, 0, 273+50)
hc_base_fluid2 = AbstractState("HEOS", 'Water')
hc_base_fluid2.update(CP.QT_INPUTS, 1, 273+50)
ext_water = AbstractState("HEOS", "Water")
ext_water.update(CP.PT_INPUTS, 101325, 273+4)   # 시수압에 맞추어 조정 필요
tgt_water = AbstractState('HEOS', 'Water')
tgt_water.update(CP.PT_INPUTS, 101325, 273+80)   # 시수압에 맞추어 조정 필요
fc_water = AbstractState('HEOS', 'Water')
fc_water.update(CP.PT_INPUTS, 101325, 273+90)   # 시수압에 맞추어 조정 필요

dhw_flowrate = 0.25

flowrate = 1
flowrate_bound = (0, 10)
lc_high_temp = 273 + 60
hc_high_temp = 273 + 90
ext_air_temp = 273 + 5
dhw_load = 0.4*1000               # J/s
heating_load = -0.1*1000          # J/s
total_load = dhw_load + heating_load
# heat_load = 1000    # J (dhw + heating)
timestep = 1        # sec


# 0. fuel cell

makeup_fluid = AbstractState("HEOS", 'Water')
makeup_fluid.update(CP.QT_INPUTS, 1, 273+80)

# 1. LC

# 외기온도 -5도 값으로 열교환 결과 상태를 정의
base_fluid.update(CP.QT_INPUTS, 1, ext_air_temp-5)

# 컴프레서 먼저 계산
low_compressor = compressor(0.9)
low_compressed_fluid, low_comp_cond = low_compressor.calc_compress(base_fluid, flowrate, lc_high_temp, timestep)
print(base_fluid.phase())
print(low_compressed_fluid.phase())
print(low_compressed_fluid.T())
print(low_compressed_fluid.Q())
print(low_compressed_fluid.p())

# 소모부 열량 비교 (건도가 0이 될 때까지 전량 소모) 하여 유량을 결정
flowrate, flowrate_condition = get_flowrate(flowrate_bound, low_compressed_fluid, total_load)

# 외기온도 -10도와 유량으로 맞추기
ext_hx = heat_exchanger({'effectiveness':0.9})
ext_air = AbstractState("HEOS", 'Air')
ext_air.update(CP.PT_INPUTS, 101325, ext_air_temp)

# 온도값을 기준으로 초기 유체를 구함
exchanging_fluid = get_initial_expanded_fluid(base_fluid, lc_high_temp, ext_air_temp-10)

# 목표온도까지 도달하도록 열교환 공기유량을 계산
# ext_hx.calc_exchange(exchanging_fluid, ext_air, flowrate, )
print(ext_air.T())
print(exchanging_fluid.T())
print(flowrate)

def func(x):
    # x = [flowrate]
    return ext_hx.calc_exchange(exchanging_fluid, ext_air, flowrate, x)[1].T() + 5 - ext_air.T()

# res = least_squares(func, 77, bounds=[0, 100], gtol=1e-30)
res = minimize_scalar(func, bounds=[0.01, 100])
print(flowrate)
print(res['x'])
ext_air_flowrate = res['x']

# 구한 유량으로 실외기 열교환 수행
exchanged_fluid, exhaust_air = ext_hx.calc_exchange(exchanging_fluid, ext_air, flowrate, ext_air_flowrate)

# 압축기 계산
low_compressed_fluid, low_comp_cond = low_compressor.calc_compress(base_fluid, flowrate, lc_high_temp, timestep)

# 응축기 계산
low_condenser = condenser()
low_condensed_fluid, heat_ascend = low_condenser.calc_condenser_actual(low_compressed_fluid, flowrate)

# 팽창밸브 계산
expansion_valve = exp_valve()
expanded_fluid = expansion_valve.calc_expansion(low_condensed_fluid, exchanging_fluid.p())

# 2. HC

# # 동일한 최적화 방식으로 HC 유량을 계산
# def func_hc(x):
#     return ext_hx.calc_exchange(hc_base_fluid, low_compressed_fluid, x, flowrate)[0].T() + 5 - lc_high_temp
#
# high_res = minimize_scalar(func, bounds=[0.01, 100])
# high_flowrate = high_res['x']

# 단순계산으로 유량을 구함
heat_dhw = heat_ascend - heating_load
d_hmass = hc_base_fluid2.hmass() - hc_base_fluid.hmass()
high_flowrate = heat_dhw / d_hmass
# print(d_hmass)
# hc_flowrate = get_flowrate((0,10), hc_base_fluid2, heat_dhw)
print(high_flowrate)

# 구한 유량으로 LC-HC 열교환 수행
high_exchanged_fluid, low_dhw_extracted_fluid = ext_hx.calc_exchange(hc_base_fluid, low_compressed_fluid, high_flowrate, flowrate)

# HC 컴프레서
high_compressor = compressor(0.9)
high_compressed_fluid, high_comp_cond = high_compressor.calc_compress(high_exchanged_fluid, high_flowrate, hc_high_temp, timestep)


print(high_compressed_fluid.T())
print(ext_water.T())
print(high_flowrate)
print(dhw_flowrate)

# 시수와 열교환 수행
# 기존 효율기반 교환 모델로는 교환율이 너무 낮아, 강제로 변환
# 상부의 건도차에 대한 열량 확보
hmass_before = high_compressed_fluid.hmass()
high_compressed_fluid.update(CP.QT_INPUTS, 0, high_compressed_fluid.T())
hmass_after = high_compressed_fluid.hmass()

# 해당 건도차만큼의 열량을 시수에 전달
d_hmass = hmass_before - hmass_after            # j/kg
ext_water.update(CP.HmassP_INPUTS, ext_water.hmass() + d_hmass * high_flowrate / dhw_flowrate, ext_water.p())
print(ext_water.T())

# 시수에서 불충분만큼을 fuel cell에서 메우고, 해당 열량을 기록
additional_heat = (tgt_water.hmass() - ext_water.hmass()) * dhw_flowrate
fc_required_flowrate = additional_heat / (fc_water.hmass() - tgt_water.hmass())

print(additional_heat)
print(fc_required_flowrate)

# 전달된 뒤 팽창밸브로 하강
high_expansion_valve = exp_valve()
expanded_fluid = high_expansion_valve.calc_expansion(high_compressed_fluid, hc_base_fluid.p())


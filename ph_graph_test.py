'''
목적 : 엑셀 파일만 넣고 코드상에서 Run을 누르면 알아서 row별로 ph선도를 그려주기
6. PH선도의 시간에 따른 운전시 그림을 animation으로 그리면 좋을 것 같음.
1. R410a, R134a에 대한 h = f(P,T) 모델링 필요.
-> 범준은 P 및 T Working range 알려주기 바람. 추후 모델링은 한솔 실행

1 엑셀 불러오기
2 원하는 컬럼 찾기
3 단위 변환
4 R410a, R134a에 대한 h = f(P,T) 모델링
 >> 냉매에 대한 변경 함수 찾아보기
5 실내기, 실외기에 대한 엔탈피 값 구하기
6 몰리에르 선도 나타내기 ok
7 초당 몰리에르 선도 그리기
8 시간 범위에 대한 애니메이션
'''

#1 엑셀 불러오기
# import pandas as pd
# df = pd.read_excel('C:/Users/HYU_PC/PycharmProjects/heat_pump_analyze/HYN35_LOG (20231019 04_2 HOUR).xlsx')
# print(df.head)

'''import CoolProp
from CoolProp.Plots import PropertyPlot
ts_plot = PropertyPlot('R290', 'Ts', tp_limits='ORC')
ts_plot.calc_isolines(CoolProp.iQ, num=2)
ts_plot.show()'''

# import CoolProp
# from CoolProp.Plots import PropertyPlot
# plot = PropertyPlot('R410A', 'ph')
# plot.calc_isolines()
# plot.show()

from numpy import shape as size
from matplotlib import pyplot as plt
from CoolProp import CoolProp as CP
from CoolProp.Plots import PropertyPlot as CPP  # StateContainer
from CoolProp.Plots import SimpleCompressionCycle as CPPSCC

import matplotlib.transforms as mtransforms

TT = ([[55, 55, 55, 55, 55],
       [33, 34, 35, 36, 37]])

n = size(TT)[1]

for i in range(size(TT)[1]):
    pp = CPP("R32", "PH", unit_system="KSI")
    # pp.title("R32 log p-h Diagramm_"+str(i))
    pp.set_axis_limits([-40, 700, 0, 15000])
    pp.xlabel("h [kJ/kg]")
    pp.ylabel("P [kPa]")
    pp.calc_isolines(CP.iQ, num=11)
    cycle = CPPSCC("R32", "PH", unit_system="KSI")
    T0 = TT[1][i] + 273.15
    pp.state.update(CP.QT_INPUTS, 0.0, T0 - 0.02)
    p0 = pp.state.keyed_output(CP.iP)
    T2 = TT[0][i] + 273.15
    pp.state.update(CP.QT_INPUTS, 1.0, T2 + 0.02)
    p2 = pp.state.keyed_output(CP.iP)
    pp.calc_isolines(CP.iT, [T0, T2], num=2)
    pp.props[CP.iT]['color'] = 'green'
    pp.props[CP.iT]['lw'] = '0.5'
    pp.title("R32 log p-h Diagramm ")

    cycle.simple_solve(T0, p0, T2, p2, 0.7, SI=True)
    cycle.steps = 50
    sc = cycle.get_state_changes()
    pp.draw_process(sc, line_opts={'color': 'blue', 'lw': 1.5})
    pp.grid()
    # View the values and units used in the calculation
    print(cycle._cycle_states)
    # LABELS
    fig = pp.figure
    ax = pp.axis
    trans_offset = mtransforms.offset_copy(ax.transData, fig=fig,
                                           x=-0.12, y=0.10, units='inches')

    # label 1
    T0 = cycle._cycle_states[0, "T"]
    pa = 0.996424  # Pressure value selected to place the labels
    h = CP.PropsSI("H", "P", pa, "T", T0, "R32") / 1000
    lb1 = "{:.2f}K".format(T0)
    ax.text(h, pa, lb1, fontsize=10, rotation=90, color='r', transform=trans_offset, horizontalalignment='left',
            verticalalignment='baseline')
    # label 2
    T2 = cycle._cycle_states[2, "T"]
    pa = 0.996424  ##Pressure value selected to place the labels
    h = CP.PropsSI("H", "P", pa, "T", T2, "R32") / 1000
    lb2 = "{:.2f}K".format(T2)
    ax.text(h, pa, lb2, fontsize=10, rotation=90, color='r', transform=trans_offset, horizontalalignment='left',
            verticalalignment='baseline')

    # Pressures
    trans_offset = mtransforms.offset_copy(ax.transData, fig=fig,
                                           x=0, y=0.02, units='inches')
    # label p1
    p0 = cycle._cycle_states[0, "P"] / 1000
    h03 = (sum(cycle._cycle_states.H[[0, 3]]) / 2) / 1000
    lbp0 = "{:.2f}KPa".format(p0)
    ax.text(h03, p0, lbp0, fontsize=10, rotation=0, color='b', horizontalalignment='center', transform=trans_offset)
    # label p2
    p1 = cycle._cycle_states[1, "P"] / 1000
    h12 = (sum(cycle._cycle_states.H[[1, 2]]) / 2) / 1000
    lbp1 = "{:.2f}KPa".format(p1)
    ax.text(h12, p1, lbp1, fontsize=10, rotation=0, color='b', horizontalalignment='center', transform=trans_offset)

    plt.close(cycle.figure)
    pp.show()

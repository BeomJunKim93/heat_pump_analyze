from CoolProp import CoolProp as CP
# for humid air properties
from CoolProp.CoolProp import PropsSI # 공기를 제외한 유체
#문법 : 목표 파라미터, input 변수 1, 값1, input 변수 2, 값2, 유체
# rho_air = PropsSI('D','P',101325,'T',300, 'air')
# print(rho_air)

# rho_l = PropsSI('D','P',2180000,'Q',0,'R22')
# rho_v = PropsSI('D','P',2180000,'Q',1,'R22')
# print(rho_l)
# print(rho_v)

# h_l = PropsSI('H','P',2180000,'Q',0,'R410')
# h_v = PropsSI('H','P',2180000,'Q',1,'R410')
# print(h_l)
# print(h_v)

#R410A 물성치 계산
#R410A : 'HEOS::R32[0.697615]&R125[0.302385]'
import CoolProp.CoolProp as CP # Calling REFPROP
rho_R410A = CP.PropsSI('D','T',300,'P',101325,'HEOS::R32[0.697615]&R125[0.302385]')
print(rho_R410A)
h_R410A = CP.PropsSI('H','T',300,'P',101325,'HEOS::R32[0.697615]&R125[0.302385]')
h_R410A_2 = CP.PropsSI('H','T',300,'P',200000,'HEOS::R32[0.697615]&R125[0.302385]')
h_R410A_3 = CP.PropsSI('H','T',300,'Q',1,'HEOS::R32[0.697615]&R125[0.302385]')
h_R410A_4 = CP.PropsSI('H','T',330,'Q',1,'HEOS::R32[0.697615]&R125[0.302385]')
h_R410A_4_1 = CP.PropsSI('H','T',330,'Q',0,'HEOS::R32[0.697615]&R125[0.302385]')
h_R410A_5 = CP.PropsSI('H','T',338,'Q',1,'HEOS::R32[0.697615]&R125[0.302385]')
print(h_R410A)
print(h_R410A_2)
print(h_R410A_3)
print(h_R410A_4)
print(h_R410A_4_1)
print(h_R410A_5)




# from CoolProp.HumidAirProp import HAPropsSI # Humid air에 대한 물성치 (EES 함수와 제일 비슷)
# density_air = PropsSI('H','P',101325,'T',300,'air')
# print(density_air)
# 주석처리 방법 : 컨트롤 + /
"""
범위주석 : 큰 따옴표 3개
"""
'''
범위주석2 : 작은 따옴표 3개
'''

# 모듈 설치
# 1) 컨트롤 + 알트 + S : Settings 창 띄우기
# 2) Project : ~~~
# 3) Project interpreter
# 4) 창 좌상단의 + 눌러서 모듈 검색
# 5) 모듈 클릭 후 'install package' 눌러서 설치

# 깃허브 연동
# VCS -> Share project on Github

# Exercise 1 :
# Two thousand cfm of air at 100 F db and F wb are mixed with 1000 cfm of air at 60 F db and 50 F wb.
# The process is adiabatic, at a steady flow rate and at standard sea-level pressure.
# Find the condition of the mixed streams.

import numpy as np

# kilometers = float(input("Enter value in kilometers:"))
# conv_fac = 0.621371 # km -> mile
# miles = kilometers*conv_fac
# print('%0.2f kilometers is equal to %0.2f miles'%(kilometers,miles))

# # while문 기본
# while True:
#     opt1 = float(input("[1] SI -> US, [2] US -> SI"))
#     if opt1 ==1 or opt1 == 2:
#         print("%0.1f을(를) 입력하셨습니다"%(opt1))
#         break
#     else:
#         print("입력좀 잘 해 :(")
#         continue
#
# #
# if opt1 == 1:
#     while True:
#         opt2 = float(input("[1] Milemeter#n[2] Centimeter#n[3] Meter#n[4] Kilometer#n[5] Gram#n[6] Kilogram#n[7] Ton"))
#         if opt2 >= 1 and opt2 <=7:
#             print(opt2)
#             break
#         else:
#             print("입력좀 잘 해 :(")
#             continue
# elif opt1 == 2:
#     while True:
#         opt2 = float(input("[1] inch#n[2] Feet"))
#         if opt2 >= 1 and opt2 <=2:
#             print(opt2)
#             break
#         else:
#             print("입력좀 잘 해 :(")
#             continue

# 중간에 코드 진행 한번 끊고 디버깅 하는 용도
# print()
# raise IOError

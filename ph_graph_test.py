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
6 몰리에르 선도 나타내기
7 초당 몰리에르 선도 그리기
8 시간 범위에 대한 애니메이션
'''

a = 5

#1 엑셀 불러오기
import pandas as pd
df = pd.read_excel('C:/Users/HYU_PC/PycharmProjects/heat_pump_analyze/HYN35_LOG (20231019 04_2 HOUR).xlsx')
print(df.head)


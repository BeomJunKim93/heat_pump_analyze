import CoolProp.CoolProp as CP  # Calling REFPROP
import pandas as pd
import traceback
import numpy as np


class status:
    def __init__(self, t_value, h_value, p_value, s_value):  # 괄호 안의 파라미터가 입력되는 것을 표현
        self.t = t_value
        self.h = h_value
        self.p = p_value
        self.s = s_value

    def write(self, value, sort):
        if sort == 't':
            self.t = value
        elif sort == 'h':
            self.h = value
        elif sort == 'p':
            self.p = value
        elif sort == 's':
            self.s = value
        else:
            raise IOError('Improper variable type')

    def export(self):
        return [self.t, self.h, self.p, self.s]


class cycle:
    def __init__(self, coolant):
        self.comp_i = CP.AbstractState('HEOS', coolant)
        self.comp_i.specify_phase(CP.iphase_gas)
        self.comp_o = CP.AbstractState('HEOS', coolant)
        self.comp_o.specify_phase(CP.iphase_gas)
        self.valve_i = CP.AbstractState('HEOS', coolant)
        self.valve_o = CP.AbstractState('HEOS', coolant)
        self.valve_o.specify_phase(CP.iphase_liquid)

    def update(self, update_dict):
        self.comp_i.update(CP.PT_INPUTS, update_dict['comp_i'].p, update_dict['comp_i'].t)
        self.comp_o.update(CP.PT_INPUTS, update_dict['comp_o'].p, update_dict['comp_o'].t)
        self.valve_i.update(CP.PT_INPUTS, update_dict['valve_i'].p, update_dict['valve_i'].t)
        self.valve_o.update(CP.HmassP_INPUTS, self.valve_i.hmass(), update_dict['valve_o'].p)

        update_dict['comp_i'].t = self.comp_i.T()
        update_dict['comp_i'].h = self.comp_i.hmass()
        update_dict['comp_i'].p = self.comp_i.p()
        update_dict['comp_i'].s = self.comp_i.smass()

        update_dict['comp_o'].t = self.comp_o.T()
        update_dict['comp_o'].h = self.comp_o.hmass()
        update_dict['comp_o'].p = self.comp_o.p()
        update_dict['comp_o'].s = self.comp_o.smass()

        update_dict['valve_i'].t = self.valve_i.T()
        update_dict['valve_i'].h = self.valve_i.hmass()
        update_dict['valve_i'].p = self.valve_i.p()
        update_dict['valve_i'].s = self.valve_i.smass()

        update_dict['valve_o'].t = self.valve_o.T()
        update_dict['valve_o'].h = self.valve_o.hmass()
        update_dict['valve_o'].p = self.valve_o.p()
        update_dict['valve_o'].s = self.valve_o.smass()
        return update_dict

    def export(self):
        return [self.comp_i, self.comp_o, self.valve_i, self.valve_o]


def read_datafile(filedir):
    col_arr = ['hc-comp_o-p (Pa)', 'hc-comp_i-p (Pa)', 'hc-comp_o-t (ºC)', 'hc-comp_i-t (ºC)', 'hc-valve_i-t (ºC)', 'hc-X1-t (ºC)', 'hc-X2-t (ºC)',
               'hc-valve_o-t (ºC)', 'hc-power-w (W) ', 'lc-comp_o-p (Pa)', 'lc-comp_i-p (Pa)', 'lc-comp_o-t (ºC)', 'lc-comp_i-t (ºC)', 'lc-valve_i-t (ºC)',
               'lc-X1-t (ºC)', 'lc-X2-t (ºC)', 'lc-valve_o-t (ºC)', 'lc-power-w (W)']
    data = pd.read_csv(filedir, encoding='utf-8 sig', names=col_arr)
    return data


def process_datafile(data):
    for colname in data.columns.values.tolist():
        if colname[-2:] == '-p':
            data[colname] = data[colname] * 1000
        elif colname[-2:] == '-t':
            data[colname] = data[colname] + 273
        elif colname[-2:] == '-w':
            data[colname] = data[colname] * 1000
    return data


# 0. 입력데이터 읽어와서 줄별로 Run
data = read_datafile('./2023-10-12-20.csv')
data = process_datafile(data)

res_dict = {'COP': [], 'status': []}
for cycle_name in ['hc', 'lc']:
    for component in ['comp_i', 'comp_o', 'valve_i', 'valve_o']:
        for variable in ['t', 'h', 'p', 's']:
            res_dict['calc-' + cycle_name + '-' + component + '-' + variable] = []

for iter, row in data.iterrows():
    try:
        # SP. 필수 데이터 값이 0일때 에러를 출력하고 스킵
        if row['lc-comp_o-p'] == 0 or row['lc-comp_o-p'] == np.nan:
            raise IOError('Essential input lc-comp-o-p is zero or nan')
        elif row['hc-comp_o-p'] == 0 or row['hc-comp_o-p'] == np.nan:
            raise IOError('Essential input hc-comp-o-p is zero or nan')

        # 1. lc/hc 클래스 객체 선언
        input_lc = {
            'comp_i': status(0, 0, 0, 0),
            'comp_o': status(0, 0, 0, 0),
            'valve_i': status(0, 0, 0, 0),
            'valve_o': status(0, 0, 0, 0)
        }
        input_hc = {
            'comp_i': status(0, 0, 0, 0),
            'comp_o': status(0, 0, 0, 0),
            'valve_i': status(0, 0, 0, 0),
            'valve_o': status(0, 0, 0, 0)
        }

        # 2. 입력 줄에서 해당되는 부분 매칭
        for colname in row.index:
            name_arr = colname.split('-')
            if name_arr[0] == 'lc':
                if 'X' not in name_arr[1] and 'power' not in name_arr[1]:
                    input_lc[name_arr[1]].write(row[colname], name_arr[2])
            elif name_arr[0] == 'hc':
                if 'X' not in name_arr[1] and 'power' not in name_arr[1]:
                    input_hc[name_arr[1]].write(row[colname], name_arr[2])
            else:
                raise IOError('Improper cycle name')
        power_hc = row['hc-power-w']
        power_lc = row['lc-power-w']

        # 3. cycle class definition
        cycle_lc = cycle('R410A')
        cycle_hc = cycle('R134a')

        # 4. comp_o.p -> valve_i.p
        input_hc['valve_i'].p = input_hc['comp_o'].p
        input_lc['valve_i'].p = input_lc['comp_o'].p

        # 5. comp_i.p -> valve_o.p
        input_hc['valve_o'].p = CP.PropsSI('P', 'T', input_hc['valve_o'].t, 'Q', 0, 'R134a')
        input_lc['valve_o'].p = CP.PropsSI('P', 'T', input_lc['valve_o'].t, 'Q', 0, 'R410A')

        # 6. bottom pressure line adjustment
        input_hc['comp_i'].p = input_hc['valve_o'].p
        input_lc['comp_i'].p = input_lc['valve_o'].p

        # SP. 유지보수용 print 단 (주석 처리)
        '''for keys in input_lc.keys():
            print(input_lc[keys].export())
        for keys in input_hc.keys():
            print(input_hc[keys].export())
        print('========================================================')'''

        # 7. point set
        output_lc = cycle_lc.update(input_lc)
        output_hc = cycle_hc.update(input_hc)

        # 8. COP calculation
        output_COP = (power_hc * (output_hc['comp_o'].h - output_hc['valve_i'].h) / (
                    output_hc['comp_o'].h - output_hc['comp_i'].h)) / (power_hc + power_lc)

        # SP. 유지보수용 print 단 (주석 처리)
        '''for keys in output_lc.keys():
            print(output_lc[keys].export())
        for keys in output_hc.keys():
            print(output_hc[keys].export())
        print('========================================================')
        print(output_COP)
        print('========================================================')'''

        # 9. save results
        for component in ['comp_i', 'comp_o', 'valve_i', 'valve_o']:
            # high-cycle save
            res_dict['calc-hc-' + component + '-t'].append(output_hc[component].t)
            res_dict['calc-hc-' + component + '-h'].append(output_hc[component].h)
            res_dict['calc-hc-' + component + '-p'].append(output_hc[component].p)
            res_dict['calc-hc-' + component + '-s'].append(output_hc[component].s)
            # low-cycle save
            res_dict['calc-lc-' + component + '-t'].append(output_lc[component].t)
            res_dict['calc-lc-' + component + '-h'].append(output_lc[component].h)
            res_dict['calc-lc-' + component + '-p'].append(output_lc[component].p)
            res_dict['calc-lc-' + component + '-s'].append(output_lc[component].s)
        res_dict['COP'].append(output_COP)
        res_dict['status'].append('SUCCESS')

    except:
        error = traceback.format_exc()
        for component in ['comp_i', 'comp_o', 'valve_i', 'valve_o']:
            # high-cycle save
            res_dict['calc-hc-' + component + '-t'].append('ERROR')
            res_dict['calc-hc-' + component + '-h'].append('ERROR')
            res_dict['calc-hc-' + component + '-p'].append('ERROR')
            res_dict['calc-hc-' + component + '-s'].append('ERROR')
            # low-cycle save
            res_dict['calc-lc-' + component + '-t'].append('ERROR')
            res_dict['calc-lc-' + component + '-h'].append('ERROR')
            res_dict['calc-lc-' + component + '-p'].append('ERROR')
            res_dict['calc-lc-' + component + '-s'].append('ERROR')
        res_dict['COP'].append('ERROR')
        if 'Two-phase inputs not supported for pseudo-pure for now' in error:
            print('Two-phase error occurred')
            res_dict['status'].append('Two-phase error')
        elif 'Essential input' in error:
            print('User-defined error occurred')
            res_dict['status'].append('Essential input blank error')
        else:
            raise IOError('Unobserved ERROR case')

# 10. Convert result dictionary into the dataframe
result_data = pd.DataFrame(res_dict)

# 11. Merge into the original dataframe
data = data.join(result_data, how='outer')

# 12. save the result
data.to_csv('./processed_result_ver3.csv', encoding='utf-8 sig')
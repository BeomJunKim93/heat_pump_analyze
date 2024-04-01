import pandas as pd
def preprocess_data(data):
    col_list = data.columns.values.tolist()
    # 타입변환 이전에 컬럼별로 문제의 소지가 있는 데이터들을 싹 정리
    # 데이터 컬럼 내부에서 이상값들을 처리
    repl_dict = {
        'NaN': ''
    }

    for colname in col_list:
        for repl_value in repl_dict.keys():
            data[colname] = data[colname].astype(str)
            data[colname] = data[colname].str.replace(repl_value, repl_dict[repl_value])
        data[colname] = data[colname].str.replace('\s+', '', regex=True)

    data = data.replace('', pd.NA)
    for colname in col_list:
        data[colname] = data[colname].astype(float)
    return data
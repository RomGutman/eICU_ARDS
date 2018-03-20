import pandas as pd
import numpy as np
import pickle
import copy
from ARDS_prone_change import Model


def calculate_unified_res(model):
    """

    :param model:
    :return:
    """
    print("Start Calculating")
    unified_res_list = []   # type: list[pd.DataFrame[int,float]]
    for patient_id, patient_data in model.patients_data.items():
        print("Start Calculating for patient {}".format(patient_id))
        if patient_data.empty:
            print("Patient {}, does not have records!".format(patient_id))
            continue
        patient_df = patient_data[['PF ratio', 'lab_time', 'toffset']].drop_duplicates()

        patient_df = patient_df[np.abs(patient_df['lab_time'] - patient_df['toffset']) < model.default_tolerance]

        patient_df['offset'] = (np.abs(patient_df['toffset'] - patient_df['lab_time'])).astype(int)
        patient_df.reset_index(inplace=True, drop=True)

        dict_before = calculate_before(model.before_tolerance, patient_df)
        fix_offset(dict_before)

        dict_after = calculate_after(patient_df)
        fix_offset(dict_after)

        set_keys = calculate_keys(dict_after, dict_before)

        uni_df = calculate_unified_df(dict_after, dict_before, set_keys)

        unified_res_list.append(uni_df.groupby('lab_time').agg('mean'))
    print("Finished Calculating")
    pickle.dump(unified_res_list, open("unified_model.pkl", "wb"))


def calculate_unified_df(dict_after, dict_before, set_keys):
    """

    :param dict_after:
    :param dict_before:
    :param set_keys:
    :return:
    """
    temp_dict = {}  # type: dict(int, pd.DataFrame)
    for key in set_keys:
        temp1 = dict_before.get(key)
        temp2 = dict_after.get(key)
        if temp1 is None:
            temp_dict[key] = temp2.copy()
            continue
        elif temp2 is None:
            temp_dict[key] = temp1.copy()
            continue
        else:
            concatenated = [temp1, temp2]
            temp_dict[key] = pd.concat(concatenated, ignore_index=True)  # type: pd.DataFrame
        temp_dict[key].set_index('id')
        temp_dict[key].sort_values('lab_time', inplace=True)
    uni_df = pd.concat(list(temp_dict.values())).reset_index(drop=True)[["PF ratio", "lab_time"]]
    return uni_df


def calculate_keys(dict_after, dict_before):
    """

    :param dict_after:
    :param dict_before:
    :return:
    """
    set_keys = set(dict_before.keys()).union(dict_after.keys())
    temp_set = pd.DataFrame(list(set_keys), columns=['set'])
    temp_set.sort_values(by='set', inplace=True)
    temp_set['diff'] = temp_set.diff()
    temp_set = temp_set[(temp_set['diff'] > 2 * 60) | (temp_set['diff'].isnull())].reset_index(drop=True)
    set_keys = set(temp_set.set.values)
    return set_keys


def fix_offset(df_dict):
    """

    :param df_dict:
    :return:
    """
    for d in df_dict.values():
        d['lab_time'] = d.loc[:, ('lab_time')] - d.loc[:, ('toffset')]
        d['id'] = d['toffset'].copy()
        d['toffset'] = 0
        d.set_index('id')


def calculate_after(patient_df):
    """

    :param patient_df:
    :return:
    """
    df_after = patient_df[patient_df['lab_time'] > patient_df['toffset']].copy()
    df_after.sort_values(['toffset', 'lab_time'], inplace=True)
    gb_after = df_after.groupby('toffset')
    dict_after = {x: gb_after.get_group(x) for x in gb_after.groups}
    return dict_after


def calculate_before(before_tolerance, patient_df):
    """

    :param before_tolerance:
    :param patient_df:
    :return:
    """
    df_before = patient_df[patient_df['lab_time'] < patient_df['toffset']].copy()
    df_before = df_before[df_before['offset'] < before_tolerance]
    df_before.reset_index(inplace=True, drop=True)
    df_before.sort_values(['toffset', 'lab_time'], inplace=True)
    gb_before = df_before.groupby('toffset')
    dict_before = {x: gb_before.get_group(x) for x in gb_before.groups}
    return dict_before


if __name__ == '__main__':
    temp_model = Model()
    temp_model.time_frame = 24
    temp_model.model_type = "total"
    temp_model.create_model()
    print(temp_model.outliers)
    pickle.dump(temp_model.outliers, open("outliers.pkl", 'wb'))
    calculate_unified_res(temp_model)

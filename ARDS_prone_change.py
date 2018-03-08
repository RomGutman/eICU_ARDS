import numpy as np
from load_data import LoadData
import pandas as pd
from collections import OrderedDict, defaultdict
from sql import prone_change_queries
from parameters_estimate import ParametersEstimate
import pickle


class Model:
    """
    This class is modeling the ARDS Prone change model,
    using SCCS (Self Control Case Series), under Non-Homogeneous Poisson process assumption.
    """

    def __init__(self, model_type="positive"):
        self._TIME_FRAME = 12 * 60  # the time frame in the model from hours to minutes
        # The ratio of the ARDS, in format of "name" -> [High, Low)
        self._adverse_ratio = {
            'Mild': (300, 200),
            'Moderate': (200, 100),
            'Severe': (100, 0)
        }  # type: dict(str, tuple(int, int))
        self._model_type = model_type
        self.patients_under_treat = defaultdict(np.ndarray)  # type: defaultdict(int,np.ndarray[int])
        self.patients_adversary_events = defaultdict(np.ndarray)  # type: defaultdict(int, np.ndarray[int])
        self.load_data = LoadData()
        self.patients_under_treat_matrix = None  # type: np.ndarray
        self.patients_adversary_events_matrix = None  # type: np.ndarray
        self.patients_data = defaultdict(pd.DataFrame)  # type: defaultdict(int, pd.DataFrame)

    @property
    def time_frame(self):
        return self._TIME_FRAME/60

    @time_frame.setter
    def time_frame(self, value):
        self._TIME_FRAME = value*60

    @property
    def model_type(self):
        return self._model_type

    @model_type.setter
    def model_type(self, value):
        if value not in ["positive","negative"]:
            raise ValueError("model type `{}` isn't valid. use \"positive\" or \"negative\" instead. ".format(value))
        self._model_type = value

    def create_matrix(self):
        """
        creates the :ref:`patients_under_treat_matrix` matrix in :class:`Model` class
        and the :ref:`patients_adversary_events_matrix` matrix in :class:`Model` class

        :return:
        :rtype: None
        """
        # max_len = np.max([len(val) for val in self.patients_under_treat.values()])
        # e = np.asarray([np.pad(val,
        #  (0, max_len - len(val)), mode='constant', constant_values=0) for val in input_dict.values()])
        ordered_dict = OrderedDict(sorted(self.patients_under_treat.items(), key=lambda x: x[0]))
        self.patients_under_treat_matrix = pd.DataFrame(list(ordered_dict.values())).fillna(0).values
        ordered_dict = OrderedDict(sorted(self.patients_adversary_events.items(), key=lambda x: x[0]))
        self.patients_adversary_events_matrix = pd.DataFrame(list(ordered_dict.values())).fillna(0).values

    def query_patient_data(self, patient_id):
        """

        :param int patient_id:
        :return:
        """
        param = {'phsid': patient_id}
        tr = self.load_data.query_db(prone_change_queries.query, params=param)
        tr2 = self.load_data.query_db(prone_change_queries.patients_query, params=param)
        self.patients_data[patient_id] = tr.merge(tr2, how='left', on=['phsid']).copy()

    def calculate_patient_under_treat(self, max_time, min_time, labels, patient_id):
        """

        :param max_time:
        :param min_time:
        :param labels:
        :param patient_id:
        :return:
        :return:
        """
        df_patient = self.patients_data.get(patient_id)
        df_time_frames = df_patient[['PF ratio', 'lab_time', 'toffset']].drop_duplicates().reset_index(drop=True)

        df_time_frames['strata'] = pd.cut(df_time_frames.toffset,
                                          range(min_time, max_time + self._TIME_FRAME, self._TIME_FRAME),
                                          right=False, labels=labels)

        df_time_frames['x'] = df_time_frames.groupby('strata')['strata'].transform('count')

        df_temp_x = df_time_frames[['strata', 'x']].copy()

        df_x_patient = pd.DataFrame(data={'strata': labels})
        df_x_patient = df_x_patient.merge(df_temp_x, on='strata', how='left')
        df_x_patient['x'] = np.where(df_x_patient['x'] > 0, 1, 0)
        df_x_patient = df_x_patient.drop_duplicates().reset_index(drop=True)

        self.patients_under_treat[patient_id] = df_x_patient.x.values
        return

    def calculate_patient_adv_events(self, max_time, min_time, labels, patient_id, adv_type=1):
        """

        :param max_time:
        :param min_time:
        :param labels:
        :param patient_id:
        :param adv_type:
        :return:
        """
        df_patient = self.patients_data.get(patient_id)
        df_pf_diff = df_patient[["PF ratio", "lab_time"]].copy().drop_duplicates()

        df_pf_diff['strata'] = pd.cut(df_pf_diff.lab_time,
                                      range(min_time, max_time + self._TIME_FRAME, self._TIME_FRAME),
                                      right=False, labels=labels)   # type: pd.DataFrame

        tolerance = 0

        df_pf_diff.sort_values("lab_time", inplace=True)
        df_pf_diff["dif"] = df_pf_diff["PF ratio"].diff()
        df_pf_diff.reset_index(inplace=True, drop=True)
        df_pf_diff['result'] = np.sign(df_pf_diff['dif'][np.abs(df_pf_diff['dif']) >= tolerance])

        df_pf_diff.sort_values("strata", inplace=True)

        df_y_patient = pd.DataFrame(data={'strata': labels})
        adv_mask = None
        if self._model_type == "positive":
            adv_mask = "df_pf_diff[\"result\"] > 0"
        elif self._model_type == "negative":
            adv_mask = "df_pf_diff[\"result\"] <= 0"
        df_temp_y = pd.DataFrame(df_pf_diff['strata'][eval(adv_mask)].copy().value_counts().reset_index())
        df_temp_y.columns = ['strata', 'y']

        df_y_patient = df_y_patient.merge(df_temp_y, on='strata', how='inner', copy=True)

        self.patients_adversary_events[patient_id] = df_y_patient.y.values

    def calculate_patient_vectors(self, patient_id):
        """

        :return:
        """
        self.query_patient_data(patient_id)
        df_patient = self.patients_data.get(patient_id)     # type: pd.DataFrame
        if df_patient.empty:
            print("Patient {}, does not have records!".format(patient_id))
            return
        max_time = np.max([df_patient['lab_time'].max(), df_patient['toffset'].max()])
        min_time = np.min([df_patient['lab_time'].min(), df_patient['toffset'].min()])

        np.ceil((max_time - min_time + 1) / self._TIME_FRAME)

        labels = ["{0} - {1}".format(i, (i + self._TIME_FRAME)) for i in range(min_time, max_time, self._TIME_FRAME)]

        # fix the last time frame
        temp = labels[-1].split(" ")
        temp[-1] = str(max_time)
        labels[-1] = " ".join(temp)

        self.calculate_patient_under_treat(max_time, min_time, labels, patient_id)
        self.calculate_patient_adv_events(max_time, min_time, labels, patient_id)

    def create_model(self):
        """
        this method creates the model, by calculating all the patients vectors and than convert it all to a matrix

        :return:
        """
        df_patient = self.load_data.query_db(prone_change_queries.all_patiens_query, params=None)
        patient_list = df_patient.values  # type: np.ndarray[int]
        for patient in patient_list:
            print("Start calculating values for patient:{}".format(patient.item()))
            self.calculate_patient_vectors(patient.item())
        print("Finished Calculating values")
        self.create_matrix()


def main():
    model = Model()
    # model.calculate_patient_vectors(patient_id=418469)
    # model.create_matrix()
    print("Start estimating for 12H time frame")
    estimate_model(model)
    model.model_type = "negative"
    estimate_model(model)
    print("Start estimating for 24H time frame")
    model.time_frame = 24
    model.model_type = "positive"
    estimate_model(model)
    model.model_type = "negative"
    estimate_model(model)
    keys = np.array(list(model.patients_under_treat.keys()))
    pickle.dump(keys, open('keys.pkl', 'wb'))


def estimate_model(model):
    model.create_model()
    parameters_estimate = ParametersEstimate(model)
    res = parameters_estimate.estimate()
    print(res.x)


if __name__ == '__main__':
    main()

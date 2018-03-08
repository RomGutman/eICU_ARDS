import pickle
from scipy.optimize import minimize
import numpy as np

# todo: check if the padding makes a different


class ParametersEstimate:
    """
    this class using BGFS to calculate gradient assent of the MLE, in order to calculate the
     intensity (beta) and baseline of the patients (phi) in the SCCS model
    """
    def __init__(self, model):
        """

        :param Model model: the ARDS SCCS prone change model
        """
        self.beta = 0
        self.model = model
        self.num_of_patients = len(model.patients_adversary_events.keys())
        self.phi = np.zeros(self.num_of_patients)
        self.param_vec = np.append(self.phi, self.beta)
        self.y = model.patients_adversary_events_matrix
        self.y_sum = self.y.sum(axis=1)
        self.x = model.patients_under_treat_matrix
        self.x_y = np.trace(self.y.transpose()@self.x)  # Frobenius inner product

    def obj_func(self, param_vec):
        """
        this method calculate the objective function value

        .. math::
         l(\Phi,\\beta) := \sum_{i=1}^{n} \sum_{d=1}^{\\tau_{i}} [e^{\phi_{i}+\\beta x_{id}} -
          y_{id}(\phi_{i}+\\beta x_{id})]

        :param np.ndarray param_vec: the vector of the function parameters
        :return: the objective function value
        """
        phi = param_vec[:-1]
        beta = param_vec[-1:].item()

        e_phi = np.exp(phi)
        inner_exp = np.exp(self.x * beta).sum(axis=1)
        exp_part = (inner_exp * e_phi).sum()

        linear_part_a = self.y.sum(axis=1).dot(phi)
        linear_part_b = self.x_y*beta
        linear_part = linear_part_a + linear_part_b

        return exp_part - linear_part

    def gradient(self, param_vec):
        """
        this method calculate the gradient of the function

        we have two gradients:

        .. math::

            \\frac{ \\partial{l}}{\\partial{\phi_{i}}} &=& \sum_{d=1}^{\\tau_{i}}
            [e^{\phi_{i}+ \\beta x_{id}} - y_{id}]

            \\frac{ \\partial{l}}{\\partial{\\beta}} = \sum_{i=1}^{n} \sum_{d=1}^{\\tau_{i}}
            [x_{id}*e^{\phi_{i}+\\beta x_{id}} - y_{id}*x_{id}]


        :param np.ndarray param_vec: the vector of the function parameters
        :return: gradient of the function
        """
        phi = param_vec[:-1]
        beta = param_vec[-1:].item()

        e_phi = np.exp(phi)

        # phi gradient
        phi_inner_exp = np.exp(self.x * beta).sum(axis=1)
        exp_part = phi_inner_exp * e_phi

        phi_grad = exp_part - self.y_sum

        # beta gradient
        beta_inner_exp = (np.exp(self.x*beta)*self.x).sum(axis=1)
        exp_part = (beta_inner_exp * e_phi).sum()

        beta_grad = exp_part - self.x_y

        res = np.append(phi_grad, beta_grad)
        return res

    def estimate(self):
        """
        this method is using BFGS in order to estimte the phi and the Beta parameter

        :return: result out of ``OptimizeResult``
        :rtype: scipy.optimize.OptimizeResult
        """
        result = minimize(method='BFGS', fun=self.obj_func, x0=self.param_vec, jac=self.gradient,
                          options={'disp': True})
        self.phi = result.x[:-1]
        self.beta = result.x[-1:].item()
        pickle.dump(result, open('optimize_res_{}_{}.pkl'.format(self.model.model_type,self.model.time_frame), 'wb'))
        print("The beta result is : {}".format(self.beta))
        return result

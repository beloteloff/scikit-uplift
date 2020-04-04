from math import ceil
import numpy as np
from sklearn.utils.extmath import stable_cumsum
from sklearn.utils.validation import check_consistent_length
from sklearn.metrics import auc


def uplift_curve(y_true, uplift, treatment):
    """Compute Uplift curve

    This is a general function, given points on a curve.  For computing the
    area under the Uplift Curve, see :func:`auuc`.

    Args:
        y_true (1d array-like): Ground truth (correct) labels.
        uplift (1d array-like): Predicted uplift, as returned by a model.
        treatment (1d array-like): Treatment labels.

    Returns:
        array (shape = [>2]), array (shape = [>2]): Points on a curve.

    See also:
        :func:`auuc`: Compute the area under the Uplift curve.

        :func:`plot_uplift_qini_curves`: Plot Uplift and Qini curves.
    """

    # ToDo: Добавить проверки на наличие обоих классов в столбце treatment
    # ToDo: Добавить проверку на наличие обоих классов в  y_true для каждого уникального значения из столбца treatment

    y_true, uplift, treatment = np.array(y_true), np.array(uplift), np.array(treatment)
    desc_score_indices = np.argsort(uplift, kind="mergesort")[::-1]
    y_true, uplift, treatment = y_true[desc_score_indices], uplift[desc_score_indices], treatment[desc_score_indices]

    y_true_ctrl, y_true_trmnt = y_true.copy(), y_true.copy()

    y_true_ctrl[treatment == 1] = 0
    y_true_trmnt[treatment == 0] = 0

    distinct_value_indices = np.where(np.diff(uplift))[0]
    threshold_indices = np.r_[distinct_value_indices, uplift.size - 1]

    num_trmnt = stable_cumsum(treatment)[threshold_indices]
    y_trmnt = stable_cumsum(y_true_trmnt)[threshold_indices]

    num_all = threshold_indices + 1

    num_ctrl = num_all - num_trmnt
    y_ctrl = stable_cumsum(y_true_ctrl)[threshold_indices]

    curve_values = (np.divide(y_trmnt, num_trmnt, out=np.zeros_like(y_trmnt), where=num_trmnt != 0) -\
                    np.divide(y_ctrl, num_ctrl, out=np.zeros_like(y_ctrl), where=num_ctrl != 0)) * num_all

    if num_all.size == 0 or curve_values[0] != 0 or num_all[0] != 0:
        # Add an extra threshold position if necessary
        # to make sure that the curve starts at (0, 0)
        num_all = np.r_[0, num_all]
        curve_values = np.r_[0, curve_values]

    return num_all, curve_values


def qini_curve(y_true, uplift, treatment):
    """Compute Qini curve.

    This is a general function, given points on a curve. For computing the
    area under the Qini Curve, see :func:`auqc`.

    Args:
        y_true (1d array-like): Ground truth (correct) labels.
        uplift (1d array-like): Predicted uplift, as returned by a model.
        treatment (1d array-like): Treatment labels.

    Returns:
        array (shape = [>2]), array (shape = [>2]): Points on a curve.

    See also:
        :func:`auqc`: Compute the area under the Qini curve.

        :func:`plot_uplift_qini_curves`: Plot Uplift and Qini curves.
    """
    # ToDo: Добавить проверки на наличие обоих классов в столбце treatment
    # ToDo: Добавить проверку на наличие обоих классов в столбце y_true для каждого уникального значения из столбца treatment

    y_true, uplift, treatment = np.array(y_true), np.array(uplift), np.array(treatment)

    desc_score_indices = np.argsort(uplift, kind="mergesort")[::-1]

    y_true = y_true[desc_score_indices]
    treatment = treatment[desc_score_indices]
    uplift = uplift[desc_score_indices]

    y_true_ctrl, y_true_trmnt = y_true.copy(), y_true.copy()

    y_true_ctrl[treatment == 1] = 0
    y_true_trmnt[treatment == 0] = 0

    distinct_value_indices = np.where(np.diff(uplift))[0]
    threshold_indices = np.r_[distinct_value_indices, uplift.size - 1]

    num_trmnt = stable_cumsum(treatment)[threshold_indices]
    y_trmnt = stable_cumsum(y_true_trmnt)[threshold_indices]

    num_all = threshold_indices + 1

    num_ctrl = num_all - num_trmnt
    y_ctrl = stable_cumsum(y_true_ctrl)[threshold_indices]

    curve_values = y_trmnt - y_ctrl * np.divide(num_trmnt, num_ctrl, out=np.zeros_like(num_trmnt), where=num_ctrl != 0)
    if num_all.size == 0 or curve_values[0] != 0 or num_all[0] != 0:
        # Add an extra threshold position if necessary
        # to make sure that the curve starts at (0, 0)
        num_all = np.r_[0, num_all]
        curve_values = np.r_[0, curve_values]

    return num_all, curve_values


def auuc(y_true, uplift, treatment):
    """
    Compute Area Under the Uplift Curve from prediction scores.

    Args:
        y_true (1d array-like): Ground truth (correct) labels.
        uplift (1d array-like): Predicted uplift, as returned by a model.
        treatment (1d array-like): Treatment labels.

    Returns:
        float: Area Under the Uplift Curve.
    """
    # ToDO: Добавить бейзлайн
    return auc(*uplift_curve(y_true, uplift, treatment))


def auqc(y_true, uplift, treatment):
    # ToDo: добавить описание функции
    """Compute Area Under the Qini Curve (aka Qini coefficient) from prediction scores.

    Args:
        y_true (1d array-like): Ground truth (correct) labels.
        uplift (1d array-like): Predicted uplift, as returned by a model.
        treatment (1d array-like): Treatment labels.

    Returns:
        float: Area Under the Qini Curve.
    """
    # ToDO: Добавить бейзлайн
    return auc(*qini_curve(y_true, uplift, treatment))


def uplift_at_k(y_true, uplift, treatment, k=0.3, average='first'):
    """Calculate the uplift score at the first k observations (ratio or absolute value) of the total sample.

    Args:
        y_true (1d array-like): Ground truth (correct) labels.
        uplift (1d array-like): Predicted uplift, as returned by a model.
        treatment (1d array-like): Treatment labels.
        k (float or int): If float, should be between 0.0 and 1.0 and represent the proportion of the dataset
            to include in the computation of uplift. If int, represents the absolute number of samples.
        average (string, ['first', 'group']): Determines the calculating strategy. Defaults to 'first'.

            * ``'first'``:
                The first step is taking the first k observations overall groups (control and treatment)
                to take the first K observations and then calculate the uplift score among them.

            * ``'group'``:
                The first step is taking the first k observations in the control group and
                the first k observations in treatment. And then calculate the uplift score among them.
    Returns:
        float: Uplift score at first k observations of the total sample.

    """
    # ToDo: checker that treatment is binary and all groups is not empty
    check_consistent_length(y_true, uplift, treatment)

    average_methods = ['first', 'group']
    if average not in average_methods:
        raise ValueError(f'Uplift score supports only calculating methods in {average_methods},'
                         f' got {average}.'
                         )

    n_samples = len(y_true)
    order = np.argsort(uplift)[::-1]
    _, treatment_counts = np.unique(treatment, return_counts=True)
    n_samples_ctrl = treatment_counts[0]
    n_samples_trmnt = treatment_counts[1]

    k_type = np.asarray(k).dtype.kind

    if (k_type == 'i' and (k >= n_samples or k <= 0)
       or k_type == 'f' and (k <= 0 or k >= 1)):
        raise ValueError(f'k={k} should be either positive and smaller'
                         ' than the number of samples {n_samples} or a float in the '
                         '(0, 1) range')

    if k_type not in ('i', 'f'):
        raise ValueError(f'Invalid value for k: {k_type}')

    if average == 'first':
        if k_type == 'f':
            n_size = ceil(n_samples * k)
        else:
            n_size = k

        # ToDo: _checker_ there are obervations among two groups among first k
        score_ctrl = y_true[order][:n_size][treatment[order][:n_size] == 0].mean()
        score_trmnt = y_true[order][:n_size][treatment[order][:n_size] == 1].mean()

    else:  # average == 'group':
        if k_type == 'f':
            n_ctrl = ceil((treatment == 0).sum() * k)
            n_trmnt = ceil((treatment == 1).sum() * k)

        else:
            n_ctrl = k
            n_trmnt = k

        if n_ctrl > n_samples_ctrl:
            raise ValueError(f'With k={k}, the number of the first k observations'
                             ' bigger than the number of samples'
                             f'in the control group: {n_samples_ctrl}'
                             )
        if n_trmnt > n_samples_trmnt:
            raise ValueError(f'With k={k}, the number of the first k observations'
                             ' bigger than the number of samples'
                             f'in the treatment group: {n_samples_ctrl}'
                             )

        score_ctrl = y_true[order][treatment[order] == 0][:n_ctrl].mean()
        score_trmnt = y_true[order][treatment[order] == 1][:n_trmnt].mean()

    return score_trmnt - score_ctrl

import pandas as pd
import numpy as np
from itertools import chain

def read_df(filepath):
    df = pd.read_json(path_or_buf=filepath, lines=True)
    df.set_index('id', inplace=True)
    df.drop(['data'], axis=1, inplace=True)
    df.rename(columns = {'label':f'labels_{filepath[:-6]}'}, inplace = True)
    return df

# https://towardsdatascience.com/inter-annotator-agreement-2f46c6d37bf3
def fleiss_kappa(M):
    """Computes Fleiss' kappa for group of annotators.
    :param M: a matrix of shape (:attr:'N', :attr:'k') with 'N' = number of subjects and 'k' = the number of categories.
        'M[i, j]' represent the number of raters who assigned the 'i'th subject to the 'j'th category.
    :type: numpy matrix
    :rtype: float
    :return: Fleiss' kappa score
    """
    N, k = M.shape  # N is # of items, k is # of categories
    n_annotators = float(np.sum(M[0, :]))  # # of annotators
    tot_annotations = N * n_annotators  # the total # of annotations
    category_sum = np.sum(M, axis=0)  # the sum of each category over all items

    # chance agreement
    p = category_sum / tot_annotations  # the distribution of each category over all annotations
    PbarE = np.sum(p * p)  # average chance agreement over all categories

    # observed agreement
    P = (np.sum(M * M, axis=1) - n_annotators) / (n_annotators * (n_annotators - 1))
    Pbar = np.sum(P) / N  # add all observed agreement chances per item and divide by amount of items

    return round((Pbar - PbarE) / (1 - PbarE), 4)

# https://towardsdatascience.com/inter-annotator-agreement-2f46c6d37bf3
def cohen_kappa(ann1, ann2):
    """Computes Cohen kappa for pair-wise annotators.
    :param ann1: annotations provided by first annotator
    :type ann1: list
    :param ann2: annotations provided by second annotator
    :type ann2: list
    :rtype: float
    :return: Cohen kappa statistic
    """
    count = 0
    for an1, an2 in zip(ann1, ann2):
        if an1 == an2:
            count += 1
    A = count / len(ann1)  # observed agreement A (Po)

    uniq = set(ann1 + ann2)
    E = 0  # expected agreement E (Pe)
    for item in uniq:
        cnt1 = ann1.count(item)
        cnt2 = ann2.count(item)
        count = ((cnt1 / len(ann1)) * (cnt2 / len(ann2)))
        E += count

    # prevent division by zero error
    if (A == 1 and E == 1):
        return 1
    else:
        return round((A - E) / (1 - E), 4)

def flatten_labels(labels):
    ent = []
    for ann in labels:
        ent.append(' '.join(map(str, ann)))
    return ent


if __name__ == '__main__':
    fiete = read_df('fiete.jsonl')
    admin = read_df('admin.jsonl')

    df = pd.merge(admin, fiete, on='id')

    df.labels_admin = df.labels_admin.map(flatten_labels)
    df.labels_fiete = df.labels_fiete.map(flatten_labels)

    df['cohen_kappa'] = df.apply(lambda x: cohen_kappa(x['labels_admin'], x['labels_fiete']), axis=1)
    print(df.cohen_kappa.mean())

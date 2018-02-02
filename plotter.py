import pandas as pd
import math
import os
import numpy as np
from glob import glob
from flask import session
import untangle
from io import StringIO
# whole bunch of defintions
gDM = 1.
gu = gd = gs = 0.25  # set to DM LHC WG stuff
mn, conv_units = 0.938, 2.568 * pow(10., 27.)
Delta_d_p, Delta_u_p, Delta_s_p = -0.42, 0.85, -0.08

DATA_LOCATION = 'data/'
DATA_FILE_EXT = '.xml'


def dataset_names():
    datasets = glob('data/*.xml')
    for dataset in datasets:
        dataset = dataset.replace(DATA_LOCATION, '')
        dataset = dataset.replace(DATA_FILE_EXT, '')
        yield dataset

def get_datasets():
    return list(dataset_names())

def set_gSM(_gU,_gD,_gS):
    global gu, gd, gs
    gu = _gU
    gd = _gD
    gs = _gS

def get_gSM():
    return gu, gd, gs

def dd2lhc(df):
    f = abs(gDM * (gu * Delta_u_p + gd * Delta_d_p + gs * Delta_s_p))

    # calculate mu
    df['mu_nDM'] = mn * df['m_DM'] / (mn + df['m_DM'])
    # apply conversion units to sigma
    df['sigma'] = df['sigma'] * conv_units
    df['sigma_in_GeV'] = df['sigma']

    # calculate m_mediator
    df['m_med'] = np.power(f * df['mu_nDM'], 0.5) / \
        np.power(math.pi * df['sigma'] / 3., 0.25)


def lhc2dd(df):
    f = abs(gDM * (gu * Delta_u_p + gd * Delta_d_p + gs * Delta_s_p))
    # calculate mu
    df['mu_nDM'] = mn * df['m_DM'] / (mn + df['m_DM'])

    # apply conversion units to sigma
    df['sigma_in_GeV'] = 3 * np.power(f * df['mu_nDM'], 2.) / (math.pi * np.power(df['m_med'], 4.))
    df['sigma'] = df['sigma_in_GeV']/conv_units

def get_metadata(dataset):
    input_file = os.path.join(DATA_LOCATION, dataset + DATA_FILE_EXT)

    #XML Parsing Test
    result = untangle.parse(input_file)

    dataComment = result.limit.data_comment.cdata
    dataLabel = result.limit.data_label.cdata
    dataReference = result.limit.data_reference.cdata
    dateOfAnnouncement = result.limit.date_of_announcement.cdata
    experiment = result.limit.experiment.cdata
    measurementType = result.limit.measurement_type.cdata
    resultType = result.limit.result_type.cdata
    spinDependency = result.limit.spin_dependency.cdata
    xRescale = result.limit.x_rescale.cdata
    xUnits = result.limit.x_units.cdata
    yRescale = result.limit.y_rescale.cdata
    yUnits = result.limit.y_units.cdata

    metadata = {'fileName':dataset,
                'dataComment':dataComment,
                'dataLabel':dataLabel,
                'dataReference':dataReference,
                'dateOfAnnouncement':dateOfAnnouncement,
                'experiment':experiment,
                'measurementType':measurementType,
                'resultType':resultType,
                'spinDependency':spinDependency,
                'xRescale':xRescale,
                'xUnits':xUnits,
                'yRescale':yRescale,
                'yUnits':yUnits}
    #print (metadata)
    return metadata

def get_data(dataset):

    input_file = os.path.join(DATA_LOCATION, dataset + DATA_FILE_EXT)
    #TODO: Validate file/dataset

    #XML Parsing
    result = untangle.parse(input_file)
    dataValues = result.limit.data_values.cdata
    experiment = result.limit.experiment.cdata
    yRescale = result.limit.y_rescale.cdata
    #print (dataValues)

    #remove leading {[, trailing ]}
    rawData = dataValues.replace("{[","").replace("]}","")
    data = StringIO(rawData)

    print(experiment)

    #Determine data type
    if experiment == 'LUX-ZEPLIN' or experiment == 'LUX':
        dataset_type = 'DD'
        names = ['m_DM', 'sigma']
    else:
        dataset_type = 'LHC'
        names = ['m_med', 'm_DM']

    #parse
    df = pd.read_csv(data, delim_whitespace=True, lineterminator=';', names=names)
    #adjust the yRescale, ie (multiply every value in column index 1 with the yRescale)
    df.iloc[:, 1] =  df.iloc[:, 1].apply(lambda x: x * float(yRescale))

    #add a coloum of labels
    label = os.path.basename(input_file).split('.')[0]
    df.insert(0, 'label', label)

    #Verification
    if experiment == 'LUX':
        print(df)

    #convert
    if dataset_type == 'DD':
        dd2lhc(df)
    elif dataset_type == 'LHC':
        lhc2dd(df)

    return df


def get_figure(df):
    import matplotlib.pyplot as plt
    plt.style.use('ggplot')
    fig = plt.figure(figsize=(6.5875, 6.2125))
    ax = fig.add_subplot(111)
    ax.set_title("DD2LHC Pico (p, axial)")
    ax.set_xlabel(r'$m_{Med}$')
    ax.set_ylabel(r'$m_{DM}$')
    ax.semilogy(df['m_med'], df['m_DM'], color='red')
    return fig
#    fig.savefig('pico2plane2.png')

if __name__ == '__main__':
    df = get_data('input/LHC_2_DD_p.dat')
    get_figure(df)

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
gSM = gu = gd = gs = 1.00  # set to DM LHC WG stuff
mn, conv_units = 0.938, 2.568 * pow(10., 27.)
Delta_d_p, Delta_d_n, Delta_u_p, Delta_u_n, Delta_s_p, Delta_s_n, = -0.42, -0.42, 0.85, 0.85, -0.08, -0.08

#Modifiers
si_modifier = 'vector' #OR scalar
sd_modifier = 'proton' #OR nuetron

#for scalar in particular
v=246
fup, fdp = 0.0208, 0.0411 #from arXiv:1506.04142
fsp=0.043 #from arXiv:1301.1114
fTG=1-fup-fdp-fsp


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

def set_SI_modifier(modifier):
    global si_modifier
    si_modifier = modifier

def get_SI_modifier():
    return si_modifier

def dd2lhc(df):
    f = abs(gDM * (gu * Delta_u_p + gd * Delta_d_p + gs * Delta_s_p))

    # calculate mu
    df['mu_nDM'] = mn * df['m_DM'] / (mn + df['m_DM'])
    # apply conversion units to sigma
    #df['sigma'] = df['sigma']
    df['sigma_in_GeV'] = df['sigma'] * conv_units

    # calculate m_mediator
    df['m_med'] = np.power(f * df['mu_nDM'], 0.5) / \
        np.power(math.pi * df['sigma'] / 3., 0.25)


def lhc2dd_SD(df,modifier='proton'):
    # calculate mu
    df['mu_nDM'] = mn * df['m_DM'] / (mn + df['m_DM'])

    if(modifier == 'neutron'):
        f = abs(gDM * (gu * Delta_u_n + gd * Delta_d_n + gs * Delta_s_n))
    else:
        f = abs(gDM * (gu * Delta_u_p + gd * Delta_d_p + gs * Delta_s_p))

    # apply conversion units to sigma
    df['sigma_in_GeV'] = 3 * np.power(f * df['mu_nDM'], 2.) / (math.pi * np.power(df['m_med'], 4.))
    df['sigma'] = df['sigma_in_GeV']/conv_units

def lhc2dd_SI(df,modifier='scalar'):
    # calculate mu
    df['mu_nDM'] = mn * df['m_DM'] / (mn + df['m_DM'])

    if(modifier == 'vector'):
        f = (2 * gu + gd) * gDM
        sigma_eq=np.power(f * df['mu_nDM'], 2.) / (math.pi * np.power(df['m_med'], 4.))
    else:
        f=(mn/v)*gSM*gDM*(fup+fdp+fsp+2./27.*fTG*3.)/np.power(df['m_med'],2.0)
        sigma_eq=np.power(f*df['mu_nDM'],2.)/(math.pi)

    # apply conversion units to sigma
    df['sigma_in_GeV'] = sigma_eq
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

def get_data(dataset,modifier=''):

    input_file = os.path.join(DATA_LOCATION, dataset + DATA_FILE_EXT)
    #TODO: Validate file/dataset

    #XML Parsing
    result = untangle.parse(input_file)
    dataValues = result.limit.data_values.cdata
    experiment = result.limit.experiment.cdata
    spinDependency = result.limit.spin_dependency.cdata
    yRescale = result.limit.y_rescale.cdata
    #print (dataValues)

    #remove leading {[, trailing ]}
    rawData = dataValues.replace("{[","").replace("]}","").replace("\n","")
    data = StringIO(rawData)

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

    #convert
    if dataset_type == 'DD':
        dd2lhc(df)
    elif dataset_type == 'LHC':
        if spinDependency == 'SD':
            lhc2dd_SD(df,modifier if modifier else sd_modifier)
        else:
            lhc2dd_SI(df,modifier if modifier else si_modifier)
        #extrapolate LHC Data
        extrap_mdm = range(1, int(min(df['m_DM'])))
        extrap_sigma = np.repeat(min(df['sigma']), len(extrap_mdm))
        extrap_df = pd.DataFrame({'label':label,'m_DM':extrap_mdm,'sigma':extrap_sigma})
        df = df.append(extrap_df)

    #Print Data to Verify
    #pd.options.display.max_rows = 5
    #pd.set_option('expand_frame_repr',False)
    #print(df)
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

def make_plot(coupling, df_lhc, name_only, df_dd):
    import matplotlib.pyplot as plt
    plt.title(coupling + ": CMS & LUX (LHC2DD)")
    plt.plot(df_lhc['m_DM'],df_lhc['sigma'], 'k-', linewidth=3, color="#0165fc", label=name_only)
    plt.plot(df_dd['m_DM'], df_dd['sigma'], 'k-', linewidth=3, color="purple", label="LUX")
    plt.ylabel("$ \sigma_{DM}$ (cross-section)")
    plt.xlabel("mDM")
    plt.yscale("log")
    plt.xscale("log")
    plt.grid(True)
    plt.legend(loc=1, ncol=1, borderaxespad=0.0, prop={'size': 9})
    plt.savefig(name_only + ".pdf")
    plt.close()
    return

if __name__ == '__main__':
    lhc_df1 = get_data('CMS_monojet_July2017_VECTOR','vector')
    lhc_df2 = get_data('CMS_monojet_July2017_VECTOR','scalar')
    lhc_df3 = get_data('CMS_monojet_July2017_AXIAL_3','proton')
    lhc_df4 = get_data('CMS_monojet_July2017_AXIAL_3','neutron')
    dd_df1 = get_data('LUX_2016_SI')
    dd_df2 = get_data('LUX_2016_SD_p')
    dd_df3 = get_data('LUX_2016_SD_n')

    make_plot("Vector",lhc_df1,"VEC_MESS5_jc",dd_df1)
    make_plot("Scalar",lhc_df2,"lhc_scalar5_jc",dd_df1)
    make_plot("Proton",lhc_df3,"lhc_axialp5_jc",dd_df2)
    make_plot("Neuton",lhc_df4,"lhc_axialn5_jc",dd_df3)

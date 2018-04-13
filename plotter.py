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

dd_exp_list = ['lux', 'zeplin', 'xenon', 'icecube', 'pico', 'crest', 'darkside', 'cdms', 'panda']
collider_exp_list = ['lhc', 'atlas', 'cms']


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

def dd2lhc_SD(df): #using for axial interactions
    f = abs(gDM * (gu * Delta_u_p + gd * Delta_d_p + gs * Delta_s_p))

    # calculate mu
    df['mu_nDM'] = mn * df['m_DM'] / (mn + df['m_DM'])
    # apply conversion units to sigma
    #df['sigma'] = df['sigma']
    df['sigma_in_GeV'] = df['sigma'] * conv_units

    # calculate m_mediator
    df['m_med'] = np.power(f * df['mu_nDM'], 0.5) / np.power(math.pi * df['sigma_in_GeV'] / 3., 0.25)


def dd2lhc_SI(df, modifier): #for scalar and vector interactins, scalar should be default (Higgs like)
    df['mu_nDM'] = mn * df['m_DM'] / (mn + df['m_DM'])
    df['sigma_in_GeV'] = df['sigma'] * conv_units
    print modifier 
    if(modifier == 'scalar'):
        fmMed2 = (mn/v)*gSM*gDM*(fup+fdp+fsp+2./27.*fTG*3.);
        df['m_med']=np.power(fmMed2*df['mu_nDM'],0.5)/np.power(math.pi*df['sigma_in_GeV'],0.25);
    else:
        df['m_med'] = np.power((2*gu+gd)*gDM*df['mu_nDM'], 0.5)/np.power(math.pi*df['sigma_in_GeV'],0.25);

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
    dataformat = result.limit.dataformat.cdata
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
                'dataformat':dataformat,
                'measurementType':measurementType,
                'resultType':resultType,
                'spinDependency':spinDependency,
                'xRescale':xRescale,
                'xUnits':xUnits,
                'yRescale':yRescale,
                'yUnits':yUnits}
    #print (metadata)
    return metadata

def parseExperimentType(experiment):
    dataset_type, names = '',''
    if any(exp in experiment.lower() for exp in dd_exp_list):
            dataset_type = 'DD'
            names = ['m_DM', 'sigma']
    elif any(exp in experiment.lower() for exp in collider_exp_list):
            dataset_type = 'LHC'
            names = ['m_med', 'm_DM']
    return dataset_type, names


def parseDataformat(dataformat):
    dataset_type, names = '',''
    if dataformat.upper() in 'DD':
            dataset_type = 'DD'
            names = ['m_DM', 'sigma']
    elif dataformat.upper() in 'LHC':
            dataset_type = 'LHC'
            names = ['m_med', 'm_DM']
    return dataset_type, names




def get_data(dataset,modifier=''):

    input_file = os.path.join(DATA_LOCATION, dataset + DATA_FILE_EXT)
    #TODO: Validate file/dataset

    #XML Parsing
    result = untangle.parse(input_file)
    dataValues = result.limit.data_values.cdata
    experiment = result.limit.experiment.cdata
    dataformat = result.limit.dataformat.cdata
    spinDependency = result.limit.spin_dependency.cdata
    yRescale = result.limit.y_rescale.cdata
    #print (dataValues)

    #remove leading {[, trailing ]}
    rawData = dataValues.replace("{[","").replace("]}","").replace("\n","")
    data = StringIO(rawData)

    #dataset_type, names = parseExperimentType(experiment)
    dataset_type, names = parseDataformat(dataformat)
    if(dataset_type == ''):
        return None

    #parse
    df = pd.read_csv(data, delim_whitespace=True, lineterminator=';', names=names)
    #adjust the yRescale, ie (multiply every value in column index 1 with the yRescale)
    df.iloc[:, 1] =  df.iloc[:, 1].apply(lambda x: x * float(yRescale))

    #add a coloum of labels
    label = os.path.basename(input_file).split('.')[0]
    df.insert(0, 'label', label)

    #convert
    if dataset_type == 'DD':
        df['type']='DD'
        if spinDependency == 'SD':  #BP
            dd2lhc_SD(df)
        else:
            dd2lhc_SI(df, modifier if modifier else si_modifier)

    elif dataset_type == 'LHC':
        df['type']='LHC'
        if spinDependency == 'SD':
            lhc2dd_SD(df,modifier if modifier else sd_modifier)
        else:
            lhc2dd_SI(df,modifier if modifier else si_modifier)
        #extrapolate LHC Data
        #note, not sure if appending in this fashion is the best way to extrapolate and expand the dataframe
        extrap_mdm = range(1, int(min(df['m_DM'])))
        extrap_sigma = np.repeat(min(df['sigma']), len(extrap_mdm))
        extrap_mMed = np.repeat(max(df['m_med']), len(extrap_mdm))
        extrap_df = pd.DataFrame({'label':label,'m_DM':extrap_mdm,'m_med':extrap_mMed,'sigma':extrap_sigma,'type':'LHC'})
        df = df.append(extrap_df)

    #Print Data to Verify
    pd.options.display.max_rows = 5
    pd.set_option('expand_frame_repr',False)
    #print(df)
    return df


if __name__ == '__main__':
    lhc_df1 = get_data('CMS_monojet_July2017_VECTOR','vector')
    lhc_df2 = get_data('CMS_monojet_July2017_VECTOR','scalar')
    lhc_df3 = get_data('CMS_monojet_July2017_AXIAL_3','proton')
    lhc_df4 = get_data('CMS_monojet_July2017_AXIAL_3','neutron')
    dd_df1 = get_data('LUX_2016_SI')
    dd_df2 = get_data('LUX_2016_SD_p')
    dd_df3 = get_data('LUX_2016_SD_n')


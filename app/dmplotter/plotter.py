# -*- coding: utf-8 -*-
import pandas as pd
import math
import os
import numpy as np
from glob import glob
from flask import session
import untangle
from io import StringIO

from bokeh.plotting import figure

from app.dmplotter.conversion import dd2lhc_SD, dd2lhc_SI, lhc2dd_SD, lhc2dd_SI

#Modifiers
si_modifier = 'vector' #OR scalar
sd_modifier = 'proton' #OR nuetron

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

def set_SI_modifier(modifier):
    global si_modifier
    si_modifier = modifier

def get_SI_modifier():
    return si_modifier

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
        elif spinDependency == 'SI':
            lhc2dd_SI(df,modifier if modifier else si_modifier)
        else:
            return None
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


################################################################################
################################################################################
################################################################################

def getSimplifiedPlot():
    plot = figure(
        title='Simplified Model Plane',
        tools='wheel_zoom, pan, save',
        toolbar_location="above",
        x_axis_label='mMed',
        x_axis_type="log",
        y_axis_label="mDM",
        y_axis_type="log",
        plot_width=500,
        plot_height=500,
    )
    plot.title.text_font_size = "1.2em"
    plot.xaxis.axis_label_text_font_size = "14pt"
    plot.yaxis.axis_label_text_font_size = "14pt"
    return plot

def getDDPlot():
    plot = figure(
        title='Direct Detection Plane',
        tools='wheel_zoom, pan, save',
        toolbar_location="above",
        x_axis_label='mDM',
        x_axis_type="log",
        y_axis_label="σDM (cross-section)",
        y_axis_type="log",
        plot_width=500,
        plot_height=500,
    )
    plot.title.text_font_size = "1.2em"
    plot.xaxis.axis_label_text_font_size = "14pt"
    plot.yaxis.axis_label_text_font_size = "14pt"
    return plot

def getLegendPlot():
    legendPlot = figure(
        plot_width=500,
        plot_height=250,
        tools="",
        toolbar_location=None
    )
    legendPlot.axis.visible = False
    legendPlot.xgrid.visible = False
    legendPlot.ygrid.visible = False
    legendPlot.outline_line_color = None
    return legendPlot


if __name__ == '__main__':
    lhc_df1 = get_data('CMS_monojet_July2017_VECTOR','vector')
    lhc_df2 = get_data('CMS_monojet_July2017_VECTOR','scalar')
    lhc_df3 = get_data('CMS_monojet_July2017_AXIAL_3','proton')
    lhc_df4 = get_data('CMS_monojet_July2017_AXIAL_3','neutron')
    dd_df1 = get_data('LUX_2016_SI')
    dd_df2 = get_data('LUX_2016_SD_p')
    dd_df3 = get_data('LUX_2016_SD_n')

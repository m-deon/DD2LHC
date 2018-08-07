# -*- coding: utf-8 -*-
import pandas as pd
import math
import os
import numpy as np

# whole bunch of defintions
gDM = 1.
gSM = gu = gd = gs = 1.00  # set to DM LHC WG stuff
mn, conv_units = 0.938, 2.568 * pow(10., 27.)
Delta_d_p, Delta_d_n, Delta_u_p, Delta_u_n, Delta_s_p, Delta_s_n, = -0.42, -0.42, 0.85, 0.85, -0.08, -0.08

#for scalar in particular
v=246
fup, fdp = 0.0208, 0.0411 #from arXiv:1506.04142
fsp=0.043 #from arXiv:1301.1114
fTG=1-fup-fdp-fsp

def set_gSM(_gU,_gD,_gS):
    global gu, gd, gs
    gu = _gU
    gd = _gD
    gs = _gS

def get_gSM():
    return gu, gd, gs

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

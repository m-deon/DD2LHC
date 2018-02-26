#CALL SEQUENCE: lhcconvert.py
#PURPOSE: Convert limits LHC to DD for all interactions
#DATE: Februrary 2018
#WRITTEN BY: Carly KleinStern, with help from Bjoern Penning
#necessary imports
from array import array
import sys
import math
import os
import numpy as np
import matplotlib.pyplot as plt

#-------INPUT DATA HERE-------#
#specify LHC DATASETS
#make a folder in current directory with all DATA in it
path_SI = "./data/CMS_monojet_July2017_VECTOR.txt"
path_SD = "./data/CMS_monojet_July2017_AXIAL_3.txt"

#specify DD DATASETS
data1 = open("./data/LUX_2016_SI.txt", "r")
data2 = open("./data/LUX_2016_SD_p.txt", "r")
data3 = open("./data/LUX_2016_SD_n.txt", "r")

#this function extracts the DD data to be graphed later, no conversion
def get_dd_data(dd_data):
	sig_dd_l = []
	mdm_dd_l = []
	for line in dd_data:

		elems = line.split();
		sig_dd = float(elems[1])
		mdm_dd = float(elems[0])
		sig_dd_l.append(float(sig_dd))
		mdm_dd_l.append(float(mdm_dd))
		#print str(sig_dd)+" "+str(mdm_dd)

	return sig_dd_l, mdm_dd_l

#this function yields the name of the dataset (without path or extension)
def base(path):
	base=os.path.basename(path)
	split = os.path.splitext(base)
	name_only = split[0]
	return name_only

#get lhc data and convert it in one go
def conv(path, coupling):
    mdm_l = []
    sigma_conv_l = []
    dataset=open(path)

    #lots of definitions
    gDM = 1.0
    #change this to whatever coupling to standard model is desired, for now call couplings to each quark the same
    gu=gd=gs=1.0
    gSM = 1.0

    mn=0.938
    Delta_d_p, Delta_d_n, Delta_u_p, Delta_u_n, Delta_s_p, Delta_s_n, = -0.42, -0.42, 0.85, 0.85, -0.08, -0.08

    #scale factor between dd and lhc
    conv_units = 2.568*pow(10.0,27.0)

    #for scalar in particular
    v=246
    fup, fdp = 0.0208, 0.0411 #from arXiv:1506.04142
    fsp=0.043 #from arXiv:1301.1114
    fTG=1-fup-fdp-fsp

    for line in dataset:
        elems = line.split();
        mmed = float(elems[0])
        mdm = float(elems[1])
        mu_nDM=mn*mdm/(mn+mdm)

        #assuming that metadata regarding interaction has been extracted...may need to tweak exact keyword
        #equations from Buchmueller et al 2015, arxiv: 1407.8257

        #scalar interaction, SI
        if coupling == "scalar SI":
            f=(mn/v)*gSM*gDM*(fup+fdp+fsp+2./27.*fTG*3.)/pow(mmed,2.0)
            sigma_eq=pow(f*mu_nDM,2.)/(math.pi)

        #vector interaction, SI
        if coupling == "vector SI":
            sigma_eq=pow((2*gu+gd)*gDM*mu_nDM,2.)/(math.pi*pow(mmed,4.))

	    #axial_p interaction, SD
        if coupling == "SD proton":
            f=abs(gDM*(gu*Delta_u_p+gd*Delta_d_p+gs*Delta_s_p))
            sigma_eq=3*pow(f*mu_nDM,2.)/(math.pi*pow(mmed,4.))

        #axial_n interaction, SD
        if coupling == "SD neutron":
            f=abs(gDM*(gu*Delta_u_p+gd*Delta_d_p+gs*Delta_s_p))
            sigma_eq=3*pow(f*mu_nDM,2.)/(math.pi*pow(mmed,4.))

        sigma_conv=sigma_eq/conv_units
        sigma_conv_l.append(float(sigma_conv))
        mdm_l.append(float(mdm))

    return mdm_l, sigma_conv_l


#-------End definitions of functions-------#

lhc_mdm_0, lhc_sigma_0 = conv(path_SI, "vector SI")
lhc_mdm_1, lhc_sigma_1 = conv(path_SI, "scalar SI")
lhc_mdm_2, lhc_sigma_2 = conv(path_SD, "SD proton")
lhc_mdm_3, lhc_sigma_3 = conv(path_SD, "SD neutron")

dd_sig_1, dd_mdm_1 = get_dd_data(data1)
dd_sig_2, dd_mdm_2 = get_dd_data(data2)
dd_sig_3, dd_mdm_3 = get_dd_data(data3)

#print arrays to make sure all is well

#vector
print lhc_mdm_0
print lhc_sigma_0

print '------------'

print dd_mdm_1
print dd_sig_1

#scalar
#print array_lhc_mdm_1
#print array_lhc_sigma_1

#axial_p
#print array_lhc_mdm_2
#print array_lhc_sigma_2

#axial_n
#print array_lhc_mdm_3
#print array_lhc_sigma_3

#----------Begin plotting in matplotlib----------#
#this should eventually be turned into a function
plt.title("VECTOR: LUX & CMS (LHC2DD)")
plt.plot(lhc_mdm_0, lhc_sigma_0, 'k-', linewidth=3, color="#0165fc", label="CMS_vector_2017, gSM = 1.0")
plt.plot(dd_mdm_1, dd_sig_1, 'k-', linewidth=3, color="purple", label="LUX_2016_vector, gSM = 1.0")
plt.ylabel("$ \sigma_{DM}$ (cross-section)")
plt.xlabel("mDM")
plt.yscale("log")
plt.xscale("log")
plt.grid(True)
plt.legend(loc=1, ncol=1, borderaxespad=0.0, prop={'size': 9})
plt.savefig("lhc_vec2_2.pdf")
plt.close()

'''
plt.title("SCALAR: LUX & CMS (LHC2DD)")
plt.plot(lhc_mdm_1, lhc_sigma_1, 'k-', linewidth=3, color="#0165fc", label="CMS_axialn_2017, gSM = 1.0")
plt.plot(dd_mdm_1, dd_sig_1, 'k-', linewidth=3, color="r", label="LUX_2016_axialn, gSM = 1.0")
plt.ylabel("$ \sigma_{DM}$ (cross-section)")
plt.xlabel("mDM")
plt.yscale("log")
plt.xscale("log")
plt.grid(True)
plt.legend(loc=1, ncol=1, borderaxespad=0.0, prop={'size': 9})
plt.savefig("lhc_scalar2.pdf")
plt.close()

plt.title("AXIAL_p: LUX & CMS (LHC2DD)")
plt.plot(lhc_mdm_2, lhc_sigma_2, 'k-', linewidth=3, color="#0165fc", label="CMS_axialp_2017, gSM = 1.0")
plt.plot(dd_mdm_2, dd_sig_2, 'k-', linewidth=3, color="g", label="LUX_2016_axialp, gSM = 1.0")
plt.ylabel("$ \sigma_{DM}$ (cross-section)")
plt.xlabel("mDM")
plt.yscale("log")
plt.xscale("log")
plt.grid(True)
plt.legend(loc=1, ncol=1, borderaxespad=0.0, prop={'size': 9})
plt.savefig("lhc_axialp2.pdf")
plt.close()

plt.title("AXIAL_n: LUX & CMS (LHC2DD)")
plt.plot(lhc_mdm_3, lhc_sigma_3, 'k-', linewidth=3, color="#0165fc", label="CMS_axialn_2017, gSM = 1.0")
plt.plot(dd_mdm_3, dd_sig_3, 'k-', linewidth=3, color="black", label="LUX_2016_axialn, gSM = 1.0")
plt.ylabel("$ \sigma_{DM}$ (cross-section)")
plt.xlabel("mDM")
plt.yscale("log")
plt.xscale("log")
plt.grid(True)
plt.legend(loc=1, ncol=1, borderaxespad=0.0, prop={'size': 9})
plt.savefig("lhc_axialn2.pdf")
plt.close()
'''

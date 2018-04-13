#CALL SEQUENCE: extrapolatelhc.py
#PURPOSE: Convert limits LHC to DD for all interactions (add LHC data extrapolation)
#DATE: Februrary 2018
#WRITTEN BY: Carly KleinStern

from array import array
import sys
import math
import os
import numpy as np
import matplotlib.pyplot as plt

#-------INPUT DATA HERE-------#
#specify LHC DATASETS
#make a folder in current directory with all DATA in it
path_SI = "./DATA/CMS_monojet_July2017_VECTOR.txt"
path_SD = "./DATA/CMS_monojet_July2017_AXIAL_3.txt"

#specify DD DATASETS
data1 = open("./DATA/LUX_2016_SI.txt", "r")
data2 = open("./DATA/LUX_2016_SD_p.txt", "r")
data3 = open("./DATA/LUX_2016_SD_n.txt", "r")

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

    la = range(1, int(min(mdm_l)))
    lb = np.repeat(min(sigma_conv_l), len(la))

    return mdm_l, la, sigma_conv_l, lb

#extrapolate lhc data
def extrapolate(path, coupling):
    orig_mdm, extrap_mdm, orig_sigma, extrap_sigma = conv(path, coupling)
    orig_mdm.extend(extrap_mdm)
    orig_sigma.extend(extrap_sigma)
    return orig_mdm, orig_sigma

##Where COUPLING is from the metadata of the input file (specifies interaction)
#def make_plot(coupling, lhc_mdm, lhc_sig, name_only, dd_mdm, dd_sig):

	#plt.title(coupling + ": CMS & LUX (LHC2DD)")
	#plt.plot(lhc_mdm, lhc_sig, 'k-', linewidth=3, color="#0165fc", label=name_only)
	#plt.plot(dd_mdm, dd_sig, 'k-', linewidth=3, color="purple", label="LUX")
	#plt.ylabel("$ \sigma_{DM}$ (cross-section)")
	#plt.xlabel("mDM")
	#plt.yscale("log")
	#plt.xscale("log")
	#plt.grid(True)
	#plt.legend(loc=1, ncol=1, borderaxespad=0.0, prop={'size': 9})

	#return plt.savefig("LUX&_" + name_only + ".pdf")

	#plt.close()

############### END FUNCTIONS ################

#vector interaction
dd_sig_1, dd_mdm_1 = get_dd_data(data1)
orig_mdm_lhc_1, orig_sigma_lhc_1 = extrapolate(path_SI, "vector SI")

#scalar interaction
dd_sig_2, dd_mdm_2 = get_dd_data(data1)
orig_mdm_lhc_2, orig_sigma_lhc_2 = extrapolate(path_SI, "scalar SI")

#axial_p interaction
dd_sig_3, dd_mdm_3 = get_dd_data(data2)
orig_mdm_lhc_3, orig_sigma_lhc_3 = extrapolate(path_SD, "SD proton")

#axial_n interaction
dd_sig_4, dd_mdm_4 = get_dd_data(data3)
orig_mdm_lhc_4, orig_sigma_lhc_4 = extrapolate(path_SD, "SD neutron")

############### PLOTTING ##################

#Plotting example
#make_plot("Vector", orig_mdm_lhc_1, orig_sigma_lhc_1, base(path_SI), dd_mdm_1, dd_sig_1)

plt.title("VECTOR: LUX & CMS (LHC2DD)")
plt.plot(orig_mdm_lhc_1, orig_sigma_lhc_1, 'k-', linewidth=3, color="#0165fc", label="CMS_vector_2017, gSM = 1.0")
plt.plot(dd_mdm_1, dd_sig_1, 'k-', linewidth=3, color="purple", label="LUX_2016_vector, gSM = 1.0")

plt.ylabel("$ \sigma_{DM}$ (cross-section)")
plt.xlabel("mDM")
plt.yscale("log")
plt.xscale("log")
plt.grid(True)
plt.legend(loc=1, ncol=1, borderaxespad=0.0, prop={'size': 9})
plt.savefig("VEC_MESS5.pdf")
plt.close()

plt.title("SCALAR: LUX & CMS (LHC2DD)")
plt.plot(orig_mdm_lhc_2, orig_sigma_lhc_2, 'k-', linewidth=3, color="#0165fc", label="CMS_scalar_2017, gSM = 1.0")
plt.plot(dd_mdm_1, dd_sig_1, 'k-', linewidth=3, color="r", label="LUX_2016_scalar, gSM = 1.0")
plt.ylabel("$ \sigma_{DM}$ (cross-section)")
plt.xlabel("mDM")
plt.yscale("log")
plt.xscale("log")
plt.grid(True)
plt.legend(loc=1, ncol=1, borderaxespad=0.0, prop={'size': 9})
plt.savefig("lhc_scalar5.pdf")
plt.close()

plt.title("AXIAL_p: LUX & CMS (LHC2DD)")
plt.plot(orig_mdm_lhc_3, orig_sigma_lhc_3, 'k-', linewidth=3, color="#0165fc", label="CMS_axialp_2017, gSM = 1.0")
plt.plot(dd_mdm_3, dd_sig_3, 'k-', linewidth=3, color="g", label="LUX_2016_axialp, gSM = 1.0")
plt.ylabel("$ \sigma_{DM}$ (cross-section)")
plt.xlabel("mDM")
plt.yscale("log")
plt.xscale("log")
plt.grid(True)
plt.legend(loc=1, ncol=1, borderaxespad=0.0, prop={'size': 9})
plt.savefig("lhc_axialp5.pdf")
plt.close()

plt.title("AXIAL_n: LUX & CMS (LHC2DD)")
plt.plot(orig_mdm_lhc_4, orig_sigma_lhc_4, 'k-', linewidth=3, color="#0165fc", label="CMS_axialn_2017, gSM = 1.0")
plt.plot(dd_mdm_4, dd_sig_4, 'k-', linewidth=3, color="black", label="LUX_2016_axialn, gSM = 1.0")
plt.ylabel("$ \sigma_{DM}$ (cross-section)")
plt.xlabel("mDM")
plt.yscale("log")
plt.xscale("log")
plt.grid(True)
plt.legend(loc=1, ncol=1, borderaxespad=0.0, prop={'size': 9})
plt.savefig("lhc_axialn5.pdf")
plt.close()


import os
import sys
import numpy as np
import pandas as pd
import time

import glob


###################################### FUNCTIONS ######################################

### Read chrpos mapping file
def read_collection(file_collection):
    """Function that reads tab seperated gzip collection file"""
    print ( "START: reading CSV file PRIM..." )
    start_time = time.time()
    f_tab = open(file_collection, 'r')
    df_collection = pd.read_csv(f_tab, index_col=False, header=0, delimiter="\t", compression="gzip") # index is snpID. # production_v2 - NEW March 2015. *REMEMBER TO correct "locate_collection_file()" as well*
    f_tab.close()
    elapsed_time = time.time() - start_time
    print( "END: read CSV file PRIM into DataFrame in %s s (%s min)" % (elapsed_time, elapsed_time/60) )

    # df_collection.head()
    #     rsID    snp_maf chr pos
    # 0   10:10001753 0.07455 10  10001753
    # 1   10:10001794 0.41050 10  10001794
    # 2   10:100023489    0.10540 10  100023489
    # 3   10:100025128    0.45430 10  100025128
    # 4   10:10002975 0.01193 10  10002975
    return df_collection

    

def read_and_process_gwas_file(file_gwas, GWAS_COL_SPECS):
    df_gwas = pd.read_csv(file_gwas, usecols=GWAS_COL_SPECS.keys(), index_col=False, header=0, delimiter="\t") # read
    df_gwas = df_gwas.rename(columns=GWAS_COL_SPECS) # rename cols. REF: https://pandas.pydata.org/pandas-docs/stable/basics.html#basics-rename
    return df_gwas


###################################### SCRIPT ######################################

def main(file_collection, file_out_prefix):

    ### Read GWAS data
    print "START: reading GWAS..."
    df_gwas = read_and_process_gwas_file(file_gwas, GWAS_COL_SPECS)
    print "END: reading GWAS..."
    # df_gwas.head()
    #     rsID    beta    se  pval
    # 0   rs1000000   0.0001  0.0043  0.98140
    # 1   rs10000010  -0.0022 0.0029  0.43840
    # 2   rs10000012  -0.0096 0.0053  0.07009
    # 3   rs10000013  -0.0096 0.0043  0.02558
    # 4   rs10000017  -0.0038 0.0045  0.39840


    n_snps_not_found_in_snpsnap = sum(~df_gwas["rsID"].isin(df_collection["rsID"]))
    print "Number of SNPs in GWAS data: {}".format(len(df_gwas))
    print "Number of SNPs in GWAS data *NOT found* in SNP chr pos mapping file: {}".format(n_snps_not_found_in_snpsnap)
    print "Percent SNPs not found: {:.2f} %".format(n_snps_not_found_in_snpsnap/float(len(df_gwas))*100)


    ### Join data
    # pd.merge(left, right, how='inner', on=None, left_on=None, right_on=None, left_index=False, right_index=False, sort=False, suffixes=('_x', '_y'), copy=True, indicator=False, validate=None)
    print "Joining data frames..."
    df_join = pd.merge(df_gwas, df_collection, how='inner', on="rsID")
    #     rsID    beta    se  pval    snp_maf chr pos
    # 0   rs1000000   0.0001  0.0043  0.98140 0.2237  12  126890980
    # 1   rs10000010  -0.0022 0.0029  0.43840 0.4901  4   21618674
    # 2   rs10000012  -0.0096 0.0053  0.07009 0.1402  4   1357325
    # 3   rs10000013  -0.0096 0.0043  0.02558 0.2296  4   37225069
    # 4   rs10000017  -0.0038 0.0045  0.39840 0.2475  4   84778125

    print "EXAMPLE output"
    print df_join.head()

    print "Dimensions of output file: {}".format(df_join.shape)

    ## Export
    print "START: exporting file..."
    file_out = "{}.gwassumstats.rolypoly_fmt.tab.gz".format(file_out_prefix)
    df_join.to_csv(file_out, sep="\t", index=False, compression='gzip')
    print "END: exported file: {}".format(file_out)




########################################################################################
###################################### GWAS PARAMETERS ######################################
########################################################################################

################## SCZ_Ripke2014 ##################
# hg19chrc        snpid   a1      a2      bp      info    or      se      p       ngt
# chr1    rs4951859       C       G       729679  0.631   0.97853 0.0173  0.2083  0
# chr1    rs142557973     T       C       731718  0.665   1.01949 0.0198  0.3298  0
# chr1    rs141242758     T       C       734349  0.666   1.02071 0.02    0.3055  0

file_gwas = "/Users/djw472/data/GWAS-sumstats/timshel-collection/SCZ_Ripke2014/ckqny.scz2snpres.gz"
file_out_prefix = "SCZ.Ripke2014"

COL_rsID = "snpid"
COL_beta = "or"
COL_se = "se"
COL_pval = "p"

################## alkes_lo_UKBB ##################

# SNP            CHR      POS     A1      A2      REF     EAF             Beta            se              P       N       INFO
# rs10399793      1       49298   T       C       T       0.37622         0.000334086     0.000731539     7.0E-01 459324  0.342797
# rs2462492       1       54676   C       T       C       0.599409        -0.000937692    0.000724671     1.7E-01 459324  0.340158
# rs3107975       1       55326   T       C       T       0.991552        0.00706826      0.0040343       8.3E-02 459324  0.324228
# rs74447903      1       57033   T       C       T       0.998221        0.00919789      0.00897642      3.8E-01 459324  0.296256
# 1:70728_C_T     1       70728   C       T       C       0.997834        0.00859618      0.00730365      2.6E-01 459324  0.365713
# rs2462495       1       79033   A       G       A       0.00129115      0.00321513      0.00929391      7.7E-01 459324  0.536566
# rs114608975     1       86028   T       C       T       0.896384        0.000549046     0.00115835      5.8E-01 459324  0.340885

# list_files = glob.glob("/Users/djw472/data/GWAS-sumstats/alkesgroup-collection/UKBB/*sumstats.gz")
# print list_files
#     # /Users/djw472/data/GWAS-sumstats/alkesgroup-collection/UKBB/body_BMIz.sumstats.gz
#     # /Users/djw472/data/GWAS-sumstats/alkesgroup-collection/UKBB/body_HEIGHTz.sumstats.gz
## file_out_prefix = <NOT DEFINED FOR ALKES FIELS>

# COL_rsID = "SNP"
# COL_beta = "Beta"
# COL_se = "se"
# COL_pval = "P"


################## BMI_Locke2015 ##################

# file_gwas = "/Users/djw472/data/GWAS-sumstats/timshel-collection/BMI_Locke2015/All_ancestries_SNP_gwas_mc_merge_nogc.tbl.uniq" # (cannot read .zip from GUI OSX zipped file)
# file_out_prefix = "BMI.Locke2015"

# COL_rsID = "SNP"
# COL_beta = "b"
# COL_se = "se"
# COL_pval = "p"

#####################################################################################
###################################### DROPPED ######################################
#####################################################################################

################## BMI.Finucane_UKB ##################
# file_gwas = "/Users/djw472/data/GWAS-sumstats/finucane-collection/public_sumstats/PASS_BMI1.sumstats"
# file_out_prefix = "BMI.Finucane_UKB"
# # SNP     A1      A2      N       CHISQ   Z
# COL_rsID = "SNP"
# COL_beta = "Z"
# COL_se = "se"
# COL_pval = "p"


#####################################################################################
###################################### CONSTANTS ######################################
#####################################################################################


file_collection = "/Users/djw472/Dropbox/0_Projects/p_sc_genetics/analysis/src/snpsnap_EUR_1KG_phase3-chrpos_mapping.tab.gz"

GWAS_COL_SPECS = {COL_rsID:"rsID",COL_beta:"beta",COL_se:"se",COL_pval:"pval"} # do not change this. This "direction" of the dict is most convenient for pandas col rename


#####################################################################################
######################################## MAIN  ######################################
#####################################################################################

df_collection = read_collection(file_collection)

### Normal mode
main(file_gwas, file_out_prefix)

## Alkes mode
# for file_gwas in list_files:
#     file_out_prefix = os.path.basename(file_gwas).split(".")[0]
#     print "RUNNING {}".format(file_out_prefix)
#     main(file_gwas, file_out_prefix)




print "SCRIPT ENDED"


#-------------------------------------------------------------------------------
# Name:        Flow Regime Assignment Script
# Purpose:     Assigning a flow regime of perennial, intermittent or ephemeral to existing WBID segments or bucketing inconclusive data in a undetermined category
#
# Author:      34617 & 184819
#
# Created:     12/03/2018
# Updated:     01/01/2020
# Copyright:   (c) 34617 & 184819 2018
# Licence:
#-------------------------------------------------------------------------------
# -*- coding: utf-8 -*-

import arcpy, string, sys
from collections import defaultdict
from datetime import datetime, timedelta
import logging

for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
logging.basicConfig(filename = 'S:/common/NHD/FlowRegimes2.log', filemode = 'w', level=logging.INFO)


start_time = datetime.now()



print("Start time: " + time.asctime())
arcpy.env.overwriteOutput = 1


####try:
arcpy.AddMessage(len(sys.argv))
if len(sys.argv) == 4:
    arcpy.env.workspace = sys.argv[1]
    FlowObs = sys.argv[2]
    FlowDesg = sys.argv[3]
else:
    arcpy.env.workspace = "S:\\common\\NHD\\Flow_Regimes.gdb"
    FlowObs = "S:\\common\\NHD\\Flow_Regimes.gdb\\FlowRegime_Observations"
    FlowDesg = "S:\\common\\NHD\\Flow_Regimes.gdb\\Benchmark_Products\\WBID_FlwRgme_Designations"


FlowRegGDB = "S:\\common\\NHD\\Flow_Regimes.gdb"
tmp = {}
flag = 0
flds = ["WBID","ReachLength_Mi","Priority","Scope_of_Observation","Length","FLOW_REGIM","RECON_YEAR","Obs_Type"]
desgflds = ["WBID", "Length_Mi"]
updateflds = ["WBID","Flow_Regime","Comments","IsEstablished"]
##OutPutFeat = "FlowRegimes"
##OutPutFeat2 = OutPutLoc + "\\" + OutPutFeat
##TemplateClass = "S:\\common\\NHD\\allstreams.gdb\\FlowRegimes_Template"
stats_fld = [["Length", "SUM"]]
case_flds = ["WBID","Recon_Year","Wet_Dry"]
out_table = "S:\\gisdev\\dm4\\scratch.gdb\\stats_out"
outflds = ["WBID","Recon_Year","Wet_Dry","SUM_Length"]

print "Creating Flow Regimes..."
arcpy.AddMessage("Creating Flow Regimes...")

i=0

print "Populating dictionary with WBIDs, Reach Lengths..."
arcpy.AddMessage("Populating dictionary with WBIDs, Reach Lengths...")

try:
    tmpObsDict= {row[0]: {'TotalLength':round(row[1],2), 'TotalCount': None,'Priority': None,'CntPriority': None,
                'Scope': None, 'SumLength': 0.0, 'Status': None, 'FlowRegime': None, 'Flag': None, 'Most Recent': None,
                'PSum': 0.0, 'ISum': 0.0, 'ESum': 0.0,'PSumR': 0.0, 'ISumR': 0.0, 'ESumR': 0.0, 'Obs_Type': 0, 'ReserveFR': None} for row in arcpy.da.SearchCursor(FlowDesg,desgflds)}
    #del(row)
    tmp = {row[0]: row[0] for row in arcpy.da.SearchCursor(FlowObs,flds)}
    #del(row)
    logging.info(len(tmpObsDict))
    logging.info(len(tmp))


    #compare master WBID designations dictionary with observations dictionary; delete WBID dict entries with no corresponding observation records
    for keyB in tmpObsDict.keys():
        if keyB not in tmp.keys():
                del tmpObsDict[keyB]

    logging.info(len(tmpObsDict))


    #count observation records
    for keyA in tmpObsDict.keys():
        cntobs = 0
        with arcpy.da.SearchCursor(FlowObs,flds) as obs_cur:
            for row in obs_cur:
                if keyA == row[0]:
                    cntobs+=1

        tmpObsDict[keyA]['TotalCount'] = cntobs
except Exception as e:
    logging.warning("Failed to populate WBID, Reach Lengths")
    logging.warning(e)
    arcpy.GetMessages(2)
    sys.exit(0)



#Determine controlling priority, scope, and count of controlling priority records
#Populate remainder of dictionary

print "Populating remainder of dictionary, sorting for high priority..."
arcpy.AddMessage("Populating remainder of dictionary, sorting for high priority...")

##try:
hipriority = 99
#SumLength = 0.0
fr =''

cntprobs = 0
# PerSum = 0.0
#IntSum = 0.0
#EphSum = 0.0
Mostrecent = 0
year = 0
frmr = ''
for keyA in tmpObsDict.iterkeys():
    reservefr = None    #if keyA == 'AZ15020008-020':
     #   print "Here..."
        #print keyA
    with arcpy.da.SearchCursor(FlowObs,flds) as obs_cur:
        for row in obs_cur:
            if keyA == row[0] and row[5]!=None:        #check for matching key and non-null flow regime
                #if row[0] ==  'AZ15060103-007':
                #    print row[0]
                priority = row[2]
                obs_type = row[7]      #added -test
                scope = row[3]
                tmpObsDict[keyA]['Obs_Type']  = obs_type


                if str(scope) == 'RCH' and (row[5] != None and row[5]!='') :
                    if tmpObsDict[keyA]['FlowRegime'] == None:
                        tmpObsDict[keyA]['FlowRegime'] = row[5]
                    else:
                        reservefr = tmpObsDict[keyA]['FlowRegime']

                if obs_type == 7 and (row[5]!= None and row[5]!=''):
                    year = row[6]                                              ##Site visit processing
                    if Mostrecent == year:
                        tmpObsDict[keyA]['Flag'] = 2
                        if tmpObsDict[keyA]['FlowRegime'] == 'P':
                            if tmpObsDict[keyA]['PSum']!= None:
                                tmpObsDict[keyA]['PSum'] = tmpObsDict[keyA]['PSum'] + row[4]
                            else:
                                 tmpObsDict[keyA]['PSum'] = row[4]
                        elif tmpObsDict[keyA]['FlowRegime'] == 'I':
                            if tmpObsDict[keyA]['ISum']!= None:
                                tmpObsDict[keyA]['ISum'] = tmpObsDict[keyA]['ISum'] + row[4]
                            else:
                                tmpObsDict[keyA]['ISum'] = row[4]
                        elif tmpObsDict[keyA]['FlowRegime'] == 'E':
                            if tmpObsDict[keyA]['ESum']!= None:
                                tmpObsDict[keyA]['ESum'] = tmpObsDict[keyA]['ESum'] + row[4]
                            else:
                                tmpObsDict[keyA]['ISum'] = row[4]
                    if Mostrecent < year:
                        Mostrecent = year
                        frmr = row[5]
                        tmpObsDict[keyA]['Most Recent'] = Mostrecent        #update Most recent in Dictionary for staff site visits
                        tmpObsDict[keyA]['FlowRegime'] = frmr             #update associated Flow regime for most recent visit
                        if tmpObsDict[keyA]['FlowRegime'] == 'P':
                            tmpObsDict[keyA]['PSum'] = row[4]
                        elif tmpObsDict[keyA]['FlowRegime'] == 'I':
                            tmpObsDict[keyA]['ISum'] = row[4]
                        elif tmpObsDict[keyA]['FlowRegime'] == 'E':
                            tmpObsDict[keyA]['ESum'] = row[4]

                if priority < hipriority:
                    if hipriority != 99:
                        reservefr =  tmpObsDict[keyA]['FlowRegime']
                    cntprobs = 0
                    next_hi_pr = hipriority
                    hipriority = priority
                    scope = row[3]

                    if scope == 'RCH' and tmpObsDict[keyA]['ReserveFR'] <> reservefr:
                       tmpObsDict[keyA]['ReserveFR'] = reservefr
                    if scope == 'RCH' and tmpObsDict[keyA]['FlowRegime'] <> row[5]:
                       tmpObsDict[keyA]['FlowRegime'] = row[5]

                    if (scope == 'SEG' or scope =='DYNSEG') and row[4] <> None and tmpObsDict[keyA]['SumLength'] <> row[1]:      #Calculate/assign Sumlength according to scope of record
                        tmpObsDict[keyA]['SumLength']= 0.0
                        if tmpObsDict[keyA]['SumLength'] != None:
                            tmpObsDict[keyA]['SumLength'] = tmpObsDict[keyA]['SumLength'] + row[4]
                        else:
                            tmpObsDict[keyA]['SumLength'] = row[4]
                    elif scope == "RCH":
                        #SumLength = row[1]
                        pass
                    else:
                        pass

                    if (row[5] != None):
                        fr = row[5]
                        cntprobs+=1
                    else:
                        pass

                    #if priority != 3:
                    if obs_type != 7:              #Added-test
                        if row[5] =='P'and row[4]!= None and tmpObsDict[keyA]['PSumR'] != row[1]:      #Summation of segment lengths by flow regime
                            if  tmpObsDict[keyA]['PSumR'] != None:
                                tmpObsDict[keyA]['PSumR'] = tmpObsDict[keyA]['PSumR'] + row[4]
                            else:
                                tmpObsDict[keyA]['PSumR'] = row[4]
                        elif row[5] =='I'and row[4]!= None and tmpObsDict[keyA]['ISumR'] != row[1]:
                            if  tmpObsDict[keyA]['ISumR'] != None:
                                tmpObsDict[keyA]['ISumR'] = tmpObsDict[keyA]['ISumR'] + row[4]
                            else:
                                tmpObsDict[keyA]['ISumR'] = row[4]
                        elif row[5] =='E'and row[4]!= None and tmpObsDict[keyA]['ESumR'] != row[1]:
                            if  tmpObsDict[keyA]['ESumR'] != None:
                                tmpObsDict[keyA]['ESumR'] = tmpObsDict[keyA]['ESumR'] + row[4]
                            else:
                                tmpObsDict[keyA]['ESumR'] = row[4]
                        else:
                            pass
                    else:
##                        if row[5] == 'P' and Mostrecent > row[6]:
##                            Persum = row[1]
##                            frmr = row[5]
##                        elif row[5] == 'I'and Mostrecent > row[6]:
##                            IntSum = row[1]
##                            frmr = row[5]
##                        elif row[5] == 'E'and Mostrecent > row[6]:
##                            EphSum = row[1]
##                            frmr = row[5]
##                        else:
                        pass

##                      if row[5] =='P'and row[4]!= None:
##                        PerSum = PerSum + row[4]
##                    elif row[5] =='I'and row[4]!= None:
##                        IntSum = IntSum + row[4]
##                    elif row[5] =='E'and row[4]!= None:
##                        EphSum = EphSum + row[4]
##                    else:
##                        pass

                elif priority == hipriority:
                    cntprobs+=1
                    scope = row[3]
                    if (scope == 'SEG' or scope =='DYNSEG') and row[4] <> None and tmpObsDict[keyA]['SumLength'] <> row[1]:      #Calculate/assign Sumlength according to scope of record
                        if tmpObsDict[keyA]['SumLength'] != None:
                            tmpObsDict[keyA]['SumLength'] = tmpObsDict[keyA]['SumLength'] + row[4]
                        else:
                            tmpObsDict[keyA]['SumLength'] = row[4]
                    elif scope == "RCH":
                        #SumLength = row[1]
                        #pass
                        if tmpObsDict[keyA]['Scope'] <> "RCH":
                            tmpObsDict[keyA]['ReserveFR'] =  tmpObsDict[keyA]['FlowRegime']
                            tmpObsDict[keyA]['FlowRegime'] =  row[5]
                            tmpObsDict[keyA]['Scope'] = scope
                    else:
                        pass
                    if fr <> row[5] and (row[5] != None and row[5] <> ''):
                        flag = 1
                    else:
                        fr = row[5]

##                    if row[5] =='P'and row[4]!= None:
##                        PerSum = PerSum + row[4]
##                    elif row[5] =='I'and row[4]!= None:
##                        IntSum = IntSum + row[4]
##                    elif row[5] =='E'and row[4]!= None:
##                        EphSum = EphSum + row[4]
##                    else:
##                        pass

                    #if priority != 3:
                    if obs_type != 7:    ###For observations other than site visits
                        if row[5] =='P'and row[4]!= None and tmpObsDict[keyA]['PSumR'] != row[1]:      #Summation of segment lengths by flow regime
                            if  tmpObsDict[keyA]['PSumR'] != None:
                                tmpObsDict[keyA]['PSumR'] = tmpObsDict[keyA]['PSumR'] + row[4]
                            else:
                                tmpObsDict[keyA]['PSumR'] = row[4]
                        elif row[5] =='I'and row[4]!= None and tmpObsDict[keyA]['ISumR'] != row[1]:
                            if  tmpObsDict[keyA]['ISumR'] != None:
                                tmpObsDict[keyA]['ISumR'] = tmpObsDict[keyA]['ISumR'] + row[4]
                            else:
                                tmpObsDict[keyA]['ISumR'] = row[4]
                        elif row[5] =='E'and row[4]!= None and tmpObsDict[keyA]['ESumR'] != row[1]:
                            if  tmpObsDict[keyA]['ESumR'] != None:
                                tmpObsDict[keyA]['ESumR'] = tmpObsDict[keyA]['ESumR'] + row[4]
                            else:
                                tmpObsDict[keyA]['ESumR'] = row[4]
##                            if row[5] =='P'and row[4]!= None and tmpObsDict[keyA]['PSumR'] != row[1]:           #Summation of segment lengths by flow regime
##                                tmpObsDict[keyA]['PSumR'] = tmpObsDict[keyA]['PSumR'] + row[4]
##                            elif row[5] =='I'and row[4]!= None and tmpObsDict[keyA]['ISumR'] != row[1]:
##                                tmpObsDict[keyA]['ISumR'] = tmpObsDict[keyA]['ISumR'] + row[4]
##                            elif row[5] =='E'and row[4]!= None and tmpObsDict[keyA]['ESum'] != row[1]:
##                                tmpObsDict[keyA]['ESumR'] = tmpObsDict[keyA]['ESumR'] + row[4]
                        else:
                            pass
                    else:
##                        if row[5] == 'P'and Mostrecent > row[6]:
##                            Persum = row[1]
##                            frmr = row[5]
##                        elif row[5] == 'I'and Mostrecent > row[6]:
##                            IntSum = row[1]
##                            frmr = row[5]
##                        elif row[5] == 'E'and Mostrecent > row[6]:
##                            EphSum = row[1]
##                            frmr = row[5]
##                        else:
                        pass


                else:
                    continue



        if tmpObsDict[keyA]['SumLength'] <> 0 and tmpObsDict[keyA]['SumLength']!= None:                      #Determine flow regime ratios to reach length for segment summations
            PRatio = tmpObsDict[keyA]['PSumR']/tmpObsDict[keyA]['SumLength']
            IRatio = tmpObsDict[keyA]['ISumR']/tmpObsDict[keyA]['SumLength']
            ERatio = tmpObsDict[keyA]['ESumR']/tmpObsDict[keyA]['SumLength']

        tmpObsDict[keyA]['Priority'] = hipriority       #assign remaining attributes to main dictionary
        tmpObsDict[keyA]['Scope'] = scope
        tmpObsDict[keyA]['CntPriority'] = cntprobs
        tmpObsDict[keyA]['SumLength'] = round(tmpObsDict[keyA]['SumLength'],2)
        if tmpObsDict[keyA]['Most Recent'] == None:
            tmpObsDict[keyA]['FlowRegime'] = fr
        else:
            pass
        if  tmpObsDict[keyA]['Flag'] != 2:
            tmpObsDict[keyA]['Flag'] = flag
        if tmpObsDict[keyA]['Priority'] == 3:                      ##Site visit updated priority
            tmpObsDict[keyA]['Most Recent'] = Mostrecent
        if flag <> 1:
            if scope =='RCH':
                tmpObsDict[keyA]['Status'] = 'Complete'
            else:
                tmpObsDict[keyA]['Status'] = 'Partial'
        else:
            tmpObsDict[keyA]['Status'] = "Processed, Complete"

            #if hipriority!= 3:
            if obs_type!= 7:              ##Added- test
                if tmpObsDict[keyA]['SumLength'] <> 0.0 and PRatio > IRatio and PRatio > ERatio and PRatio > 0.5:
                        tmpObsDict[keyA]['FlowRegime'] = 'P'
                        logging.info("{0}  P Ratio:  {1}".format(keyA, round(PRatio,3)))
                elif tmpObsDict[keyA]['SumLength'] <> 0.0 and IRatio > PRatio and IRatio > ERatio and IRatio > 0.5:
                        tmpObsDict[keyA]['FlowRegime'] = 'I'
                        logging.info("{0}  I Ratio:  {1}".format(keyA, round(IRatio,3)))
                elif tmpObsDict[keyA]['SumLength'] <> 0.0 and ERatio > PRatio and ERatio > IRatio and ERatio > 0.5:
                        tmpObsDict[keyA]['FlowRegime'] = 'E'
                        logging.info("{0}  E Ratio:  {1}".format(keyA, round(ERatio,3)))
                else:
                        tmpObsDict[keyA]['FlowRegime'] = 'U'
                        logging.info("{0}  Max Ratio:   {1}     Status: {2}".format(keyA, round(max(PRatio, IRatio, ERatio),3), tmpObsDict[keyA]['FlowRegime']))
            #elif hipriority == 3 and tmpObsDict[keyA]['Flag'] == 2:
            elif obs_type== 7 and tmpObsDict[keyA]['Flag'] == 2:       ##Added-test
                if tmpObsDict[keyA]['PSum']>tmpObsDict[keyA]['ISum'] and tmpObsDict[keyA]['PSum']>tmpObsDict[keyA]['ESum']:
                    tmpObsDict[keyA]['FlowRegime'] = 'P'
                elif tmpObsDict[keyA]['ISum']>tmpObsDict[keyA]['PSum'] and tmpObsDict[keyA]['ISum']>tmpObsDict[keyA]['ESum']:
                    tmpObsDict[keyA]['FlowRegime'] = 'I'
                elif tmpObsDict[keyA]['ESum']>tmpObsDict[keyA]['PSum'] and tmpObsDict[keyA]['ESum']>tmpObsDict[keyA]['ISum']:
                    tmpObsDict[keyA]['FlowRegime'] = 'E'
                logging.info("{0} Most Recent Year: {1}  Multiple Most Recent Obs, Max Length: {2}  Flow Regime: {3}".format(keyA, tmpObsDict[keyA]['Most Recent'],
                            max(tmpObsDict[keyA]['PSum'],tmpObsDict[keyA]['ISum'], tmpObsDict[keyA]['ESum']), tmpObsDict[keyA]['FlowRegime']))
            else:
                #tmpObsDict[keyA]['FlowRegime'] = frmr
                logging.info("{0} Most Recent Year: {1}  Flow Regime Most Recently:  {2}".format(keyA, Mostrecent, frmr))


        hipriority= 99
        SumLength = 0.0
        fr = ''
        cntprobs = 0
        #PerSum = 0.0
        #IntSum = 0.0
        #EphSum = 0.0
        flag = 0
        Mostrecent = 0
        frmr = ''
        #if tmpObsDict[keyA]['ReserveFR'] == None:                      #tmpObsDict[keyA]['ReserveFR'] <> reservefr or
         #   tmpObsDict[keyA]['ReserveFR'] == reservefr


print "Output: ", tmpObsDict['AZ15070102-006A']

for keyA in tmpObsDict.iterkeys():
##        if keyA == 'AZ15010003-024':
##            print keyA
    if tmpObsDict[keyA]['FlowRegime'] == None or tmpObsDict[keyA]['FlowRegime'] =='':
        tmpObsDict[keyA]['FlowRegime'] = 'U'
    if tmpObsDict[keyA]['Status'] == 'Partial':
        #print keyA, tmpObsDict[keyA]
        if tmpObsDict[keyA]['SumLength']/tmpObsDict[keyA]['TotalLength']  < 0.5:
            tmpObsDict[keyA]['FlowRegime'] = 'U'
            tmpObsDict[keyA]['Status'] = 'Complete'

for keyA in tmpObsDict.iterkeys():
    if tmpObsDict[keyA]['FlowRegime'] == 'U' and tmpObsDict[keyA]['ReserveFR']!= None and tmpObsDict[keyA]['ReserveFR']!='':
        tmpObsDict[keyA]['FlowRegime'] = tmpObsDict[keyA]['ReserveFR']


##except Exception as e:
##    print("Failed to populate remainder of dictionary")
##    print(e)
##    arcpy.GetMessages(2)
##    sys.exit(0)

try:
    print "Generating subset dictionaries for log file..."
    arcpy.AddMessage("Generating subset dictionaries for log file...")
    logging.info( len(tmpObsDict))

    newdict1 = {k: val for (k, val) in tmpObsDict.items() if tmpObsDict[k]['TotalCount']<tmpObsDict[k]['CntPriority'] }
    logging.info("Printing newdict1...Records with Priority count higher than total count")
    for key, value in newdict1.iteritems():
        logging.info(key, value)
    logging.info( "Size, newdict1: {0}".format(len(newdict1)))


    newdict2 = {k: val for (k, val) in tmpObsDict.items() if tmpObsDict[k]['TotalLength']<tmpObsDict[k]['SumLength'] and tmpObsDict[k]['SumLength'] != 'N.A.' }
    logging.info("Printing newdict2...Records where SumLength is greater than total length")
    for key, value in newdict2.iteritems():
        #for item in value:
            logging.info( key, value)


    logging.info( "Size, newdict2: {0}".format(len(newdict2)))

    newdict3 = {k: val for (k, val) in tmpObsDict.items() if tmpObsDict[k]['Flag']==1 }
    logging.info("Printing newdict3...Mixed flow regime records")
    for key, value in newdict3.iteritems():
        logging.info(key, value)
    logging.info( "Size, newdict3: {0}".format(len(newdict3)))

    ##newdict4 = {k: val for (k, val) in tmpObsDict.items() if tmpObsDict[k]['Priority'] == 1 }
    ##logging.info("Printing newdict4...Wet-dry mapping reaches")
    ##for key, value in newdict4.iteritems():
    ##    logging.info(key, value)
    ##logging.info( "Size, newdict4: {0}".format(len(newdict4)))

    #newdict5 = {k: val for (k, val) in newdict3.items() if not isinstance(newdict3[k]['FlowRegime'], unicode)}
    newdict5 = {k: val for (k, val) in newdict3.items() if tmpObsDict[k]['Status']=='Complete' or tmpObsDict[k]['Status']=='Processed, Complete'}
    logging.info("Printing newdict5...processed mixed reaches")
    for key, value in newdict5.iteritems():

            logging.info(key, value)
    logging.info( "Size, newdict5: {0}".format(len(newdict5)))

    newdict6 = {k: val for (k, val) in newdict3.items() if tmpObsDict[k]['Status']!='Complete' and tmpObsDict[k]['Status']!='Processed, Complete'}
    logging.info("Printing newdict6...unprocessed mixed reaches")
    for key, value in newdict6.iteritems():

            logging.info(key, value)
    logging.info( "Size, newdict6: {0}".format(len(newdict6)))

    newdict7 = {k: val for (k, val) in tmpObsDict.items() if tmpObsDict[k]['Status']!='Partial'}
    logging.info("Printing newdict7...partial processed reaches")
    for key, value in newdict7.iteritems():

            logging.info(key, value)
    logging.info( "Size, newdict7: {0}".format(len(newdict7)))

except Exception as e:
    print("Failed to generate subset dictionaries")
    print(e)
    arcpy.GetMessages(2)
    #sys.exit(0)

print "Calculating statistics for Wet-dry mapped reaches..."
arcpy.AddMessage("Calculating statistics for Wet-dry mapped reaches...")

try:
    arcpy.MakeTableView_management(FlowObs,"vFlowObs",'\"Obs_Type\" = 10')
    arcpy.Statistics_analysis("vFlowObs",out_table,stats_fld,case_flds)
    tmpWDMpDict = defaultdict(dict)

    i=0
    print "Summarizing Wet-dry mapped statistics..."
    arcpy.AddMessage("Summarizing Wet-dry mapped statistics...")
    logging.info( "Wet-dry summary log:")
    with arcpy.da.SearchCursor(out_table,outflds) as obs_cur2:
            for row in obs_cur2:

                i+=1

                if i % 2 != 0:
                    WBID = row[0]
                    Year = row[1]
                    if row[2] == "Dry":
                        Drysum = round(row[3],4)
                    elif row[2] == "Wet":
                        Wetsum = round(row[3],4)
                else:
                    if row[2] == "Dry":
                        Drysum = round(row[3],4)
                    elif row[2] == "Wet":
                        Wetsum = round(row[3],4)
                    logging.info("WBID: {0}, Year:  {1}, Wet Sum: {2}, Dry Sum {3}, Total Length: {4}".format(WBID, Year, Wetsum, Drysum, tmpObsDict[WBID]['TotalLength']))

                    if Wetsum > Drysum and Wetsum/tmpObsDict[WBID]['TotalLength'] > 0.5:
                        pr1fr = 'P'
                    elif Drysum > Wetsum and Drysum/tmpObsDict[WBID]['TotalLength'] > 0.5:
                        pr1fr = 'I'
                    else:
                        pr1fr = 'U'

                    if WBID in tmpWDMpDict.keys():
                        if (WBID, pr1fr) in tmpWDMpDict.items():
                            pass
                        elif pr1fr == 'pI' and pr1fr != tmpWDMpDict.values:
                            tmpWDMpDict[WBID] = pr1fr
                        else:
                            pass
                    else:
                        tmpWDMpDict[WBID] = pr1fr


                    logging.info( "Final Assignment: ", tmpWDMpDict.items())
    arcpy.JoinField_management(out_table,'WBID', FlowDesg,'WBID', 'Length__Mi' )
except Exception as e:
    print("Failed to calculate, summarize Wet-dry mapped Statistics")
    print(e)
    arcpy.GetMessages(2)
    #sys.exit(0)

print "Updating master dictionary with Wet-Dry mapping attributes..."
arcpy.AddMessage("Updating master dictionary with Wet-Dry mapping attributes...")

try:
    for key, value in tmpWDMpDict.items():
        if tmpObsDict[key]['FlowRegime'] !=None and tmpObsDict[key]['Scope'] != 'RCH' and tmpObsDict[key]['Status']!='Complete':           ###Restrict W-D mapping results to reaches only where RCH scope not achieved and FR not assigned
            tmpObsDict[key]['FlowRegime'] = value
            tmpObsDict[key]['Priority'] = 2
            tmpObsDict[key]['Scope'] = u'DYNSEG'
            tmpObsDict[key]['CntPriority'] = tmpObsDict[key]['TotalCount'] - tmpObsDict[key]['CntPriority']
            tmpObsDict[key]['Status'] = "PR1 Processed, Complete"
            logging.info("{0}   {1}".format(key,tmpObsDict[key].items()))

    newdict4 = {k: val for (k, val) in tmpObsDict.items() if tmpObsDict[k]['Obs_Type'] == 10 }
    logging.info("Printing newdict4...Wet-dry mapping reaches")
    for key, value in newdict4.iteritems():
        #for item in value:
        logging.info(key, value)
    logging.info( "Size, newdict4: {0}".format(len(newdict4)))

except Exception as e:
    print("Failed to calculate, summarize Wet-Dry mapping Statistics")
    print(e)
    arcpy.GetMessages(2)
    sys.exit(0)

print "Final pass...resolving undetermined reaches where possible"
for keyA in tmpObsDict.iterkeys():
    if tmpObsDict[keyA]['FlowRegime'] == 'U' and tmpObsDict[keyA]['ReserveFR']!= None:
        tmpObsDict[keyA]['FlowRegime'] = tmpObsDict[keyA]['ReserveFR']
    #if keyA == 'AZ15050203-004C':
     #   print tmpObsDict[keyA]



print "Updating FlowRegime Designations layer..."
arcpy.AddMessage("Updating FowRegime Designations layer...")

try:
    z = 0
    PCnt = 0
    ICnt = 0
    ECnt = 0
    UCnt = 0
    with arcpy.da.UpdateCursor(FlowDesg, updateflds) as cursor:
        for row in cursor:
            for key in tmpObsDict:
                if row[0] == key:
                    if row[3] == 'T':
                        pass
                    else:

                        row[1] = tmpObsDict[key]['FlowRegime']
                        if tmpObsDict[key]['FlowRegime'] == 'P':
                            PCnt +=1
                        elif tmpObsDict[key]['FlowRegime'] == 'I':
                            ICnt +=1
                        elif tmpObsDict[key]['FlowRegime'] == 'E':
                            ECnt +=1
                        elif tmpObsDict[key]['FlowRegime'] == 'U':
                            UCnt +=1
                        if tmpObsDict[key]['Flag'] == 1:
                            if row[2] == None:
                                row[2] = "Mixed flow regime observations"
                            elif 'Mixed flow regime observations' in row[2]:
                                pass
                            else:
                                row[2] = row[2] + "; Mixed flow regime observations"
                        cursor.updateRow(row)
                        z+=1
                        logging.info( "Updated row: {0}  {1}".format(key, row[1]))
                else:
                    continue

        logging.info("Count Ps: {0}\tCount Is: {1}\tCount Es: {2}\tCount Us: {3}".format(PCnt,ICnt,ECnt,UCnt))
        logging.info( "Total updates: {0}".format(z))

	stop_time = datetime.now()
    elapsed_time = stop_time - start_time
    print("End time: " + time.asctime())
    print "Elapsed time: ", elapsed_time



except Exception as e:
    print("Failed to update Flow Regime designations")
    print(e)
    arcpy.GetMessages(2)
    sys.exit(0)

arcpy.MetadataImporter_conversion("S:\\gisdev\\dm4\\Metadata\\Copies SDC metadata\\FlowRegimes_metadata.xml", FlowObs)
arcpy.MetadataImporter_conversion("S:\\gisdev\\dm4\\Metadata\\Copies SDC metadata\\FlowRegimes_metadata.xml", FlowDesg)
arcpy.MetadataImporter_conversion("S:\\gisdev\\dm4\\Metadata\\Copies SDC metadata\\FlowRegimes_metadata.xml", FlowRegGDB)
cursor.reset()
obs_cur.reset()
obs_cur2.reset()

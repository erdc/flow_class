import geopandas as gpd
from datetime import datetime
import os
import sys


def flow_classification(*, Obs_Path,
                        Shp_Path, 
                        Obs_Layer, 
                        SHP_Layer, 
                        Unique_ID_Shp, 
                        Geometry_Column, 
                        Unique_ID_Obs, 
                        Flow_Regime_Column, 
                        Priority_Column="", 
                        SHP_Fields=[], 
                        Case=True, 
                        Perennial_Input_List=['P', 'Perennial', 'Potentially Perennial'], 
                        Intermittent_Input_List=['I', 'Intermittent', 'Potentially Intermittent'], 
                        Ephemeral_Input_List=['E', 'Ephemeral', 'Potentially Ephemeral'], 
                        At_Least_Intermittent_Input_List=['At Least Intermittent'], 
                        At_Least_Intermittent_Include=True, 
                        At_Least_Intermittent_Override=True, 
                        Weighted_Flag=True, 
                        Override_Flag=False, 
                        Output=None, 
                        Output_Columns_Weighted=True):
    """
    Determine the flow classification using a weighted approach or override approach, 
    given a shape file with WBIDs and a file with observations corresponding to the WBIDs with (at minimum) a priority and a flow regime classification
    
    :param Obs_Path: The path to the .gdb file with the layers for the observation data
    :type Obs_Path: String

    :param Shp_Path: The path to the .gdb file with the layers with the shape data
    :type Shp_Path: String
    
    :param Obs_Layer: The layer with the observations in the .gdb file. Observation file must include columns "WBID", "Priority", "Flow_Regime"
    :type Obs_Layer: String

    :param SHP_Layer: The layer with the WBID and shape data in the .gdb file
    :type SHP_Layer: String

    :param Unique_ID_Shp: The name of the column SHP_Layer which contains the unique identifer. Note: These values must match the unique identifiers in the Unique_ID_Obs column
    :type Unique_ID_Shp: String

    :param Geometry_Column: The name of the column which holds the geometry data in the SHP_Layer
    :type Geometry_Column: String

    :param Unique_ID_Obs: The name of the column in the layer which contains the unique identifer. Note: These values must match the unique identifiers in the Unique_ID_Shp column
    :type Unique_ID_Obs: String

    :param Flow_Regime_Column: The name of the column which holds the flow regime (P, I, E, etc) values data in the Obs_Layer
    :type Flow_Regime_Column: String

    :param Priority_Column: The name of the column which holds the priority values data in the Obs_Layer. If this is empty, all priorities will be set to 0. This is not suggested
    :type Priority_Column: String
    :default Priority_Column: ""

    :param SHP_Fields: The list of the fields from the SHP_Layer which should be included in the output (geometry and unique_ID is already included and does not need to be listed again)
    :type SHP_Fields: String Array
    :default SHP_Fields: []

    :param Case: Whether the flow_regime matches should be case-sensitive (True) or not (False)
    :type Case: boolean
    :default Case: True

    :param Perennial_Input_List: The list of possible values in the Flow_Regime variable which should be considered as Perennial
    :type Perennial_Input_List: String Array
    :default Perennial_Input_List: ['P', 'Perennial', 'Potentially Perennial']

    :param Intermittent_Input_List: The list of possible values in the Flow_Regime variable which should be considered as Intermittent
    :type Intermittent_Input_List: String Array
    :default Intermittent_Input_List: ['I', 'Intermittent', 'Potentially Intermittent']

    :param Ephemeral_Input_List: The list of possible values in the Flow_Regime variable which should be considered as Ephemeral
    :type Ephemeral_Input_List: String Array
    :default Ephemeral_Input_List: ['E', 'Ephemeral', 'Potentially Ephemeral']

    :param At_Least_Intermittent_Input_List: The list of possible values in the Flow_Regime variable which should be considered as At Least Intermittent
    :type At_Least_Intermittent_Input_List: String Array
    :default At_Least_Intermittent_Input_List: ['At Least Intermittent']

    :param At_Least_Intermittent_Include: Whether 'At Least Intermittent' values should be added as an Intermittent classification. 
    :type At_Least_Intermittent_Flag: boolean
    :default At_Least_Intermittent_Flag: True

    :param At_Least_Intermittent_Override: Whether 'At Least Intermittent' values should be used to immediately override an ephemeral classification (True) or not (False). If both 'At_Least_Intermittent_Include' and At_Least_Intermittent_Override' are set to false, 'At Least Intermittent' observations are completely ignored.
    :type At_Least_Intermittent_Flag: boolean
    :default At_Least_Intermittent_Flag: False

    :param Weighted_Flag: Whether the Weighted Approach should be used (True) or not (False). This will create a column labelled 'Class_Wt' in the output and can be used in collaboration with an Override Approach
    :type Override_Flag: boolean
    :default Override_Flag: True

    :param Override_Flag: Whether the Override Approach should be used (True) or not (False). This will create a column labelled 'Class_OR' in the output and can be used in collaboration with an Weighted Approach
    :type Override_Flag: boolean
    :default Override_Flag: True

    :param Output: The name/location of the output file.
    :type Output: String 
    :default Output: None (if specified to None, the output will be a .shp file labelled Flow_Classification_Output_{Date}.shp)

    :param Output_Columns_Weighted: Whether the output file should have the columns with the sum of weights for each classification (P,I,E) (True) or not (False)
    :type Output_Columns_Weighted: boolean
    :default Output_Columns_Weighted: True

    :output: A shape file (by default, unless otherwise specified), and a csv file are created with the WBID, shape data, 
    and a classificiation of I, P, or E under the category "Class_wt" (if weighted approach was used) or 
    "Class_OR" (if the override approach was used)
    """
    print("Started..")

    #Raise exception if both flags are set to false (this means that no flow classification will be returned)
    if(Weighted_Flag==False and Override_Flag==False):
        raise Exception("Error 1.1: Weighted_Flag and Override_Flag connot both be set to False")

    # Read the observation file, Select the necessary fields, and Identify the Unique_ID
    if(Priority_Column==""):
        Obs_layer_IDS=[Unique_ID_Obs, Flow_Regime_Column]
    else:
        Obs_layer_IDS=[Unique_ID_Obs, Priority_Column, Flow_Regime_Column]
    try:
        FlowObs_gdf = gpd.read_file(Obs_Path, layer=Obs_Layer)
    except: 
        print("The observation layer was not found in the GDB document") 
        sys.exit("Error 1.2: Please correct observation layer or GBD path")
    try:
        FlowObs_gdf = FlowObs_gdf[Obs_layer_IDS]
    except:
        print("Unique_ID_Obs, Priority_Column and/or Flow_Regime_Column are not in observation layer") 
        sys.exit("Error 1.3: Please correct observation layer column names")
    FlowObs_WBID_list = FlowObs_gdf[Unique_ID_Obs].to_list()

    # Read the shape file
    try:
        FlowDesg_gdf = gpd.read_file(Shp_Path, layer=SHP_Layer)
    except:
        print("The shape layer was not found in the GDB document") 
        sys.exit("Error 1.4: Please correct shape layer")       

    #Cleaning- Remove any NA unique identifiers
    obs_none_count=FlowObs_gdf[Unique_ID_Obs].isna().sum() #determine how many missing WBID cells there are in observation file
    FlowObs_gdf = FlowObs_gdf.dropna(subset=[Unique_ID_Obs]) #remove rows with missing WBID
    FlowObs_gdf[Unique_ID_Obs] = [str(x).strip() for x in FlowObs_gdf[Unique_ID_Obs]] #remove spaces
    print("Removed", obs_none_count, "rows with missing Unique ID from the observation file.")

    desg_none_count=FlowDesg_gdf[Unique_ID_Shp].isna().sum() #determine how many missing WBID cells there are in .shp file
    FlowDesg_gdf = FlowDesg_gdf.dropna(subset=[Unique_ID_Shp]) #remove rows with missing WBID
    FlowDesg_gdf[Unique_ID_Shp] = [str(x).strip() for x in FlowDesg_gdf[Unique_ID_Shp]] #remove spaces
    print("Removed", desg_none_count, "rows with missing Unique ID from the shape file.")

    # remove fields in flowline gdf (shape layer) that have no observations in the observation file
    FlowDesg_filtered_gdf = FlowDesg_gdf[FlowDesg_gdf[Unique_ID_Shp].isin(FlowObs_WBID_list)]
    if(FlowDesg_filtered_gdf.empty==True):
        raise Exception("Error 1.5: There are no matches between the Unique ID for the Obs layer and the Unique ID for the shape layer")

    # Create a new file (FlowDesg_value) which will document the output. Add the desired columns as specified in SHP_Fields
    All_SHP_Fields=[Unique_ID_Shp, Geometry_Column]

    for i in SHP_Fields:
        All_SHP_Fields.append(i)
    try:
        FlowDesg_values=FlowDesg_filtered_gdf.loc[:,All_SHP_Fields]
    except:
        print("Unique_ID_Shp, Geometry_Column and/or a column name in SHP_Fields are not in shape layer") 
        sys.exit("Error 1.6: Please correct observation layer column names")
    FlowDesg_values=FlowDesg_values.reset_index()

    #If Case=False, the list will not be case-sensitive
    if Case==False: #change everything to lower if not case-sensitive
        Perennial_Input_List=[x.lower() for x in Perennial_Input_List]
        Intermittent_Input_List=[x.lower() for x in Intermittent_Input_List]
        Ephemeral_Input_List=[x.lower() for x in Ephemeral_Input_List]
        At_Least_Intermittent_Input_List=[x.lower() for x in At_Least_Intermittent_Input_List]
    
    
    # Create columns for the different cateogires of classification
    FlowDesg_values['P']=0 #Sum of priorities
    FlowDesg_values['I']=0 #Sum of priorities
    FlowDesg_values['E']=0 #Sum of priorities
    FlowDesg_values['Unknown']=0 #Count of unknowns
    FlowDesg_values['ALI']=0 #Sum of priorities

    # 1- For each observation in the observation file, 
    # 2- identify the index of the row in the values file which has the same unique ID
    # 3- If there is a corresponding row, continue
    # 4- Based on the flow_regime (which identifies the classification) add the priority value to the 
    # 5- corresponding classification category in the values file
    # 6- If the 'At_Least_Intermittent_Include' variable is set to true, 
    # 7- add any 'At least intermittent' observations to the 'intermittent' category
    # 8- If the 'At_Least_Intermittent_Override' variable is set to true, 
    # 9- set the 'ALI' to 1 when there are 'at least intermittent' observations
    # 10- If the flow_regime is unknown, it will be included as a count rather than the sum of priorities
    print("Begin Assessing Flow Regimes..")
    for i in FlowObs_gdf.index: #1
        row=FlowDesg_values.loc[FlowDesg_values[Unique_ID_Shp] == FlowObs_gdf.loc[i,Unique_ID_Obs]] #2
        if(len(row)!=0): #3
            obs=FlowObs_gdf.loc[i,Flow_Regime_Column]
            if (Case==False and isinstance(obs, str)):
                obs=obs.lower()
            j=row.index[0]
            try:
                if(Priority_Column==""):
                    value=1
                else:
                    value=int(FlowObs_gdf.loc[i, Priority_Column])
            except:
                print("The priority column data for row", i, "is not acceptable") 
                sys.exit("Error 2.1: Please edit data to be an integer")    
            if obs in Perennial_Input_List: #4-5
                FlowDesg_values.loc[j,'P']+= value
            elif (obs in Intermittent_Input_List): #4-5
                FlowDesg_values.loc[j,'I']+= value
            elif obs in Ephemeral_Input_List: #4-5
                FlowDesg_values.loc[j,'E']+= value
            elif obs in At_Least_Intermittent_Input_List:
                if(At_Least_Intermittent_Include==True):  #6-7
                    FlowDesg_values.loc[j,'I']+= value
                if(At_Least_Intermittent_Override==True): #8-9
                    FlowDesg_values.loc[j,'ALI']= 1
            else:  #10
                FlowDesg_values.loc[j,'Unknown']+= 1
            

    print("Begin Documenting Flow Regimes..")   
    if(Weighted_Flag==True):
        # weighted approach- Determine the classification based on the max value
        # if equal values, default to higher classification (P>I>E)
        # if all are 0, return a U
        FlowDesg_values['Class_Wt']=None #Sum
        for i,m in enumerate(FlowDesg_values[Unique_ID_Shp]):
            Pval=FlowDesg_values.loc[i, 'P']
            Ival=FlowDesg_values.loc[i, 'I']
            Eval=FlowDesg_values.loc[i, 'E']
            ALIval=FlowDesg_values.loc[i, 'ALI']

            #If P values are the greatest, set classification to P
            if(Pval>=Ival and Pval >=Eval and Pval !=0): 
                FlowDesg_values.loc[i,'Class_Wt']='P'
            #If I values are greater than E, set classification to I
            #If ALIVal is 1, then the Override option for the 'At Least Intermittent' is true and there was an override-set classification to I
            elif(Ival>=Eval and Ival !=0 or ALIval==1):
                FlowDesg_values.loc[i,'Class_Wt']='I'
            #If E vals are not 0, set classification to E
            elif(Eval !=0):
                FlowDesg_values.loc[i,'Class_Wt']='E'
            #If all were 0, set classification to U
            else:
                FlowDesg_values.loc[i,'Class_Wt']='U'
    
    if(Override_Flag==True):
        # override approach- Determine the classification based on the 
        # highest classification which isn't 0 (P>I>E)
        # if all are 0, return a U
        FlowDesg_values['Class_OR']=None #Sum
        for i,m in enumerate(FlowDesg_values[Unique_ID_Shp]):
            Pval=FlowDesg_values.loc[i, 'P']
            Ival=FlowDesg_values.loc[i, 'I']
            Eval=FlowDesg_values.loc[i, 'E']
            ALIval=FlowDesg_values.loc[i, 'ALI']
            if(Pval!=0):
                FlowDesg_values.loc[i,'Class_OR']='P'
            elif(Ival!=0 or ALIval!=0):
                FlowDesg_values.loc[i,'Class_OR']='I'
            elif(Eval!=0):
                FlowDesg_values.loc[i,'Class_OR']='E'
            else:
                FlowDesg_values.loc[i,'Class_OR']='U'

    path = "Output"
    #print(os.getcwd())

    #If Output_Columns_Weighted is false, then the output should not have individual summations
    if(Output_Columns_Weighted==False):
        listofcolumns=["P","I","E","Unknown","ALI"]
        FlowDesg_values= FlowDesg_values.drop(listofcolumns, axis=1)

    # Check if the path exists
    if not os.path.exists(path):
        os.makedirs(path)

    print("Finished. Saving output..")
    #Return an Output Shape File with the date if output is not specified, return the output file if it is specified
    if(Output==None):
        current_date = datetime.now().strftime("%Y-%m-%d")
        #FlowDesg_values.to_excel(f'Flow_Classification_Output_{current_date}.xlsx', index=False)
        FlowDesg_values.to_csv(f'Output\Flow_Classification_Output_{current_date}.txt', index=False)
        FlowDesg_values.to_file(f'Output\Flow_Classification_Output__{current_date}.shp', index=False)
    else:
        try:
            FlowDesg_values.to_file(Output, index=False)
        except:
            print("Output file designation is not acceptable. Output file must be a supported geopandas file")
        #FlowDesg_values.to_excel(Output, index=False)
    return FlowDesg_values
    

    



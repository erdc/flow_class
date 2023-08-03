# FlowClass: Flow Classification Code
## Description
This code takes an input shape file and an observation file which have unique identifiers which match in both files. Additionally, the shape file must have associated geometry. The observation file must include a priority for each observation and a flow regime for each observation. The flow regime can have a variety of names, but will ultimately be divided into perennial, intermittent, or ephemeral. An 'at least intermittent' observation type is also supported, and the user has several options how to handle these observation types. The code returns and saves a file which assigns a flow classification of perennial, intermittent, or ephemeral (or unknown) to each flow line based on the observations and their weights.

## Background and Use
Flows are typically classified into ephemeral (flow only during preciptation events), intermittent (flow seasonally), and perennial (flow year-round). The code allows for two approaches to classifying streams- a Weighted Approach and an Override Approach.

Each observation must have a unique identifier, a priority, and a flow regime. The priorities can be set based on the reliability and effectivenesses of the different observations and observation types. The flow regime can be set to different values (for example, 'perennial', 'possibly perennial', etc), however, these will ultimately need to be classified into one of three main classification- ephemeral, intermittent, perennial (E, I, or P). 

The Weighted Approach sums the priorities of each observation for a given WBID, then selects the classification based on the highest sum. For example, if a certain flow has three observations- a priority 9 labelled as perennial, a priority 7 labelled as intermittent, and a priority 5 labelled as intermittent, then the sum of intermittent priorities would be 13 and the sum of perennial priorities would be 9. Therefore, intermittent would be selected as this has the highest sum.

The Override Approach assigns the classification as the highest flow regime observation (where perennial>intermittent>ephemeral). For example, if a certain flow has three observations- a priority 9 labelled as perennial, a priority 7 labelled as intermittent, and a priority 5 labelled as intermittent, then the highest classification would be perennial. Therefore, perennial would be selected. This approach ignores priority/weights.

An 'At Least Intermittent' observation type is also supported. The user has two choices of how to handle these. First, the user can decide if they want to include these observations as Intermittent observations (At_Least_Intermittent_Include). The system defaults to including these. In addition to this choice, the user can also decide if these observations should immediately override an ephemeral observation (At_Least_Intermittent_Flag). The will default to not immediately overriding. If the run is set to the Override Approach and the At_Least_Intermittent_Include is set to true, this choice will automatically be True, even if manually set to False. If both choices are set to false, 'At Least Intermittent' observations are ignored. This is not suggested. 

## Download, Install, Test, and Run
### Download:
HTTPS: ``` $ git clone https://github.com/erdc/flow_class.git ```

SSH: ``` $ git clone git@github.com:erdc/flow_class.git ```

### Install:
When the working directory is set to the clone of the package from above, the following commands can be used to save the code as a package.

* For General Use: ``` $ pip install . ```
* For Editting: ``` $ pip install -e . ```

### Test:
To test the function, from the 'flow_class' file folder, run 

``` $ py tests\test_flowclass.py ```

### Run:
To use the function, edit the document 'flow_class_workflow.py' on the top lines which are commented '#EDIT REQUIRED' and run it:

``` $ py flow_class_workflow.py ```

## Install as a Package
To install the package for general use, run pip install 

```$ git+https://github.com/erdc/flow_class.git ```

## Dependencies
The following packages are required for use:
* geopandas
* datetime
* os
* pandas (for testing)
* unittest (for testing)

## Flow_Classification Method

The flow_classification has many inputs, but only eight are required. All inputs must be labelled in the call.

Required:
* **Obs_Path**: (String) The path to the .gdb file with the layer for the observation data. Note that an r must be placed in front of the String path if using a Windows

* **Obs_Path**: (String) The path to the .gdb file with the layers for flowline/shape data. Note that an r must be placed in front of the String path if using a Windows
    
* **Obs_Layer**: (String) The layer with the observations in the .gdb file. 

* **SHP_Layer**: (String) The layer with the WBID and shape data in the .gdb file

* **Unique_ID_Shp**: (String) The name of the column SHP_Layer which contains the unique identifer. Note: These values must match the unique identifiers in the Unique_ID_Obs column

* **Geometry_Column**: (String) The name of the column which holds the geometry data in the SHP_Layer

* **Unique_ID_Obs**: (String) The name of the column in the layer which contains the unique identifer. Note: These values must match the unique identifiers in the Unique_ID_Shp column

* **Flow_Regime_Column**: (String) The name of the column which holds the flow regime (P, I, E, etc) values data in the Obs_Layer

Highly Recommended:

* **Priority_Column**: (String) The name of the column which holds the priority values data in the Obs_Layer. If it is left blank, all priorities will be set to 1.

    Default: ""

Optional:
* **SHP_Fields**: (String Array) The list of the fields from the SHP_Layer which should be included in the output (geometry and unique_ID is already included and does not need to be listed again)

    Default: []

* **Case**: (boolean) Whether the flow_regime matches should be case-sensitive (True) or not (False)
    
    Default: True

* **Perennial_Input_List**: (array of Strings) The list of possible values in the Flow_Regime variable which should be considered as Perennial
    
    Default: ['P', 'Perennial', 'Potentially Perennial']

* **Intermittent_Input_List**: (array of Strings) The list of possible values in the Flow_Regime variable which should be considered as Intermittent
    
    Default: ['I', 'Intermittent', 'Potentially Intermittent']

* **Ephemeral_Input_List**: (array of Strings) The list of possible values in the Flow_Regime variable which should be considered as Ephemeral

    Default: ['E', 'Ephemeral', 'Potentially Ephemeral']

* **At_Least_Intermittent_Input_List**: (array of Strings) The list of possible values in the Flow_Regime variable which should be considered as At Least Intermittent
    
    Default: ['At Least Intermittent']

* **At_Least_Intermittent_Include**: (boolean) Whether 'At Least Intermittent' values should be added as an Intermittent classification. 

    Default: True

* **At_Least_Intermittent_Override**: (boolean) Whether 'At Least Intermittent' values should be used to immediately override an ephemeral classification (True) or not (False). If both 'At_Least_Intermittent_Include' and At_Least_Intermittent_Override' are set to false, 'At Least Intermittent' observations are completely ignored.

    Default: False

* **Weighted_Flag**: (boolean) Whether the weighted approach should be used (True) or not (False). This will create a column labelled 'Class_Wt' in the output and can be used in collaboration with an Override Approach

    Default: True

* **Override_Flag**: (boolean) Whether the override approach should be used (True) or not (False). This will create a column labelled 'Class_OR' in the output and can be used in collaboration with an Weighted Approach

    Default: False

* **Output**: (String) The name/location of the output file.

    Default: None (if specified to None, the output will be a .shp file labelled Flow_Classification_Output_{Date}.shp)

* **Output_Columns_Weighted**: (boolean) Whether the output file should have the columns with the sum of weights for each classification (P,I,E) (True) or not (False)

    Deafult: True

## Flow Classification Example:

```
from flow_class import flow_classification

def main()
    flow_classification.flow_classification(Obs_Path=r"Flow Regime CLassifications\Flow_Regimes.gdb",
                                            Shp_Path=r"Flow Regime CLassifications\Flow_Regimes.gdb", 
                                            Obs_Layer="FlowRegime_Observations", 
                                            SHP_Layer="WBID_FlwRgme_Designations",  
                                            Unique_ID_Shp="WBID", 
                                            Geometry_Column='geometry', 
                                            Unique_ID_Obs="WBID", 
                                            Priority_Column="Priority", 
                                            Flow_Regime_Column="Flow_Regime", 
                                            SHP_Fields=["Length_Mile"], 
                                            Weighted_Flag=False, 
                                            Override_Flag=True)

if __name__ =="__main__":
    main()
```

## Disclaimer:
Description: A software that uses a weight-of-evidence approach to assign a flow regime classification to streams.

Disclaimer: The authors and creators of the Flow Regime Algorithm V1 are Water Quality Division staff at the Arizona Department of Environmental Quality (ADEQ) in Phoenix, AZ. The Flow Regime Algorithm V1 was used from 2020 to 2022 to assign flow regimes to surface waters in Arizona. In 2023, ADEQ utilized the principles of the Flow Regime Algorithm V1, along with the best available credible science, to develop an updated process for assigning flow regime to Arizona waters. Flow regime is not static and can change based on environmental conditions and new data or information. ADEQ cannot ensure the results of the Flow Regime Algorithm V1 are accurate, current or complete. For more information and the most recent information on flow regimes for Arizona waters, email WOTUS@azdeq.gov. 



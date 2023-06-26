# FlowClass: Flow Classification Code
## Description
This code takes an input shape file which has associated 'WBID' values and an observation file which has 'WBID' values, a priority for each obersation, and a flow regime for each observation. The flow regime can have a variety of names, but will ultimately be divided into perennial, intermittent, or ephemeral. An 'at least intermittent' observation type is also supported, and the user has several options how to handle these observation types.

## Background
Flows are typically classified into ephemeral (flow only during preciptation events), intermittent (flow seasonally), and perennial (flow year-round). The code allows for two approaches to classifying streams- a Weighted Approach and an Override Approach.

Each observation must have a 'WBID' value, a priority, and a flow regime. The priorities can be set based on the reliability and effectivenesses of the different observations and observation types. The flow regime can be set to different values (for example, 'perennial', 'possibly perennial', etc), however, these will ultimately need to be classified into one of three main classification- ephemeral, intermittent, perennial (E, I, or P). 

The weighted approach sums the priorities of each observation for a given WBID, then selects the classification based on the highest sum. For example, if a certain flow has three observations- a priority 9 labelled as perennial, a priority 7 labelled as intermittent, and a priority 5 labelled as intermittent, then the sum of intermittent priorities would be 13 and the sum of perennial priorities would be 9. Therefore, intermittent would be selected as this has the highest sum.

The override approach assigns the classification as the highest flow regime observation (where perennial>intermittent>ephemeral). For example, if a certain flow has three observations- a priority 9 labelled as perennial, a priority 7 labelled as intermittent, and a priority 5 labelled as intermittent, then the highest classification would be perennial. Therefore, perennial would be selected. This approach ignores priority and weights.

## Download, Install, and Tests for Editting
### Download:
HTTPS: ``` $ git clone https://github.com/meg8mhs2/flow_class.git ```

SSH: ``` $ git clone git@github.com:meg8mhs2/flow_class.git ```

### Install:
When the working directory is set to the clone of the package from above, the following command can be used to save the code as a package and run it. This also allows for the tests to be run.

``` $ pip install -e . ```

### Test:
To test the function, from the 'flow_class' file folder, run 

``` $ py tests\test_flowclass.py ```

## Install for General Use
To install the function for general use, run pip install 

```$ git+https://github.com/meg8mhs2/flow_class.git ```

## Dependencies
The following packages are required for use:
* geopandas
* datetime
* os
* pandas (for testing)
* unittest (for testing)

## Flow_Classification Method

The flow_classification has many inputs, but only four are required. All inputs must be labelled in the call.

Required:
* **GDB_Path**: (String) The path to the .gdb file with the layers for the observation and WBID values paired with the shape data
    
* **Obs_Layer**: (String) The layer with the observations in the .gdb file. Observation file must include columns "WBID", "Priority", "Flow_Regime"

* **SHP_Layer**: (String) The layer with the WBID and shape data in the .gdb file

Optional:
* **SHP_Fields**: (array of Strings) The list of the fields from the shape file which should be included in the output. At minimum, the default fields are required.

    Default: ["WBID", "geometry"]

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

* **Override_Flag**: (boolean) Whether the weighted approach (False) or override approach (True) should be used

    Default: False

* **Output**: (String) The name/location of the output file.

    Default: None (if specified to None, the output will be a .shp file labelled Flow_Classification_Output_{Date}.shp)

## Flow Classification Example:

```
from flow_class import flow_classification

def main()
    flow_classification.flow_classification(GDB="Flow Regime CLassifications\Flow_Regimes.gdb", Obs_Layer="FlowRegime_Observations", SHP_Layer="WBID_FlwRgme_Designations", Override_Flag=True)

if __name__ =="__main__":
    main()
```
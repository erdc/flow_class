from flow_class import flow_classification

def main():
    flow_classification.flow_classification(GDB_Path=r"C:\Users\megij\Documents\ERDC 23\ADEQ_FlowRegimes\Flow_Regimes.gdb",   #EDIT REQUIRED 
                                            Obs_Layer="FlowRegime_Observations",                        #EDIT REQUIRED 
                                            SHP_Layer="WBID_FlwRgme_Designations",                      #EDIT REQUIRED   
                                            Unique_ID_Shp="WBID",                                       #EDIT REQUIRED 
                                            Geometry_Column='geometry',                                 #EDIT REQUIRED 
                                            Unique_ID_Obs="WBID",                                       #EDIT REQUIRED 
                                            Priority_Column="Priority",                                 #EDIT REQUIRED 
                                            Flow_Regime_Column="Flow_Regime",                           #EDIT REQUIRED 
                                            #Edits Below are optional
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
                                            Output_Columns_Weighted=True)

if __name__ =="__main__":
    main()
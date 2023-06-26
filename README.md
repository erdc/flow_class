# FlowClass: Flow Classification Code
## Description
This code takes an input shape file which has associated 'WBID' values and an observation file which has 'WBID' values, a priority for each obersation, and a flow regime for each observation. The flow regime can have a variety of names, but will ultimately be divided into perennial, intermittent, or ephemeral. An 'at least intermittent' observation type is also supported, and the user has several options how to handle these observation types.

## Background
Flows are typically classified into ephemeral (flow only during preciptation events), intermittent (flow seasonally), and perennial (flow year-round). The code allows for two approaches to classifying streams- a Weighted Approach and an Override Approach.

Each observation must have a 'WBID' value, a priority, and a flow regime. The priorities can be set based on the reliability and effectivenesses of the different observations and observation types. The flow regime can be set to different values (for example, 'perennial', 'possibly perennial', etc), however, these will ultimately need to be classified into one of three main classification- ephemeral, intermittent, perennial (E, I, or P). 

The weighted approach sums the priorities of each observation for a given WBID, then selects the classification based on the highest sum. For example, if a certain flow has three observations- a priority 9 labelled as perennial, a priority 7 labelled as intermittent, and a priority 5 labelled as intermittent, then the sum of intermittent priorities would be 13 and the sum of perennial priorities would be 9. Therefore, intermittent would be selected as this has the highest sum.

The override approach assigns the classification as the highest flow regime observation (where perennial>intermittent>ephemeral). For example, if a certain flow has three observations- a priority 9 labelled as perennial, a priority 7 labelled as intermittent, and a priority 5 labelled as intermittent, then the highest classification would be perennial. Therefore, perennial would be selected. This approach ignores priority and weights.

## Download & Usage





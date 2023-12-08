from func_timeout import FunctionTimedOut, func_set_timeout
import xfoil_module

currentNACA = "0000" #Stores the current NACAXXXX airfoil the program is on

NACAlist = []
takeoffCL = []
maxCL = []

#Increments NACA number in 5s
def nextNACA(currentNACA):
    maxposincrease = False
    maxcamberincrease = False
    thickness = currentNACA[2:]
    maxpos = currentNACA[1:2]
    maxcamber = currentNACA[:1]
    if thickness == "40":
        maxposincrease = True
        thickness = "05"
    elif thickness != "40":
        thickness = int(thickness)+5
        if thickness < 10:
            thickness = "0"+str(thickness)
    if maxposincrease:
        if maxpos == "9":
            maxcamberincrease = True
            maxpos = "0"
        else:
            maxpos = int(maxpos)+1
    if maxcamberincrease:
        if maxcamber[:1] == "9":
            maxcamber = "0"
        else:
            maxcamber = int(maxcamber)+1
    return str(maxcamber)+str(maxpos)+str(thickness)

#Passes parameters to Xfoil to calculate, times out after 10 seconds to avoid program hang
@func_set_timeout(10)
def xfoilprocess(currentNACA, j):
    return xfoil_module.find_coefficients(airfoil=("naca"+currentNACA), alpha=j, Reynolds=25000, iteration=500).get("CL") #CL for AOA of j

#Returns the CLmax from the list of CLs for each AOA.
#This is needed because sometimes the max CL in a list is the last index that isnt None, in case Xfoil has failed for whatever reason
def getCLmax(AOAvsCL):
    CLmax = max([item for item in AOAvsCL if item is not None])
    if ((CLmax != AOAvsCL[-1]) and (AOAvsCL[AOAvsCL.index(CLmax)+1]) != None):
        return CLmax

for i in range(0, 3159): #Iterates through 3159 possible 4 digit NACA airfoils
    currentNACA = nextNACA(currentNACA)
    print("Calculating NACA"+currentNACA+"...")
    AOAvsCL = [] #Index corresponds to AOA
    for j in range(0, 40): # Iterates through 40 degrees of AOA
        try:
            currentCL = xfoilprocess(currentNACA, j)
        except FunctionTimedOut: #Sets result to None if Xfoil times out
            currentCL = None
        AOAvsCL.append(currentCL)
        del currentCL #Deletes Xfoil process to save memory
    print("---------------------------------------------------------------------------------------------------------------------------------------------")
    print("Index corresponds to AOA (degrees, zero based)")
    print("CL =", AOAvsCL)
    if AOAvsCL[7] == None or getCLmax(AOAvsCL) == None:
        print("NACA"+currentNACA, "has failed and will be omitted from the final result")
    else:
        NACAlist.append(currentNACA)
        print("Takeoff CL:", AOAvsCL[7])
        takeoffCL.append(AOAvsCL[7])
        print("CLmax:", getCLmax(AOAvsCL))
        maxCL.append(getCLmax(AOAvsCL))
        print("Highest Takeoff CL so far:", NACAlist[takeoffCL.index(max(takeoffCL))], "with Takeoff CL", max(takeoffCL))
        print("NACA"+currentNACA, "has succeeded and will be included in the final result")
    print("---------------------------------------------------------------------------------------------------------------------------------------------")
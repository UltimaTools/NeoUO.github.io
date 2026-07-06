from AutoComplete import *
import time
import math
import sys   
#
from System.Collections.Generic import List
from System import Byte, Int32
#
#
import System
HatchetID = 0x0F43
HatchetID = 0x0F49 # LoS server
HatchetColor = 0x0973

####
def FindPackanimal():
    pack_animal = None
    findPack = Mobiles.Filter()
    findPack.Enabled = True
    findPack.RangeMax = 2
    findPack.Bodies = List[Int32]((0x011C, 0x0123, 0x0319))
    listPack = Mobiles.ApplyFilter(findPack)
    if len(listPack) > 0:
        for i in listPack:
            pack_animal = listPack[0]
            Misc.SendMessage("Pack is 0x{:x}".format(pack_animal.Serial))
    else:
        Misc.SendMessage("NO PACK ANIMAL")
        pack_animal = None
    return pack_animal 
#
PackAnimal = FindPackanimal()
####
#
#
def MoveWoodToPack():
    # Move to PackAnimal
    if not PackAnimal:
        return
    woodID = 0x1BD7
    wood = Items.FindByID(woodID, -1, Player.Backpack.Serial) 
    prev_wood = 0  
    max_tries = 10 
    while wood != None:
        #Misc.SendMessage("{} 0x{:x} - 0x{:x}".format(wood.Name, prev_wood, wood.Serial), 5)
        prev_wood = wood.Serial
        if Player.DistanceTo(PackAnimal) > 1:
                Misc.Pause(2000)
        Items.Move(wood.Serial, PackAnimal, 0)
        Misc.Pause(1000)
        test = Items.FindBySerial(wood.Serial)
        if test != None:
            Misc.SendMessage("UNABLE TO MOVE WOOD", 6)
            #break
        wood = Items.FindByID(woodID, -1, Player.Backpack.Serial)
        max_tries = max_tries - 1
        if max_tries <= 0:
            break
#
def FindAxe():
    axe = Items.FindByID(HatchetID, HatchetColor, Player.Backpack.Serial, -1)
    # if one in pack use it
    if axe:
        return axe
    Misc.SendMessage("No Hatchet found to chop wood with", 32)
    Player.HeadMessage(32, "No Hatchet found to chop wood with")
    sys.exit(4)        
#
def CheckTreeFinished(tree):
    if Misc.CheckSharedValue("StaticTrees"):
        return Journal.Search("not enough wood here")
    else:    
        check_tree = Items.FindBySerial(tree.Serial)
        if check_tree == None:
            return True
        else:
            return False
#
def ConvertLogsToWood():
    axe = FindAxe()
    if not axe:
        Misc.SendMessage("Unable to Find suitable Axe")
        Stop()
    logID = 0x1BDD
    log = Items.FindByID(logID, -1, Player.Backpack.Serial, -1) 
    prev_log = 0  
    max_tries = 10 
    while log != None:
        #Misc.SendMessage("{} 0x{:x} - 0x{:x}".format(wood.Name, prev_wood, wood.Serial), 5)
        prev_log = log.Serial
        Items.UseItem(axe)
        Target.WaitForTarget(5000, False)
        #Misc.SendMessage("0x{:x}".format(log.Serial), 5)
        Target.TargetExecute(log)
        Misc.Pause(1000)
        log = Items.FindByID(logID, -1, Player.Backpack.Serial)
#   
#    
#
ConvertLogsToWood()
MoveWoodToPack()

wait_secs = 0
wood_to_chop = True
Journal.Clear()               
while wood_to_chop:
    Misc.Pause(1000)
    failed_chop_time = time.time() + 6
    axe = FindAxe()
    Target.TargetResource(axe.Serial, "wood")
    if Journal.Search("not enough wood here"):
        Misc.SendMessage("Stopping due to finished")
        wood_to_chop = False
    if Journal.Search("You put") or Journal.Search("You put"):
        failed_chop_time = time.time() + 6
    if Journal.Search("no more wood"):
        Misc.SendMessage("Stopping due to Journal")
        wood_to_chop = False
    if Player.Weight > Player.MaxWeight * .95:
        ConvertLogsToWood()
        if Player.Weight > Player.MaxWeight * .95:
            Misc.SendMessage("Stopping due to Player Weight")
            wood_to_chop = False
    if Journal.Search("far away"):
        Misc.SendMessage("Stopping due to Unreachable")
        #Misc.IgnoreObject(tree)
        wood_to_chop = False
    if Journal.Search("lack the skill"):
        Misc.SendMessage("Stopping due to lack of skill")
        #Misc.IgnoreObject(tree)
        wood_to_chop = False    
    if Journal.Search("cannot be seen"):
        Misc.SendMessage("Stopping due to lack of visibility")
        #Misc.IgnoreObject(tree)
        wood_to_chop = False  
    if Journal.Search("can't use an axe"):
        Misc.SendMessage("Stopping due to invalid target")
        #Misc.IgnoreObject(tree)
        wood_to_chop = False                     
    if Journal.Search("You broke your axe"):
        axe = FindAxe()
        if axe:
            failed_chop_time = time.time() + 6
            wood_to_chop = True
        else:
            Misc.SendMessage("Cannot find a new axe")
            wood_to_chop = False
    if failed_chop_time <= time.time():
        Misc.SendMessage("Stopping due to Time-out")
        #Misc.IgnoreObject(tree)
        wood_to_chop = False       
    if Player.Weight > (Player.MaxWeight * .9):
        ConvertLogsToWood()
        MoveWoodToPack()                    

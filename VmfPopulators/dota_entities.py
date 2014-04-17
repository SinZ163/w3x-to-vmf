class VmfPop:
    def __init__(self, base):
        self.base = base
            
    def populate_vmf(self, w3iFile):
    
        id = 1;
       
        playerSpawns = w3iFile.info["playerData"]
        #Work out the average spawn, for the player start
        startX = 0
        startY = 0
        for i in xrange(playerSpawns["count"]):
            startX = startX + playerSpawns["data"][i]["startX"]
            startY = startY + playerSpawns["data"][i]["startY"]
        
        startX = startX / playerSpawns["count"]
        startY = startY / playerSpawns["count"]
        

        entityText = open("VmfPopulators/template/info_player_start.txt").format(ID=id,A0=0,A1=0,A2=0,X=startX,Y=startY,Z=0,type="")
        id = id + 1
        
        #For convenience lets assume player 1 is goodguys, and player 2 is badguys
        #anyone using this map can fix it themselves the lazy bugger
        
        goodX = playerSpawns["data"][0]["startX"]
        goodY = playerSpawns["data"][0]["startY"]
                
        goodText = open("VmfPopulators/template/info_player_start.txt").format(ID=id, A0=0,A1=0,A2=0,X=goodX,Y=goodY,Z=0,type="_goodguys")
        id = id + 1
        
                
        badX = playerSpawns["data"][1]["startX"]
        badY = playerSpawns["data"][1]["startY"]
        
        badText = open("VmfPopulators/template/info_player_start.txt").format(ID=id, A0=0,A1=0,A2=0,X=badX,Y=badY,type="_badguys")
        id = id + 1
        
        #Now for the ent_dota_lightinfo
        
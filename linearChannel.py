"""linearChannel.py: LinearChannel class which represent the data of a linear channel including the relevant information of its programs"""

import sys

__author__      = "Ana Hernandez ana.hernandez@vodafone.com"


import datetime

class LinearChannel(object):
  

    def __init__(self, json_channel_data):
        self.parseChannel(json_channel_data)
        self.endOffset=0
        self.startOffset=0
        self.numPrograms=0
        self.totalImagesReferences=0
        self.average_event_size=0
        
    
    #Receives a JSON with the channel metadata, parses it and creates a LinearChannel object
    def parseChannel(self, channel):
        
        self.name=channel["MediaName"]
        #get the Tags
        self.tags= channel["Tags"]
        self.parseTags(self.tags)
        #get the Metas
        self.metas = channel["Metas"]
        self.parseMetas(self.metas)
        #get the files
        self.files = channel["Files"]
        self.parseFiles(self.files)
        #get the Pictures
        self.pictures = channel["Pictures"]
        self.parseChannelPictures(self.pictures)
    
    #Parses the TAGS from the Media Json    
    def parseTags(self,tags):
        for j in range (len(self.tags)):
            tag = self.tags[j]
            
            if (tag["Key"]=="Linear Stream Type"):
                self.streamType = tag["Value"]
    
    #Parses the METAS from the Media Json
    def parseMetas(self,metas):
        for j in range (len(self.metas)):
            meta = metas[j]
            if (meta["Key"]=="Channel number"):
                self.channelNumber = meta["Value"]
            if (meta["Key"]=="EPG_ID"):
                self.epg_id = meta["Value"] 
                print self.epg_id
    
    #Parses the Files from the Media Json
    def parseFiles(self,files):
           
        self.filesFormat = ""
        self.numFiles = len(self.files)
        for j in range (self.numFiles):
            file = files[j]
            self.filesFormat = self.filesFormat+" "+file["Format"]
            
    #Parses the Pictures/Logos from the Linear Channel      
    def parseChannelPictures(self, pictures ):
        #getting the number of logos of the channel
        self.numChannelPictures = len (pictures)    
    
    #Given a Json containing the EPG data of a Linear Channel, stores and parses the information   
    def setProgramsInformation(self,json_programs):
        self.json_programs = json_programs
        self.parseJsonPrograms(json_programs)
     
    #Given a Json containing the EPG data of a Linear Channel, parses the information   
    def parseJsonPrograms(self, json_programs):
        
        #If the channel has programs, parse them
        if self.json_programs:
            element = self.json_programs[0]
            self.programs = element["EPGChannelProgrammeObject"]
            self.parseNumPrograms()
            self.parseOffset()
            self.parseProgramsPictures()
            #self.parseProgramsInfo()
            
    #set the number of programs of the channel    
    def parseNumPrograms(self):
            self.numPrograms=len(self.programs)
            
   
   
    #Parse the maximun and minimun offset of the channel
    def parseOffset(self):
        olderProgram = self.programs[0]
        self.startOffset = self.getDateOffset(olderProgram)
        newerProgram = self.programs[self.numPrograms-1]
        self.endOffset = self.getDateOffset(newerProgram)
    
   
     #returns the day offset        
    def getDateOffset(self,program):
        #Date in format: "15/06/2016 23:05:00"  
        strdate = program["END_DATE"]
        date = datetime.datetime.strptime(strdate,"%d/%m/%Y %H:%M:%S")
        date2 = datetime.datetime.strptime("%d/%d/%d" %(date.day, date.month,date.year),"%d/%m/%Y" )
        currentdate = datetime.datetime.now()
        currentdate2 = datetime.datetime.strptime("%d/%d/%d" %(currentdate.day, currentdate.month,currentdate.year),"%d/%m/%Y" )
        return (date2-currentdate2).days
    
    #This function will loop over the programs calculating:
    # - The total image references
    # - The average size of a event/program   
    def parseProgramsInfo(self):
        self.totalImagesReferences =0
        total_size=0
        #looping over all the programs of the channel and counting the number of images references
        for i in range (self.numPrograms):
            program = self.programs[i]
            self.parseProgramPicture(program)
            program_size= sys.getsizeof(program)
            total_size = total_size + program_size
            print "program size ", program_size, " total size ",total_size
        #if(self.numPrograms!=0 & total_size!=0):
        self.average_event_size = total_size/self.numPrograms
        print "Average event size ",self.average_event_size
            
        
            
    
    def parseProgramPicture(self, program):
        epg_pictures =program["EPG_PICTURES"]
        self.totalImagesReferences +=len(epg_pictures)
    
        

    
    def parseProgramsPictures(self):
        self.totalImagesReferences =0
        #looping over all the programs of the channel and counting the number of images references
        for i in range (self.numPrograms):
            program = self.programs[i]
            epg_pictures =program["EPG_PICTURES"]
            self.totalImagesReferences +=len(epg_pictures)
            
   
        
    def printChannelInfo(self,size):
        print self.channelNumber," \t",self.streamType," \t",self.name,"\t",self.startOffset, " \t", self.endOffset, " \t",self.numPrograms," \t",self.totalImagesReferences," \t",size
    
    def writeExcelChannelInfo(self,i,ws,size):
        r = 7+i
        ws.write(r, 0, self.channelNumber) 
        ws.write(r, 1, self.streamType)   
        ws.write(r, 2, self.name)   
        ws.write(r, 3, self.startOffset)
        ws.write(r, 4,  self.endOffset)
        ws.write(r, 5, self.numPrograms) 
        ws.write(r, 6, self.totalImagesReferences) 
        ws.write(r, 7, size)    
             
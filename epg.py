
"""epg.py: Calculates the size of the EPG data for a given environment and Opco"""

__author__      = "Ana Hernandez ana.hernandez@vodafone.com"



import json
import xlwt
import linearChannel
import urllib2
import StringIO
import gzip
import datetime

URL = {
    'Prod' : 'https://vfgtv.vodafone.com/api/v3_4/gateways/jsonpostgw.aspx?m=',
    'PreProd': 'https://vfgtv-pp.vodafone.com/api/v3_4/gateways/jsonpostgw.aspx?m='
}

OpcoAPICredentials ={
   'ITALY':{
            "ApiUser": "tvpapi_222",
            "ApiPass": "11111"
            },
    'UK':{
            "ApiUser": "tvpapi_185si",
            "ApiPass": "A2d4G6"
            }
}

kalturaMethods = {
    'GetMenu': 'GetMenu',
    'GetChannelMultiFilter':'GetChannelMultiFilter',
    'GetEPGMultiChannelProgram':'GetEPGMultiChannelProgram'
}

parameters_GetMenu = {
    "initObj": {
        "Locale": {
            "LocaleLanguage": "",
            "LocaleCountry": "",
            "LocaleDevice": "",
            "LocaleUserState": "Unknown"
        },
        "Platform": "STB",
        "SiteGuid": "",
        "DomainID": 0,
        "UDID": "",
        "ApiUser": "",
        "ApiPass": ""
    },

   "ID": 47
}


parameters_GetChannelMultiFilter ={
  "initObj": {
    "UDID": "615316000941",
    "SiteGuid": "644051",
    "ApiUser": "tvpapi_185",
    "ApiPass": "11111",
    "Locale": {
            "LocaleLanguage": "",
            "LocaleCountry": "",
            "LocaleDevice": "",
            "LocaleUserState": "Unknown"
        },
    "Platform": "STB",
    "DomainID": "491343"
  },
  "orderBy": "ABC",
  "ChannelID": "340767",
  "pageSize": "0",
  "cutWith": "AND",
  "picSize": "All",
  "orderDir": "Asc",
  "tagsMetas": [],
  "pageIndex": 0
}

timeUnits ={
    'Hours': 'Hours',
    'Days': 'Days'
}

parameters_GetEPGMultiChannelProgram ={
  "initObj": {
    "UDID": "90D406BE39CC43FEA9EC04EE073DF7DE",
    "SiteGuid": "644051",
    "ApiUser": "tvpapi_185",
    "ApiPass": "11111",
    "Locale": {
            "LocaleLanguage": "",
            "LocaleCountry": "",
            "LocaleDevice": "",
            "LocaleUserState": "Unknown"
        },
    "Platform": "STB",
    "DomainID": "0"
  },
"sEPGChannelID": [
    
],
"sPicSize": "full",
"oUnit": "Days",
"iFromOffset": -7,
"iToOffset": 5,
"iUTCOffSet": 0
}




#Execute an API given an url and the parameters and calculates the size of the response
#compressed and uncompressed, the size is returned in the parameter responseSize
def executeAPIwithSize (url, parameters,responseSize):
    
    req = urllib2.Request(url)
    req.add_header('Content-Type', 'application/json')
    req.add_header('Accept-Encoding', 'gzip')
    req.add_header('User-Agent', 'phil1') 
   
    response = urllib2.urlopen(req, parameters)
    
    if response.headers.getheader('Content-Encoding') == 'gzip':
        data = response.read()
        responseSize["sizegzip"] = len(data)
        buf = StringIO.StringIO(data)
        f = gzip.GzipFile(fileobj=buf)
        fdata = f.read()
        responseSize["sizejson"] = len(fdata)
        json_response = json.loads(fdata)
    else:
        
        data = response.read()
        responseSize["sizejson"] =len(data)
        json_response = json.loads(data)
    

    return json_response

#Execute an API given an url and the parameters
def executeAPI (url, parameters):
    
    req = urllib2.Request(url)
    req.add_header('Content-Type', 'application/json')
    req.add_header('Accept-Encoding', 'gzip')
    req.add_header('User-Agent', 'phil1') 
    
    response = urllib2.urlopen(req, parameters)
    
    if response.headers.getheader('Content-Encoding') == 'gzip':
        data = response.read()
        buf = StringIO.StringIO(data)
        f = gzip.GzipFile(fileobj=buf)
        fdata = f.read()
        json_response = json.loads(fdata)
    else:
        data = response.read()
        json_response = json.loads(data)
    
    return json_response

#returns the ChannelID for the EPG from the Menu
def getEPGChannelID(json_response):
   
    for i in range(len(json_response)):
        menu_url = json_response["MenuItems"][i]["URL"]
        jmenu_url = json.loads(menu_url)
       
        if jmenu_url['Type']=='EPG':
            return jmenu_url["ChannelID"]
    

#retrieves the channel line up. First call to GetMenu to retrieve the correct ChannelID for EPG 
#and later calls GetChannelMultiFilter for this channel to retrieve the Channel Line up
#Returns a Json with the response. The size (compressed and uncompressed) is retrieved in responseSize
def getChannelLineUp(url, opco, responseSize):
    
    #set the opco credentials to the parameters
    parameters_GetMenu['initObj']["ApiUser"]=OpcoAPICredentials[opco]['ApiUser']
    parameters_GetMenu['initObj']["ApiPass"]=OpcoAPICredentials[opco]['ApiPass']
    
    #calling to GetMenu to retrieve the correct Channel ID which contains the Linear Channels
    response = executeAPI(url+kalturaMethods["GetMenu"],json.dumps(parameters_GetMenu))
    
    #getting the ChannelID of the Linear Channels
    epg_channelID = getEPGChannelID(response)
    
    #setting the correct ChannelID to the parameters 
    parameters_GetChannelMultiFilter["ChannelID"]= epg_channelID
     #set the opco credentials to the parameters
    parameters_GetChannelMultiFilter['initObj']["ApiUser"]=OpcoAPICredentials[opco]['ApiUser']
    parameters_GetChannelMultiFilter['initObj']["ApiPass"]=OpcoAPICredentials[opco]['ApiPass']
    parameters = json.dumps(parameters_GetChannelMultiFilter)
    
    #calling GetChannelMultiFilter
    response = executeAPIwithSize(url+kalturaMethods["GetChannelMultiFilter"],parameters,responseSize)
    return response

#Calls GetEPGMultiChannelPrograms for a given channel to retrieve the programs information
#returns the json of the response (compressed and uncompressed) and the size in the responseSize parameter
def getLinearChannelPrograms (url,opco, epg_id, iFromOffset,iToOffset,responseSize):      
    
    #Setting the correct EPG_ID and offset to the parameters
    parameters = parameters_GetEPGMultiChannelProgram  
    parameters["sEPGChannelID"]=[]
    parameters["sEPGChannelID"].append(epg_id)
    parameters["iFromOffset"]=iFromOffset
    parameters["iToOffset"]=iToOffset
     #set the opco credentials to the parameters
    parameters['initObj']["ApiUser"]=OpcoAPICredentials[opco]['ApiUser']
    parameters['initObj']["ApiPass"]=OpcoAPICredentials[opco]['ApiPass']
    
    #call to GetEPGMultiChannelProgram
    response = executeAPIwithSize (url+kalturaMethods["GetEPGMultiChannelProgram"],json.dumps(parameters_GetEPGMultiChannelProgram),responseSize)
    
    return response

#Calls GetEPGMultiChannelPrograms for a given channel to retrieve the programs information
#returns the json of the response (compressed and uncompressed) and the size in the responseSize parameter
def getLinearChannelPrograms2 (url,opco, list_epg_id,oUnit, iFromOffset,iToOffset,responseSize):      
    
    #Setting the correct EPG_ID and offset to the parameters
    parameters = parameters_GetEPGMultiChannelProgram  
   # parameters["sEPGChannelID"]=[]
    parameters["sEPGChannelID"]=list_epg_id
    parameters["oUnit"]= oUnit
    parameters["iFromOffset"]=iFromOffset
    parameters["iToOffset"]=iToOffset
     #set the opco credentials to the parameters
    parameters['initObj']["ApiUser"]=OpcoAPICredentials[opco]['ApiUser']
    parameters['initObj']["ApiPass"]=OpcoAPICredentials[opco]['ApiPass']
    
    #call to GetEPGMultiChannelProgram
    response = executeAPIwithSize (url+kalturaMethods["GetEPGMultiChannelProgram"],json.dumps(parameters_GetEPGMultiChannelProgram),responseSize)
    
    return response


#write in the output excel the channel line up size
def writeExcelChannelLineUpData (ws, numChannels,size,sizeZip): 
    
    ws.write(1, 0, "Number of channels configured")
    ws.write(1, 1, numChannels)
    ws.write(2, 0, "Size of EPG in JSON format")
    ws.write(3, 0, "uncompressed")
    ws.write(3,1,size)
    ws.write(4, 0, "compressed")
    ws.write(4,1,sizeZip)


def writeExcelHeaders(ws):
    #printing channel line up information
    ws.write(6, 0, "ChannelNum") 
    ws.write(6, 1, "StreamType")   
    ws.write(6, 2, "Name")   
    ws.write(6, 3, "Offset Start")
    ws.write(6, 4, "Offset End")
    ws.write(6, 5, "Total Event") 
    ws.write(6, 6, "Picture References") 
    ws.write(6, 7, "Size Uncomppresed") 
    
#Retrieves the channel line up and EPG data for all the channel calculating the Size 
#of this responses compressed and uncompressed
def EPGSizingCalculations(environment,opco):
    
    
    wb = xlwt.Workbook()
    ws = wb.add_sheet(opco+" "+environment)
    ws.write(0, 1, environment)

    
    channelListSize = {
        "sizegzip":0,
        "sizejson":0
    } 
    
    #getting the url based on the environment
    url = URL[environment]
    #get the Channel Line up (list of linear channels configured)
    response_channelLineUp = getChannelLineUp(url,opco,channelListSize)
    print "Size of getting the channel line up "
    print "Size of Json ",channelListSize["sizejson"]
    print "Size of gzip: ",channelListSize["sizegzip"]
    
    #Size and sizezip will contains the total size including the channel list size + channel's programs size
    size=channelListSize["sizejson"]
    sizeZip=channelListSize["sizegzip"]
    
    numChannels = len(response_channelLineUp)
    print "Number of channels configured ",numChannels
   
    
    #printing channel line up information
    print "ChannelNum \tStreamType \tName \tOffsetStart \tOffsetEnd \tTotalEvents \tIPictureReferences \tSize"
    writeExcelHeaders(ws)
    
    #looping over all the channels
    for i in range(len(response_channelLineUp)):
        channel = response_channelLineUp[i]
        lchannel = linearChannel.LinearChannel(channel)
        
        #if the channel has a valid epg_id get the Events available in Kaltura for this channel
        if lchannel.epg_id:
            
            channelSize = {
                "sizegzip":0,
                "sizejson":0
            }
            #retreiving the EPG programs of this linear channel for -7 to 14 days
            programs_response=getLinearChannelPrograms(url, opco,lchannel.epg_id,-7,14,channelSize)
            #parsing the EPG programs information retrieved
            lchannel.setProgramsInformation(programs_response)
            #printing Channel info
            lchannel.printChannelInfo(channelSize["sizejson"])
            lchannel.writeExcelChannelInfo(i,ws,channelSize["sizejson"])
            size+=channelSize["sizejson"]
            sizeZip+=channelSize["sizegzip"]
    
    #Printint total size
    print "total size: ",size
    print"total size compressed", sizeZip
    writeExcelChannelLineUpData (ws, numChannels,size,sizeZip)
    currentdate = datetime.datetime.now()
    
  
    
    #save the excel file
    wb.save(opco+environment+currentdate+'.xls')

    
    
#Retrieves the channel line up and EPG data for all the channel simulating the calls done by the STB requesting
#only the data to display at the screen when the user is scrolling down throw the channels
def SizeEPGForScreenChannelScrolling(environment,opco,numChaScreen,numHourScreen):
    
    channelListSize = {
        "sizegzip":0,
        "sizejson":0
    } 
    
    #getting the url based on the environment
    url = URL[environment]
    #get the Channel Line up (list of linear channels configured)
    response_channelLineUp = getChannelLineUp(url,opco,channelListSize)
    print "Size of getting the channel line up "
    print "Size of Json ",channelListSize["sizejson"]
    print "Size of gzip: ",channelListSize["sizegzip"]
    
    #Size and sizezip will contains the total size including the channel list size + channel's programs size
    size=channelListSize["sizejson"]
    sizeZip=channelListSize["sizegzip"]
    
    numChannels = len(response_channelLineUp)
    print "Number of channels configured ",numChannels
   
    
    #printing channel line up information
    print "ChannelNum \tStreamType \tName \tOffsetStart \tOffsetEnd \tTotalEvents \tIPictureReferences \tSize"
  #  writeExcelHeaders(ws)
    
    nchannels=0
    iFromOffset = -numHourScreen-numHourScreen//2
    iToOffset = numHourScreen + numHourScreen//2
    print "From ",iFromOffset," To: ",iToOffset
    #looping over all the channels
    while nchannels < len(response_channelLineUp):
        
        list_epg_id =[]
        list_channel_names=[]
        i=0
        for i in range(numChaScreen):
            if (nchannels+i)<len(response_channelLineUp):
                channel = response_channelLineUp[nchannels+i]
                lchannel = linearChannel.LinearChannel(channel)
                #if the channel has a valid epg_id get the Events available in Kaltura for this channel
                if lchannel.epg_id:
                    list_epg_id.append(lchannel.epg_id)
                    list_channel_names(lchannel.name)
        
        nchannels = nchannels + i +1          
            
        channelSize = {
            "sizegzip":0,
             "sizejson":0
        }
        if list_epg_id:
            print "channles: ", list_channel_names
            #retreiving the EPG programs of this linear channel for -7 to 14 days
            programs_response=getLinearChannelPrograms2(url, opco,list_epg_id,timeUnits["Hours"],iFromOffset,iToOffset,channelSize)
            print "Call size:", channelSize["sizejson"]
            size+=channelSize["sizejson"]
            sizeZip+=channelSize["sizegzip"]
            
    
    #Printint total size
    print "total size: ",size
    print"total size compressed", sizeZip
    
   
   
#Retrieves the channel line up and EPG data for all the channel simulating the calls done by the STB requesting
#only the data to display at the screen when the user is scrolling throw the time
def SizeEPGForScreenTimeScrolling(environment,opco,numChaScreen,numHourScreen):
    
    channelListSize = {
        "sizegzip":0,
        "sizejson":0
    } 
    
    #getting the url based on the environment
    url = URL[environment]
    #get the Channel Line up (list of linear channels configured)
    response_channelLineUp = getChannelLineUp(url,opco,channelListSize)
    print "Size of getting the channel line up "
    print "Size of Json ",channelListSize["sizejson"]
    print "Size of gzip: ",channelListSize["sizegzip"]
    
    #Size and sizezip will contains the total size including the channel list size + channel's programs size
    size=channelListSize["sizejson"]
    sizeZip=channelListSize["sizegzip"]
    
    numChannels = len(response_channelLineUp)
    print "Number of channels configured ",numChannels
   
    
    #printing channel line up information
    print "ChannelNum \tStreamType \tName \tOffsetStart \tOffsetEnd \tTotalEvents \tIPictureReferences \tSize"
  #  writeExcelHeaders(ws)
    
    nchannels=30
    
        
    list_epg_id =[]
    list_channel_names=[]
    i=0
    for i in range(numChaScreen):
        if (nchannels+i)<len(response_channelLineUp):
            channel = response_channelLineUp[nchannels+i]
            lchannel = linearChannel.LinearChannel(channel)
            #if the channel has a valid epg_id get the Events available in Kaltura for this channel
            if lchannel.epg_id:
                list_epg_id.append(lchannel.epg_id)
                list_channel_names.append(lchannel.name)
        
           
    channelSize = {
        "sizegzip":0,
        "sizejson":0
    }
    if list_epg_id:
        iFromOffset = -numHourScreen//2
        iToOffset = numHourScreen//2
        
        print "channles: ", list_channel_names
        time=0
        numcalls =0
        while iToOffset<(24*7):
            
            iFromOffset=  iFromOffset+numHourScreen
            iToOffset=  iToOffset+numHourScreen
            
            if iToOffset>(24*7):
                iToOffset = 24*7
                
            print "From ",iFromOffset," To: ",iToOffset
   
            
            #retreiving the EPG programs of this linear channel for -7 to 14 days
            programs_response=getLinearChannelPrograms2(url, opco,list_epg_id,timeUnits["Hours"],iFromOffset,iToOffset,channelSize)
            numcalls = numcalls +1
            print "Call size:", channelSize["sizejson"]
            size+=channelSize["sizejson"]
            sizeZip+=channelSize["sizegzip"]
            
        
    
    #Printint total size
    print "For ",numHourScreen,"hours per call the total number of calls is: ",numcalls
    print "total size: ",size
    print"total size compressed", sizeZip
    print "averange size per call ",size/numcalls

    
#enviroment = 'PreProd'  
enviroment = 'Prod'  
opCo= 'UK'
#opCo ='ITALY'

EPGSizingCalculations(enviroment,opCo)

numChaScreen= 15
numHourScreen=10

#SizeEPGForScreenChannelScrolling(enviroment,opCo,numChaScreen,numHourScreen)
#SizeEPGForScreenTimeScrolling(enviroment,opCo,numChaScreen,numHourScreen)   
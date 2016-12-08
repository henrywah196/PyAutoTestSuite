'''
FileName: Utilities.py
Description: utilities class which will be used by enteliWEB test case 
             for any special usage during test execution. 
Created on Jan 31, 2013
@author: WAH
'''
import pyodbc
from settings import WebGroupDBConn


DataPointType = {'Temperature' : 'ODT',
                 'Power_Electric' : 'DEMAND',
                 'Energy_Electric' : 'CONSUMPTION',
                 'Apparent_Power_Electric' : 'DEMAND',
                 'Apparent_Energy_Electric' : 'CONSUMPTION',
                 'Flow_Volume_Gas' : 'DEMAND',
                 'Volume_Gas' : 'CONSUMPTION',
                 'Power_Gas' : 'DEMAND',
                 'Energy_Gas' : 'CONSUMPTION',
                 'Flow_Volume_Water' : 'DEMAND',
                 'Volume_Water' : 'CONSUMPTION',
                 'Flow_Mass_Steam' : 'DEMAND',
                 'Weight_Steam' : 'CONSUMPTION',
                 'Power_Thermal' : 'DEMAND',
                 'Energy_Thermal' : 'CONSUMPTION',
                 'Flow_Volume_Fuel' : 'DEMAND',
                 'Volume_Fuel' : 'CONSUMPTION',
                 'Weight_Carbon' : 'CONSUMPTION'}

EnergyType = {'Power_Electric' : 'Electric_Energy',
              'Energy_Electric' : 'Electric_Energy',
              'Apparent_Power_Electric' : 'Electric_Apparent',
              'Apparent_Energy_Electric' : 'Electric_Apparent',
              'Flow_Volume_Gas' : 'Gas_Volume',
              'Volume_Gas' : 'Gas_Volume',
              'Power_Gas' : 'Gas_Energy',
              'Energy_Gas' : 'Gas_Energy',
              'Flow_Volume_Water' : 'Water_Volume',
              'Volume_Water' : 'Water_Volume',
              'Flow_Mass_Steam' : 'Steam_Weight',
              'Weight_Steam' : 'Steam_Weight',
              'Power_Thermal' : 'Thermal_Energy',
              'Energy_Thermal' : 'Thermal_Energy',
              'Flow_Volume_Fuel' : 'Fuel_Volume',
              'Volume_Fuel' : 'Fuel_Volume',
              'Weight_Carbon' : 'Carbon_Emission'}


class DBConnect( ):
    def __init__( self, settingClass ):
        self.Driver = settingClass["DRIVER"]
        self.Server = settingClass["SERVER"]
        self.Port = settingClass["PORT"]
        self.Database = settingClass["DATABASE"]
        self.User = settingClass["USER"]
        self.Password = settingClass["PASSWORD"]
        self.cnxn = None
        self.cursor = None

    def mkConnect(self):
        ''' start pyodbc connection'''
        #pyodbc.pooling = False
        #self.cnxn = pyodbc.connect(self.getConnString())
        self.cnxn = pyodbc.connect(self.getConnString())
        self.cursor = self.cnxn.cursor()
        
    def getConnString(self):
        ''' return the pyodbc dsnless connect string '''
        connString = 'Driver={' + self.Driver + '};Server=' + self.Server + ';Port=' + self.Port + ';Database=' + self.Database + ';UID=' + self.User + ';PWD=' + self.Password + ';'
        if self.getDriverType == 'MYSQL':
            connString = 'Driver={' + self.Driver + '};Server=' + self.Server + ';Port=' + self.Port + ';Database=' + self.Database + ';User=' + self.User + ';Password=' + self.Password + ';'
        return connString

    def disConnect(self):
        ''' stop pyodbc connection'''
        self.cnxn.close()
        
    def getDriverType(self):
        ''' verify whether it is MYSQL, MSSQL or PostgreSQL '''
        if 'MySQL' in self.Driver:
            return 'MYSQL'
        elif "PostgreSQL" in self.Driver:
            return "POSTGRESQL"
        else:
            return 'MSSQL'
        
        
def getMeterInstance(DBConn, treePath):
    """
    using the given treePath search webgroupdb and return the unique meter/area ID
    treePath example: div id="loader"\TestArea#1\Building F\Water Meter 1
    """
    # get treepath node list
    nodeList = treePath.split('\\')
    rootNodeIDX = 0
    targetNodeIDX = len(nodeList) - 1
    targetID = None
    parentID = None
    for i in range(len(nodeList)):
        if i == rootNodeIDX:
            cursor = DBConn.cursor.execute("SELECT ID FROM area WHERE Parent is NULL and Name = ?", nodeList[i])
            row = cursor.fetchone()
            if row:
                parentID = row.ID
            if rootNodeIDX == targetNodeIDX:
                targetID = parentID
        elif i == targetNodeIDX:
            if parentID:
                cursor = DBConn.cursor.execute("SELECT ID FROM area WHERE Parent = ? and Name = ?", parentID, nodeList[i])
                row = cursor.fetchone()
                if row:
                    targetID = row.ID
                else:
                    # try meter table
                    cursor = DBConn.cursor.execute("SELECT ID FROM meter WHERE Area = ? and Name = ?", parentID, nodeList[i])
                    row = cursor.fetchone()
                    if row:
                        targetID = row.ID    
        else:
            if parentID:
                cursor = DBConn.cursor.execute("SELECT ID FROM area WHERE Parent = ? and Name = ?", parentID, nodeList[i])
                row = cursor.fetchone()
                if row:
                    parentID = row.ID
                else:
                    parentID = None
            else:
                targetID = None
                break
    return targetID


def getInstanceByGroup(DBConn, groupID):
    """
    return the instance from datapoint_group_map table by the given group ID
    """
    result = None
    cursor = DBConn.cursor.execute("select Instance from datapoint_group_map where `Group` = ?", groupID)
    row = cursor.fetchone()    
    if row:
        result = row.Instance
    return result


def getDataPointGroupID(DBConn, treePath):
    """
    get the datapoint_group id for the given area/meter
    """
    result = None
    meterID = getMeterInstance(DBConn, treePath)    # get area or meter ID
    if meterID:
        cursor = DBConn.cursor.execute("SELECT `Group` FROM datapoint_group_map WHERE instance = ?", meterID)
        row = cursor.fetchone()
        if row:
            result = row.Group
    return result


def getDataPointID(DBConn, areaMeterID, AggreEnergyType, dataPointType):
    """
    return the id of the datapoint which is assigned to the given meter 
    
    @param string treePath:         the full path to refer to t area or meter in the tree in the format of A\B\C
    @param string AggreEnergyType   the energy type of datapoint, could be one of Electric_Energy, Gas_Volume, Water_Volume, ...
    @param string dataPointType:    the type of datapoint, could be one of ODT, DEMAND or CONSUMPTION
    """
    result = None
    if dataPointType == 'ODT':
        cursor = DBConn.cursor.execute("SELECT ID FROM datapoint WHERE Area = ?", areaMeterID)
        row = cursor.fetchone()
        if row:
            result = row.ID
    else:
        cursor = DBConn.cursor.execute("SELECT datapoint.ID, datapoint_detail.`Type` FROM datapoint LEFT JOIN datapoint_detail ON datapoint.Instance = datapoint_detail.FullRef WHERE datapoint.Meter = ?", areaMeterID)
        rows = cursor.fetchall()
        if rows:
            for row in rows:
                if EnergyType[row.Type] == AggreEnergyType:
                    if DataPointType[row.Type] == dataPointType:
                        result = row.ID
                        break
    return result


def getTLinstance(DBConn, areaMeterID, AggreEnergyType, dataPointType):
    """
    get the tlinstance ID of the given meter/area and its tlinstance type
    
    @param string AggreEnergyType   the energy type of datapoint, could be one of Electric_Energy, Gas_Volume, Water_Volume, ...
    @param string dataPointType:    the type of datapoint, could be one of ODT, DEMAND or CONSUMPTION
    """
    result = None
    datapointID = getDataPointID(DBConn, areaMeterID, AggreEnergyType, dataPointType)
    if datapointID:
        cursor = DBConn.cursor.execute("SELECT report_rate_tlinstance.ID FROM report_rate_tlinstance LEFT JOIN datapoint ON report_rate_tlinstance.FullRef = datapoint.Instance WHERE datapoint.ID = ?", datapointID)
        row = cursor.fetchone()
        if row:
            result = row.ID
    return result


def getAggreEnergyType(DBConn, areaMeterID):
    """
    return a list of aggregation energy type which the given meter / area contains
    """
    result = None
    # verify if it is an area or a meter
    cursor = DBConn.cursor.execute("SELECT * FROM meter where ID = ?", areaMeterID)
    row = cursor.fetchone()
    if row:
        # it's a meter
        cursor = DBConn.cursor.execute("select distinct datapoint.Meter, datapoint_detail.Type from datapoint left join datapoint_detail on datapoint.Instance = datapoint_detail.FullRef where datapoint.Meter = ?", areaMeterID)
        rows = cursor.fetchall()
        if rows:
            result = []
            for row in rows:
                result.append(EnergyType[row.Type])
            result = list(set(result))
    else:
        # it's an area
        meterList = getMeterList(DBConn, areaMeterID)
        if meterList:
            meterList.append(' ')    # to prevent a single item tuple
            meterList = tuple(meterList)
            cursor = DBConn.cursor.execute("select Type from (select distinct datapoint.Meter, datapoint_detail.Type from datapoint left join datapoint_detail on datapoint.Instance = datapoint_detail.FullRef) t where Meter in %s" %(meterList,))
            #cursor = myDBConn.cursor.execute("select distinct datapoint.Meter, datapoint_detail.Type from datapoint left join datapoint_detail on datapoint.Instance = datapoint_detail.FullRef where datapoint.Meter in %s" %(meterList,))
            rows = cursor.fetchall()
            if rows:
                result = []
                for row in rows:
                    result.append(EnergyType[row.Type])
                result = list(set(result))    # remove duplicates in list
    return result


def getAggregationType(DBConn, areaMeterID, AggreEnergyType):
    """
    return a list of aggregation type based on the given area/meter id and aggregation energy type
    """
    # convert from aggreEnergType to energy type
    result = None
    targetEnergyType = []
    for key, value in EnergyType.items():
        if value == AggreEnergyType:
            targetEnergyType.append(key)
    # verify if it is an area or a meter
    cursor = DBConn.cursor.execute("SELECT * FROM meter where ID = ?", areaMeterID)
    row = cursor.fetchone()
    if row:
        # it's a meter
        cursor = DBConn.cursor.execute("select datapoint.Meter, datapoint_detail.Type from datapoint left join datapoint_detail on datapoint.Instance = datapoint_detail.FullRef where datapoint.Meter = ?", areaMeterID)
        rows = cursor.fetchall()
        if rows:
            result = []
            for row in rows:
                if EnergyType[row.Type] == AggreEnergyType:
                    if DataPointType[row.Type] == 'CONSUMPTION':
                        result.append('Sum')
                    if DataPointType[row.Type] == 'DEMAND':
                        result.append('Avg')
                        result.append('Max')
                        result.append('Min')
    else:
        # it's an area
        meterList = getMeterList(DBConn, areaMeterID, AggreEnergyType)
        if meterList:
            meterList.append(' ')    # to prevent a single item tuple
            meterList = tuple(meterList)
            cursor = DBConn.cursor.execute("select datapoint.Meter, datapoint_detail.`Type` from datapoint left join datapoint_detail on datapoint.Instance = datapoint_detail.FullRef where datapoint.Meter in %s" %(meterList,))
            rows = cursor.fetchall()
            if rows:
                result = []
                for row in rows:
                    if row.Type in targetEnergyType:
                        if DataPointType[row.Type] == 'CONSUMPTION':
                            result.append('Sum')
                        if DataPointType[row.Type] == 'DEMAND':
                            result.append('Avg')
                            result.append('Max')
                            result.append('Min')
                result = list(set(result))    # remove duplicates in list
    return result


def getTotalDatapointGroup(DBConn):
    """
    return a number of total datapoint groups which doesn't including report group
    it only calculate total area and meter group
    """
    result = None
    # calculate meter
    cursor = DBConn.cursor.execute("select distinct Meter from datapoint where Meter is not NULL")
    rows = cursor.fetchall()
    if rows:
        meterList = []
        for row in rows:
            meterList.append((row.Meter).encode('ascii', 'ignore'))
        result = len(meterList)
        meterList.append(' ')    # to prevent a single item tuple
        meterList = tuple(meterList)
        # calculate area of meter
        cursor = DBConn.cursor.execute("select distinct Area from meter where ID in %s" %(meterList,))
        rows = cursor.fetchall()
        areaList = []
        for row in rows:
            areaList.append((row.Area).encode('ascii', 'ignore'))
        result = result + len(areaList)
        areaList.append(' ')    # to prevent a single item tuple
        areaList = tuple(areaList)
        # calculate parent area
        finish = False
        while not finish:
            cursor = DBConn.cursor.execute("select distinct Parent from area where ID in %s and Parent is not NULL" %(areaList,))
            rows = cursor.fetchall()
            if rows:
                parentList = []
                for row in rows:
                    item = (row.Parent).encode('ascii', 'ignore')
                    if item not in areaList:
                        parentList.append(item)
                if len(parentList) == 0:
                    finish = True
                else:
                    result = result + len(parentList)
                    parentList.append(' ') # to prevent a single itme tuple
                    areaList = tuple(parentList)
            else:
                finish = True
    return result


def getDirectSubMeters(DBConn, areaID, AggreEnergyType=None):
    """
    return a list of direct child meters of the given aggre energy type
    """
    meterList = []
    cursor = DBConn.cursor.execute("select ID from Meter where area = ?", areaID)
    rows = cursor.fetchall()
    if rows:
        for row in rows:
            if not AggreEnergyType:
                meterList.append((row.ID).encode('ascii', 'ignore'))
            else:
                if AggreEnergyType in getAggreEnergyType(DBConn, row.ID):
                    meterList.append((row.ID).encode('ascii', 'ignore'))
    if meterList:
        return meterList
    else:
        return None
    

def getDirectSubAreas(DBConn, areaID):
    """
    return a list of direct sub areas"
    """
    areaList = []
    cursor = DBConn.cursor.execute("select ID from area where parent = ?", areaID)
    rows = cursor.fetchall()
    if rows:
        for row in rows:
            areaList.append((row.ID).encode('ascii', 'ignore'))
    if areaList:
        return areaList
    else:
        return None


def getMeterList(DBConn, areaID, AggreEnergyType=None):
    """
    return a list of meter instances which belongs to the give area.
    if energy type was assigned it will return a list of meters based on the area within area rule
    if energy type is None, it will return all the meters under it directly or indirectly.
    """
    if not AggreEnergyType:
        meterList = []
        # search for direct child meters
        cursor = DBConn.cursor.execute("select ID from Meter where area = ?", areaID)
        rows = cursor.fetchall()
        if rows:
            for row in rows:
                meterList.append((row.ID).encode('ascii', 'ignore'))
        # search for grand child meters
        cursor = DBConn.cursor.execute("select ID from area where parent = ?", areaID)
        rows = cursor.fetchall()
        if rows:
            areaList = []
            for row in rows:
                areaList.append((row.ID).encode('ascii', 'ignore'))
            for item in areaList:
                tempList = getMeterList(DBConn, item)
                meterList.extend(tempList)
        if meterList:
            return meterList
        else:
            return None
    else:
        meterList = getDirectSubMeters(DBConn, areaID, AggreEnergyType)
        if meterList:
            return meterList
        else:
            meterList = []
            subAreaList = getDirectSubAreas(DBConn, areaID)
            if subAreaList:
                for area in subAreaList:
                    meters = getMeterList(DBConn, area, AggreEnergyType)
                    if meters:
                        meterList.extend(meters)
            if meterList:
                return meterList
            else:
                return None
                   
        
def getGroupModel(DBConn, groupID):
    """
    return the Model of the given group from datapoint_group_map table
    it could be Meter, Area or Report
    """  
    result = None
    cursor = DBConn.cursor.execute("select Model from datapoint_group_map where Model in ('Meter', 'Area') and `Group` = ?", groupID)
    row = cursor.fetchone()    
    if row:
        result = row.Model
    return result


def getFirstTimestamp(DBConn, meterID, AggreEnergyType=None, dataPointType=None):
    """
    based on the give meter, check its assigned datapoints and return the earliest timestamp
    """
    result = None
    start_C = None
    start_D = None
    firstTimeStamp = None
    aggreEnergies = []
    if not AggreEnergyType:
        aggreEnergies = getAggreEnergyType(DBConn, meterID)
    else:
        aggreEnergies.append(AggreEnergyType)
    for aggreEnergy in aggreEnergies:
        if not dataPointType:
            tlInstance_C = getTLinstance(DBConn, meterID, aggreEnergy, 'CONSUMPTION')
            if tlInstance_C:
                cursor = DBConn.cursor.execute("select min(timestamp) as start from report_rate_data where tlinstance = ?", tlInstance_C)
                row = cursor.fetchone()
                start_C = row.start
            tlInstance_D = getTLinstance(DBConn, meterID, aggreEnergy, 'DEMAND')
            if tlInstance_D:
                cursor = DBConn.cursor.execute("select min(timestamp) as start from report_rate_data where tlinstance = ?", tlInstance_D)
                row = cursor.fetchone()
                start_D = row.start
            if start_C and start_D:
                if start_C < start_D:
                    firstTimeStamp = start_C
                else:
                    firstTimeStamp = start_D
            else:
                if start_C:
                    firstTimeStamp = start_C
                else:
                    firstTimeStamp = start_D
            if firstTimeStamp:
                if not result:
                    result = firstTimeStamp
                else:
                    if firstTimeStamp < result:
                        result = firstTimeStamp
        else:
            if dataPointType in ('CONSUMPTION', 'DEMAND'):
                tlInstance = getTLinstance(DBConn, meterID, aggreEnergy, dataPointType)
                if tlInstance:
                    cursor = DBConn.cursor.execute("select min(timestamp) as start from report_rate_data where tlinstance = ?", tlInstance)
                    row = cursor.fetchone()
                    result = row.start
    return result


def getLastTimestamp(DBConn, meterID, AggreEnergyType=None, dataPointType=None):
    """
    based on the give meter, check its assigned datapoints and return the Last timestamp
    """
    result = None
    finish_C = None
    finish_D = None
    lastTimeStamp = None
    aggreEnergies = []
    if not AggreEnergyType:
        aggreEnergies = getAggreEnergyType(DBConn, meterID)
    else:
        aggreEnergies.append(AggreEnergyType)
    for aggreEnergy in aggreEnergies:
        if not dataPointType:
            tlInstance_C = getTLinstance(DBConn, meterID, aggreEnergy, 'CONSUMPTION')
            if tlInstance_C:
                cursor = DBConn.cursor.execute("select max(timestamp) as finish from report_rate_data where tlinstance = ?", tlInstance_C)
                row = cursor.fetchone()
                finish_C = row.finish
            tlInstance_D = getTLinstance(DBConn, meterID, aggreEnergy, 'DEMAND')
            if tlInstance_D:
                cursor = DBConn.cursor.execute("select max(timestamp) as finish from report_rate_data where tlinstance = ?", tlInstance_D)
                row = cursor.fetchone()
                finish_D = row.finish
            if finish_C and finish_D:
                if finish_C > finish_D:
                    lastTimeStamp = finish_C
                else:
                    lastTimeStamp = finish_D
            else:
                if finish_C:
                    lastTimeStamp = finish_C
                else:
                    lastTimeStamp = finish_D
            if lastTimeStamp:
                if not result:
                    result = lastTimeStamp
                else:
                    if lastTimeStamp > result:
                        result = lastTimeStamp
        else:
            if dataPointType in ('CONSUMPTION', 'DEMAND'):
                tlInstance = getTLinstance(DBConn, meterID, aggreEnergy, dataPointType)
                if tlInstance:
                    cursor = DBConn.cursor.execute("select max(timestamp) as finish from report_rate_data where tlinstance = ?", tlInstance)
                    row = cursor.fetchone()
                    result = row.finish
    return result


class TLInstance():
    """
    place holder for all methods related to webgroup.report_rate_tlinstance and report_rate_data DB query
    """

    @classmethod
    def getReport_Rate_Tlinstances(cls, DBConn, TLInstance_Under_Test=None):
        """
        search webgroup.report_rate_tlinstance table and return a list of tlinstance in the format of
        [{"FullRef": "//RV Site/1100.AV201.Value", "Type": "Historian"}]
        """
        result = None
        cursor = DBConn.cursor.execute("select * from report_rate_tlinstance")
        rows = cursor.fetchall()
        if rows:
            result = []
            for row in rows:
                tlReference = {}
                tlReference["FullRef"] = (row.FullRef).encode('ascii', 'ignore')
                tlReference["Type"] = (row.Type).encode('ascii', 'ignore')
                if tlReference["Type"] == "Historian":
                    cursor = DBConn.cursor.execute("select host from settings_historian where ID = ?", (row.Historian).encode('ascii', 'ignore'))
                    row = cursor.fetchone()
                    tlReference["Host"] = (row.host).encode('ascii', 'ignore')
                if tlReference["Type"] == "CopperCube":
                    cursor = DBConn.cursor.execute("select IP from settings_archiver where ID = ?", (row.Historian).encode('ascii', 'ignore'))
                    row = cursor.fetchone()
                    tlReference["Host"] = (row.IP).encode('ascii', 'ignore')
                if TLInstance_Under_Test is not None:
                    if tlReference["FullRef"] in TLInstance_Under_Test:
                        result.append(tlReference)
                else:
                    result.append(tlReference)
            
        return result
    
    @classmethod
    def getReport_Rate_Tlinstance_ID(cls, DBConn, FullRef):
        result = None
        cursor = DBConn.cursor.execute("select ID from report_rate_tlinstance where FullRef = ?", FullRef)
        row = cursor.fetchone()
        if row is not None:
            result = row.ID
        return result
    
    @classmethod
    def getRawTlinstanceID(cls, DBConn, FullRef):
        """
        return TLInstance (TLInstance ID of Historian) from report_rate_tlinstnace if the tlInstance type is Historian
        return TLInstance and convert it to the name of tl table of coppercube if the tlinstance type is CopperCube
        """
        result = None
        cursor = DBConn.cursor.execute("select TLInstance, Type from report_rate_tlinstance where FullRef = ?", FullRef)
        row = cursor.fetchone()
        if row is not None:
            result = (row.TLInstance).encode('ascii', 'ignore')
            if (row.Type).encode('ascii', 'ignore') == "CopperCube":
                result = result.lower()
                result = result.replace('/', '_') 
                result = result.replace('.', '_')
                result = result[2:]
        return result
    
    @classmethod
    def containsBaselineData(cls, DBConn, FullRef):
        """
        return True if the assigned tl reference has baseline data assigned
        """
        result = None
        cursor = DBConn.cursor.execute("SELECT count(*) as total FROM webgroup.report_rate_data_baseline where FullRef = ?", FullRef)
        row = cursor.fetchone()
        return row.total > 0
           

if __name__ == "__main__":

    myDBConn = DBConnect(WebGroupDBConn)
    myDBConn.connect()
    
    print getAggreEnergyType(myDBConn, getMeterInstance(myDBConn, 'div id="loader"\_333\Campus 01\Building AA\Electric Meter A'))
    
    myDBConn.disConnect()
    
    
    
    
    


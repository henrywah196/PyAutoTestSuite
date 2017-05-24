'''
Created on Oct 29, 2015

@author: hwang
'''
import pyodbc
import settings
import datetime
import calendar
from __builtin__ import classmethod

# Days mapping
Days = {
         'Sun': 1,
         'Mon': 2,
         'Tue': 3,
         'Wed': 4,
         'Thu': 5,
         'Fri': 6,
         'Sat': 7
       }

# mapping between energy meter types and Area or Meter energy type
MeterTypes = {
               'Electrical Energy' : 'Electric_Energy',
               'Apparent Energy'   : 'Electric_Apparent',
               'Gas Volume'        : 'Gas_Volume',
               'Gas Energy'        : 'Gas_Energy',
               'Fuel Volume'       : 'Fuel_Volume',
               'Water Volume'      : 'Water_Volume',
               'Thermal Energy'    : 'Thermal_Energy',
               'Steam Energy'      : 'Steam_Weight',
               'Carbon Emission'   : 'Carbon_Emission'
             }

# mapping between Datapoint energy type and Area or Meter energy type
EnergyType = {
               'Power_Electric'           : 'Electric_Energy',
               'Energy_Electric'          : 'Electric_Energy',
               'Apparent_Power_Electric'  : 'Electric_Apparent',
               'Apparent_Energy_Electric' : 'Electric_Apparent',
               'Flow_Volume_Gas'          : 'Gas_Volume',
               'Volume_Gas'               : 'Gas_Volume',
               'Power_Gas'                : 'Gas_Energy',
               'Energy_Gas'               : 'Gas_Energy',
               'Flow_Volume_Water'        : 'Water_Volume',
               'Volume_Water'             : 'Water_Volume',
               'Flow_Mass_Steam'          : 'Steam_Weight',
               'Weight_Steam'             : 'Steam_Weight',
               'Power_Thermal'            : 'Thermal_Energy',
               'Energy_Thermal'           : 'Thermal_Energy',
               'Flow_Volume_Fuel'         : 'Fuel_Volume',
               'Volume_Fuel'              : 'Fuel_Volume',
               'Weight_Carbon'            : 'Carbon_Emission'
             }

DataPointType = {
                  'Temperature'              : 'ODT',
                  'Power_Electric'           : 'DEMAND',
                  'Energy_Electric'          : 'CONSUMPTION',
                  'Apparent_Power_Electric'  : 'DEMAND',
                  'Apparent_Energy_Electric' : 'CONSUMPTION',
                  'Flow_Volume_Gas'          : 'DEMAND',
                  'Volume_Gas'               : 'CONSUMPTION',
                  'Power_Gas'                : 'DEMAND',
                  'Energy_Gas'               : 'CONSUMPTION',
                  'Flow_Volume_Water'        : 'DEMAND',
                  'Volume_Water'             : 'CONSUMPTION',
                  'Flow_Mass_Steam'          : 'DEMAND',
                  'Weight_Steam'             : 'CONSUMPTION',
                  'Power_Thermal'            : 'DEMAND',
                  'Energy_Thermal'           : 'CONSUMPTION',
                  'Flow_Volume_Fuel'         : 'DEMAND',
                  'Volume_Fuel'              : 'CONSUMPTION',
                  'Weight_Carbon'            : 'CONSUMPTION'
                }


class WebGroupDBObj(object):
    """ Model enteliWEB webgroup dtabase"""
    
    def __init__(self, infoHash=None):
        if infoHash is None:
            infoHash = settings.WebGroupDBConn
        self.Driver = infoHash["DRIVER"]
        self.Server = infoHash["SERVER"]
        self.Port = infoHash["PORT"]
        self.Database = infoHash["DATABASE"]
        self.User = infoHash["USER"]
        self.Password = infoHash["PASSWORD"]
        self.cnxn = None
        self.cursor = None
        self._connect()
        
        self.DataPointType = DataPointType
    
    def __repr__(self):
        super(WebGroupDBObj, self).__repr__()
        
    def __del__(self):
        self._disConnect()
        
    def _connect(self):
        ''' start pyodbc connection'''
        self.cnxn = pyodbc.connect(self._getConnString())
        self.cursor = self.cnxn.cursor()
        
    def _disConnect(self):
        ''' stop pyodbc connection'''
        if self.cnxn is not None:
            self.cnxn.close()
        
    def _getConnString(self):
        ''' return the pyodbc dsnless connect string '''
        connString = 'Driver={' + self.Driver + '};Server=' + self.Server + ';Port=' + self.Port + ';Database=' + self.Database + ';User=' + self.User + ';Password=' + self.Password + ';'
        return connString
    
    def getAreaMeterInstanceID(self, treePath):
        """
        using the given treePath search webgroup db and return the unique meter or area ID
        @param string treePath: treePath example: div id="loader"\TestArea#1\Building F\Water Meter 1
        """
        # get treepath node list
        nodeList = treePath.split('\\')
        rootNodeIDX = 0
        targetNodeIDX = len(nodeList) - 1
        targetID = None
        parentID = None
        for i in range(len(nodeList)):
            if i == rootNodeIDX:
                cursor = self.cursor.execute("SELECT ID FROM area WHERE Parent is NULL and Name = ?", nodeList[i])
                row = cursor.fetchone()
                if row:
                    parentID = row.ID
                if rootNodeIDX == targetNodeIDX:
                    targetID = parentID
            elif i == targetNodeIDX:
                if parentID:
                    cursor = self.cursor.execute("SELECT ID FROM area WHERE Parent = ? and Name = ?", parentID, nodeList[i])
                    row = cursor.fetchone()
                    if row:
                        targetID = row.ID
                    else:
                        # try meter table
                        cursor = self.cursor.execute("SELECT ID FROM meter WHERE Area = ? and Name = ?", parentID, nodeList[i])
                        row = cursor.fetchone()
                        if row:
                            targetID = row.ID    
            else:
                if parentID:
                    cursor = self.cursor.execute("SELECT ID FROM area WHERE Parent = ? and Name = ?", parentID, nodeList[i])
                    row = cursor.fetchone()
                    if row:
                        parentID = row.ID
                    else:
                        parentID = None
                else:
                    targetID = None
                    break
        return targetID
    
    def getChildAreas(self, areaInstanceID):
        """
        looking for the direct sub areas of the give area and return a list of area id
        """
        result = None
        cursor = self.cursor.execute("select ID from area where parent = ?", areaInstanceID)
        rows = cursor.fetchall()
        if len(rows) > 0:
            result = []
            for row in rows:
                result.append((row.ID).encode('ascii', 'ignore'))
        return result
    
    def getChildMeters(self, areaInstanceID, EnergyType=None):
        """
        looking for the direct sub meters of the give area and return a list of meter id
        if energy type is given only return the the list of meters of that type.
        @param string EnergyType: the energy type of the meter, such as 'Electric_Energy', 'Water_Volume'
        """
        meterList = None
        cursor = self.cursor.execute("select ID from Meter where area = ?", areaInstanceID)
        rows = cursor.fetchall()
        if len(rows) > 0:
            meterList = []
            for row in rows:
                if not EnergyType:
                    meterList.append((row.ID).encode('ascii', 'ignore'))
                else:
                    if EnergyType in self.getAreaMeterEnergyType(row.ID):
                        meterList.append((row.ID).encode('ascii', 'ignore'))
        return meterList
    
    def getAreaMeterEnergyType(self, instanceID):
        """
        with the given area or meter instance ID 
        looking for the datapoint energy type assigned, the area could contains more then one
        energy types if there are several meters assigned.
        @param string instanceID: the instance ID of Area or Meter
        """
        result = None
        # verify if it is an area or a meter
        instanceType = self.getInstanceType(instanceID)
        if instanceType == "meter":
            # it's a meter
            cursor = self.cursor.execute("select distinct datapoint.Meter, datapoint_detail.Type from datapoint left join datapoint_detail on datapoint.Instance = datapoint_detail.FullRef where datapoint.Meter = ?", instanceID)
            rows = cursor.fetchall()
            if len(rows) > 0:
                result = []
                for row in rows:
                    result.append(EnergyType[row.Type])
                result = list(set(result))
        elif instanceType == "area":
            # it's an area
            meterList = self.getMeterList(instanceID)
            if meterList:
                meterList.append(' ')    # to prevent a single item tuple
                meterList = tuple(meterList)
                cursor = self.cursor.execute("select Type from (select distinct datapoint.Meter, datapoint_detail.Type from datapoint left join datapoint_detail on datapoint.Instance = datapoint_detail.FullRef) t where Meter in %s" %(meterList,))
                #cursor = myDBConn.cursor.execute("select distinct datapoint.Meter, datapoint_detail.Type from datapoint left join datapoint_detail on datapoint.Instance = datapoint_detail.FullRef where datapoint.Meter in %s" %(meterList,))
                rows = cursor.fetchall()
                if len(rows) > 0:
                    result = []
                    for row in rows:
                        result.append(EnergyType[row.Type])
                    result = list(set(result))    # remove duplicates in list
        return result
    
    def getAggregationType(self, areaMeterID, AggreEnergyType):
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
        cursor = self.cursor.execute("SELECT * FROM meter where ID = ?", areaMeterID)
        row = cursor.fetchone()
        if row:
            # it's a meter
            cursor = self.cursor.execute("select datapoint.Meter, datapoint_detail.Type from datapoint left join datapoint_detail on datapoint.Instance = datapoint_detail.FullRef where datapoint.Meter = ?", areaMeterID)
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
            meterList = self.getMeterList(areaMeterID, AggreEnergyType)
            if meterList:
                meterList.append(' ')    # to prevent a single item tuple
                meterList = tuple(meterList)
                cursor = self.cursor.execute("select datapoint.Meter, datapoint_detail.`Type` from datapoint left join datapoint_detail on datapoint.Instance = datapoint_detail.FullRef where datapoint.Meter in %s" %(meterList,))
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
    
    def getMeterList(self, areaInstanceID, EnergyType=None):
        """
        return a list of meter instances which belongs to the give area.
        if energy type was assigned it will return a list of meters based on the area within area rule,
        which means if the type of energy meter was found under direct child meter, no need to search for 
        grand child meters.
        if energy type is None, it will return all the meters under it directly or indirectly.
        @param string EnergyType: the energy type of the meter, such as 'Electric_Energy', 'Water_Volume'
        """
        if not EnergyType:
            # search for direct child meters
            meterList = self.getChildMeters(areaInstanceID)
            
            # search for grand child meters
            areaList = self.getChildAreas(areaInstanceID)
            if areaList:
                for item in areaList:
                    tempList = self.getMeterList(item)
                    if tempList:
                        if meterList:
                            meterList.extend(tempList)
                        else:
                            meterList = []
                            meterList.extend(tempList)
            return meterList
        else:
            # search for direct child meters of that energy type
            meterList = self.getChildMeters(areaInstanceID, EnergyType)
            if meterList:
                return meterList
            else:
                # search for grand child meters of that energy type
                areaList = self.getChildAreas(areaInstanceID)
                if areaList:
                    for area in areaList:
                        tempList = self.getMeterList(area, EnergyType)
                        if tempList:
                            if meterList:
                                meterList.extend(tempList)
                            else:
                                meterList = []
                                meterList.extend(tempList)
                return meterList
    
    def getEnergyReportInstanceID(self, treePath):
        """
        using the given treePath search webgroup db and return the unique energy report instance ID
        @param string treePath: treePath example: Consumption\Consumpption002 - Area Only
        """
        nodeList = treePath.split('\\')
        nodeFilePath = nodeList[0]
        nodeName = nodeList[1]
        targetID = None
        cursor = self.cursor.execute("SELECT ID FROM report WHERE FilePath = ? and Name = ?", nodeFilePath, nodeName)
        row = cursor.fetchone()
        if row:
            targetID = row.ID
        return targetID
    
    def getDataPointGroupID(self, instanceID):
        """
        return the datapoint_group id for the given area, meter or report instance ID
        @param string instanceID: the instance ID of Area, Meter or energy report instance
        """
        result = None
        cursor = self.cursor.execute("SELECT `Group` FROM datapoint_group_map WHERE instance = ?", instanceID)
        row = cursor.fetchone()
        if row:
            result = row.Group
        return result
    
    def getInstanceType(self, instanceID):
        """
        based on the give instance ID looking for the type of this instance, the return
        could be Area, Meter or Report
        """
        instanceType = None
        cursor = self.cursor.execute("SELECT * FROM area WHERE ID = ?", instanceID)
        row = cursor.fetchone()
        if row:
            instanceType = "area"
            return instanceType
        cursor = self.cursor.execute("SELECT * FROM meter WHERE ID = ?", instanceID)
        row = cursor.fetchone()
        if row:
            instanceType = "meter"
            return instanceType
        cursor = self.cursor.execute("SELECT * FROM report WHERE ID = ?", instanceID)
        row = cursor.fetchone()
        if row:
            instanceType = "report"
            return instanceType
        return instanceType
    
    def getDataPointInfo(self, instanceID):
        """
        with the given area or meter instance ID 
        looking for assigned datapoint reference and return the related information in
        the format of [{'Id':'', 'FullRef':'', 'DatapointEnergyType':'', 'Unit':''}]. None is returned if no datapoint
        is assigned to the given meter or area.
        @param string instanceID: the instance ID of Area or Meter
        """
        instanceType = self.getInstanceType(instanceID)
        curosr = None
        if instanceType == "area":
            cursor = self.cursor.execute("SELECT ID, Instance FROM datapoint WHERE Area = ?", instanceID)
        elif instanceType == "meter":
            cursor = self.cursor.execute("SELECT ID, Instance FROM datapoint WHERE Meter = ?", instanceID)
        info = None
        if cursor is not None:
            rows = cursor.fetchall()
            if len(rows) > 0:
                info = []
                for row in rows:
                    item = {}
                    item["Id"] = row.ID
                    item["FullRef"] = row.Instance
                    cursor = self.cursor.execute("SELECT Type, Unit FROM datapoint_detail WHERE FullRef = ?", row.Instance)
                    row = cursor.fetchone()
                    item["EnergyType"] = row.Type
                    item["Unit"] = row.Unit
                    info.append(item)
        return info
    
    
    def getDatapointEnergyType(self, Energy_Type, Datapoint_Type):
        """
        with the given meter energy type and datapoint type (consumption or demand)
        return the datapoint energy type.
        """
        datapointTypeList = []
        for key, value in EnergyType.iteritems():
            if value == Energy_Type:
                datapointTypeList.append(key)
                
        for item in datapointTypeList:
            if DataPointType[item] == Datapoint_Type:
                return item
            
        
    ##############################################################    
    # report_rate_tlinstance and report_rate_data related methods
    ##############################################################
    def getDataPointID(self, areaMeterID, AggreEnergyType, dataPointType):
        """
        return the id of the datapoint which is assigned to the given meter 
    
        @param string AggreEnergyType   the energy type of datapoint, could be one of Electric_Energy, Gas_Volume, Water_Volume, ...
        @param string dataPointType:    the type of datapoint, could be one of ODT, DEMAND or CONSUMPTION
        """
        result = None
        if dataPointType == 'ODT':
            cursor = self.cursor.execute("SELECT ID FROM datapoint WHERE Area = ?", areaMeterID)
            row = cursor.fetchone()
            if row:
                result = row.ID
        else:
            cursor = self.cursor.execute("SELECT datapoint.ID, datapoint_detail.`Type` FROM datapoint LEFT JOIN datapoint_detail ON datapoint.Instance = datapoint_detail.FullRef WHERE datapoint.Meter = ?", areaMeterID)
            rows = cursor.fetchall()
            if rows:
                for row in rows:
                    if EnergyType[row.Type] == AggreEnergyType:
                        if DataPointType[row.Type] == dataPointType:
                            result = row.ID
                            break
        return result
    
    def getDataPointFullRef(self, areaMeterID, AggreEnergyType, dataPointType):
        """
        return the tlinstance full reference string of the given meter/area and its tlinstance type
    
        @param string AggreEnergyType   the energy type of datapoint, could be one of Electric_Energy, Gas_Volume, Water_Volume, ...
        @param string dataPointType:    the type of datapoint, could be one of ODT, DEMAND or CONSUMPTION
        """
        result = None
        datapointID = self.getDataPointID(areaMeterID, AggreEnergyType, dataPointType)
        if datapointID:
            cursor = self.cursor.execute("SELECT report_rate_tlinstance.FullRef FROM report_rate_tlinstance LEFT JOIN datapoint ON report_rate_tlinstance.FullRef = datapoint.Instance WHERE datapoint.ID = ?", datapointID)
            row = cursor.fetchone()
            if row:
                result = row.FullRef
        return result
    
    def getTLInstanceID(self, datapointFullRef):
        """
        return the tl ionstance Id of the given datapoint full reference.
        @param string datapointFullRef: example: //Mainsite/1100.AV201.Present_Value
        """
        result = None
        cursor = self.cursor.execute("SELECT ID FROM report_rate_tlinstance WHERE FullRef = ?", datapointFullRef)
        row = cursor.fetchone()
        if row:
            result = row.ID
        return result
    
    def getTLInstanceType(self, datapointFullRef):
        """
        return the tl ionstance Energy Type of the given datapoint full reference.
        @param string datapointFullRef: example: //Mainsite/1100.AV201.Present_Value
        """
        result = None
        cursor = self.cursor.execute("SELECT Type FROM datapoint_detail WHERE FullRef = ?", datapointFullRef)
        row = cursor.fetchone()
        if row:
            result = row.Type
        return result
    
    def getReport_Rate_Tlinstances(self, TLInstance_Under_Test=None):
        """
        search webgroup.report_rate_tlinstance table and return a list of tlinstance in the format of
        [{"FullRef": "//RV Site/1100.AV201.Value", "Type": "Historian"}]
        """
        result = None
        cursor = self.cursor.execute("select * from report_rate_tlinstance")
        rows = cursor.fetchall()
        if len(rows) > 0:
            result = []
            for row in rows:
                tlReference = {}
                tlReference["FullRef"] = (row.FullRef).encode('ascii', 'ignore')
                tlReference["Type"] = (row.Type).encode('ascii', 'ignore')
                if tlReference["Type"] == "Historian":
                    cursor = self.cursor.execute("select host from settings_historian where ID = ?", (row.Historian).encode('ascii', 'ignore'))
                    row = cursor.fetchone()
                    tlReference["Host"] = (row.host).encode('ascii', 'ignore')
                if tlReference["Type"] == "CopperCube":
                    cursor = self.cursor.execute("select IP from settings_archiver where ID = ?", (row.Historian).encode('ascii', 'ignore'))
                    row = cursor.fetchone()
                    tlReference["Host"] = (row.IP).encode('ascii', 'ignore')
                if TLInstance_Under_Test is not None:
                    for item in TLInstance_Under_Test:
                        if isinstance(item, str):
                            if tlReference["FullRef"] == item:
                                result.append(tlReference)
                        else:
                            if tlReference["FullRef"] == item[0]:
                                itemNew = dict(tlReference)
                                itemNew["Date Range"] = item[1]
                                result.append(itemNew)
                        
                else:
                    result.append(tlReference)
            
        return result
    
    def getRawTlinstanceID(self, datapointFullRef, ReturnTableName=True):
        """
        return TLInstance (TLInstance ID of Historian) from report_rate_tlinstnace if the tlInstance type is Historian
        return TLInstance and convert it to the name of tl table of coppercube if the tlinstance type is CopperCube
        
        @ReturnTableName - will return the coppercube table name instead of the raw tlinstance ID
        """
        result = None
        cursor = self.cursor.execute("select TLInstance, Type from report_rate_tlinstance where FullRef = ?", datapointFullRef)
        row = cursor.fetchone()
        if row is not None:
            result = (row.TLInstance).encode('ascii', 'ignore')
            if (row.Type).encode('ascii', 'ignore') == "CopperCube":
                if ReturnTableName:
                    result = result.lower()
                    result = result.replace('/', '_') 
                    result = result.replace('.', '_')
                    result = result[2:]
        return result
    
    def containsBaselineData(self, datapointFullRef):
        """
        return True if the assigned tl reference has baseline data assigned
        """
        cursor = self.cursor.execute("SELECT count(*) as total FROM webgroup.report_rate_data_baseline where FullRef = ?", datapointFullRef)
        row = cursor.fetchone()
        return row.total > 0
    
    def validateTimeStampInterpolation(self, datapointFullRef):
        """
        the samples timestamp should interpolated to 5 minutes interval in 
        report_rate_data table. verify and return a list of timestamps which
        is not interpolated to 5 minutets interval. return None if no one found
        """
        result = None
        tlinstanceID = self.getTLInstanceID(datapointFullRef)
        cursor = self.cursor.execute("select Timestamp from report_rate_data where tlinstance = ? and date_format(timestamp, '%i:%s') not in ('00:00','05:00','10:00','15:00','20:00','25:00','30:00','35:00','40:00','45:00','50:00','55:00');", tlinstanceID)
        rows = cursor.fetchall()
        if len(rows) > 0:
            result = []
            for row in rows:
                result.append(row.Timestamp)
        return result
    
    def validateTimeStampDuplication(self, datapointFullRef):
        """
        the samples timestamp should unique in report_rate_data table. 
        verify and return a list of timestamps which
        are duplicated. return None if no one found
        """
        result = None
        tlinstanceID = self.getTLInstanceID(datapointFullRef)
        cursor = self.cursor.execute("select TimeStamp, count(*) from report_rate_data where tlinstance = ? group by TimeStamp having count(*) > 1;", tlinstanceID)
        rows = cursor.fetchall()
        if len(rows) > 0:
            result = []
            for row in rows:
                result.append(row.Timestamp)
        return result
    
    def getTLInstanceTimeStamps(self, datapointFullRef):
        """
        return a list of timestamp (in datetime format) for the datapoint in report_rate_data table
        """
        tlinstanceID = self.getTLInstanceID(datapointFullRef)
        cursor = self.cursor.execute("select Timestamp from report_rate_data where tlinstance = ? order by timestamp asc", tlinstanceID)
        rows = cursor.fetchall()
        for row in rows:
            yield row.Timestamp
        
    
    def getTLInstanceStart(self, datapointFullRef, from_Data_Table=False):
        """
        looking for the first timestamp for the datapoint in report_rate_data table
        """
        tlinstanceID = self.getTLInstanceID(datapointFullRef)
        if from_Data_Table:    # get it from report_rate_data table
            cursor = self.cursor.execute("select Timestamp from report_rate_data where tlinstance = ? order by timestamp asc limit 1", tlinstanceID)
            row = cursor.fetchone()
            if row:
                return row.Timestamp
            else:
                import time
                time.sleep(1)
                cursor = self.cursor.execute("select Timestamp from report_rate_data where tlinstance = ? order by timestamp asc limit 1", tlinstanceID)
                row = cursor.fetchone()
                if row:
                    return row.Timestamp
                else:
                    return None
        else:    # directly get from report_rate_tlinstance table
            cursor = self.cursor.execute("select Start from report_rate_tlinstance where ID = ?", tlinstanceID)
            row = cursor.fetchone()
            return row.Start    
        
    def getTLInstanceFinish(self, datapointFullRef, from_Data_Table=False, fullDayCircle=False):
        """
        if from_Data_table is ture, looking for the last timestamp for the datapoint 
        in report_rate_data table
        otherwise direct get it from report_rate_tlinstance table
        if fullDayCircle is true, which means the day should have 288 records and the timestamp
        returned should be yyy-mm-dd 23:55:00. so if the day of last timestamp doesn't has full day
        samples (288) return the last sample of previous day.
        """
        tlinstanceID = self.getTLInstanceID(datapointFullRef)
        if from_Data_Table:    # get it from report_rate_data table
            cursor = self.cursor.execute("select Timestamp from report_rate_data where tlinstance = ? order by timestamp desc limit 1", tlinstanceID)
            row = cursor.fetchone()
            if not row:
                # try one more time
                import time
                time.sleep(1)
                cursor = self.cursor.execute("select Timestamp from report_rate_data where tlinstance = ? order by timestamp desc limit 1", tlinstanceID)
                row = cursor.fetchone()

            if row:
                if fullDayCircle:
                    myDay = (row.Timestamp).date()
                    myDayStr = myDay.strftime('%Y-%m-%d')
                    cursor = self.cursor.execute("select count(*) as total from report_rate_data where tlinstance = ? and date(timestamp) = ?", tlinstanceID, myDayStr)
                    newRow = cursor.fetchone()
                    if newRow.total == 288:
                        return row.Timestamp
                    else:
                        cursor = self.cursor.execute("select Timestamp from report_rate_data where tlinstance = ? and date(timestamp) < ? order by timestamp desc limit 1", tlinstanceID, myDayStr)
                        row = cursor.fetchone()
                        return row.Timestamp
                else:
                    return row.Timestamp
            else:
                return None
        else:    # directly get from report_rate_tlinstance table
            cursor = self.cursor.execute("select Finish from report_rate_tlinstance where ID = ?", tlinstanceID)
            row = cursor.fetchone()
            return row.Finish  
        
    def getTLInstanceTotalDays(self, datapointFullRef, fullDayCircle=False):
        """
        return how many days of records for the specifieced datapoint reference. 
        if fullDayCircle is true, it will omit days which doesn't have full records (288) 
        """
        tlinstanceID = self.getTLInstanceID(datapointFullRef)
        if fullDayCircle:
            finish = self.getTLInstanceFinish(datapointFullRef, from_Data_Table=True, fullDayCircle=True)
            finishStr = (finish.date()).strftime('%Y-%m-%d')
            cursor = self.cursor.execute("select count(*) as days from (select date(timestamp) from report_rate_data where tlinstance = ? and date(timestamp) <= ? group by date(timestamp)) as t", tlinstanceID, finishStr)
            row = cursor.fetchone()
            return row.days
        
        else:
            cursor = self.cursor.execute("select count(*) as days from (select date(timestamp) from report_rate_data where tlinstance = ? group by date(timestamp)) as t", tlinstanceID)
            row = cursor.fetchone()
            return row.days
        
    
    def getTLInstanceBaseLineStart(self, datapointFullRef):
        """
        looking for the first timestamp for the datapoint in report_rate_data_baseline table
        """
        result = None
        cursor = self.cursor.execute("SELECT Timestamp FROM report_rate_data_baseline where FullRef = ? order by Timestamp asc limit 1;", datapointFullRef)
        row = cursor.fetchone()
        if row:
            result = row.Timestamp
        return result
    
    def getTLInstanceBaseLineFinish(self, datapointFullRef, from_Tlinstance_Table=False):
        """
        looking for the last timestamp for the datapoint in report_rate_data_baseline table
        if from_Tlinstance_Table is true, get the timestamp from BaselineFinish in 
        report_rate_tlinstance table
        """
        result = None
        if from_Tlinstance_Table:
            cursor = self.cursor.execute("SELECT BaselineFinish FROM report_rate_tlinstance where FullRef = ?;", datapointFullRef)
            row = cursor.fetchone()
            if row:
                result = row.BaselineFinish
        else:
            cursor = self.cursor.execute("SELECT Timestamp FROM report_rate_data_baseline where FullRef = ? order by Timestamp desc limit 1;", datapointFullRef)
            row = cursor.fetchone()
            if row:
                result = row.Timestamp
        return result
    
    def isTimestampExisting(self, datapointFullRef, timeStamp):
        """
        verify a sample of the timestamp existing in report_rate_data table for the tl instance
        @param datetime timeStamp: timestamp in datetime format
        """
        tlinstanceID = self.getTLInstanceID(datapointFullRef)
        cursor = self.cursor.execute("select * from webgroup.report_rate_data where tlinstance = ? and timestamp = ?",
                                     tlinstanceID, timeStamp.strftime("%Y-%m-%d %H:%M:%S"))
        row = cursor.fetchone()
        if row is not None:
            return True
        else:
            return False
        
    def getTLInstanceDateTotalHours(self, datapointFullRef, dateString):
        """
        for the specified datapoint reference and date, look in report_rate_data table
        for how many hours it cover.
        """
        result = None
        tlinstanceID = self.getTLInstanceID(datapointFullRef)
        cursor = self.cursor.execute("select distinct hour(timestamp) from report_rate_data where tlinstance = ? and date(timestamp) = ?", tlinstanceID, dateString)
        rows = cursor.fetchall()
        if len(rows) > 0:
            result = len(rows)
        return result
        
    ################################################
    # datapoint and datapoint_group related methods
    ################################################
    def getDatapointGroup(self, Datapoint_Groups_Under_Test=None):
        """
        return a list of area meter datapoint groups from datapoint_group_map table
        """
        result = None
        cursor = self.cursor.execute("select `Group` from datapoint_group_map where Model in ('Meter', 'Area')")
        rows = cursor.fetchall()
        if len(rows) > 0:
            result = []
            for row in rows:
                groupID = row.Group
                if Datapoint_Groups_Under_Test is not None:
                    if groupID in Datapoint_Groups_Under_Test:
                        result.append(groupID)
                else:
                    result.append(groupID)
            
        return result
    
    
    def getTotalAreaMeterDatapointGroup(self):
        """
        using a different way verify and return a list of 
        area and meter id which should have datapoint group
        """
        result = []
        # calculate meter
        cursor = self.cursor.execute("select distinct Meter from datapoint where Meter is not NULL")
        rows = cursor.fetchall()
        if len(rows) > 0:
            meterList = []
            for row in rows:
                meterList.append((row.Meter).encode('ascii', 'ignore'))
            result.extend(meterList)
            meterList.append(' ')    # to prevent a single item tuple
            meterList = tuple(meterList)
            
            # calculate area of meter
            cursor = self.cursor.execute("select distinct Area from meter where ID in %s" %(meterList,))
            rows = cursor.fetchall()
            areaList = []
            for row in rows:
                areaList.append((row.Area).encode('ascii', 'ignore'))
            result.extend(areaList)
            areaList.append(' ')    # to prevent a single item tuple
            areaList = tuple(areaList)
            
            # calculate parent area
            finish = False
            while not finish:
                cursor = self.cursor.execute("select distinct Parent from area where ID in %s and Parent is not NULL" %(areaList,))
                rows = cursor.fetchall()
                if len(rows) > 0:
                    parentList = []
                    for row in rows:
                        item = (row.Parent).encode('ascii', 'ignore')
                        if item not in areaList:
                            parentList.append(item)
                    if len(parentList) == 0:
                        finish = True
                    else:
                        result.extend(parentList)
                        parentList.append(' ') # to prevent a single item tuple
                        areaList = tuple(parentList)
                else:
                    finish = True
        if len(result) == 0:
            result = None
        return result
    
    def getDatapoingGroupEnergyType(self, groupID):
        """
        search datapoint_group_data table and return a list of meter energy type for the group
        """
        result = None
        cursor = self.cursor.execute("select distinct Type from datapoint_group_data where `Group` = ?", groupID)
        rows = cursor.fetchall()
        if len(rows) > 0:
            result = []
            for row in rows:
                result.append(row.Type)
        return result
    
    def getDatapointGroupEnergyAggregation(self, groupID):
        """
        search datapoint_group_data table and return a list of Aggregation for the group
        """
        result = None
        cursor = self.cursor.execute("select distinct Aggregation from datapoint_group_data where `Group` = ?", groupID)
        rows = cursor.fetchall()
        if len(rows) > 0:
            result = []
            for row in rows:
                result.append(row.Aggregation)
        return result
    
    def getDatapointGroupAreaMeterID(self, groupID):
        """
        search datapoint_group_map table and return the Area or Meter instance ID for the group 
        """
        result = None
        cursor = self.cursor.execute("select Instance from datapoint_group_map where `Group` = ?", groupID)
        row = cursor.fetchone()
        if row:
            result = row.Instance
        return result
    
    def getDatapointGroupTLinstanceList(self, groupID, datapointEnergyType):
        """
        look for datapoints in datapoint_group_member table
        return a list of datapoint fullref which is associated with the group ID and datapoint energy type
        """
        result = None
        # get all the datapoints
        cursor = self.cursor.execute("select DataPoint from datapoint_group_member where `Group` = ?", groupID)
        rows = cursor.fetchall()
        if len(rows) > 0:
            result = []
            for row in rows:
                result.append(row.DataPoint)
        
        # convert to FullRef        
        if result:
            result_FullRef = []
            for item in result:
                cursor = self.cursor.execute("select Instance from datapoint where ID = ?", item)
                row = cursor.fetchone()
                if row:
                    result_FullRef.append(row.Instance)
            result = result_FullRef
        
        # pick up the one based on energy type    
        if result:
            result_Type = []
            for item in result:
                cursor = self.cursor.execute("select Type from datapoint_detail where FullRef = ?", item)
                row = cursor.fetchone()
                if row and (row.Type == datapointEnergyType):
                    result_Type.append(item)
            result = result_Type
            
        return result
        
    def validateDatapointGroupDateTotalHours(self, groupID, Energy_Type, Energy_Aggregation, dateString):
        """
        using a different way to verify the total hours for the give day. 
        this method is used to examine no missing hour samples in datapoint_group_data table
        """
        # define datapoint type
        datapointType = None
        if Energy_Aggregation == "Sum":
            datapointType = "CONSUMPTION"
        elif Energy_Aggregation in ("Avg", "Min", "Max"):
            datapointType = "DEMAND"
            
        datapointEnergyType = self.getDatapointEnergyType(Energy_Type, datapointType)
        
        TLInstanceList = self.getDatapointGroupTLinstanceList(groupID, datapointEnergyType)
        
        result = None
        for datapointFullRef in TLInstanceList:
            hours = self.getTLInstanceDateTotalHours(datapointFullRef, dateString)
            if hours:
                if result:
                    if hours > result:
                        result = hours
                else:
                    result = hours
                    
        return result
    
    
class Consumption(object):
    """
    class used to calculate energy consumption
    """
    
    DBInfo = settings.WebGroupDBConn
    AreaMeterList = []
    TLInstanceIDList = None
    DBConn = None
    MeterType = None
    DateRange = {"from": None, "to": None}
    Occupancy = {"from": None, "to": None, "days": None}
    
    @classmethod
    def _getTLInstanceIDList(cls):
        """
        helper method, which will convert and return a list
        of consumption tlinstnace ID 
        """
        try:
            webgroupdb = cls.DBConn
            if webgroupdb is None:
                webgroupdb = WebGroupDBObj(cls.DBInfo)
            
            # differentiate area and meter
            areas = []
            meters = []
            for item in cls.AreaMeterList:
                instanceID = webgroupdb.getAreaMeterInstanceID(item)
                if webgroupdb.getInstanceType(instanceID) == "area":
                    areas.append(instanceID)
                if webgroupdb.getInstanceType(instanceID) == "meter":
                    meters.append(instanceID)
                    
            # obtain meter list from Areas
            if len(areas) > 0:
                for areaInstanceID in areas:
                    meterList = webgroupdb.getMeterList(areaInstanceID, EnergyType=MeterTypes[cls.MeterType])
                    if meterList:
                        meters.extend(meterList)
                        
            # obtain datapoint info from each meter
            tlinstances = []
            if len(meters) > 0:
                for instanceID in meters:
                    datapointInfo = webgroupdb.getDataPointInfo(instanceID)
                    if datapointInfo:
                        for item in datapointInfo:
                            datapointFullRef = item["FullRef"]
                            datapointEnergyType = item["EnergyType"]
                            if webgroupdb.getDatapointEnergyType(Energy_Type=MeterTypes[cls.MeterType], Datapoint_Type="CONSUMPTION") == datapointEnergyType :
                                tlinstanceID = webgroupdb.getTLInstanceID(datapointFullRef)
                                tlinstances.append(tlinstanceID)
                         
            return tlinstances
        finally:
            del webgroupdb
        
    @classmethod
    def getTotal(cls):
        """
        get total consumption
        """
        return cls._getTotalBy()
    
    @classmethod
    def getTotalByYear(cls):
        """
        get total consumption group by year
        """
        return cls._getTotalBy(groupBy="YEAR")
    
    @classmethod
    def getTotalByMonth(cls):
        """
        get total consumption group by Month
        """
        return cls._getTotalBy(groupBy="MONTH")
    
    @classmethod
    def getTotalByWeek(cls):
        """
        get total consumption group by week
        """
        return cls._getTotalBy(groupBy="WEEK")
    
    @classmethod
    def getTotalByDay(cls):
        """
        get total consumption group by day
        """
        return cls._getTotalBy(groupBy="DAY")
    
    @classmethod
    def _getTotalBy(cls, groupBy=None):
        """
        helper method to get total consumption without grouping
        or group by Year, Month, Week, or Day
        """
        try:
            result = None
            tlinstances = cls.TLInstanceIDList
            if tlinstances is None:
                tlinstances = cls._getTLInstanceIDList()
            timestampFrom = cls.DateRange["from"]
            timestampTo = cls.DateRange["to"]
            webgroupdb = cls.DBConn
            if webgroupdb is None:
                webgroupdb = WebGroupDBObj(cls.DBInfo)
            placeholders = ",".join("?" * len(tlinstances))
            sqlStatement = None
            if groupBy == "YEAR":       # group by Year
                sqlStatement = "Select year(timestamp) as groupby, sum(somevalue) as total from " \
                               "(SELECT timestamp,sum(cast(value as decimal(38,10))) as somevalue " \
                               "FROM report_rate_data r " \
                               "where tlinstance in ({0}) " \
                               "and date(timestamp) between ? and ? " \
                               "group by timestamp) as r group by year(timestamp)".format(placeholders)
            
            elif groupBy == "MONTH":    # group by Month
                sqlStatement = "Select date_format(timestamp, '%Y-%m') as groupby, sum(somevalue) as total from " \
                               "(SELECT timestamp,sum(cast(value as decimal(38,10))) as somevalue " \
                               "FROM report_rate_data r " \
                               "where tlinstance in ({0}) " \
                               "and date(timestamp) between ? and ? " \
                               "group by timestamp" \
                               ") as r group by date_format(timestamp, '%Y-%m')".format(placeholders)
                
            elif groupBy == "WEEK":     # group by Week
                
                sqlStatement = "Select STR_TO_DATE(CONCAT(weekNum, ' Sunday'), '%X%V %W') as groupby, total from (" \
                               "Select yearweek(date) as weekNum, sum(somevalue) as total from (" \
                               "SELECT date(timestamp) as date, sum(cast(value as decimal(38,10))) as somevalue " \
                               "FROM report_rate_data r " \
                               "where tlinstance in ({0}) " \
                               "and date(timestamp) between ? and ? " \
                               "group by date(timestamp)" \
                               ") as r group by yearweek(date)) as t".format(placeholders)
                
            elif groupBy == "DAY":      # group by Day
                sqlStatement = "Select date(timestamp) as groupby, sum(somevalue) as total from (" \
                               "SELECT timestamp,sum(cast(value as decimal(38,10))) as somevalue " \
                               "FROM report_rate_data r " \
                               "where tlinstance in ({0}) " \
                               "and date(timestamp) between ? and ? " \
                               "group by timestamp" \
                               ") as r group by date(timestamp)".format(placeholders)
                
            else:                       # without grouping
                sqlStatement = "Select sum(somevalue) as total from " \
                               "(SELECT timestamp,sum(cast(value as decimal(38,10))) as somevalue " \
                               "FROM report_rate_data r " \
                               "where tlinstance in ({0}) " \
                               "and timestamp between ? and ? " \
                               "group by timestamp) as r".format(placeholders)
            params = []
            params.extend(tlinstances)
            params.append(timestampFrom)
            params.append(timestampTo)
            cursor = webgroupdb.cursor.execute(sqlStatement, params)
            
            if not groupBy:
                row = cursor.fetchone()
                if row:
                    result = row.total
            else:
                rows = cursor.fetchall()
                if len(rows) > 0:
                    result = []
                    for row in rows:
                        record = {'groupby': row.groupby, 'total': row.total}
                        result.append(record)
                
            return result
        finally:
            del webgroupdb
            
    @classmethod
    def getOccupied(cls):
        """
        get occupied consumption
        """
        return cls._getOccupiedBy()
    
    @classmethod
    def getOccupiedByYear(cls):
        """
        get occupied consumption group by Year
        """
        return cls._getOccupiedBy(groupBy="YEAR")
    
    @classmethod
    def getOccupiedByMonth(cls):
        """
        get occupied consumption group by month
        """
        return cls._getOccupiedBy(groupBy="MONTH")
    
    @classmethod
    def getOccupiedByWeek(cls):
        """
        get occupied consumption group by week
        """
        return cls._getOccupiedBy(groupBy="WEEK")
    
    @classmethod
    def getOccupiedByDay(cls):
        """
        get occupied consumption group by day
        """
        return cls._getOccupiedBy(groupBy="DAY")
    
    @classmethod
    def _getOccupiedBy(cls, groupBy=None):
        """
        helper method to get Occupied consumption without grouping or
        group by Year, Month, Week or Day
        """
        try:
            result = None
            tlinstances = cls._getTLInstanceIDList()
            timestampFrom = cls.DateRange["from"]
            timestampTo = cls.DateRange["to"]
            occupancyFrom = cls.Occupancy["from"]
            occupancyTo = cls.Occupancy["to"]
            occupancyDays = []
            for item in cls.Occupancy["days"]:
                occupancyDays.append(Days[item])
                
            webgroupdb = WebGroupDBObj(cls.DBInfo)
            placeholders01 = ",".join("?" * len(tlinstances))
            placeholders02 = ",".join("?" * len(occupancyDays))
            sqlStatement = None
            if groupBy == "YEAR":
                sqlStatement = "Select year(timestamp) as groupby, sum(somevalue) as total from (" \
                               "SELECT timestamp,sum(cast(value as decimal(38,10))) as somevalue " \
                               "FROM report_rate_data r " \
                               "where tlinstance in ({0}) " \
                               "and date(timestamp) between ? and ? " \
                               "and date_format(timestamp, '%T') between ? and ? " \
                               "and dayofweek(timestamp) in ({1}) " \
                               "group by timestamp" \
                               ") as r group by year(timestamp)".format(placeholders01,placeholders02)
                
            elif groupBy == "MONTH":
                sqlStatement = "Select date_format(timestamp, '%Y-%m') as groupby, sum(somevalue) as total from (" \
                               "SELECT timestamp,sum(cast(value as decimal(38,10))) as somevalue " \
                               "FROM report_rate_data r " \
                               "where tlinstance in ({0}) " \
                               "and date(timestamp) between ? and ? " \
                               "and date_format(timestamp, '%T') between ? and ? " \
                               "and dayofweek(timestamp) in ({1}) " \
                               "group by timestamp" \
                               ") as r group by date_format(timestamp, '%Y-%m')".format(placeholders01,placeholders02)
                               
            elif groupBy == "WEEK":
                sqlStatement = "Select STR_TO_DATE(CONCAT(weekNum, ' Sunday'), '%X%V %W') as groupby, total from (" \
                               "Select yearweek(date) as weekNum, sum(somevalue) as total from (" \
                               "SELECT date(timestamp) as date,sum(cast(value as decimal(38,10))) as somevalue " \
                               "FROM report_rate_data r " \
                               "where tlinstance in ({0}) " \
                               "and date(timestamp) between ? and ? " \
                               "and date_format(timestamp, '%T') between ? and ? " \
                               "and dayofweek(timestamp) in ({1}) " \
                               "group by date(timestamp)" \
                               ") as r group by yearweek(date)) as t".format(placeholders01,placeholders02)
                               
            elif groupBy == "DAY":
                sqlStatement = "Select date(timestamp) as groupby, sum(somevalue) as total from (" \
                               "SELECT timestamp,sum(cast(value as decimal(38,10))) as somevalue " \
                               "FROM report_rate_data r " \
                               "where tlinstance in ({0}) " \
                               "and date(timestamp) between ? and ? " \
                               "and date_format(timestamp, '%T') between ? and ? " \
                               "and dayofweek(timestamp) in ({1}) " \
                               "group by timestamp" \
                               ") as r group by date(timestamp)".format(placeholders01,placeholders02)
                               
            else:
                sqlStatement = "Select sum(somevalue) as total from " \
                               "(SELECT timestamp,sum(cast(value as decimal(38,10))) as somevalue " \
                               "FROM report_rate_data r " \
                               "where tlinstance in ({0}) " \
                               "and date(timestamp) between ? and ? " \
                               "and date_format(timestamp, '%T') between ? and ? " \
                               "and dayofweek(timestamp) in ({1}) " \
                               "group by timestamp) as r".format(placeholders01,placeholders02) 
            params = []
            params.extend(tlinstances)
            params.append(timestampFrom)
            params.append(timestampTo)
            params.append(occupancyFrom)
            params.append(occupancyTo)
            params.extend(occupancyDays)
            cursor = webgroupdb.cursor.execute(sqlStatement, params)
            if not groupBy:
                row = cursor.fetchone()
                if row:
                    result = row.total
            else:
                rows = cursor.fetchall()
                if len(rows) > 0:
                    result = []
                    for row in rows:
                        record = {'groupby': row.groupby, 'total': row.total}
                        result.append(record)
                
            return result
        finally:
            del webgroupdb
    
    @classmethod
    def getUnoccupied(cls):
        """
        get Unoccupied consumption
        """
        try:
            result = None
            tlinstances = cls._getTLInstanceIDList()
            timestampFrom = cls.DateRange["from"]
            timestampTo = cls.DateRange["to"]
            occupancyFrom = cls.Occupancy["from"]
            occupancyTo = cls.Occupancy["to"]
            occupancyDays = []
            for item in cls.Occupancy["days"]:
                occupancyDays.append(Days[item])
                
            webgroupdb = WebGroupDBObj(cls.DBInfo)
            placeholders01 = ",".join("?" * len(tlinstances))
            placeholders02 = ",".join("?" * len(occupancyDays))
            
            sqlStatement = "Select sum(somevalue) as total from " \
                           "(SELECT timestamp,sum(cast(value as decimal(38,10))) as somevalue " \
                           "FROM report_rate_data r " \
                           "where tlinstance in ({0}) " \
                           "and timestamp between ? and ? " \
                           "and " \
                           "((date_format(timestamp, '%T') not between ? and ? " \
                           "and dayofweek(timestamp) in ({1})) " \
                           "or " \
                           "dayofweek(timestamp) not in ({1})) " \
                           "group by timestamp) as r".format(placeholders01,placeholders02)
            params = []
            params.extend(tlinstances)
            params.append(timestampFrom)
            params.append(timestampTo)
            params.append(occupancyFrom)
            params.append(occupancyTo)
            params.extend(occupancyDays)
            params.extend(occupancyDays)
            cursor = webgroupdb.cursor.execute(sqlStatement, params)
            row = cursor.fetchone()
            if row:
                result = row.total
                
            return result
        finally:
            del webgroupdb
            
            
class Demand(object):
    """
    class used to calculate energy demand
    """
    
    DBInfo = settings.WebGroupDBConn
    AreaMeterList = []
    TLInstanceIDList = None
    DBConn = None
    MeterType = None
    DateRange = {"from": None, "to": None}
    Occupancy = {"from": None, "to": None, "days": None}
    
    @classmethod
    def _getTLInstanceIDList(cls):
        """
        helper method, which will convert and return a list
        of demand tlinstnace ID 
        """
        try:
            webgroupdb = cls.DBConn
            if webgroupdb is None:
                webgroupdb = WebGroupDBObj(cls.DBInfo)
            
            # differentiate area and meter
            areas = []
            meters = []
            for item in cls.AreaMeterList:
                instanceID = webgroupdb.getAreaMeterInstanceID(item)
                if webgroupdb.getInstanceType(instanceID) == "area":
                    areas.append(instanceID)
                if webgroupdb.getInstanceType(instanceID) == "meter":
                    meters.append(instanceID)
                    
            # obtain meter list from Areas
            if len(areas) > 0:
                for areaInstanceID in areas:
                    meterList = webgroupdb.getMeterList(areaInstanceID, EnergyType=MeterTypes[cls.MeterType])
                    if meterList:
                        meters.extend(meterList)
                        
            # obtain datapoint info from each meter
            tlinstances = []
            if len(meters) > 0:
                for instanceID in meters:
                    datapointInfo = webgroupdb.getDataPointInfo(instanceID)
                    if datapointInfo:
                        for item in datapointInfo:
                            datapointFullRef = item["FullRef"]
                            datapointEnergyType = item["EnergyType"]
                            if webgroupdb.getDatapointEnergyType(Energy_Type=MeterTypes[cls.MeterType], Datapoint_Type="DEMAND") == datapointEnergyType :
                                tlinstanceID = webgroupdb.getTLInstanceID(datapointFullRef)
                                tlinstances.append(tlinstanceID)
                         
            return tlinstances
        finally:
            del webgroupdb
        
    
    @classmethod
    def getAverage(cls):
        """
        get average demand
        """
        try:
            result = None
            tlinstances = cls.TLInstanceIDList
            if tlinstances is None:
                tlinstances = cls._getTLInstanceIDList()
            timestampFrom = cls.DateRange["from"]
            timestampTo = cls.DateRange["to"]
            webgroupdb = cls.DBConn
            if webgroupdb is None:
                webgroupdb = WebGroupDBObj(cls.DBInfo)
            placeholders = ",".join("?" * len(tlinstances))
            sqlStatement = "Select avg(somevalue) as average from " \
                           "(SELECT timestamp,sum(cast(value as decimal(38,10))) as somevalue " \
                           "FROM report_rate_data r " \
                           "where tlinstance in ({0}) " \
                           "and timestamp between ? and ? " \
                           "group by timestamp) as r".format(placeholders) 
            params = []
            params.extend(tlinstances)
            params.append(timestampFrom)
            params.append(timestampTo)
            cursor = webgroupdb.cursor.execute(sqlStatement, params)
            row = cursor.fetchone()
            if row:
                result = row.average
                
            return result
        finally:
            del webgroupdb
    
    @classmethod
    def getOccupiedMax(cls):
        """
        get occupied max demand
        """
        return cls._getOccupied("MAX")
    
    @classmethod
    def getOccupiedMin(cls):
        """
        get occupied min demand
        """
        return cls._getOccupied("MIN")
    
    @classmethod
    def _getOccupied(cls, valueType):
        """
        helper method to get Occupied Max and Min demand
        """
        try:
            result = None
            tlinstances = cls.TLInstanceIDList
            if tlinstances is None:
                tlinstances = cls._getTLInstanceIDList()
            timestampFrom = cls.DateRange["from"]
            timestampTo = cls.DateRange["to"]
            occupancyFrom = cls.Occupancy["from"]
            occupancyTo = cls.Occupancy["to"]
            occupancyDays = []
            for item in cls.Occupancy["days"]:
                occupancyDays.append(Days[item])
                
            webgroupdb = cls.DBConn
            if webgroupdb is None:
                webgroupdb = WebGroupDBObj(cls.DBInfo)
            placeholders01 = ",".join("?" * len(tlinstances))
            placeholders02 = ",".join("?" * len(occupancyDays))
            sqlStatement = "Select min(somevalue) as valuemin, max(somevalue) as valuemax from " \
                           "(SELECT timestamp,sum(cast(value as decimal(38,10))) as somevalue " \
                           "FROM report_rate_data r " \
                           "where tlinstance in ({0}) " \
                           "and timestamp between ? and ? " \
                           "and date_format(timestamp, '%T') between ? and ? " \
                           "and dayofweek(timestamp) in ({1}) " \
                           "group by timestamp) as r".format(placeholders01,placeholders02)
            params = []
            params.extend(tlinstances)
            params.append(timestampFrom)
            params.append(timestampTo)
            params.append(occupancyFrom)
            params.append(occupancyTo)
            params.extend(occupancyDays)
            cursor = webgroupdb.cursor.execute(sqlStatement, params)
            row = cursor.fetchone()
            if row:
                if valueType == "MAX":
                    result = row.valuemax
                if valueType == "MIN":
                    result = row.valuemin
                
            return result
        finally:
            del webgroupdb
    
    @classmethod
    def getUnoccupiedMax(cls):
        """
        get Unoccupied Max demand
        """
        return cls._getUnoccupied("MAX")
        
    @classmethod
    def getUnoccupiedMin(cls):
        """
        get Unoccupied Min demand
        """
        return cls._getUnoccupied("MIN")
    
    @classmethod
    def _getUnoccupied(cls, valueType):
        """
        helper method to get Unoccupied Max and Min demand
        """
        try:
            result = None
            tlinstances = cls._getTLInstanceIDList()
            timestampFrom = cls.DateRange["from"]
            timestampTo = cls.DateRange["to"]
            occupancyFrom = cls.Occupancy["from"]
            occupancyTo = cls.Occupancy["to"]
            occupancyDays = []
            for item in cls.Occupancy["days"]:
                occupancyDays.append(Days[item])
                
            webgroupdb = WebGroupDBObj(cls.DBInfo)
            placeholders01 = ",".join("?" * len(tlinstances))
            placeholders02 = ",".join("?" * len(occupancyDays))
            sqlStatement = "Select min(somevalue) as valuemin, max(somevalue) as valuemax from " \
                           "(SELECT timestamp,sum(cast(value as decimal(38,10))) as somevalue " \
                           "FROM report_rate_data r " \
                           "where tlinstance in ({0}) " \
                           "and timestamp between ? and ? " \
                           "and " \
                           "((date_format(timestamp, '%T') not between ? and ? " \
                           "and dayofweek(timestamp) in ({1})) " \
                           "or " \
                           "dayofweek(timestamp) not in ({1})) " \
                           "group by timestamp) as r".format(placeholders01,placeholders02)
            params = []
            params.extend(tlinstances)
            params.append(timestampFrom)
            params.append(timestampTo)
            params.append(occupancyFrom)
            params.append(occupancyTo)
            params.extend(occupancyDays)
            params.extend(occupancyDays)
            cursor = webgroupdb.cursor.execute(sqlStatement, params)
            row = cursor.fetchone()
            if row:
                if valueType == "MAX":
                    result = row.valuemax
                if valueType == "MIN":
                    result = row.valuemin
                
            return result
        finally:
            del webgroupdb
            
            
class AccessActivity(object):
    """
    class used filter query access activity event
    """
    
    db_info = settings.WebGroupDBConn
    db_conn = None
    
    @classmethod
    def get_filtered_events(cls, testData, timestamp_format=None):
        """
        return events info based on search criteria in testData
        """
        try:
            webgroupdb = cls.db_conn
            if webgroupdb is None:
                webgroupdb = WebGroupDBObj(cls.db_info)

            site          = testData.site
            date_range     = testData.dateRange
            card_users     = testData.cardUsers
            doors         = testData.doors
            events        = testData.events
            card_number    = testData.cardNumber
            site_code      = testData.siteCode
            params = []
            
            clause_string = "where SiteName = '%s'"%site
            clause_string += " and Time_Stamp %s"%cls._get_date_range(date_range)
            if events != "ALL":
                clause_string += " and EventType in %s"%(tuple(events),)
            card_users_range, selections = cls._get_objects_range(card_users)
            if card_users_range is not None:
                clause_string += " and CardUserName %s"%card_users_range
                params.extend(selections)
            doors_range, selections = cls._get_objects_range(doors)
            if doors_range is not None:
                clause_string += " and DeviceDoorObjectName %s"%doors_range
                params.extend(selections)
            if card_number is not None:
                clause_string += " and CardUserNumber = '%s'"%card_number
            if site_code is not None:
                clause_string += " and CardUsersiteCode = '%s'"%site_code
                
            
            sql_string = """select * from (select ID, str_to_date(TimeStamp, '%Y/%m/%d/%w %H:%i:%s') as Time_Stamp, SiteName, EventType, 
                           EventName, DeviceDoorRef, DeviceDoorObjectName, CardUserRef, CardUserName, CardUsersiteCode, CardUserNumber 
                           from (select access_event.ID, event.TimeStamp, access_event.SiteName, access_event.EventType, access_eventtype.`Value` 
                           as EventName, access_event.DeviceDoorRef, access_event.DeviceDoorObjectName, CONCAT_WS('', access_event.CardUserObjectAbbr, 
                           access_event.CardUserInstance) as CardUserRef, access_event.CardUserName, access_event.CardUsersiteCode, 
                           access_event.CardUserNumber from access_event left join access_eventtype on access_event.EventType = access_eventtype.ID 
                           left join event on access_event.ID = event.RecNo) as t) as t"""
                           
            sql_string += " %s;"%clause_string
             
            cursor = None
            if len(params) > 0:
                cursor = webgroupdb.cursor.execute(sql_string, params)
            else:               
                cursor = webgroupdb.cursor.execute(sql_string)
            rows = cursor.fetchall()
            
            result = []
            for row in rows:
                record = {}
                record["Timestamp"] = row.Time_Stamp
                if timestamp_format is not None:
                    record["Timestamp"] = cls._get_timestamp_format(row.Time_Stamp, timestamp_format)
                if row.CardUserName is None:
                    record["Card User"]  = ""
                else:
                    record["Card User"]  = row.CardUserName
                if row.CardUserNumber is None:
                    record["Card Number"] = ""
                else:
                    record["Card Number"] = row.CardUserNumber
                record["Door"] = (row.DeviceDoorObjectName).strip()
                record["Event Type"] = row.EventName
                result.append(record)
                
            return result
                
        
        finally:
            del webgroupdb
            
            
    @classmethod
    def _get_timestamp_format(cls, dt_timestamp, timestamp_format):
        """ change datetime of timestamp to a pre formatted datetime string """
        return dt_timestamp.strftime("%Y/%m/%d %I:%M %p")
        
            
            
    @classmethod
    def _get_objects_range(cls, objects_setting):
        """ helper used by get_filtered_events() """
        if objects_setting is None:
            return None, None
        elif objects_setting["Find Option"] == "Find by Keyword" and objects_setting["Filter By"] == "*":
            return None, None
        else:
            if objects_setting["Find Option"] == "Find by Keyword":
                key_word = list(objects_setting["Filter By"])
                if key_word[0] == "*":
                    key_word[0] = "%"
                if key_word[len(key_word) - 1] == "*":
                    key_word[len(key_word) - 1] = "%"
                key_word = "".join(key_word)
                return "like '%s'"%key_word, None
                
            elif objects_setting["Find Option"] == "Find and Select by Name":
                selections = []
                for object_setting in objects_setting["Filter By"]:
                    selections.append(object_setting[0])
                    placeholder = ",".join("?" * len(selections))
                return "in ({0})".format(placeholder), selections 
            
            
    @classmethod
    def _get_date_range(cls, date_range):
        """ helper used by get_filtered_events() """
        
        date_range_option = date_range[0]
        if date_range_option == "Custom":
            dt_from = date_range[1]
            dt_to = date_range[2]
            date_start = cls._get_date_string(dt_from[0])
            date_end = cls._get_date_string(dt_to[0])
            return "BETWEEN '%s %s' AND '%s %s'"%(date_start, dt_from[1], date_end, dt_to[1])
        elif date_range_option == "Today":
            date_string = datetime.date.today().strftime("%Y-%m-%d")
            return "BETWEEN '%s 00:00:00' AND '%s 23:59:59'"%(date_string, date_string)
        elif date_range_option == "Yesterday":
            date_string = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
            return "BETWEEN '%s 00:00:00' AND '%s 23:59:59'"%(date_string, date_string)
        elif date_range_option == "Previous 2 Days":
            date_start = (datetime.date.today() - datetime.timedelta(days=2)).strftime("%Y-%m-%d")
            date_end = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
            return "BETWEEN '%s 00:00:00' AND '%s 23:59:59'"%(date_start, date_end)
        elif date_range_option == "This Week":
            date_start = (datetime.datetime.today() - datetime.timedelta(days=datetime.datetime.today().isoweekday() % 7)).strftime("%Y-%m-%d")
            date_end = (datetime.datetime.today() + datetime.timedelta(days=6 - datetime.datetime.today().isoweekday() % 7)).strftime("%Y-%m-%d")
            return "BETWEEN '%s 00:00:00' AND '%s 23:59:59'"%(date_start, date_end)
        elif date_range_option == "Previous Week":
            target_date = datetime.date.today() - datetime.timedelta(days=7)
            date_start = (target_date - datetime.timedelta(days=target_date.isoweekday() % 7)).strftime("%Y-%m-%d")
            date_end = (target_date + datetime.timedelta(days=6 - target_date.isoweekday() % 7)).strftime("%Y-%m-%d")
            return "BETWEEN '%s 00:00:00' AND '%s 23:59:59'"%(date_start, date_end)
        elif date_range_option == "Previous 7 Days":
            date_start = (datetime.date.today() - datetime.timedelta(days=7)).strftime("%Y-%m-%d")
            date_end = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
            return "BETWEEN '%s 00:00:00' AND '%s 23:59:59'"%(date_start, date_end)
        elif date_range_option == "Previous 10 Days":
            date_start = (datetime.date.today() - datetime.timedelta(days=10)).strftime("%Y-%m-%d")
            date_end = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
            return "BETWEEN '%s 00:00:00' AND '%s 23:59:59'"%(date_start, date_end)
        elif date_range_option == "Previous 30 Days":
            date_start = (datetime.date.today() - datetime.timedelta(days=30)).strftime("%Y-%m-%d")
            date_end = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
            return "BETWEEN '%s 00:00:00' AND '%s 23:59:59'"%(date_start, date_end)
        elif date_range_option == "Month-to-Date":
            today = datetime.date.today()
            year = today.year
            month = today.month
            date_start = (datetime.date(year, month, 1)).strftime("%Y-%m-%d")
            date_end = today.strftime("%Y-%m-%d")
            return "BETWEEN '%s 00:00:00' AND '%s 23:59:59'"%(date_start, date_end)
        elif date_range_option == "Current Month":
            today = datetime.date.today()
            num_days = calendar.monthrange(today.year, today.month)
            date_start = (datetime.date(today.year, today.month, 1)).strftime("%Y-%m-%d")
            date_end = (datetime.date(today.year, today.month, num_days[1])).strftime("%Y-%m-%d")
            return "BETWEEN '%s 00:00:00' AND '%s 23:59:59'"%(date_start, date_end)
        elif date_range_option == "Previous Month":
            today = datetime.date.today()
            first_day = today.replace(day=1)
            day_of_last_month = first_day - datetime.timedelta(days=1)
            year = day_of_last_month.year
            month = day_of_last_month.month
            num_days = calendar.monthrange(year, month)
            date_start = (datetime.date(year, month, 1)).strftime("%Y-%m-%d")
            date_end = (datetime.date(year, month, num_days[1])).strftime("%Y-%m-%d")
            return "BETWEEN '%s 00:00:00' AND '%s 23:59:59'"%(date_start, date_end)
        elif date_range_option == "Year-to-Date":
            today = datetime.date.today()
            year = today.year
            date_start = (datetime.date(year, 1, 1)).strftime("%Y-%m-%d")
            date_end = today.strftime("%Y-%m-%d")
            return "BETWEEN '%s 00:00:00' AND '%s 23:59:59'"%(date_start, date_end)
        elif date_range_option == "Current Year":
            today = datetime.date.today()
            year = today.year
            date_start = (datetime.date(year, 1, 1)).strftime("%Y-%m-%d")
            date_end = (datetime.date(year, 12, 31)).strftime("%Y-%m-%d")
            return "BETWEEN '%s 00:00:00' AND '%s 23:59:59'"%(date_start, date_end)
        elif date_range_option == "Previous Year":
            today = datetime.date.today()
            year = today.year - 1
            date_start = (datetime.date(year, 1, 1)).strftime("%Y-%m-%d")
            date_end = (datetime.date(year, 12, 31)).strftime("%Y-%m-%d")
            return "BETWEEN '%s 00:00:00' AND '%s 23:59:59'"%(date_start, date_end)
        
        
    @classmethod    
    def _get_date_string(cls, date_string):
        """ helper used by _get_date_range() """
        if date_string == "%today%":
            return datetime.date.today().strftime("%Y-%m-%d")
        elif date_string == "%yesterday%":
            result = datetime.date.today() - datetime.timedelta(days=1)
            return result.strftime("%Y-%m-%d")
        elif date_string == "%tomorrow%":
            result = datetime.date.today() + datetime.timedelta(days=1)
            return result.strftime("%Y-%m-%d")
        else:
            return date_string    
    
        
if __name__ == "__main__":
    Consumption.AreaMeterList = ['div id="loader"\TestArea#1\Combined#1']
    Consumption.DateRange["from"] = '2015-01-01'
    Consumption.DateRange["to"] = '2015-11-18'
    Consumption.Occupancy["from"] = '09:00:00'
    Consumption.Occupancy["to"] = '16:59:59'
    Consumption.Occupancy["days"] = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
    Consumption.MeterType = 'Electrical Energy'
    Consumption.getTotal()
    
    
        
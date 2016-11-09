# FileName: DataSetup.py
# Description:
# setup testing data as an object model 

from lxml import etree


# ###############################################
# Classes to model base unit configuration data
# ###############################################
class Unit():
    def __init__(self):
        self.Value = ''
        self.Type = ''


class PointType():
    def __init__(self):
        self.Name = ''
        self.Units = []

    def getDefault(self, unitType):
        for unit in self.Units:
            if (unit.Type == unitType) or (unit.Type == 'Default'):
                return unit
            
    def getUnits(self):
        result = []
        for unit in self.Units:
            result.append(unit.Value)
        return result


class BaseUnits( ):
    def __init__(self, dataFile):
        self.PointTypes = {}    # a dictionary

        tree = etree.parse(dataFile)
        pointTypeElements = tree.findall('PointType')
        for pointTypeElem in pointTypeElements:
            myPointType = PointType()    # create a new pointtype data model
            myPointType.Name = pointTypeElem.get('Name')
            unitElements = pointTypeElem.findall('Unit')
            for unitElem in unitElements:
                myUnit = Unit()    # create a new unit data model
                myUnit.Value = unitElem.get('Value')
                myUnit.Type = unitElem.get('Type')
                myPointType.Units.append(myUnit)
            self.PointTypes[myPointType.Name] = myPointType

        del pointTypeElements
        del tree
                                       
        
    def getPointType(self, theName):
        ''' return the specified pointtype data '''
        myPointType = self.PointTypes.get(theName, None)
        return myPointType


    def getKeys(self):
        ''' return all defined keys from the test data model'''
        return self.PointTypes.keys()


# ###################################################
# Classes to model Area and Meter configuration data
# ###################################################
class DataPoint():
    def __init__(self):
        self.Type = ''
        self.Instance = ''
        self.Unit = ''


class Area():
    def __init__(self):
        self.Name = ''
        self.Type = ''
        self.NodePath = ''
        self.Address = ''
        self.Description=''
        self.Datapoint = None

    def getParent(self):
        '''return the name of parent area'''
        nodePath = self.NodePath
        nodes = nodePath.split('\\')
        return nodes[len(nodes) - 1]

    def getDatapointInstance(self):
        '''return the datapoint instance of the area'''
        return self.Datapoint.Instance

    def getDatapointUnit(self):
        '''return the datapoint unit of the area'''
        return self.Datapoint.Unit

    def getNodePath(self):
        '''return a formatted nodepath string based on NodePath field value'''
        if self.NodePath == '':
            return self.Name
        else:
            return self.NodePath + '\\' + self.Name


class Meter():
    def __init__(self):
        self.Name = ''
        self.Type = ''
        self.NodePath = ''
        self.Description = ''
        self.RateEngine = ''
        self.Datapoints = []

    def getArea(self):
        '''return the name of parent area'''
        nodePath = self.NodePath
        nodes = nodePath.split('\\')
        return nodes[len(nodes) - 1]

    def hasPointType(self, pointType):
        ''' verify if the meter contains the specified datapoint type '''
        result = False
        for dataPoint in self.Datapoints:
            if dataPoint.Type == pointType:
                result = True

        return result
        

    def getDatapointInstance(self, pointType):
        '''return the datapoint instance of the specified datapoint type'''
        instance = ''
        for dataPoint in self.Datapoints:
            if dataPoint.Type == pointType:
                instance = dataPoint.Instance
                break

        return instance

    def getDatapointUnit(self, pointType):
        '''return the datapoint unit of the specified datapoint type'''
        unit = ''
        for dataPoint in self.Datapoints:
            if dataPoint.Type == pointType:
                unit = dataPoint.Unit
                break

        return unit
                
    def getNodePath(self):
        '''return a formatted nodepath string based on NodePath field value'''
        if self.NodePath == '':
            return self.Name
        else:
            return self.NodePath + '\\' + self.Name
        

class AreaAndMeter():
    def __init__(self, dataFile):
        self.AreaList = []
        self.MeterList = []

        tree = etree.parse(dataFile)
        elements = tree.findall('Area')
        for elem in elements:
            myArea = Area()    # create a new Area data model
            myArea.Name = elem.get('Name')
            myArea.Type = elem.get('Type')
            myArea.NodePath = elem.get('NodePath')
            subElem = elem.find('Address')
            myArea.Address = subElem.get('Value')
            subElem = elem.find('Description')
            myArea.Description = subElem.get('Value')
            subElem = elem.find('Datapoint')
            myDatapoint = DataPoint()    # create a new datapoint data model
            myDatapoint.Type = subElem.get('Type')
            myDatapoint.Instance = subElem.get('Instance')
            myDatapoint.Unit = subElem.get('Unit')
            myArea.Datapoint = myDatapoint
            self.AreaList.append(myArea)

        elements = tree.findall('Meter')
        for elem in elements:
            myMeter = Meter()    # create a new Meter data model
            myMeter.Name = elem.get('Name')
            myMeter.Type = elem.get('Type')
            myMeter.NodePath = elem.get('NodePath')
            subElem = elem.find('Description')
            myMeter.Description = subElem.get('Value')
            subElem = elem.find('RateEngine')
            myMeter.RateEngine = subElem.get('Value')
            subElements = elem.findall('Datapoint')
            for subElem in subElements:
                myDatapoint = DataPoint()    # create a new Datapoint data model
                myDatapoint.Type = subElem.get('Type')
                myDatapoint.Instance = subElem.get('Instance')
                myDatapoint.Unit = subElem.get('Unit')
                myMeter.Datapoints.append(myDatapoint)
            self.MeterList.append(myMeter)

        del elements
        del tree
        
        
    def getRootAreas(self):
        '''return a list of all areas directly underneath the root'''
        areas = []
        for area in self.AreaList:
            if area.NodePath == '':
                areas.append(area)

        return areas


    def getChildAreas(self, areaObj):
        ''' return a list of child areas of the given area'''
        areas = []
        nodePath = areaObj.NodePath
        if nodePath != '':
            nodePath = nodePath + '\\' + areaObj.Name
        else:
            nodePath = areaObj.Name
        for area in self.AreaList:
            if area.NodePath == nodePath:
                areas.append(area)

        return areas


    def getMeters(self, areaObj):
        ''' return a list of meters which belongs to the given area'''
        meters = []
        nodePath = areaObj.NodePath
        if nodePath != '':
            nodePath = nodePath + '\\' + areaObj.Name
        else:
            nodePath = areaObj.Name
        for meter in self.MeterList:
            if meter.NodePath == nodePath:
                meters.append(meter)

        return meters


    def getDatapointInstances(self, areaObj, pointType, breakDown = False):
        '''
        it will return a list of all the datapoint instances of the give type
        it will follow the rules of area within area.
        '''
        instances = []
        if breakDown == False:
            children = self.getMeters(areaObj)    # get all meters directly underneath the given area
            if len(children) != 0:    # the given area containing meters
                for child in children:
                    if child.hasPointType(pointType):
                        instances.append(child.getDatapointInstance(pointType))
            else:    # the given area containing no meter
                children = self.getChildAreas(areaObj)
                if len(children) != 0:    # the given area containing sub areas
                    for child in children:
                        myLists = self.getDatapointInstances(child, pointType)
                        if len(myLists) != 0:
                            for item in myLists:
                                instances.append(item)
        else:    # is breakdown
            children = self.getChildAreas(areaObj)
            if len(children) != 0:
                for child in children:
                    myLists = self.getDatapointInstances(child, pointType)
                    if len(myLists) != 0:
                        for item in myLists:
                            instances.append(item)
            else:
                children = self.getMeters(areaObj)
                if len(children) != 0:
                    for child in children:
                        if child.hasPointType(pointType):
                            instances.append(child.getDatapointInstance(pointType))

        return instances



# #################################
# class to model energy type data
# #################################
class EnergyType( ):
    def __init__(self, dataFile):
        self.Energies = []    # a list

        tree = etree.parse(dataFile)
        elements = tree.findall('Energy')
        for elem in elements:
            self.Energies.append(elem.get('Name'))

        del elements
        del tree
        

if __name__ == "__main__":
    myAreaAndMeter = AreaAndMeter('AreaAndMeter.xml')
    for area in myAreaAndMeter.AreaList:
        print 'Area: ' + area.Name
        print 'Type: ' + area.Type
        print 'NodePath: ' + area.NodePath
        print 'Parent: ' + area.getParent()
        print 'Address: ' + area.Address
        print 'Description: ' + area.Description
        print 'Datapoint: ' + area.Datapoint.Type
        print 'Instance: ' + area.getDatapointInstance()
        print 'Unit: ' + area.getDatapointUnit()
        print ' '

    for meter in myAreaAndMeter.MeterList:
        print 'Meter: ' + meter.Name
        print 'Type: ' + meter.Type
        print 'NodePath: ' + meter.NodePath
        print 'Area: ' + meter.getArea()
        print 'Description: ' + meter.Description
        print 'RateEngine: ' + meter.RateEngine
        for datapoint in meter.Datapoints:
            print 'Datapoint: ' + datapoint.Type
            print 'Instance: ' + datapoint.Instance
            print 'Unit: ' + datapoint.Unit

    myLists = myAreaAndMeter.getRootAreas()
    rootArea = myLists[0]
    myLists = myAreaAndMeter.getChildAreas(rootArea)
    
    for item in myLists:
        print ' '
        print 'Area ' + item.Name + ' containing following meters:'
        meters = myAreaAndMeter.getMeters(item)
        if len(meters) != 0:
            for meter in meters:
                print meter.Name
        else:
            print 'no meters !'

    for item in myLists:
        print ' '
        print 'Area ' + item.Name + ' containing following sub areas: '
        areas = myAreaAndMeter.getChildAreas(item)
        if len(areas) != 0:
            for area in areas:
                print area.Name
        else:
            print 'no sub areas !'

   
    for item in myLists:
        print ' '
        print 'Area ' + item.Name + ' containing following Electricity Consumption datapoints:'
        datapoints = myAreaAndMeter.getDatapointInstances(item, 'Electricity Consumption')
        if len(datapoints) != 0:
            for datapoint in datapoints:
                print datapoint
        else:
            print 'no dtapoints !'

    for item in myLists:
        print ' '
        print 'Area ' + item.Name + ' containing following Electricity Consumption datapoints in breakdown view:'
        datapoints = myAreaAndMeter.getDatapointInstances(item, 'Electricity Consumption', True)
        if len(datapoints) != 0:
            for datapoint in datapoints:
                print datapoint
        else:
            print 'no datapoints!'
   


    del myAreaAndMeter
        
        
    
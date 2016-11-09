'''
Description:
auto calculate the combination of addon
Created on Jul 17, 2014

@author: User
'''

PointsList = range (5000, 302500, 2500)
CodesList = [[5000, 'enteliWEB-Ent'],
             [100000, 'enteliWEB-Ent-100000IO-AddOn'],
             [50000, 'enteliWEB-Ent-50000IO-AddOn'],
             [25000, 'enteliWEB-Ent-25000IO-AddOn'],
             [2500, 'enteliWEB-Ent-2500IO-AddOn']]

def calcuPoints(pointNumber):
    PointString = None
    result = pointNumber - CodesList[0][0]
    PointString = str(pointNumber) + "\n"
    PointString = PointString + CodesList[0][1] + " x 1\n"
    if result > 0:
        for j in range(1, len(CodesList)):
            i = 0
            while result >= CodesList[j][0]:
                result = result - CodesList[j][0]
                i = i + 1
            if i > 0:
                PointString = PointString + CodesList[j][1] + " x " + str(i) + "\n"
    return PointString
            


if __name__ == "__main__":
    for item in PointsList:
        print calcuPoints(item)

'''
Created on Feb 18, 2016

@author: hwang
'''
import datetime

def test_01():
    timestampBegin = datetime.datetime.strptime("2015-05-26 12:12:47", "%Y-%m-%d %H:%M:%S")
    timestampFinish = datetime.datetime.strptime("2016-02-12 14:29:53", "%Y-%m-%d %H:%M:%S")
    valueBegin = 2.0
    valueFinish = 703146.0

    timestampDiff = timestampFinish - timestampBegin
    valueDiff = valueFinish - valueBegin

    totalSeconds = timestampDiff.total_seconds()

    valuePerSec = valueDiff / totalSeconds

    valuePerDay = 24 * 60 * 60 * valuePerSec

    print "test_01 - estimated day consumption: %s"%valuePerDay
    
def test_02():
    '''
    Finds missing integer within an unsorted list and return a list of 
    missing items

    >>> find_missing_items([1, 2, 5, 6, 7, 10])
    [3, 4, 8, 9]

    >>> find_missing_items([3, 1, 2])
    []
    '''
    
    int_list = [3, 1, 2]
    timestamp_list = [datetime.datetime(2009, 10, 7, 0, 25), datetime.datetime(2009, 10, 7, 0, 30), datetime.datetime(2009, 10, 7, 0, 35), datetime.datetime(2009, 10, 7, 0, 40)]

    # Put the list in a set, find smallest and largest items
    original_set  = set(int_list)

    # Create a super set of all items from smallest to largest
    #full_set = set(xrange(smallest_item, largest_item + 1))
    full_set = set(xrange(min(original_set), max(original_set) + 1))

    # Missing items are the ones that are in the full_set, but not in
    # the original_set
    return sorted(full_set - original_set)

    
if __name__ == "__main__":
    print test_02()



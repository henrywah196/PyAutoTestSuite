'''
Created on Feb 18, 2015

@author: hwang
'''
import requests
from xml.etree import ElementTree

Base_URL = "http://192.168.50.99/cgi-bin/WSLicGen.exe/license"

setXML = "<License>"
setXML += "<PO>WAH20150220132001</PO>"
setXML += "<Partner>Software Licensing SQA Tester</Partner>"
setXML += "<Product>enteliweb_v2</Product>"
setXML += "<BaseSKU>"
setXML += "<ID>345713</ID>"
setXML += "<Name>enteliWEB-Ent</Name><!-- Optional -->"
setXML += "</BaseSKU>"
setXML += "<SKUList>"
setXML += "<SKU>"
setXML += "<Name>enteliWEB-Ent-100000IO-AddOn</Name> <!-- Optional -->"
setXML += "<ID>345827</ID>"
setXML += "<Qty>2</Qty>"
setXML += "</SKU>"
setXML += "<SKU>"
setXML += "<Name>enteliWEB-Ent-50000IO-AddOn</Name> <!-- Optional -->"
setXML += "<ID>345826</ID>"
setXML += "<Qty>1</Qty>"
setXML += "</SKU>"
setXML += "<SKU>"
setXML += "<Name>enteliWEB-Ent-2500IO-AddOn</Name> <!-- Optional -->"
setXML += "<ID>345796</ID>"
setXML += "<Qty>3</Qty>"
setXML += "</SKU>"
setXML += "<SKU>"
setXML += "<Name>eWEB-Ent-KEE-AddOn</Name> <!-- Optional -->"
setXML += "<ID>345809</ID>"
setXML += "<Qty>1</Qty>"
setXML += "</SKU>"
setXML += "<SKU>"
setXML += "<Name>eWEB-Ent-KEE-100000IO-AddOn</Name> <!-- Optional -->"
setXML += "<ID>345831</ID>"
setXML += "<Qty>2</Qty>"
setXML += "</SKU>"
setXML += "<SKU>"
setXML += "<Name>eWEB-Ent-KEE-50000IO-AddOn</Name> <!-- Optional -->"
setXML += "<ID>345830</ID>"
setXML += "<Qty>1</Qty>"
setXML += "</SKU>"
setXML += "<SKU>"
setXML += "<Name>eWEB-Ent-KEE-2500IO-AddOn</Name> <!-- Optional -->"
setXML += "<ID>345810</ID>"
setXML += "<Qty>3</Qty>"
setXML += "</SKU>"
setXML += "<SKU>"
setXML += "<Name>eWEB-Ent-API-AddOn</Name> <!-- Optional -->"
setXML += "<ID>345823</ID>"
setXML += "<Qty>1</Qty>"
setXML += "</SKU>"
setXML += "</SKUList>"
setXML += "</License>"
      
setHeaders = {'Accept' : 'text/xml',
              'Content-length' : len(setXML)} 

r = requests.post(Base_URL, data=setXML, headers=setHeaders)

print(r.url)
print (r.text)
element = ElementTree.fromstring(r.text)
element = element.find("LicenseSerial")
element = element.find("SerialNumber")
licenseSerial = element.text
print ("Licenser Serial: %s"%licenseSerial)

setXML = "<License>"
setXML += "<PO>WAH20150220132002</PO>"
setXML += "<Partner>Software Licensing SQA Tester</Partner>"
setXML += "<Product>enteliweb_v2</Product>"
setXML += "<BaseSKU>"
setXML += "<ID>345713</ID>"
setXML += "<Name>enteliWEB-Ent</Name><!-- Optional -->"
setXML += "</BaseSKU>"
setXML += "<VMInfo><!-- Optional -->"
setXML += "<SiteName>Toyota Inc</SiteName>"
setXML += "<SiteAddress>Toyota Dr, Montreal, QC</SiteAddress>"
setXML += "</VMInfo>"
setXML += "<SKUList>"
setXML += "<SKU>"
setXML += "<Name>enteliWEB-Ent-100000IO-AddOn</Name> <!-- Optional -->"
setXML += "<ID>345827</ID>"
setXML += "<Qty>2</Qty>"
setXML += "</SKU>"
setXML += "<SKU>"
setXML += "<Name>enteliWEB-Ent-50000IO-AddOn</Name> <!-- Optional -->"
setXML += "<ID>345826</ID>"
setXML += "<Qty>1</Qty>"
setXML += "</SKU>"
setXML += "<SKU>"
setXML += "<Name>enteliWEB-Ent-2500IO-AddOn</Name> <!-- Optional -->"
setXML += "<ID>345796</ID>"
setXML += "<Qty>3</Qty>"
setXML += "</SKU>"
setXML += "<SKU>"
setXML += "<Name>eWEB-Ent-KEE-AddOn</Name> <!-- Optional -->"
setXML += "<ID>345809</ID>"
setXML += "<Qty>1</Qty>"
setXML += "</SKU>"
setXML += "<SKU>"
setXML += "<Name>eWEB-Ent-KEE-100000IO-AddOn</Name> <!-- Optional -->"
setXML += "<ID>345831</ID>"
setXML += "<Qty>2</Qty>"
setXML += "</SKU>"
setXML += "<SKU>"
setXML += "<Name>eWEB-Ent-KEE-50000IO-AddOn</Name> <!-- Optional -->"
setXML += "<ID>345830</ID>"
setXML += "<Qty>1</Qty>"
setXML += "</SKU>"
setXML += "<SKU>"
setXML += "<Name>eWEB-Ent-KEE-2500IO-AddOn</Name> <!-- Optional -->"
setXML += "<ID>345810</ID>"
setXML += "<Qty>3</Qty>"
setXML += "</SKU>"
setXML += "<SKU>"
setXML += "<Name>eWEB-Ent-API-AddOn</Name> <!-- Optional -->"
setXML += "<ID>345823</ID>"
setXML += "<Qty>1</Qty>"
setXML += "</SKU>"
setXML += "<SKU>"
setXML += "<Name>eWEB-Ent-EV-AddOn</Name> <!-- Optional -->"
setXML += "<ID>345801</ID>"
setXML += "<Qty>1</Qty>"
setXML += "</SKU>"
setXML += "<SKU>"
setXML += "<Name>eWEB-Ent-VM-AddOn</Name> <!-- Optional -->"
setXML += "<ID>345819</ID>"
setXML += "<Qty>1</Qty>"
setXML += "</SKU>"
setXML += "</SKUList>"
setXML += "<LicenseSerial>"
setXML += "<SerialNumber>" + licenseSerial + "</SerialNumber>"
setXML += "</LicenseSerial>"
setXML += "</License>"

setHeaders = {'Accept' : 'text/xml',
              'Content-length' : len(setXML)} 

r = requests.put(Base_URL, data=setXML, headers=setHeaders)

print("\nAfter update...")
print(r.url)
print (r.text)
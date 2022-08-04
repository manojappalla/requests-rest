import requests
from PyQt5.QtCore import Qt, QSettings, QSize,QVariant, QTranslator, qVersion, QCoreApplication
import xml.etree.ElementTree as ET

def qtype(odktype):
    if odktype == 'binary':
        return QVariant.String,{'DocumentViewer': 2, 'DocumentViewerHeight': 0, 'DocumentViewerWidth': 0, 'FileWidget': True, 'FileWidgetButton': True, 'FileWidgetFilter': '', 'PropertyCollection': {'name': None, 'properties': {}, 'type': 'collection'}, 'RelativeStorage': 0, 'StorageMode': 0}
    elif odktype=='string':
        return QVariant.String,{}
    elif odktype[:3] == 'sel' :
        return QVariant.String,{}
    elif odktype[:3] == 'int':
        return QVariant.Int, {}
    elif odktype[:3]=='dat':
        return QVariant.Date, {}
    elif odktype[:3]=='ima':
        return QVariant.String,{'DocumentViewer': 2, 'DocumentViewerHeight': 0, 'DocumentViewerWidth': 0, 'FileWidget': True, 'FileWidgetButton': True, 'FileWidgetFilter': '', 'PropertyCollection': {'name': None, 'properties': {}, 'type': 'collection'}, 'RelativeStorage': 0, 'StorageMode': 0}
    elif odktype == 'Hidden':
        return 'Hidden'
    else:
        return (QVariant.String),{}

def getProxiesConf():
    s = QSettings() #getting proxy from qgis options settings
    proxyEnabled = s.value("proxy/proxyEnabled", "")
    proxyType = s.value("proxy/proxyType", "" )
    proxyHost = s.value("proxy/proxyHost", "" )
    proxyPort = s.value("proxy/proxyPort", "" )
    proxyUser = s.value("proxy/proxyUser", "" )
    proxyPassword = s.value("proxy/proxyPassword", "" )
    if proxyEnabled == "true" and proxyType == 'HttpProxy': # test if there are proxy settings
        proxyDict = {
            "http"  : "http://%s:%s@%s:%s" % (proxyUser,proxyPassword,proxyHost,proxyPort),
            "https" : "http://%s:%s@%s:%s" % (proxyUser,proxyPassword,proxyHost,proxyPort)
        }
        return proxyDict
    else:
        return None

user = 'manojappalla'
password = 'Zekrom1997'
turl = 'https://kobo.humanitarianresponse.info/'

def assets():
    url = turl+'/assets/'
    para = {'format':'json'}
    response = requests.get(url, proxies=getProxiesConf(), auth=(user, password), params=para)
    forms = response.json()
    print(forms)

def particularAsset():
    url = turl+'/assets/'+'aumGeYCKpLmoK6jkcDgcUv'
    para = {'format':'xml'}
    response = requests.get(url, proxies=getProxiesConf(), auth=(user, password), params=para)
    xml = response.content
    return xml

def updateLayerXML():

    # THIS SET OF STATEMENTS IS USED TO ACCESS ROOT, LAYER_NAME, AND INSTANCE
    geoField = ''
    ns = '{http://www.w3.org/2002/xforms}'
    nsh = '{http://www.w3.org/1999/xhtml}'
    root = ET.fromstring(particularAsset())
    # key= root[0][1][0][0].attrib['id']
    layer_name = root[0].find(nsh + 'title').text
    instance = root[0][1].find(ns + 'instance')
    fields = {}
    # print(root)
    print(layer_name)
    # print(instance)

    for bind in root[0][1].findall(ns + 'bind'): # THIS IS OBTAINED FROM BIND TAG

        # THIS SET OF STATEMENTS PRINT THE FIELD NAME AND TYPE OF THE INPUTS FROM THE SELECTED FORM
        attrib = bind.attrib
        # print(attrib)
        fieldName = attrib['nodeset'].split('/')[-1]
        fieldType = attrib['type']


        # PRINT QGSTYPE AND CONFIG
        fields[fieldName]=fieldType

        qgstype, config = qtype(attrib['type'])
        print(qgstype, config) # TODO: didn't understand
        inputs = root[1].findall('.//*[@ref]') # THI IS OBTAINED FROM INPUTS TAG

        if fieldType[:3] != 'geo':
            # print('creating new field:'+ fieldName)
            isHidden = True
            if fieldName == 'instanceID':
                fieldName = 'ODKUUID'
                fields[fieldName] = fieldType
                isHidden = False
            for input in inputs:
                if fieldName == input.attrib['ref'].split('/')[-1]:
                    isHidden = False
                    break
            if isHidden:
                print('Reached Hidden')
                config['type'] = 'Hidden'
        else:
            geoField = fieldName
            print('geometry field is =', fieldName)
            continue

    print("Field names and types dictionary: {}".format(fields))
    print(inputs)
updateLayerXML()
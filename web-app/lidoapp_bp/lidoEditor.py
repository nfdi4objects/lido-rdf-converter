import sys
sys.path.insert(0, '..')
from pathlib import Path
from x3ml import getMapping, getNamespaces,ExP
import LidoRDFConverter as LRC
from lxml import etree

def dlftMappingFile(): return './defaultMapping.x3ml'
def dlftLidoFile(): return './defaultLido.xml'

def workFolder(): return './work'
def workMappingFile(): return workFolder()+'/mapping.x3ml'
def workLidoFile(): return workFolder()+'/lido.xml'

def makeWorkspace():
    Path(workFolder()).mkdir(exist_ok=True)
    mFile = Path(workMappingFile())
    if not mFile.exists():
        mFile.write_text(Path(dlftMappingFile()).read_text())
    sFile = Path(workLidoFile())
    if not sFile.exists():
        sFile.write_text(Path(dlftLidoFile()).read_text())

def fromFile(fname):
    return Path(fname).read_text()

def toFile(fname,data):
    Path(fname).write_text(data)
    return fname

def dfltLidoText(): 
    return fromFile(dlftLidoFile())

def workLidoText():
    return fromFile(workLidoFile())

def processString(lidoString,mapingFile=workMappingFile()):
    fmt = 'turtle'
    result = '<no-data/>'
    if lidoFile := toFile(workLidoFile(),lidoString):
        converter = LRC.LidoRDFConverter(mapingFile)
        graph,_ = converter.processXML(lidoFile)
        result = graph.serialize(format=fmt)
    return result

def processRequest(request,mapingFile=workMappingFile()):
    return processString(request.json['xmlData'],mapingFile)

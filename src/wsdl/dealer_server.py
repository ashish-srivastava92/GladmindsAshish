##################################################
# file: dealer_server.py
#
# skeleton generated by "ZSI.generate.wsdl2dispatch.ServiceModuleWriter"
#      /usr/bin/wsdl2py -b dealer.wsdl
#
##################################################

from ZSI.schema import GED, GTD
from ZSI.TCcompound import ComplexType, Struct
from dealer_types import *
from ZSI.ServiceContainer import ServiceSOAPBinding

# Messages  
GetDealerInput = GED("http://www.example.org/dealer/", "dealerInput").pyclass

GetDealerOutput = GED("http://www.example.org/dealer/", "dealerOutput").pyclass


# Service Skeletons
class dealer(ServiceSOAPBinding):
    soapAction = {}
    root = {}

    def __init__(self, post='/', **kw):
        ServiceSOAPBinding.__init__(self, post)

    def soap_getDealer(self, ps, **kw):
        request = ps.Parse(GetDealerInput.typecode)
        return request,GetDealerOutput()

    soapAction['http://www.example.org/productPurchase/GetDealer'] = 'soap_getDealer'
    root[(GetDealerInput.typecode.nspname,GetDealerInput.typecode.pname)] = 'soap_getDealer'


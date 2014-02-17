##################################################
# file: dealer_client.py
# 
# client stubs generated by "ZSI.generate.wsdl2python.WriteServiceModule"
#     /usr/bin/wsdl2py -b dealer.wsdl
# 
##################################################

from dealer_types import *
import urlparse, types
from ZSI.TCcompound import ComplexType, Struct
from ZSI import client
from ZSI.schema import GED, GTD
import ZSI
from ZSI.generate.pyclass import pyclass_type

# Locator
class dealerLocator:
    dealerSOAP_address = "http://www.example.org/"
    def getdealerSOAPAddress(self):
        return dealerLocator.dealerSOAP_address
    def getdealerSOAP(self, url=None, **kw):
        return dealerSOAPSOAP(url or dealerLocator.dealerSOAP_address, **kw)

# Methods
class dealerSOAPSOAP:
    def __init__(self, url, **kw):
        kw.setdefault("readerclass", None)
        kw.setdefault("writerclass", None)
        # no resource properties
        self.binding = client.Binding(url=url, **kw)
        # no ws-addressing

    # op: getDealer
    def getDealer(self, request, **kw):
        if isinstance(request, GetDealerInput) is False:
            raise TypeError, "%s incorrect request type" % (request.__class__)
        # no input wsaction
        self.binding.Send(None, None, request, soapaction="http://www.example.org/productPurchase/GetDealer", **kw)
        # no output wsaction
        response = self.binding.Receive(GetDealerOutput.typecode)
        return response

GetDealerInput = GED("http://www.example.org/dealer/", "dealerInput").pyclass

GetDealerOutput = GED("http://www.example.org/dealer/", "dealerOutput").pyclass

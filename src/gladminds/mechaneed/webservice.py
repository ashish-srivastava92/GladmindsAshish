from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from spyne.application import Application
from spyne.protocol.soap import Soap11
from spyne.server.django import DjangoApplication
from gladminds.bajajib.services.coupons import feed_models as fsc_feed

tns = settings.IB_WSDL_TNS

all_app = Application([fsc_feed.BrandService,
                       fsc_feed.DealerService,
                       fsc_feed.ProductDispatchService,
                       fsc_feed.ProductPurchaseService,
                       fsc_feed.ASCService,
                       ],
                      tns=tns,
                      in_protocol=Soap11(validator='lxml'),
                      out_protocol=Soap11()
                      )

brand_app = Application([fsc_feed.BrandService],
                        tns=tns,
                        in_protocol=Soap11(validator='lxml'),
                        out_protocol=Soap11()
                        )

dealer_app = Application([fsc_feed.DealerService],
                         tns=tns,
                         in_protocol=Soap11(validator='lxml'),
                         out_protocol=Soap11()
                         )

asc_app = Application([fsc_feed.ASCService],
                         tns=tns,
                         in_protocol=Soap11(validator='lxml'),
                         out_protocol=Soap11()
                         )

dispatch_app = Application([fsc_feed.ProductDispatchService],
                           tns=tns,
                           in_protocol=Soap11(validator='lxml'),
                           out_protocol=Soap11()
                           )

purchase_app = Application([fsc_feed.ProductPurchaseService],
                           tns=tns,
                           in_protocol=Soap11(validator='lxml'),
                           out_protocol=Soap11()
                           )

all_service = csrf_exempt(DjangoApplication(all_app))
brand_service = csrf_exempt(DjangoApplication(brand_app))
dealer_service = csrf_exempt(DjangoApplication(dealer_app))
asc_service = csrf_exempt(DjangoApplication(asc_app))
dispatch_service = csrf_exempt(DjangoApplication(dispatch_app))
purchase_service = csrf_exempt(DjangoApplication(purchase_app))

from django.core.management.base import BaseCommand

from gladminds.core.auth.service_handler import Services
from gladminds.default import models


_BAJAJ_SERVICES = [Services.AFTERBUY, Services.FREE_SERVICE_COUPON, Services.LOYALTY, Services.SERVICE_DESK]
_BAJAJIB_SERVICES = [Services.AFTERBUY, Services.FREE_SERVICE_COUPON, Services.LOYALTY, Services.SERVICE_DESK]
_DEMO_SERVICES = [Services.SERVICE_DESK]
_DAIMLER_SERVICES = [Services.SERVICE_DESK]
_INDUSTRIES = ['automobiles']
_BRANDS = {'bajaj': [_INDUSTRIES[0]], 'demo': [_INDUSTRIES[0]], 'daimler': [_INDUSTRIES[0]], 'bajajib': [_INDUSTRIES[0]]}

class Command(BaseCommand): 
    
    def handle(self, *args, **options):
        self.create_service_types()
        self.create_services()
        self.create_industries()
        self.create_brands()
        self.create_brands_services()
        
    def create_service_types(self):
        for service in _BAJAJ_SERVICES:
            try:
                service_obj = models.ServiceType.objects.get(name=service)
                print "service type {0} already exists.".format(service)
            except:
                print "service type {0} does not exists, creating that.".format(service)
                service_obj = models.ServiceType(name=service)
                service_obj.save()
    
    def create_services(self):
        for service in _BAJAJ_SERVICES:
            service_type_obj = models.ServiceType.objects.filter(name=service)
            if len(service_type_obj) > 0:
                try:
                    service_obj = models.Service.objects.get(name=service)
                except:
                    print "service {0} does not exists, creating that.".format(service)
                    service_obj = models.Service(name=service, service_type=service_type_obj[0])
                    service_obj.save()
            else:
                print "service type {0} does not exists.Check create_service_types to create service.".format(service)
                
                
    def create_industries(self):
        for industry in _INDUSTRIES:
            try:
                industry_obj = models.Industry.objects.get(name=industry)
                print "Industry {0} already exists.".format(industry)
            except:
                print "Industry {0} does not exists, creating that.".format(industry)
                industry_obj = models.Industry(name=industry)
                industry_obj.save()
                
    def create_brands(self):
        for brand in _BRANDS:
            for industry in _BRANDS[brand]:
                industry_obj = models.Industry.objects.filter(name=industry)
                if len(industry_obj) > 0:
                    try:
                        brand_obj = models.Brand.objects.get(name=brand, industry=industry_obj[0])
                    except:
                        print "Brand {0} with industry {1} does not exists, creating that.".format(brand, industry)
                        brand_obj = models.Brand(name=brand, industry=industry_obj[0])
                        brand_obj.save()
                else:
                    print "Industry {0} does not exists.Check create_industries to create industry.".format(industry)
                    
                    
    def create_brands_services(self):
        for brand in _BRANDS:
            for industry in _BRANDS[brand]:
                brand_obj = models.Brand.objects.filter(name=brand, industry__name=industry)
                if len(brand_obj)>0:
                    if brand == 'bajaj':
                        SERVICES = _BAJAJ_SERVICES
                    if brand == 'bajajib':
                        SERVICES = _BAJAJIB_SERVICES
                    elif brand == 'demo':
                        SERVICES = _DEMO_SERVICES
                    elif brand == 'daimler':
                        SERVICES = _DAIMLER_SERVICES
                    for service in SERVICES:                        
                        try:
                            brand_service_obj = models.BrandService.objects.get(brand=brand_obj[0],
                                                                                service__name=service)
                        except:
                            print "Brand {0} with service {1} does not exists, creating that.".format(brand, service)
                            service_obj = models.Service.objects.get(name=service)
                            brand_service_obj = models.BrandService(brand=brand_obj[0], service=service_obj)
                            brand_service_obj.save()
                else:
                    print "Brand {0} by industry {1} does not exists.".format(brand, industry)
                    
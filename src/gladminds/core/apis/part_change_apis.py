import csv
from datetime import datetime
import json
import logging
import itertools

from django.conf import settings
from django.conf.urls import url
from django.forms.models import model_to_dict
from django.core.exceptions import ObjectDoesNotExist
from django.http.response import HttpResponse, HttpResponseBadRequest
from tastypie import fields
from tastypie.authorization import Authorization
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie.utils.urls import trailing_slash

from gladminds.core.apis.authentication import AccessTokenAuthentication
from gladminds.core.apis.base_apis import CustomBaseModelResource
from gladminds.core.core_utils.utils import format_part_csv
from gladminds.core.model_fetcher import get_model



LOG = logging.getLogger('gladminds')

class BrandVerticalResource(CustomBaseModelResource):
    '''
       Resource for all the verticals of a brand
    '''
    class Meta:
        queryset = get_model('BrandVertical').objects.all()
        resource_name = "brand-verticals"
        authorization = Authorization()
        authentication = AccessTokenAuthentication()
        detail_allowed_methods = ['get', 'post']
        always_return_data = True
        filtering = {
                     "name" : ALL
                     }
        
class BrandProductRangeResource(CustomBaseModelResource):
    '''
       Resource for all the product range of a brand
    '''
    class Meta:
        queryset = get_model('BrandProductRange').objects.all()
        resource_name = "brand-product-range"
        authorization = Authorization()
        authentication = AccessTokenAuthentication()
        detail_allowed_methods = ['get', 'post']
        always_return_data = True 
        filtering = {
                     "sku_code": ALL,
                     }
        
    def dehydrate(self, bundle):
        if bundle.data['image_url']:
            bundle.data['image_url'] = bundle.data['image_url'].split('?')[0]
        return bundle    
    
class BOMHeaderResource(CustomBaseModelResource):
    '''
       Resource for all the SKU-code BOM number association
    '''
    class Meta:
        queryset = get_model('BOMHeader').objects.all()
        resource_name = 'bom-headers'
        authorization = Authorization()
        authentication = AccessTokenAuthentication()
        detail_allowed_methods = ['get', 'post'] 
        always_return_data = True
        include_resource_uri = False
        filtering = {
                     "sku_code" : ALL,
                     "bom_number" : ALL
                     }
        
class BOMPlateResource(CustomBaseModelResource):
    '''
       Resource for all the plates included in a BOM
    '''
    class Meta:
        queryset = get_model('BOMPlate').objects.all()
        resource_name = 'bom-plates'
        authorization = Authorization()
        authentication = AccessTokenAuthentication()
        detail_allowed_method = ['get', 'post']
        always_return_data = True
        include_resource_uri = False
        filtering = {
                     "plate_id" : ALL
                     }
        
class BOMPartResource(CustomBaseModelResource):
    '''
       Resource for all the parts included in a BOM
    '''
    class Meta:
        queryset = get_model('BOMPart').objects.all()
        resource_name = 'bom-parts'
        authorization = Authorization()
        authentication = AccessTokenAuthentication()
        always_return_date = True
        include_resource_uri = False
        filtering = {
                     "part_number" : ALL
                     }
        
        
class BOMPlatePartResource(CustomBaseModelResource):
    '''
       Resource for BOMheader, plate and part associations
    '''
    bom = fields.ForeignKey(BOMHeaderResource, 'bom', null=True , blank=True)
    plate = fields.ForeignKey(BOMPlateResource, 'plate', null=True, blank=True, full=True)
    part = fields.ForeignKey(BOMPartResource, 'part', null=True, blank=True, full=True)
    class Meta:
        queryset = get_model('BOMPlatePart').objects.all()
        resource_name = 'bom-plate-parts'
        authorization = Authorization()
        authentication = AccessTokenAuthentication()
        detail_allowed_methods = ['get', 'post']
        always_return_data = True
        include_resource_uri = False
        
        filtering = {
                     "bom" : ALL_WITH_RELATIONS,
                     "plate" : ALL_WITH_RELATIONS,
                     "part" : ALL_WITH_RELATIONS,
                     "valid_to": ALL,
                     "valid_from": ALL
                     }
    
    def prepend_urls(self):
        return [
                 url(r"^(?P<resource_name>%s)/save-part%s" % (self._meta.resource_name,trailing_slash()),
                     self.wrap_view('save_plate_part'), name="save_plate_part"),
                 url(r"^(?P<resource_name>%s)/get-plates%s" % (self._meta.resource_name,trailing_slash()),
                     self.wrap_view('get_plates'), name="get_plates"),
                 url(r"^(?P<resource_name>%s)/search-sbom%s" % (self._meta.resource_name,trailing_slash()),
                     self.wrap_view('search_sbom'), name="search_sbom")
                ]
    
    def alter_list_data_to_serialize(self, request, data):
        if request.GET.get('plate__plate_id'):
            plate =  get_model('BOMPlate').objects.get(plate_id=request.GET.get('plate__plate_id'))
            data['meta']['plate_id'] = plate.plate_id
            data['meta']['plate_image'] = "{0}/{1}".format(settings.S3_BASE_URL, plate.plate_image)
            data['meta']['plate_image_with_part'] = "{0}/{1}".format(settings.S3_BASE_URL, plate.plate_image_with_part)
        return data
        
    def dehydrate(self, bundle):
        bom_visualization = get_model('BOMVisualization').objects.filter(bom=bundle.data['id'])
        bundle.data['bom_visualization'] = [model_to_dict(b) for b in bom_visualization]
        return bundle    
    
    def get_plates(self, request, **kwargs):
        '''
           Returns all the plates and their images
           associated with a sku-code and bom number
           params:
               sku_code: SKU code of the product
               bom_number: bom number of the sku
        '''
        self.is_authenticated(request)
        sku_code = request.GET.get('sku_code')
        bom_number = request.GET.get('bom_number')
        try:
            bom_plate_part =  get_model('BOMPlatePart', settings.BRAND).objects.\
            select_related('plate').filter(bom__sku_code=sku_code, bom__bom_number=bom_number)
            plate_details = []
            for data in bom_plate_part:
                plate = {}
                plate['plate_id'] = data.plate.plate_id
                plate['image_url'] = "{0}/{1}".format(settings.S3_BASE_URL, data.plate.plate_image)
                if not data.plate.plate_image:
                    plate['image_url'] = ""
                plate['description'] = data.plate.plate_txt
                plate_details.append(plate)
            return HttpResponse(content=json.dumps(plate_details),
                                content_type='application/json')
        except Exception as ex:
            LOG.error('Exception while fetching plate images : {0}'.format(ex))
            return HttpResponseBadRequest()
    
    def save_plate_part(self, request, **kwargs):
        '''
           Parses the uploaded CSV and adds the
           co-ordinates for each bomplatepart entry 
           and uploads the image of the plate with parts
           params:
               model: the model of the product selected
               skuCode: the sku code of the model
               bomNumber: the bom number associated to the sku code
               plateId: the plate id of the plate details being uploaded
               platImage: the plate part image of the plate
               plateMap: the csv containing the co-ordinates of the parts in the plate
            returns:
               A json object:{'plate_id':plate_id, 
                               'sku_code':sku_code,
                              'bom_number':bom_number,
                               'model':model, 
                               'part':[]}
              where 'part' is a list consisting of all the
              coordinates uploaded in csv with following status messages.
              SUCCESS: if the co-ordinates are added successfully
              INCOMPLETE: if a co-ordinate is not given in csv
              ERROR: if any param is invalid
              MISSING: if any part present in DB has not been sent in csv
        '''
        self.is_authenticated(request)
        if request.method != 'POST':
            return HttpResponse(json.dumps({"message" : "Method not allowed"}), content_type= "application/json",
                                status=400)
        try:
            post_data=request.POST
            model = post_data.get('model')
            sku_code = post_data.get('skuCode')
            bom_number = post_data.get('bomNumber')
            plate_id = post_data.get('plateId')
            plate_image=request.FILES['plateImage']
            plate_map=request.FILES['plateMap']
            dashboard_image=request.FILES['dashboardImage']
            plate_name= post_data.get('plateName')
            sbom_part_mapping=[]
            bom_queryset = get_model('BOMPlatePart').objects.filter(bom__sku_code=sku_code,
                                                                bom__bom_number=bom_number,
                                                                plate__plate_id=plate_id).select_related(
                                                                                        'bom','plate','part')
            if not bom_queryset:
                raise ValueError('Provided SKU, BOM number and plate ID combination does not exists')
            visual_queryset=get_model('BOMVisualization').objects.filter(bom__in=bom_queryset).select_related(
                                                                            'bom__bom','bom__plate','bom__part')
            insert_visual_bom=[]
            for bom in bom_queryset:
                visual_bom = filter(lambda visual_bom: visual_bom.bom == bom, visual_queryset)
                if not visual_bom:
                    insert_visual_bom.append(get_model('BOMVisualization')(bom=bom))
            
            new_visual_queryset=get_model('BOMVisualization').objects.bulk_create(insert_visual_bom)
         
            for query in itertools.chain(visual_queryset, new_visual_queryset):
                temp={}
                temp['part_number']=query.bom.part.part_number
                temp['bomvisualization_object']=query
                sbom_part_mapping.append(temp)

            plate_obj=bom_queryset[0].plate
            plate_obj.plate_image.save(plate_image.name, dashboard_image)
            plate_obj.plate_image_with_part.save(plate_image.name, plate_image)
            plate_obj.plate_txt = plate_name
            plate_obj.save(using=settings.BRAND)
            data={'plate_id':plate_id, 'sku_code':sku_code,
                  'bom_number':bom_number,
                  'model':model, 'part':[]}
            spamreader = csv.reader(plate_map, delimiter=',')
            next(spamreader)
            csv_data=format_part_csv(spamreader)
            for part_entry in csv_data:
                try:
                    bom_visual = filter(lambda bom_visual: bom_visual['part_number'] == part_entry['part_number'], sbom_part_mapping)
                    visual_obj=bom_visual[0]['bomvisualization_object']
                    bompartplate_obj = visual_obj.bom
                    part_data=bompartplate_obj.part
                    part_data.description=part_entry['desc']
                    part_data.save(using=settings.BRAND)
                    if part_entry['x-axis'] and part_entry['y-axis'] and part_entry['z-axis']:
                        visual_obj.x_coordinate=part_entry['x-axis']
                        visual_obj.y_coordinate=part_entry['y-axis']
                        visual_obj.z_coordinate=part_entry['z-axis']
                        visual_obj.serial_number=part_entry['serial_number']
                        visual_obj.part_href=part_entry['href']
                        visual_obj.save(using=settings.BRAND)
                        part_entry['status']='SUCCESS'
                    else:
                        LOG.error('[save_plate_part]: Coordinate is missing {0}'.format(part_entry))
                        part_entry['status']='INCOMPLETE'
                except Exception as ex:
                    LOG.info('[save_plate_part]: {0} :: {1}'.format(part_entry['part_number'], ex))
                    part_entry['status']='ERROR'
                data['part'].append(part_entry)
            for part in sbom_part_mapping:
                active = filter(lambda active: active['part_number'] == part['part_number'], data['part'])
                if not active:
                    temp={}
                    temp['part_number']=part['part_number']
                    temp['status']='MISSING'
                    data['part'].append(temp)
        except Exception as ex:
            error_message='Error [save_plate_part]:  {0}'.format(ex)
            LOG.info(error_message)
            data = {'message': error_message}
        return HttpResponse(json.dumps(data), content_type="application/json")
    
    def search_sbom_for_vin(self, request):
        '''
           Gives the sbom data for a particular VIN
        '''
        get_data=request.GET
        vin = get_data.get('value')
        try:
            product_obj=get_model('ProductData').objects.get(product_id=vin)
            bom_header_obj=get_model('BOMHeader').objects.get(sku_code=product_obj.sku_code,
                                                           valid_from__lte=product_obj.invoice_date,
                                                           valid_to__gte=product_obj.invoice_date)
            return self.get_list(request, bom=bom_header_obj,
                                   valid_from__lte=product_obj.invoice_date,
                                   valid_to__gte=product_obj.invoice_date)
        except Exception as ex:
            LOG.error('[search_sbom_for_vin]: {0}'.format(ex))
            data = {'status':0 , 'message': 'VIN has no matching BOM number'}
            return HttpResponse(json.dumps(data), content_type="application/json")
        

    def search_sku_for_desc(self, request):
        '''
           Gives list of sku code for a desc
        '''
        get_data=request.GET
        product_description = get_data.get('value')
        product_obj=get_model('BrandProductRange').objects.filter(description__startswith=product_description)
        data = {'objects': [model_to_dict(c, exclude='image_url') for c in product_obj]}
        return HttpResponse(json.dumps(data), content_type="application/json")
    
    def search_revison_for_sku(self, request):
        '''
           Gives list of revision for a sku code
        '''
        get_data=request.GET
        sku_code = get_data.get('value')
        header_obj=get_model('BOMHeader').objects.filter(sku_code=sku_code)
        data = {'objects': [model_to_dict(c, fields=['sku_code','revision_number']) for c in header_obj]}
        return HttpResponse(json.dumps(data), content_type="application/json")
    
    def search_sbom_for_revision(self, request):
        '''
           Gives the sbom data for a given revision
        '''
        get_data=request.GET
        revision_number = int(get_data.get('value'))
        sku_code = get_data.get('sku_code')
        try:
            bom_header_obj=get_model('BOMHeader').objects.get(sku_code=sku_code,
                                                revision_number=revision_number)
            return self.get_list(request, bom=bom_header_obj)
        except Exception as ex:
            LOG.error('[search_sbom_for_revision]: {0}'.format(ex))
            data = {'status':0 , 'message': 'SKU and Revision has no matching BOM data'}
            return HttpResponse(json.dumps(data), content_type="application/json")
        
    
    def search_sbom(self, request, **kwargs):
        if request.method != 'GET':
            return HttpResponse(json.dumps({"message" : "Method not allowed"}), content_type= "application/json",
                                status=400)
        get_data=request.GET
        parameter = get_data.get('parameter').lower()
        search_handler = {
                          'vin': self.search_sbom_for_vin,
                          'description': self.search_sku_for_desc,
                          'sku_code': self.search_revison_for_sku,
                          'revision': self.search_sbom_for_revision
                          }
        return search_handler[parameter](request)

class BOMVisualizationResource(CustomBaseModelResource):
    '''
       Resource for BOM visualization that saves
       co-ordinates of a bom plate part image
    '''
    bom = fields.ForeignKey(BOMPlatePartResource, 'bom', null=True, blank=True, full=True)
    
    class Meta:
        queryset = get_model('BOMVisualization').objects.all()
        resource_name = 'bom-visualizations'
        authorization = Authorization()
        authentication = AccessTokenAuthentication()
        detail_allowed_methods = ['get']
        filtering = {
                     "bom" : ALL_WITH_RELATIONS,
                     "status" : ALL
                     }
     
    def prepend_urls(self):
        return [
                 url(r"^(?P<resource_name>%s)/review-sbom%s" % (self._meta.resource_name,trailing_slash()),
                     self.wrap_view('review_sbom_details'), name="review_sbom_details")
                ]
        
    def review_sbom_details(self, request, **kwargs):
        '''
           saves the review of a sbom
           params:
               sku_code: the sku code of the model
               bom_number: the bom number associated to the sku code
               plate_id: the plate_id of the bom
               part_number: the part of the plate
               quantity: the quantity of the part
               status: status of the sbom review
               remarks: remarks of the review
        '''
        self.is_authenticated(request)
        if request.method != 'POST':
            return HttpResponse(json.dumps({"message" : "Method not allowed"}), content_type= "application/json",
                                status=400)
        try:
            load = json.loads(request.body)
        except:
            return HttpResponse(content_type="application/json", status=404)
        bom_number = load.get('bom_number')
        sku_code = load.get('sku_code')
        plate_id = load.get('plate_id')
        part_number = load.get('part_number')
        quantity = load.get('quantity')
        status = load.get('status')
        remarks = load.get('remarks')
        try:
            bom_details = get_model('BOMPlatePart').objects.get(bom__sku_code=sku_code,
                                                                bom__bom_number=bom_number,
                                                                plate__plate_id=plate_id,
                                                                part__part_number=part_number,
                                                                quantity=quantity)
            bom_visualizations = get_model('BOMVisualization').objects.filter(bom=bom_details)
            bom_visualization = bom_visualizations[0]
            bom_visualization.status = status
            if remarks:
                bom_visualization.remarks = remarks
            if status == 'Publish':
                bom_visualization.published_date = datetime.now()
            bom_visualization.save(using=settings.BRAND)
            return HttpResponse(json.dumps({"message": "Success"}), content_type='application/json')
        except Exception as ex:
            LOG.info('[review_sbom]: {0}'.format(ex))
            return HttpResponseBadRequest()

class ECOReleaseResource(CustomBaseModelResource):
    '''
       Resource for ECO release data
    '''
    class Meta:
        queryset = get_model('ECORelease').objects.all()
        resource_name = 'eco-releases'
        authorization = Authorization()
        authentication = AccessTokenAuthentication()
        detail_allowed_methods = ['get', 'post']

class ECOImplementationResource(CustomBaseModelResource):
    '''
       Resource for ECO Implementation data
    '''
    class Meta:
        queryset = get_model('ECOImplementation').objects.all()
        resource_name = 'eco-implementations'
        authorization = Authorization()
        authentication = AccessTokenAuthentication()
        detail_allowed_methods = ['get', 'post']
        always_return_data = True

class ManufacturingDataResource(CustomBaseModelResource):
    '''
       Resource for Manufacturing Data
    '''
    class Meta:
        queryset = get_model('ManufacturingData').objects.all()
        resource_name = 'manufacturing-details'
        authorization = Authorization()
        authentication = AccessTokenAuthentication()
        allowed_methods = ['get']
        always_return_data =True

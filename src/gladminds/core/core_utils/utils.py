import base64
import hashlib
import datetime
import re
import time
import logging

LOG = logging.getLogger('gladminds')


def dictfetchall(cursor):
    "Returns all rows from a cursor as a dict"
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]


def get_list_from_set(set_data):
    created_list = []
    for set_object in set_data:
        created_list.append(list(set_object)[1])
    return created_list

def generate_temp_id(prefix_value):
    for x in range(5):
        key = base64.b64encode(hashlib.sha256(str(datetime.datetime.now())).digest())
        key = re.sub("[a-z/=+]", "", key)
        if len(key) < 6:
            continue
        return "%s%s" % (prefix_value, key[:6])

def generate_mech_id():
    mechanic_id=generate_temp_id('TME')
    return mechanic_id

################ ADDED FOR RETAILER ##################
def generate_retailer_temp_id(prefix_value):
    for x in range(5):
        key = base64.b64encode(hashlib.sha256(str(datetime.datetime.now())).digest())
        key = re.sub("[a-z/=+]", "", key)
        if len(key) < 6:
            continue
        return "%s%s" % (prefix_value, key[:6])

def generate_retailer_id():
    retailer_tem_id = generate_retailer_temp_id('TRE')
    return retailer_tem_id
################ END #################################


def generate_partner_id():
    partner_id=generate_temp_id('PRT')
    return partner_id

def generate_nsm_id():
    nsm_id=generate_temp_id('NSM')
    return nsm_id

def generate_asm_id():
    asm_id=generate_temp_id('ASM')
    return asm_id

def generate_agency_id():
    agency_id=generate_temp_id('AGY')
    return agency_id

def generate_qualitycheck_id():
    qualitycheck_id=generate_temp_id('QC')
    return qualitycheck_id

def debug(fn):
    '''
    Use as print utility
    :param fn:
    :type fn:
    '''
    def wrapper(*args, **kwargs):
        result = fn(*args, **kwargs)
        print 'name:{0} args:{1} kwargs:{2} result: {3}'.format(fn.__name__, args, kwargs, result)
        return result
    return wrapper


def log_time(func_to_decorate):
    '''
    Decorator generator that logs the time it takes a function to execute
    :param func_to_decorate:
    :type func_to_decorate:
    '''
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func_to_decorate(*args, **kwargs)
        elapsed = (time.time() - start)
        LOG.info("[TIMING]:%s - %s" % (func_to_decorate.__name__, elapsed))
        return result
    wrapper.__doc__ = func_to_decorate.__doc__
    wrapper.__name__ = func_to_decorate.__name__
    return wrapper


def get_search_query_params(request, class_self):
    custom_search_enabled = False
    if 'custom_search' in request.GET and 'val' in request.GET:
        class_self.search_fields = ()
        request.GET = request.GET.copy()
        class_self.search_fields = (request.GET.pop("custom_search")[0],)
        search_value = request.GET.pop("val")[0]
        request.GET["q"] = search_value
        request.META['QUERY_STRING'] = 'q=%s'% search_value
        custom_search_enabled = True
    return custom_search_enabled

def format_part_csv(spamreader):
    csv_data=[]
    for row_list in spamreader:
        temp={}
        temp['serial_number']=row_list[0]
        temp['part_number']=row_list[1]
        temp['desc']=row_list[2]
        temp['x-axis']=row_list[3] if row_list[3] else None
        temp['y-axis']=row_list[4] if row_list[4] else None
        temp['z-axis']=row_list[5] if row_list[5] else None
        temp['href']=row_list[6] if row_list[6] else None
        csv_data.append(temp)
    return csv_data

GM_USER = {
           "customer_name": "test_user",
            "isActive": True,
            "phone_number": "1234567890",
            "user": {
                     "phone_number": "999999999",
                    "user": {
                            "email": "",
                            "first_name": "",
                            "last_name": "",
                            "username": "ppa",
                            "password" :"123"
                            }
                    }
           }

CIRCLE_HEAD = {
    "name": "chtesting",
    "email": "chtesting@abc.com",
    "phone-number": "+919988776655"
}

RM_DATA = {
    "name": "rmtesting",
    "email": "rmtesting@abc.com",
    "phone-number": "+917988776655",
    "regional-office": "Delhi",
    "circle_head_user_id": 2
}


USER = {
        "date_joined":"2015-02-04T17:10:24",
         "email":"test@gladminds.co",
         "first_name":"TEST USER",
         "is_active":True,
         "is_staff":False,
         "last_login":"2015-02-04T17:10:24",
         "last_name":"",
         "username":"user"
        }

USER1 = {
        "date_joined":"2015-02-04T17:10:24",
         "email":"asc@xyz.com",
         "first_name":"TEST USER",
         "is_active":True,
         "is_staff":True,
         "last_name":"",
         "username":"user"
        }

GM_PRODUCTS = {
                "customer_product_number": None,
                "engine": None,
                "insurance_loc": None,
                "insurance_yrs": None,
                "invoice_loc": None,
                "isActive": True,
                "order": 0,
                "product_type": {
                                "brand": {
                                          "brand_id": "Bajaaaaj",
                                          "brand_image_loc": " ",
                                          "brand_name": "Bajaj",
                                          "isActive": True
                                          },
                               "isActive": True,
                               "order": 0,
                               "product_image_loc": None,
                               "product_name": "3700DHPP",
                               "product_type": "3700DHPP",
                               "warranty_email": None,
                               "warranty_phone": None
                               },
               "purchased_from": None,
               "sap_customer_id": None,
               "seller_email": None,
               "seller_phone": None,
               "veh_reg_no": None,
               "vin": 22,
               "warranty_loc": None,
               "warranty_yrs": None
               }

GM_COUPONS = {
           "order": 0,
           "service_type": 2,
           "status": 1,
           "unique_service_coupon": "1",
           "valid_days": 260,
           "valid_kms": 8000,
            "vin": {
                    "created_on": "2014-04-25T15:56:34",
                    "invoice_date": "2013-04-06T00:00:00",
                    "isActive": True,
                    "last_modified": "2014-04-25T15:56:34",
                    "order": 0,
                    "product_type": {
                                     "brand": {
                                               "brand_id": "Bajaj",
                                               "brand_image_loc": " ",
                                               "brand_name": "Bajaj",
                                               "isActive": True
                                               },
                                     "isActive": True,
                                     "order": 0,
                                     "product_image_loc": "",
                                     "product_name": "3700DHFS",
                                     "product_type": "3700DHFS",
                                     "product_type_id": 101959
                                    },
                    "vin": "22"
                    }
            }

USER_PREFERENCE = {
                   "user_profile" : 1,
                   "key" : "name",
                   "value" : "test_user"
                }

APP_PREFERENCE = {
                   "brand" : 1,
                   "key" : "name",
                   "value" : "test_brand"
                }

AFTERBUY_PRODUCT = {
                    "brand_product_id": "zxcvbnm",
                    "color": "",
                    "consumer": {
                                 "accepted_terms": False,
                                 "address": "",
                                 "consumer_id": "08b59d1a-e838-42ea-84de-33174f2c30c9",
                                 "country": None,
                                 "created_date": "2015-06-19T11:20:17",
                                 "date_of_birth": None,
                                 "gender": None,
                                 "image_url": "guest.png",
                                 "is_phone_verified": False,
                                 "modified_date": "2015-06-19T15:21:06",
                                 "phone_number": "7760814043",
                                 "pincode": None,
                                 "resource_uri": "/afterbuy/v1/consumers/5/",
                                 "state": None,
                                 "tshirt_size": None,
                                 "user": {
                                          "date_joined": "2015-06-19T11:20:17",
                                          "first_name": "",
                                          "id": 5,
                                          "is_active": True,
                                          "is_staff": False,
                                          "last_login": "2015-06-19T12:38:47",
                                          "last_name": "",
                                          "resource_uri": "",
                                          "username": "7760814043"
                                          }
                                 },
                    "created_date": "2015-06-19T11:21:25",
                    "description": "",
                    "details_completed": None,
                    "image_url": "",
                    "is_accepted": True,
                    "is_deleted": False,
                    "manual_link": "",
                    "modified_date": "2015-06-19T12:39:14",
                    "nick_name": "ddq",
                    "product_type": {
                                     "brand": {
                                               "created_date": "2015-06-19T11:20:37",
                                               "description": "",
                                               "id": 1,
                                               "image_url": "sss",
                                               "industry": {
                                                            "created_date": "2015-06-19T11:20:33",
                                                            "description": "",
                                                            "id": 1,
                                                            "modified_date": "2015-06-19T15:23:56",
                                                            "name": "Automobiles",
                                                            "resource_uri": "/afterbuy/v1/industries/1/"
                                                            },                                              
                                               "is_active": True,
                                               "modified_date": "2015-06-19T15:23:56",
                                               "name": "bajaj",
                                               "resource_uri": "/afterbuy/v1/brands/1/"
                                               },
                                     "created_date": "2015-06-19T11:20:56",
                                     "id": 1,
                                     "image_url": "",
                                     "is_active": True,
                                     "modified_date": "2015-06-19T15:23:56",
                                     "overview": "",
                                     "product_type": "motorcycle",
                                     "resource_uri": "/afterbuy/v1/product-types/1/"
                                     },
                    "purchase_date": "2015-06-19T11:21:11",
                    "resource_uri": "/afterbuy/v1/products/1/",
                    "service_reminder": None
                    }                   
AFTERBUY_PRODUCTS = {
                     "brand_product_id": "zxcvbnm",
                     "warranty_year" : "2015-01-01",
                     "color": "",
                     "consumer": {
                                  "accepted_terms": False,
                                  "address": "",
                                  "consumer_id": "08b59d1a-e838-42ea-84de-33174f2c30c9",
                                  "country": None,
                                  "created_date": "2015-06-19T11:20:17",
                                  "date_of_birth": None,
                                  "gender": None,
                                  "image_url": "guest.png",
                                  "is_phone_verified": False,
                                  "modified_date": "2015-06-19T15:21:06",
                                  "pincode": None,
                                  "resource_uri": "/afterbuy/v1/consumers/5/",
                                  "state": None,
                                  "tshirt_size": None,
                                  "user": {
                                           "date_joined": "2015-06-19T11:20:17",
                                           "first_name": "",
                                           "id": 5,
                                           "is_active": True,
                                           "is_staff": False,
                                           "last_login": "2015-06-19T12:38:47",
                                           "last_name": "",
                                           "resource_uri": "",
                                           "username": "7760814041"
                                           }
                                  },
                     "created_date": "2015-06-19T11:21:25",
                     "description": "",
                     "details_completed": None,
                     "image_url": "",
                     "is_accepted": True,
                     "is_deleted": False,
                     "manual_link": "",
                     "modified_date": "2015-06-19T12:39:14",
                     "nick_name": "ddq",
                     "product_type": {
                                      "brand": {
                                                "created_date": "2015-06-19T11:20:37",
                                                "description": "",
                                                "id": 1,
                                                "image_url": "sss",
                                                "industry": {
                                                             "created_date": "2015-06-19T11:20:33",
                                                             "description": "",
                                                             "id": 1,
                                                             "modified_date": "2015-06-19T15:23:56",
                                                             "name": "Automobiles",
                                                             "resource_uri": "/afterbuy/v1/industries/1/"
                                                             },
                                                "is_active": True,
                                                "modified_date": "2015-06-19T15:23:56",
                                                "name": "bajaj",
                                                "resource_uri": "/afterbuy/v1/brands/1/"
                                                },
                                      "created_date": "2015-06-19T11:20:56",
                                      "id": 1,
                                      "image_url": "",
                                      "is_active": True,
                                      "modified_date": "2015-06-19T15:23:56",
                                      "overview": "",
                                      "product_type": "motorcycle",
                                      "resource_uri": "/afterbuy/v1/product-types/1/"
                                      },
                     "purchase_date": "2015-06-19T11:21:11",
                     "resource_uri": "/afterbuy/v1/products/1/",
                     "service_reminder": None
                     }
AFTERBUY_INSURANCES = {
                        "product":AFTERBUY_PRODUCTS,
                        "modified_date": "2010-11-10T03:07:43",
                        "premium": 23.6,
                        "insurance_type": "type1",
                        "nominee": "type1",
                        "policy_number":"type1",
                        "vehicle_value": "123456",
                        "issue_date": "2010-11-10T03:07:43",
                        "agency_name":"type1",
                        "expiry_date":"2012-11-10T03:07:43",
                        "image_url": "type1",
                        "created_date":"2010-10-10T03:07:43",
                        "agency_contact":"bajaj",
                        "is_expired": False
                     }

AFTERBUY_INVOICES = {
                     "product": AFTERBUY_PRODUCTS,
                     "invoice_number":"123456",
                     "dealer_name":"Bajaj",
                     "dealer_contact":"1234",        
                     "amount":"12345",
                     "image_url":"aaa"                                                              
                     }

AFTERBUY_LICENCES = {
                     "product": AFTERBUY_PRODUCTS,
                     "license_number":"12345",
                     "issue_date":"2010-11-10T03:07:43",
                     "expiry_date":"2012-11-10T03:07:43",
                     "blood_group":"B+",
                     "image_url" :"aaa"
                     }

AFTERBUY_POLLUTION = {
                      "product": AFTERBUY_PRODUCTS,                                         
                      "pucc_number":"123",
                      "issue_date":"2010-10-10T03:07:43",
                      "expiry_date":"2015-11-10T03:07:43",
                      "image_url":"aaa"
                      }

AFTERBUY_PRODUCTSUPPORT = {
                           "product": AFTERBUY_PRODUCTS, 
                           "name ":"Bajaj",
                           "contact":"1234567890",
                           "website":"bajaj.com",
                           "email_id":"afterbuy@gmail.com",
                           "address":""
                           }

AFTERBUY_SELLINFORMATION = {
                            "product": AFTERBUY_PRODUCTS,                                         
                            "amount ":"",
                            "address ":"",
                            "state":"",
                            "country":"",
                            "pincode":"",
                            "description ":"",
                            "is_negotiable ":True,
                            "is_sold":False                          
                            }

AFTERBUY_USERPRODUCTIMAGES = {
                              "product": AFTERBUY_PRODUCTS,                                         
                              "image_url":"aaa",
                              "type":"primary"
                              }

AFTERBUY_REGISTATION = {
                        "product": AFTERBUY_PRODUCTS,
                        "registration_number":"1234",
                        "registration_date":"2012-11-10T03:07:43",
                        "chassis_number" :"1234",
                        "engine_number" :"1234",
                        "owner_name" :"asdf",
                        "relation_name" :"owner",
                        "address":"",
                        "registration_upto":"201-11-10T03:07:43",
                        "model_year":"2012-11-10T03:07:43",
                        "model":"123",
                        "image_url ":"aaa",
                        "fuel ":"petrol",
                        "cylinder":"",
                        "seating ":"",
                        "cc":"",
                        "body":""                                             
                        }

AFTERBUY_SUPPORT = {
                    "brand":AFTERBUY_PRODUCTS.get("product_type")['brand'],
                    "brand_product_category":AFTERBUY_PRODUCTS.get("brand"), 
                    "company_name ":"Bajaj",
                    "toll_free":"18001800",
                    "website":"www.afterbuy.com",
                    "email_id":"afterbuy@gmail.com"
                    }

AFTERBUY_REGISTATION = {
                        "product": AFTERBUY_PRODUCTS,
                        "registration_number":"asdf",
                        "chassis_number" :"",
                        "engine_number" :"",
                        "owner_name" :"asdf",
                        "relation_name" :"owner",
                        "model":"aaa"
                        }

USER_PROFILE = {
                "created_date":"2015-04-10T12:43:33",
                "address":"CHENNAI",
                "country":"",
                "date_of_birth":"1992-12-29T00:00:00",
                "gender":"",
                "image_url":"",
                "phone_number":"",
                "pincode":"",
                "resource_uri":"",
                "state":"karnataka",
                "status":"",
                "user": USER
                }

NATIONAL_SPARES_MANAGER = {
        "email": "rkrishnan@bajajauto.co.in",
        "name": "Raghunath",
        "nsm_id": "NSM002",
        "phone_number": "1234567890",
        "territory": "/v1/territories/1/",
        "user": " "
        }

AREA_SPARES_MANAGER = {
        "asm_id": "ASM005",
        "email": "spremnath@bajajauto.co.in",
        "name": "PREM NATH",
        "phone_number": "9999999999",
        "state": {
         'state_name':'Karnataka',
         'state_code':'KAR',
         'territory': "/v1/territories/1/",
         },
        "user":USER,
        "nsm":""
       }

PARTNER = {
            "address": "F-89,Kamla nagar,kanpur",
            "name": "Anchit",
            "partner_id": "PRT5Y76YB",
            "partner_type": "Merchant",
            "user":"",
        }

DISTRIBUTOR = {
               "user": USER_PROFILE,
               "asm":AREA_SPARES_MANAGER,
                "city": "VASAI EAS",
                "created_date": "2015-04-10T12:43:33",
               "distributor_id": "15666",
                "email": "",
                "id": 1,
                "modified_date": "2015-04-10T12:43:33",
                "name": "SAI SERVICE AGENCY",
                "phone_number": "1111111111",
                "sent_to_sap": False
               }

RETAILER = {
            "retailer_name": "Ayush",
            "retailer_town": "devghar",
            }


PRODUCT_TYPE = {
                "brand_product_category":"",
                "image_url": "http://test",
                "is_active": True,
                "product_type": ""
                }

SPARE_MASTER = {
                "category": "cat1",
                "description": "TEST DESCRIPTION",
                "part_model": "2S",
                "part_number": "11111111",
                "product_type": PRODUCT_TYPE,
                "segment_type": "",
                "supplier": ""
                }

PRODUCT = {
           "partner": PARTNER,
           "brand": "",
            "category": "",
            "description": "",
            "image_url": "",
            "is_active": True,
            "model": "",
            "points": 12,
            "price": 12,
            "product_id": "123",
            "resource_uri": "/v1/productcatalog/1/",
            "sub_category": "",
            "variation": ""
        }

MEMBER = {
            "address_line_1": "",
            "address_line_2": "",
            "address_line_3": "",
            "address_line_4": "",
            "address_line_5": "",
            "address_line_6": "",
            "date_of_birth": "1971-10-20T05:30:00",
            "district": "MADURAI",
            "first_name": "Ramu",
            "form_number": 9156,
            "form_status": "Incomplete",
            "genuine_parts_used": 85,
            "image_url": "ww",
            "last_name": "M",
            "locality": "",
            "mechanic_id": "ME00003",
            "middle_name": "",
            "phone_number": "+919842461800",
            "pincode": "625002",
            "registered_date": "2014-09-06T00:00:00",
            "resource_uri": "",
            "sent_sms": False,
            "sent_to_sap": False,
            "serviced_2S": 180,
            "serviced_4S": 20,
            "serviced_CNG_LPG":0,
            "serviced_diesel": 0,
            "shop_address": "SELLUR",
            "shop_name": "SRI MEENAKSHI AMMAN AUTO WORKS",
            "shop_number": "34",
            "shop_wall_length": 0,
            "shop_wall_width": 0,
            "spare_per_month": 50000,
            "state": {
                     'state_name':'Karnataka',
                     'state_code':'KAR',
                     'territory':{
                                  'territory':'NORTH' 
                                  },
                     },
            "tehsil": "",
            "total_points": 1000,
            "distributor":DISTRIBUTOR
            }
MEMBER1 = {
            "address_line_1": "",
            "address_line_2": "",
            "address_line_3": "",
            "address_line_4": "",
            "address_line_5": "",
            "address_line_6": "",
            "date_of_birth": "1971-10-20T05:30:00",
            "district": "MADURAI",
            "first_name": "Ramu",
            "form_number": 9156,
            "form_status": "Incomplete",
            "genuine_parts_used": 85,
            "image_url": "qqq",
            "last_name": "M",
            "locality": "",
            "mechanic_id": "ME00004",
            "middle_name": "",
            "phone_number": "+919842461801",
            "pincode": "625002",
            "registered_date": "2014-09-06T00:00:00",
            "resource_uri": "",
            "sent_sms": False,
            "sent_to_sap": False,
            "serviced_2S": 180,
            "serviced_4S": 20,
            "serviced_CNG_LPG":0,
            "serviced_diesel": 0,
            "shop_address": "SELLUR",
            "shop_name": "SRI MEENAKSHI AMMAN AUTO WORKS",
            "shop_number": "34",
            "shop_wall_length": 0,
            "shop_wall_width": 0,
            "spare_per_month": 50000,
            "state": "/v1/states/1/",
            "tehsil": "",
            "total_points":100
                        }

REDEMPTION_REQUEST =  {
                        "delivery_address": "HSR",
                        "due_date": "2015-02-09T17:49:45",
                        "expected_delivery_date": "2015-02-10T16:49:45",
                        "image_url": "",
                        "is_approved": False,
                        "member": MEMBER,
                        "packed_by": "user",
                        "refunded_points": False,
                        "resolution_flag": True,
                        "status": "Open",
                        "tracking_id": "",
                        "product":PRODUCT,
                        "partner":"/v1/partners/1/",
                    }
    
SPARE_PART_UPC = {  
                "is_used":False,
                "unique_part_code":"UPCC50",
                "part_number":'/v1/spare-masters/1/', 
                }

    
SPARE_PART_UPC_1 = {  
                "is_used":False,
                "unique_part_code":"UPCC51",
                "part_number": '/v1/spare-masters/1/', 
                }

SPARE_POINT = {
               "MRP": 30,
               "part_number":  '/v1/spare-masters/1/',
               "points":18,
               "price":None,
               "territory":"South",
               "valid_from":"2014-12-22T00:00:00",
               "valid_till":"2015-12-22T00:00:00"
               }

SLA = {  
       "status":"Open",
       "action":"Redemption",
       "reminder_time":4,
       "reminder_unit":"hrs",
       "resolution_time": 6,
       "resolution_unit":"hrs",
       "member_resolution_time": 8,
       "member_resolution_unit":"hrs"
       }

ACCUMULATION = {  
                "asm":AREA_SPARES_MANAGER,
                "member":MEMBER,
                "points":100,
                "total_points":500,
                "transaction_id":1,
                "upcs":[{"unique_part_code":"UPCC50"},{"unique_part_code":"UPCC51"},]
                }

WELCOMEKIT = {
                "delivery_address": "HSR LAYOUT ",
                "delivery_date": None,
                "image_url": None,
                "member": {"mechanic_id":1},
                "packed_by": None,
                "partner":{"partner_id":1},
                "resolution_flag": False,
                "shipped_date": None,
                "status": "Open",
                "tracking_id":"",
                "transaction_id": 1
            }

COMMENT_THREAD =  {
                    "is_edited": False,
                    "message": "Gladminds",
                    "welcome_kit": "/v1/welcome-kits/1/",
                    "user":USER,
                }

TRANSFERPOINTS = {
                "upc": "UPCC50",
                "from": "ME00003",
                "to": "ME00004",
                }

TERRITORY = {
             'territory':'NORTH' 
             }

STATE = {
         'state_name':'Karnataka',
         'state_code':'KAR',
         'territory':  {
             'territory':'NORTH' 
             },
         }

CITY = {
        'city':'Bangalore',     
        'state':{
                 'state_name':'Karnataka',
                 'state_code':'KAR',
                 'territory':{
                              'territory':'NORTH' 
                            },
                 }
        }

REDEMPTION_REQUEST1={   
                    "delivery_address": "HSR",
                    "due_date": "2015-02-09 17:49:45",
                    "expected_delivery_date": "2015-02-10 16:49:45",
                    "image_url": None,
                    "is_approved": False,
                    "member": {
                        "address_line_1": "",
                        "address_line_2": "",
                        "address_line_3": "",
                        "address_line_4": "",
                        "address_line_5": "",
                        "address_line_6": "",
                        "date_of_birth": "1971-10-20T05:30:00",
                        "district": "MADURAI",
                        "first_name": "Ramu",
                        "form_number": 9156,
                        "form_status": "Incomplete",
                        "genuine_parts_used": 85,
                        "image_url": "",
                        "last_name": "M",
                        "locality": "aaaaaa",
                        "mechanic_id": "ME00003",
                        "middle_name": "",
                        "phone_number": "+919842461800",
                        "pincode": "625002",
                        "registered_date": "2014-09-06T00:00:00",
                        "resource_uri": "",
                        "sent_sms": False,
                        "sent_to_sap": False,
                        "serviced_2S": 180,
                        "serviced_4S": 20,
                        "serviced_CNG_LPG": 0,
                        "serviced_diesel": 0,
                        "shop_address": "SELLUR",
                        "shop_name": "SRI MEENAKSHI AMMAN AUTO WORKS",
                        "shop_number": "34",
                        "shop_wall_length": 0,
                        "shop_wall_width": 0,
                        "spare_per_month": 50000,
                        "state": {
                            "state_name": "Karnataka",
                            "state_code": "KAR",
                            "territory": {
                                "territory": "NORTH"
                            }
                        },
                        "tehsil": "",
                        "total_points": 1000
                    },
                    "packed_by": "user",
                    "refunded_points": False,
                    "resolution_flag": True,
                    "status": "Open",
                    "tracking_id": "",
                    "product": {
                        "partner": {},
                        "brand": "",
                        "category": "",
                        "description": "",
                        "image_url": "",
                        "is_active": True,
                        "model": "",
                        "points": 123,
                        "price": 12,
                        "product_id": 123,
                        "sub_category": "",
                        "variation": ""
                    },
                    "partner": PARTNER,
                    "points": 123
                }

BRAND_PRODUCT_RANGE = {
                     "description": "sss",
                     "sku_code": "112"
                     }

BRAND_VERTICAL =  {
                   "description": "dasdas",
                   "name": "vertical2"
                   }

BOM_HEADER =  {
               "bom_number": "1232",
               "bom_type": "1",
               "created_date": "2015-05-08T12:02:00",
               "created_on": "2015-05-08",
               "modified_date": "2015-05-08T12:02:00",
               "plant": "112",
               "sku_code": "112",
               "valid_from": "2015-05-08",
               "valid_to": "2015-05-08"
               }

BOM_PLATE_PART = {
                  "bom": {
                          "bom_number": "211760",
                          "bom_type": None,
                          "created_on": None,
                          "id": 3,
                          "plant": None,
                          "sku_code": 112,
                          "valid_from": None,
                          "valid_to": None
                          },
                  "change_number": "SCH01011210",
                  "change_number_to": "",
                  "item": "1",
                  "item_id": "1",
                  "modified_date": "2015-05-11T18:16:06",
                  "part": {
                           "description": None,
                           "id": 1175,
                           "part_number": "15161069",
                           "revision_number": "0",
                           "timestamp": "2015-05-11T18:16:05"
                           },
                  "plate": {
                            "id": 103,              
                            "plate_id": "44",
                            "plate_image": None,
                            "plate_image_with_part": None,
                            "plate_txt": "Chain Case"
                            },
                  "quantity": "1",
                  "serial_number": "",
                  "uom": "EA"
                  }
ECO_RELEASE = {
               "action": "delete",
               "add_part": "12",
               "add_part_loc_code": "12",
               "add_part_qty": 12,
               "add_part_rev": "1",
               "created_date": "2015-05-12T12:18:45",
               "del_part": "1",
               "del_part_loc_code": "12",
               "del_part_qty": 12,
               "del_part_rev": 12,
               "eco_description": "pp",
               "eco_number": "451",
               "eco_release_date": "2015-05-12",
               "id": 1,
               "interchangebility": "1",
               "models_applicable": "112",
               "modified_date": "2015-05-12T12:19:21",
               "parent_part": "11",
               "reason_for_change": "p",
               "resource_uri": "/v1/eco-release/1/",
               "serviceability": "1"
               }


ECO_IMPLEMENTATION =  {
                       "action": "delete",
                       "added_part": "2",
                       "added_part_qty": 2,
                       "change_date": "2015-05-12",
                       "change_no": "21",
                       "change_time": "12:35:04",
                       "chassis_number": "1234567891234567",
                       "created_date": "2015-05-12T12:35:29",
                       "deleted_part": "2",
                       "deleted_part_qty": 2,
                       "eco_number": "451",
                       "engine_number": "2",
                       "id": 1,
                       "modified_date": "2015-05-12T12:35:29",
                       "parent_part": "2",
                       "plant": "1",
                       "reason_code": "2",
                       "remarks": "pp",
                       "resource_uri": "/v1/eco-implementation/1/"
                       }

BOM_VISUALIZATION = {
                     "bom": {
                             "bom": {
                                     "bom_number": "211760",
                                     "bom_type": None,
                                     "id": 5,
                                     "plant": None,
                                     "sku_code": "112",
                                     "valid_from": None,
                                     "valid_to": None
                                     },
                             "change_number": "SCH01011210",
                             "change_number_to": "",
                             "id": 4701,
                             "item": "1",
                             "item_id": "1",
                             "part": {
                                      "description": None,
                                      "id": 2487,
                                      "part_number": "15161069",
                                      "revision_number": "0"
                                      },
                             "plate": {
                                       "id": 205,
                                       "plate_id": "44",
                                       "plate_image": None,
                                        "plate_image_with_part": None,
                                        "plate_txt": "Chain Case"
                                        },
                             "quantity": "1",
                             "serial_number": "",
                             "uom": "EA"
                             },

                             "resource_uri": "/v1/bom-visualizations/1/",
                             "serial_number": 123,
                             "x_coordinate": 10,
                             "y_coordinate": 20,
                             "z_coordinate": 30
                             } 

SERVICE_CIRCULAR = dict((('product_type','p1'),('type_of_circular','1'),('change_no','12'),('new_circular','1'),('buletin_no','123'),('circular_date','2015-04-12'),('from_circular','a'),('to_circular','s'),('cc_circular','d'),('circular_subject','dd'),('part_added','lk'),('circular_title','hj'),('part_deleted','jh'),('part_changed','kj'),('model_name','hn'),('sku_description','uu'),('model_sku_code','00DJ07ZZ'),('model_sku_code','00DK04ZZ')))

SBOM_REVIEW = {"bom_number":"211760",
               "sku_code":"112",
               "plate_id" : "44",
               "part_number" : "15161069",
               "status" : "Publish",
               "quantity" : "1"
               }

PRODUCT_SPECIFICATIONS =  {
                           "created_date": "2015-06-16T14:23:29",
                           "engine_displacement": "125 cc",
                           "engine_starting": "electric",
                           "engine_type": "1 cylinder",
                           "maximum_power": "15",
                           "modified_date": "2015-06-16T14:23:29",
                           "product_type": AFTERBUY_PRODUCTS.get("product_type")
                           }
PRODUCT_FEATURES = {
                    "created_date": "2015-06-16T14:23:53",
                    "description": "Electronics",
                    "modified_date": "2015-06-16T14:23:53",
                    "product_type": AFTERBUY_PRODUCTS.get("product_type")
                    }

PRODUCT_RECOMMENDED_PARTS = {
                             "created_date": "2015-06-17T15:04:15",
                             "material": "copper",
                             "modified_date": "2015-06-17T15:04:15",
                             "name": "dasdasd",
                             "part_id": "121",
                             "price": "1200",
                             "product_type":[AFTERBUY_PRODUCTS.get("product_type")],
                             "resource_uri": "/afterbuy/v1/product-parts/1/"
                             }

ADD_PRODUCT = {
               "brand_name": "bajaj",
               "product_id" : "VBKJUC4L2FC035111",
               "model_name" : "bike",
               "model_year" : "2014-02-01"
            }

PRODUCT_BRAND =  {
                  "created_date": "2015-06-19T11:20:37",
                  "description": "",
                  "image_url": "sss",
                  "industry": {
                               "created_date": "2015-06-19T11:20:33",
                               "description": "",
                               "id": 1,
                               "modified_date": "2015-06-19T15:42:55",
                               "name": "Automobiles",
                               "resource_uri": "/afterbuy/v1/industries/1/"
                               },
                  "is_active": True,
                  "modified_date": "2015-06-19T15:42:55",
                  "name": "bajaj",
                  "resource_uri": "/afterbuy/v1/brands/1/"
                  } 

USER_MOBILE_INFO = {
                    "ICCID": "689",
                    "IMEI": "4567008",
                    "available_memory": None,
                    "brand": "",
                    "capacity": "",
                    "consumer": "/afterbuy/v1/consumers/1/",
                    "created_date": "2015-07-14T13:39:30",
                    "mac_address": "",
                    "model": "",    
                    "modified_date": "2015-07-14T13:39:30",
                    "network_provider": "",
                    "operating_system": "",
                    "phone_name": "rtyu",
                    "resource_uri": "/afterbuy/v1/user-mobile-info/1/",
                    "serial_number": "",
                    "total_memory": None,
                    "version": ""
                    }

SERVICE_CENTER_LOCATION = {
                           "address": "",
                           "brand": "bajaj",
                           "country": "",
                           "created_date": "2015-07-14",
                           "latitude": 10,
                           "longitude": 8,
                           "modified_date": "2015-07-14",
                           "name": "name1",
                           "phone_number": "",
                           "pincode": "",
                           "state": ""            
                           }

BOOK_SERVICE = {
                "asc_id": "1",
                "service_date" : "2015-09-06",
                "product_id" : "VBK23456789098765"
                }
   
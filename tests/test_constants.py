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
                     "brand": {
                               "created_date": "2014-11-20T14:49:11",
                               "description": "",
                               "id": 1,
                               "image_url": "a",
                               "industry": {
                                            "created_date": "20-11-2014T12:49:10",
                                            "description": "a",
                                            "id": 1,                                    
                                            "modified_date": "20-11-20T12:49:10",
                                            "name": "Aruba",                            
                                            "resource_uri": "/afterbuy/v1/industries/1/"
                                            },
                               "is_active": True,
                               "modified_date": "2014-11-20T12:49:11",
                               "name": "Aruba",
                               "resource_uri": "/afterbuy/v1/brands/1/"
                               },
                     "brand_product_id": "11",
                     "color": "red",
                     "consumer": {
                                  "accepted_terms": False,
                                  "address": "",
                                  "consumer_id": "2c099e10-043d-4b59-9243-8ece03b137d0",
                                  "country": "",
                                  "created_date": "20-11-2012T14:48:51",
                                  "date_of_birth": None,
                                  "gender": None,
                                  "image_url": "guest.png",
                                  "modified_date": "20-11-2012T14:48:51",
                                  "phone_number": "7760814041",
                                  "pincode": "",
                                  "resource_uri": "/afterbuy/v1/consumers/2/",
                                  "state": "h",
                                  "tshirt_size": None,
                                  "user": {
                                           "date_joined": "20-11-2014T12:48:24",
                                           "email":"test.ab@gmail.com",
                                           "first_name": "",
                                           "id": 1,                                   
                                           "last_login": "20-11-2014T12:48:23",
                                           "last_name": "",
                                           "resource_uri": "",
                                           "username": "test"
                                           }
                                  },
                     "description": "",

                     "image_url": "sss",
                     "is_deleted": False,
                     "nick_name": "aaa",
                     "product_type": {
                                      "created_date": "20-11-2014T12:49:20",
                                      "id": 1,
                                      "image_url": "a",
                                      "is_active": True,
                                      "modified_date": "20-11-2014T12:49:20",
                                      "product_type": "aaa",
                                      "resource_uri": "/afterbuy/v1/product-types/1/"
                                      },
                     "purchase_date": "20-11-2014T12:49:24"
                     }

AFTERBUY_PRODUCTS = {
                     "brand": {
                               "created_date": "2014-11-20T14:49:11",
                               "description": "",
                               "id": 1,
                               "image_url": "a",
                               "industry": {
                                            "created_date": "20-11-2014T12:49:10",
                                            "description": "a",
                                            "id": 1,                                    
                                            "modified_date": "20-11-20T12:49:10",
                                            "name": "Aruba",                            
                                            "resource_uri": "/afterbuy/v1/industries/1/"
                                            },
                               "is_active": True,
                               "modified_date": "2014-11-20T12:49:11",
                               "name": "Aruba",
                               "resource_uri": "/afterbuy/v1/brands/1/"
                               },
                     "brand_product_id": "11",
                     "color": "red",
                     "consumer": {
                                  "accepted_terms": False,
                                  "address": "",
                                  "consumer_id": "2c099e10-043d-4b59-9243-8ece03b137d0",
                                  "country": "",
                                  "created_date": "20-11-2012T14:48:51",
                                  "date_of_birth": None,
                                  "gender": None,
                                  "image_url": "guest.png",
                                  "modified_date": "20-11-2012T14:48:51",                                  
                                  "pincode": "",
                                  "resource_uri": "/afterbuy/v1/consumers/2/",
                                  "state": "h",
                                  "tshirt_size": None,
                                  "user": {
                                           "date_joined": "20-11-2014T12:48:24",                                           
                                           "first_name": "",
                                           "id": 1,                                   
                                           "last_login": "20-11-2014T12:48:23",
                                           "last_name": "",
                                           "resource_uri": "",
                                           "username": "test"
                                           }
                                  },
                     "description": "",

                     "image_url": "sss",
                     "is_deleted": False,
                     "nick_name": "aaa",
                     "product_type": {
                                      "created_date": "20-11-2014T12:49:20",
                                      "id": 1,
                                      "image_url": "a",
                                      "is_active": True,
                                      "modified_date": "20-11-2014T12:49:20",
                                      "product_type": "aaa",
                                      "resource_uri": "/afterbuy/v1/product-types/1/"
                                      },
                     "purchase_date": "20-11-2014T12:49:24"
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
                           "address":"",
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
                    "brand":AFTERBUY_PRODUCTS.get("brand"), 
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
                        "model":"aaa",
                        }
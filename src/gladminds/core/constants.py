from gladminds.core.auth_helper import Roles

TIME_FORMAT = '%Y-%m-%d %H:%M:%S'

DATE_FORMAT = '%d-%m-%Y %H:%M' 

PAGINATION_LINKS = 3

RECORDS_PER_PAGE = ['5', '10', '25', '50']

BY_DEFAULT_RECORDS_PER_PAGE = RECORDS_PER_PAGE[0]

ALL = 'all'

PROVIDERS = ['asc', 'dasc', 'dealer', 'helpdesk', 'asm', 'rps']

PROVIDER_MAPPING = {
                    'dealer' : 'dealer/login.html',
                    'helpdesk' : 'service-desk/login.html',
                 }

SERVICE_MAPPING = {
                    'service_desk' : '/aftersell/helpdesk',
                 }

GROUP_MAPPING = {
                Roles.DEALERS : '/aftersell/dealer/login',
                Roles.ASCS : '/aftersell/asc/login',
                Roles.DASCS :'/aftersell/asc/login',
                Roles.SDOWNERS :'/aftersell/helpdesk/login',
                Roles.SDMANAGERS : '/aftersell/helpdesk/login',
                Roles.SDREADONLY : '/aftersell/helpdesk/login'
                }

USER_GROUPS = [ Roles.DEALERS, Roles.ASCS, Roles.DASCS, Roles.SDOWNERS, Roles.SDMANAGERS, Roles.DEALERADMIN, Roles.SDREADONLY]

REDIRECT_USER ={
                 Roles.DEALERS : '/aftersell/register/asc',
                 Roles.ASCS : '/aftersell/register/sa',
                 Roles.SDOWNERS : '/aftersell/helpdesk',
                 Roles.SDMANAGERS : '/aftersell/helpdesk',
                 Roles.SDREADONLY : '/aftersell/helpdesk'
                }

TEMPLATE_MAPPING = {
                    'asc' :'portal/asc_registration.html',
                    'sa' :'portal/sa_registration.html',
                    'customer' : 'portal/customer_registration.html'
                    }
ACTIVE_MENU ={
              'asc' : 'register_asc',
              'sa' : 'register_sa',
              'customer' : 'register_customer'
              }

FEEDBACK_STATUS = (
        ('Open', 'Open'),
        ('Closed', 'Closed'),
        ('Resolved', 'Resolved'),
        ('In Progress', 'In Progress'),
        ('Pending', 'Pending')
    )

FEEDBACK_STATUS_LEVEL_ONE = (
        ('Open', 'Open'),
        ('Closed', 'Closed'),
        ('Resolved', 'Resolved'),
        ('In Progress', 'In Progress'),
        ('Pending', 'Pending'),
        ('Assigned', 'Assigned')
    )

FEEDBACK_STATUS_LEVEL_TWO = (
        ('Open', 'Open'),
        ('Closed', 'Closed'),
        ('Resolved', 'Resolved'),
        ('In Progress', 'In Progress'),
        ('Pending', 'Pending')
    )

ECO_RELEASE_STATUS = (
                      ('Open', 'Open'),
                      ('Closed', 'Closed'),
                      ('Under Review', 'Under Review'),
    )

ECO_IMPLEMENTATION_STATUS = (
                      ('Open', 'Open'),
                      ('Closed', 'Closed'),
                      ('Rejected', 'Rejected'),
                      ('Approved', 'Approved'),
                      ('Under Review', 'Under Review'),
    )


PRIORITY = (
        ('Low', 'Low'),
        ('High', 'High'),
        ('Medium', 'Medium'),
        ('Urgent', 'Urgent'),
    )

DEMO_PRIORITY = (
        ('P3', 'P3'),
        ('P2', 'P2'),
        ('P1', 'P1'),
    )

PRIORITIES = { 'bajaj' : (
        ('Low', 'Low'),
        ('High', 'High'),
        ('Medium', 'Medium'),
        ('Urgent', 'Urgent'),
    ),
            'daimler' : (
        ('P3', 'P3'),
        ('P2', 'P2'),
        ('P1', 'P1'),
    ),
}

FEEDBACK_TYPE = (('Problem', 'Problem'),
                 ('Question', 'Question'),
                 ('Feature Request', 'Feature Request'),
                 ('Suggestion', 'Suggestion'),)

SLA_PRIORITY = (('Low', 'Low'),
                ('Medium', 'Medium'),
                ('High', 'High'),
                ('Urgent', 'Urgent'),)

LOYALTY_SLA_STATUS = (('Open','Open'),
                      ('Accepted','Accepted'),
                      ('Approved','Approved'),
                      ('Packed','Packed'),
                      ('Shipped','Shipped'),
                      ('Delivered','Delivered'))

LOYALTY_SLA_ACTION = (('Welcome Kit','Welcome Kit'),
                      ('Redemption','Redemption'))

TIME_UNIT = (('mins', 'mins'),
             ('hrs', 'hrs'),
             ('days', 'days'),)

RATINGS = (
           ('1','Glad'),
           ('2','Very Glad'),
           ('3','Not Glad')
        )

SAVE_PLATE_PART_STATUS = (
                          ('Pending','Pending'),
                          ('Approved','Approved'),
                          ('Rejected','Rejected')
                          )

ROOT_CAUSE = (('Data','Data'),
              ('Infrastructure','Infrastructure'),
              ('Bug','Bug'),
              ('New Requirement','New Requirement'),
              ('Network','Network'),
              ('Non-issue','Non-issue'),
              ('External System','External System'))

MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

GENDER_CHOICES = (
    ('M', 'Male'),
    ('F', 'Female'),
    ('X', 'Other'),
)

SIZE_CHOICES = (
    ('S', 'Small'),
    ('M', 'Medium'),
    ('L', 'Large'),
    ('XL', 'Extra Large'),
)

FUEL_CHOICES = (
    ('Petrol', 'Petrol'),
    ('Diesel', 'Diesel'),
    ('Electric', 'Electric'),
    ('Other', 'Other'),
)

STATUS_CHOICES = ((1, 'Unused'), (2, 'Closed'), (
    3, 'Expired'), (4, 'In Progress'), (
       5, 'Exceeds Limit'), (6, 'Closed Old Fsc'))


COUPON_STATUS = dict((v, k) for k, v in dict(STATUS_CHOICES).items())

MAX_UPC_ALLOWED=10
MANDATORY_MECHANIC_FIELDS = ['first_name', 'phone_number','shop_address', 'shop_name', 'district', 'state', 'pincode', 'registered_by_distributor', 'image_url']

FORM_STATUS_CHOICES = (
                       ('Complete', 'Complete'),
                       ('Incomplete', 'Incomplete'),
                       )

FEED_TYPES = ['Dispatch Feed', 'Purchase Feed', 'Credit Note Feed', 'CDMS Feed', 'Old Fsc Feed', 'ContainerTracker Feed', 'Manufacture data Feed']

STATUS_TO_NOTIFY = ['Approved', 'Rejected', 'Accepted', 'Shipped', 'Delivered']

REDEMPTION_STATUS = (
        ('Open', 'Open'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
        ('Accepted', 'Accepted'),
        ('Packed', 'Packed'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered')
    )

GP_REDEMPTION_STATUS = (
        ('Approved', 'Approved'),
        ('Accepted', 'Accepted'),
        ('Packed', 'Packed'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered')
    )

LP_REDEMPTION_STATUS = (
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered')
    )

PARTNER_TYPE = (
        ('Merchant', 'Merchant'),
        ('Redemption', 'Redemption'),
        ('Logistics', 'Logistics'),
        ('Marketing', 'Marketing')
    )

WELCOME_KIT_STATUS = (
        ('Open', 'Open'),
        ('Accepted', 'Accepted'),
        ('Packed', 'Packed'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered')
    )

class FeedStatus():
    RECEIVED = 'Received'
    SENT = 'Sent'


class FeedSentType():
    COUPON_REDEEM = 'Coupon Redeem Feed'
    CUSTOMER_REGISTRATION = 'Customer Registration Feed'
    PURCHASE_SYNC_FEED = 'Purchase Sync Feed'

FEED_SENT_TYPES = [getattr(FeedSentType, x) for x in dir(FeedSentType) if (not x.startswith("__"))]


class CouponStatus():
    UNUSED = 1
    CLOSED = 2
    EXPIRED = 3
    IN_PROGRESS = 4
    EXCEEDS_LIMIT = 5
    CLOSED_OLD_FSC = 6

class TicketStatus():
    OPEN = 'Open'
    CLOSED = 'Closed'
    IN_PROGRESS = 'In Progress'
    RESOLVED = 'Resolved'
    PENDING = 'Pending'

DOWNLOAD_MECHANIC_FIELDS = ['permanent_id', 'first_name', 'middle_name', 'last_name', 'phone_number', 'date_of_birth', 'address_line_1', 'address_line_2', 'address_line_3', 'address_line_4', 'address_line_5', 'address_line_6','shop_number', 'shop_name', 'shop_address', 'district', 'state', 'pincode', 'registered_by_distributor', 'image_url',]
DOWNLOAD_WELCOME_KIT_FIELDS = ['permanent_id', 'first_name', 'middle_name', 'last_name', 'phone_number', 'delivery_address', 'district', 'state', 'pincode', 'image_url']
DOWNLOAD_REDEMPTION_FIELDS = ['permanent_id', 'first_name', 'middle_name', 'last_name', 'phone_number', 'delivery_address', 'district', 'state', 'pincode', 'product']
DOWNLOAD_ACCUMULATION_FIELDS = ['permanent_id', 'first_name', 'middle_name', 'last_name', 'phone_number', 'state', 'shop_name','asm', 'points', 'total_points', 'upcs', 'created_date']
MEMBER_FIELDS = ['permanent_id','first_name', 'middle_name', 'last_name', 'phone_number', 'state', 'shop_name']


'''Below headers are used in API for Powerrwards'''

MEMBER_API_HEADER = ['Mechanic Id', 'Mechanic Name','District','Mobile Number','State','Distributor Code','Date Of Registration','Address of garage']
ACCUMULATION_API_HEADER = ['mechanic_id', 'first_name','district','phone_number','state_name','distributor_id','unique_part_code','points','created_date']
ACCUMULATION_API_HEADER_MEMBER_FIELDS = ['mechanic_id','first_name', 'district','phone_number']
REDEMPTION_API_HEADER = ['mechanic_id', 'first_name','district','phone_number','state_name','distributor_id','created_date','points','product_id']
ACCUMULATION_FITMENT_API_HEADER = ['mechanic_id', 'first_name','district','phone_number','state_name','distributor_id', 'unique_part_code','points','part_number', 'description', 'created_date']
MONTHLY_ACTIVE_API_HEADER = ['State', 'No of Mechanic Registered (till date)','No of Mechanic messaged','%active','ASM Name']

LOYALTY_ACCESS = {
                'query_field' : {
                                  Roles.RPS:{
                                             'user':'packed_by' 
                                             },
                                  Roles.LPS : {
                                                'user':'partner__user__user__username'
                                              },
                                  Roles.DISTRIBUTORS:{
                                                 'user':'member__registered_by_distributor__city', 
                                                 'area':'district',
                                                 'group_region': 'district'
                                                 }, 
                                  Roles.AREASPARESMANAGERS : {
                                                'user':'member__state__in',
                                                'area':'state__in',
                                                'group_region': 'state__state_name'
                                               },
                                 Roles.NATIONALSPARESMANAGERS : {
                                                'user':'member__state__territory__in',
                                                'area':'state__territory__in',
                                                'group_region': 'state__territory__territory'
                                               },
                                
                                }
                }
CONSIGNMENT_STATUS = (
        ('Open', 'Open'),
        ('Inprogress', 'Inprogress'),
        ('Closed', 'Closed')
    )

KTM_VIN ='VBK'
SBOM_STATUS = (('Reject', 'Reject'),
               ('Publish', 'Publish'))

SERVICE_STATUS = (('Pending', 'Pending'),
                  ('Confirmed', 'Confirmed'),
                  ('Completed', 'Completed'),
                  ('Cancelled', 'Cancelled'))

WORKFLOW_STATUS = (
        ('Open', 'Open'),
        ('Completed', 'Completed')
    )

#################### ADDED FOR RETAILER STATUS TAKEN FROM SFA#################################
STATUS = {'REJECTED': 0, 'WAITING_FOR_APPROVAL': 1, 'APPROVED': 2}
RETAILER_SEQUENCE_INCREMENT = 1
RETAILER_SEQUENCE =  600001

APPROVE_RETAILER_SUBJECT = "retailer is approved"

APPROVE_RETAILER_MESSAGE = "your retailer membership is approved.\
                           you can login with your registered username and password"

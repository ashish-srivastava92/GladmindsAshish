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

FEED_TYPES = ['Dispatch Feed', 'Purchase Feed', 'Credit Note Feed', 'CDMS Feed', 'Old Fsc Feed']

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

WELCOME_KIT_MECHANIC_FIELDS = ['Mechanic ID', 'first_name', 'middle_name', 'last_name', 'phone_number', 'date_of_birth', 'address_line_1', 'address_line_2', 'address_line_3', 'address_line_4', 'address_line_5', 'address_line_6','shop_name', 'shop_address', 'district', 'state', 'pincode', 'registered_by_distributor', 'image_url',]

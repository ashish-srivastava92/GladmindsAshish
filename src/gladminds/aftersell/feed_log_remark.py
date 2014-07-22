import json
import uuid
import logging
import os
from collections import Counter
from django.conf import settings
from gladminds.sqs_tasks import send_report_mail_for_feed_failure
from gladminds.audit import feed_log
from gladminds.utils import uploadFileToS3


logger = logging.getLogger('gladminds')

class FeedLogWithRemark():

    def __init__(self, total_feeds, feed_type, action, status):
        self.total_feeds = total_feeds
        self.failed_feeds = 0
        self.feed_type = feed_type
        self.action = action
        self.status = status
        self.remarks = Counter()

    def fail_remarks(self, remark):
        self.remarks[remark] += 1
        self.failed_feeds = self.failed_feeds + 1

    def save_to_feed_log(self):
        success_data_count = self.total_feeds - self.failed_feeds
        remarks = json.dumps(self.remarks)

        path = ""
        if self.failed_feeds and settings.FEED_FAILURE_MAIL_ENABLED:
            send_report_mail_for_feed_failure(remarks=remarks, 
                                              feed_type = self.feed_type)
        if self.failed_feeds:
            try:
                path = self.upload_file(remarks)
            except Exception as ex :
                logger.error("Feed file not updated on s3 : %s" % ex)
        
        feed_log(feed_type=self.feed_type, total_data_count=self.total_feeds,
              failed_data_count=self.failed_feeds,
              success_data_count=success_data_count, status=self.status,
              action=self.action, remarks=remarks, file_location=path)
    
    def upload_file(self, remarks):
        file_name = self.get_file_name()
        
        file_obj = open(file_name, 'w')
        file_obj.write(remarks)
        file_obj.close()
        file_obj = open(file_name, 'r')
        destination = settings.FEED_FAILURE_DIR.format('bajaj')
        
        path = uploadFileToS3(destination=destination, file_obj=file_obj, 
                  bucket=settings.FEED_FAILURE_BUCKET, file_mimetype='text/plain',
                  logger_msg="Feed File Failure Uploaded")
        file_obj.close()
        
        os.remove("{0}/{1}".format(settings.BASE_DIR, file_name))
        
        return path
    
    def get_file_name(self):
        filename_suffix = str(uuid.uuid4())
        filename_prefix = '_'.join(self.feed_type.split(" "))
        return str(filename_prefix)+'_'+filename_suffix+'.'+'log'

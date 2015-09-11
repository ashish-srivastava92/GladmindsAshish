sudo crontab -r
sudo crontab -l | (cat;echo "*/5 * * * *  python /opt/app/gladminds/src/gladminds/core/cron_jobs/trigger_sqs_tasks.py send_reminders_for_servicedesk gladminds-prod2") | sudo crontab
sudo crontab -l | (cat;echo "00 */4 * * *  python /opt/app/gladminds/src/gladminds/core/cron_jobs/trigger_sqs_tasks.py export_coupon_redeem_to_sap gladminds-prod2") | sudo  crontab
sudo crontab -l | (cat;echo "00 00 * * *  python /opt/app/gladminds/src/gladminds/core/cron_jobs/trigger_sqs_tasks.py expire_service_coupon gladminds-prod2") | sudo  crontab
sudo crontab -l | (cat;echo "00 00 * * *  python /opt/app/gladminds/src/gladminds/core/cron_jobs/trigger_sqs_tasks.py send_reminder gladminds-prod2") | sudo crontab
sudo crontab -l | (cat;echo "00 00 * * *  python /opt/app/gladminds/src/gladminds/core/cron_jobs/trigger_sqs_tasks.py import_data gladminds-prod2") | sudo crontab
sudo crontab -l | (cat;echo "00 00 * * *  python /opt/app/gladminds/src/gladminds/core/cron_jobs/trigger_sqs_tasks.py send_schedule_reminder gladminds-prod2") | sudo crontab
sudo crontab -l | (cat;echo "00 00 * * *  python /opt/app/gladminds/src/gladminds/core/cron_jobs/trigger_sqs_tasks.py delete_unused_otp gladminds-prod2") | sudo crontab
sudo crontab -l | (cat;echo "00 15 * * *  python /opt/app/gladminds/src/gladminds/core/cron_jobs/trigger_sqs_tasks.py export_customer_reg_to_sap gladminds-prod2") | sudo  crontab
sudo crontab -l | (cat;echo "00 19 * * *  python /opt/app/gladminds/src/gladminds/core/cron_jobs/trigger_sqs_tasks.py send_report_mail_for_feed gladminds-prod2") | sudo crontab
sudo crontab -l | (cat;echo "00 19 * * *  python /opt/app/gladminds/src/gladminds/core/cron_jobs/trigger_sqs_tasks.py send_mail_for_feed_failure gladminds-prod2") | sudo crontab
sudo crontab -l | (cat;echo "00 19 * * *  python /opt/app/gladminds/src/gladminds/core/cron_jobs/trigger_sqs_tasks.py send_mail_for_customer_phone_number_update gladminds-prod2") | sudo crontab
sudo crontab -l | (cat;echo "00 19 * * *  python /opt/app/gladminds/src/gladminds/core/cron_jobs/trigger_sqs_tasks.py send_vin_sync_feed_details gladminds-prod2") | sudo crontab
sudo crontab -l | (cat;echo "00 19 * * *  python /opt/app/gladminds/src/gladminds/core/cron_jobs/trigger_sqs_tasks.py export_purchase_feed_sync_to_sap gladminds-prod2") | sudo crontab
sudo crontab -l | (cat;echo "00 19 * * *  python /opt/app/gladminds/src/gladminds/core/cron_jobs/trigger_sqs_tasks.py send_mail_customer_phone_number_update_exceeds gladminds-prod2") | sudo crontab
sudo crontab -l | (cat;echo "00 19 * * *  python /opt/app/gladminds/src/gladminds/core/cron_jobs/trigger_sqs_tasks.py send_mail_for_policy_discrepency gladminds-prod2") | sudo crontab 

sudo crontab -l | (cat;echo "00 19 * * *  python /opt/app/gladminds/src/gladminds/core/cron_jobs/trigger_sqs_tasks.py brand_sync_to_afterbuy gladminds-prod2") | sudo crontab 


sudo crontab -l | (cat;echo "00 19 * * *  python /opt/app/gladminds/src/gladminds/core/cron_jobs/trigger_sqs_tasks.py export_member_temp_id_to_sap gladminds-prod2 bajajcv") | sudo crontab 
sudo crontab -l | (cat;echo "00 00 * * *  python /opt/app/gladminds/src/gladminds/core/cron_jobs/trigger_sqs_tasks.py export_member_accumulation_to_sap gladminds-prod2 bajajcv") | sudo crontab 
sudo crontab -l | (cat;echo "00 00 * * *  python /opt/app/gladminds/src/gladminds/core/cron_jobs/trigger_sqs_tasks.py export_member_redemption_to_sap gladminds-prod2 bajajcv") | sudo crontab 

sudo crontab -l | (cat;echo "00 00 * * *  python /opt/app/gladminds/src/gladminds/core/cron_jobs/trigger_sqs_tasks.py expire_service_coupon gladminds-prod2 bajajib") | sudo  crontab

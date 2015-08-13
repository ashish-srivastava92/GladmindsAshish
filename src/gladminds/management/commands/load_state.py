import csv
from django.conf import settings
from django.core.management.base import BaseCommand
from gladminds.core.model_fetcher import get_model
APP='bajaj'

class Command(BaseCommand):

    def handle(self, *args, **options):
        self.upload_state()

    def upload_state(self):
        print "Started uploading state..."
        file_list = ['STATE_LIST.csv']
        state_list = []
        state_model = get_model('State', APP)
        for i in range(0, 1):
            with open(settings.PROJECT_DIR + '/upload_data/' + file_list[i], 'r') as csvfile:
                spamreader = csv.reader(csvfile, delimiter=',')
                next(spamreader)
                for row_list in spamreader:
                    temp ={}
                    temp['state_code'] = row_list[0].strip()
                    temp['state_name'] = row_list[1].strip()
                    state_list.append(temp)
        for state in state_list:
            state_obj = state_model.objects.filter(state_name=state['state_name']).using(APP)
            if not state_obj:
                state_obj = state_model(
                                            state_name=state['state_name'],
                                            state_code = state['state_code']
                                )
                state_obj.save(using=APP)

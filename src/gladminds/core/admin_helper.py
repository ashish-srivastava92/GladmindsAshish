from django.contrib.admin.options import ModelAdmin
from suit.admin import SortableTabularInline
from suit.widgets import EnclosedInput, AutosizedTextarea
from django.forms.models import ModelForm
from django.contrib.admin.views.main import ORDER_VAR, ChangeList
from gladminds.core import utils
from django.core.urlresolvers import reverse
from django.http.response import HttpResponseRedirect
from django.contrib import messages
from gladminds.core.model_fetcher import models
from gladminds.core.auth_helper import Roles


class GmModelAdmin(ModelAdmin):
    groups_update_not_allowed = [Roles.READONLY]
    
    def changelist_view(self, request, extra_context={}):
        searchable_fields=[]
        if not extra_context.has_key('custom_search'):
            for field in self.search_fields:
                searchable_fields.append(field.split('__')[0].replace('_', ' ',).replace('^','').title())
            extra_context['searchable_fields'] = ', '.join(searchable_fields)
        return super(GmModelAdmin, self).changelist_view(request, extra_context=extra_context)     

    def change_view(self, request, object_id, form_url='', extra_context=None):
        model = self.model
        opts = model._meta
        self.groups_update_not_allowed.append(Roles.READONLY)
        if request.method == 'POST' and not "_saveasnew" in request.POST:
            if request.user.groups.filter(name__in=self.groups_update_not_allowed).exists():
                post_url_continue = reverse('admin:%s_%s_changelist' %
                                   (opts.app_label, opts.model_name),
                                   current_app=self.admin_site.name)
                self.message_user(request, "Sorry, you do not have permission to update.",
                                  level=messages.ERROR)
                return HttpResponseRedirect(post_url_continue)
        return super(GmModelAdmin, self).change_view(request, object_id,
                                                     form_url=form_url,
                                                     extra_context=extra_context)

    def get_user(self, obj):
        if obj.user:
            return obj.user.user.first_name
        return None
    
    def get_profile_number(self, obj):
        return obj.user.phone_number
    
    def get_profile_address(self, obj):
        return obj.user.address
    
    def get_mechanic_id(self, obj):
        if obj.permanent_id:
            return obj.permanent_id
        return obj.mechanic_id

    get_profile_number.short_description = 'Phone number'
    get_profile_address.short_description = 'Address'
    get_user.short_description = 'Name'
    
    def get_mechanic_name(self, obj):
        return obj.member.first_name

    def get_transporter_username(self, obj):
        return obj.user.user.username
    
    def get_transporter_name(self, obj):
        return obj.user.user.first_name
    
    def get_supervisor_username(self, obj):
        return obj.user.user.username

    def get_supervisor_name(self, obj):
        return obj.user.user.first_name
        
    def get_mechanic_pincode(self, obj):
        return obj.member.pincode

    def get_mechanic_district(self, obj):
        return obj.member.district
    
    def get_asm(self, obj):
        asm_obj = models.AreaSparesManager.objects.filter(state=obj.member.state)
        if asm_obj:
            asm_list = []
            for asm in asm_obj:
                asm_list.append(str(asm.name))
        return asm_list

    def get_mechanic_state(self, obj):
        return obj.member.state.state_name
    
    def get_transporter(self, obj):
        return obj.transporter.transporter_id
    
    def get_indent_status(self, obj):
        return obj.zib_indent_num.status
    
    get_indent_status.short_description = 'Status'
    get_mechanic_id.short_description = 'Mechanic ID'
    get_mechanic_name.short_description = 'Name'
    get_mechanic_pincode.short_description = 'PIN code'
    get_mechanic_district.short_description = 'City'
    get_mechanic_state.short_description = 'State'
    get_transporter_username.short_description = 'Username'
    get_transporter_name.short_description = 'Name'
    get_supervisor_username.short_description = 'Username'
    get_supervisor_name.short_description = 'Name'
    get_transporter.short_description = 'Transporter ID'
    get_asm.short_description = "ASM "
    
    def get_part_description(self, obj):
        return obj.part_number.description

    get_part_description.short_description = 'Description'

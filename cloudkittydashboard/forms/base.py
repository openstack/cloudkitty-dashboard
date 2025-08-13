# Copyright 2012 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
#
# Copyright 2012 Nebula, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
from django import forms


class DateForm(forms.Form):
    """A simple form for selecting a range of time."""
    start = forms.DateField(input_formats=("%Y-%m-%d",))
    end = forms.DateField(input_formats=("%Y-%m-%d",))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['start'].widget.attrs['data-date-format'] = "yyyy-mm-dd"
        self.fields['end'].widget.attrs['data-date-format'] = "yyyy-mm-dd"


class CheckBoxForm(forms.Form):
    """A form for selecting fields to group by in the rating summary."""
    checkbox_fields = ["type", "id", "user_id"]
    for field in checkbox_fields:
        locals()[field] = forms.BooleanField(required=False)

    def get_selected_fields(self):
        """Return list of selected groupby fields."""
        if not self.is_valid():
            return []
        # Get all selected checkbox fields
        selected = [
            field for field in self.checkbox_fields
            if self.cleaned_data.get(field)
        ]
        return selected

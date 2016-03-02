/*
 Copyright 2015 Objectif Libre

    Licensed under the Apache License, Version 2.0 (the "License"); you may
    not use this file except in compliance with the License. You may obtain
    a copy of the License at

         http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
    License for the specific language governing permissions and limitations
    under the License.
*/

pricing = {
    is_price: false, // Is this a price display ?

    init: function() {
        this._attachInputHandlers(); // handler
    },

    init_work: function() {
        this.is_price = true;
        //$('#price').text('0');

        this.init();
        this.work();
    },

    /*
     Attaches event handlers for the form elements associated with the price
     (see horizon.Quota._attachInputHandlers).
     */
    _attachInputHandlers: function() {
        var scope = this;

        if (this.is_price) {
            var eventCallback = function(evt) {
                scope.work();
            };

            $('#id_flavor').on('change', eventCallback);
            $('#id_count').on('change', eventCallback);
            $('#id_image_id').on('change', eventCallback);
        }
    },

    work: function() {
        // Quota available → what about the selected flavor
        if (horizon.Quota.selected_flavor) {
            // get data of the flavor (form)
            _image = horizon.Quota.getSelectedImage();
            var flavor = horizon.Quota.selected_flavor.name;
            var vcpus = horizon.Quota.selected_flavor.vcpus;
            var disk = horizon.Quota.selected_flavor.disk;
            var ephemeral = horizon.Quota.selected_flavor["OS-FLV-EXT-DATA:ephemeral"];
            var disk_total = horizon.Quota.selected_flavor.disk + horizon.Quota.selected_flavor["OS-FLV-EXT-DATA:ephemeral"];
            var disk_total_display = disk_total;
            var ram = horizon.Quota.selected_flavor.ram;
            var source_type = $('#id_source_type option:selected').val();
            var source_val = $('#id_' + source_type + ' option:selected').val();
            var instance_count = parseInt($("#id_count").val());

            // make the json data form
            desc_form = {
                'flavor': flavor,
                'source_type': source_type,
                'source_val': source_val, // images : horizon.Quota.findImageById(source_val);
                'vcpus': vcpus,
                'disk': disk,
                'ephemeral': ephemeral,
                'disk_total': disk_total,
                'disk_total_display': disk_total_display,
                'ram': ram
            }
            if (_image != undefined) {
                desc_form['image_id'] = _image.id
            }
            var form_data = [{"service": "compute", "desc": desc_form, "volume": instance_count}];

            // send the JSON by a POST request
            var url_data = [
                '/dashboard/project/rating/quote',
                '/project/rating/quote']
            this.sendPost(form_data, url_data);
        }
    },

    sendPost: function(form_data, url_data) {
        var url = url_data.shift();
        $.ajax({
            type: "post",  // send POST data
            url: url,
            dataType: 'json',
            data: JSON.stringify(form_data), // data sent
            contentType: 'application/json; charset=utf-8',
            success: function (data) {
                $("#price").text(data);
            },
            error: function () {
                if (url_data)
                    pricing.sendPost(form_data, url_data);
            },
            beforeSend: function(xhr, settings){
                $.ajaxSettings.beforeSend(xhr, settings);
            }
        });
    }
};

// https://docs.djangoproject.com/en/dev/ref/contrib/csrf/#ajax
// http://stackoverflow.com/a/6199592
// http://coreymaynard.com/blog/performing-ajax-post-requests-in-django/
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
            // Only send the token to relative URLs i.e. locally.
            xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
        }
    }
});

if(typeof horizon.Quota !== 'undefined') {
    pricing.init_work();
} else {
    addHorizonLoadEvent(function() {
        pricing.init_work();
    });
}


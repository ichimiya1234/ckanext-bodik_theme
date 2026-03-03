import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import ckan.lib.helpers as helpers
from ckan.common import config
import sys
import json
import datetime
from ckan.lib.plugins import DefaultTranslation

def dataset_count( search_org ):
    if search_org != "":
        search_org = 'organization:' + search_org
        count = toolkit.get_action('package_search')( data_dict={'fq':search_org } )
        return count['count']
    else:
        count = toolkit.get_action('package_list')( data_dict={} )
        return len(count)

def toshiken_dataset_count( search_query ):
    count = toolkit.get_action('package_search')( data_dict={ 'q':'organization:' + search_query } )
    return count['count']

def get_tag():
    result = toolkit.get_action('package_search')( data_dict={'facet.field':'["tags"]' ,'rows':0 } )
    tags1 = result['facets']['tags']

    '''url = 'http://ckan.open-governmentdata.org/api/3/action/package_search?facet.field=[%22tags%22]&rows=0'
    response = urllib2.urlopen(url)
    s = response.read()
    result = json.loads(s)
    tags2 = result['result']['facets']['tags']

    tags = dict(tags1,**tags2)'''

    return tags1

def render_datetime(datetime_, date_format=None, with_hours=False):
    datetime_ = helpers._datestamp_to_datetime(datetime_)
    jstTime = datetime_ + datetime.timedelta(hours=9)
    return helpers.render_datetime(jstTime, date_format, with_hours)

def resource_count( search_org ):

    if search_org != "":
        search_org = 'organization:' + search_org
        datasets = toolkit.get_action('package_search')( data_dict={'q':search_org , 'rows':1000 } )
        count=0
        for dataset in datasets['results']:
            count += dataset['num_resources']
        return count
    else:
        return 0

def site_url():
    return toolkit.config.get('ckan.site_url', '#')

def wordpress_url():
    return toolkit.config.get('bodik.wordpress_url', '#')

def map_url():
    return toolkit.config.get('bodik.map_url', '#')

def translate_license_title(title):
    # Translate license names. using ckanext-bodik_theme translations
    from ckan.common import _
    return _(title) if title else '' 


class BodikThemePlugin(plugins.SingletonPlugin, DefaultTranslation):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.ITranslation)
    plugins.implements(plugins.IPackageController, inherit=True)
    # IConfigurer

    def update_config(self, config_):
        import os
        licenses_path = os.path.join(
            os.path.dirname(__file__), 'data', 'licenses.json'
        )
        config_['licenses_group_url'] = 'file://' + licenses_path
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'bodik_theme')
        
    def get_helpers(self):
        return {
            'bodik_theme_dataset_count': dataset_count,
            'bodik_theme_toshiken_dataset_count': toshiken_dataset_count,
            'bodik_theme_get_tag': get_tag,
            'bodik_theme_render_datetime': render_datetime,
            'bodik_theme_resource_count': resource_count,
            'bodik_theme_site_url': site_url,
            'bodik_theme_wordpress_url': wordpress_url,
            'bodik_theme_map_url': map_url,
            'bodik_theme_translate_license': translate_license_title,
        }
    
    def after_dataset_search(self, search_results, search_params):
        # Translate the display name for the license facet.
        facets = search_results.get('search_facets')
        if not facets or 'license_id' not in facets:
            return search_results

        for item in facets['license_id']['items']:
            display_name = item.get('display_name')
            if display_name:
                item['display_name'] = translate_license_title(display_name)

        return search_results


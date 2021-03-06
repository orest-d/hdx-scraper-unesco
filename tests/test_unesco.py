#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Unit tests for scrapername.

'''
from os.path import join
from pprint import pprint

import pytest
from hdx.hdx_configuration import Configuration
from hdx.hdx_locations import Locations
from hdx.location.country import Country

from tests.testing_data import countrydata, dimensions, observations
from unesco import generate_dataset_and_showcase, get_countriesdata, get_endpoints_metadata


class TestUnesco:
    @pytest.fixture(scope='function')
    def configuration(self):
        Configuration._create(hdx_read_only=True, user_agent='test',
                              project_config_yaml=join('tests', 'config', 'project_configuration.yml'))
        Locations.set_validlocations([{'name': 'arg', 'title': 'Argentina'}])  # add locations used in tests
        Country.countriesdata(use_live=False)

    @pytest.fixture(scope='class')
    def endpoints_metadata(self):
        return {'EDU_FINANCE': ('Education: Financial resources',
                                'http://yyyy/data/UNESCO,EDU_FINANCE/..........%s.?',
                                'http://uis.unesco.org/en/topic/education-finance')}

    @pytest.fixture(scope='function')
    def downloader(self):
        class Response:
            @staticmethod
            def json():
                pass

        class Download:
            @staticmethod
            def download(url):
                response = Response()
                if url == 'http://xxx/codelist/UNESCO/CL_AREA/latest?format=sdmx-json':
                    def fn():
                        return {'Codelist': [{'items': [countrydata]}]}
                    response.json = fn
                elif 'http://yyyy/data/UNESCO,EDU_FINANCE/' in url:
                    def fn():
                        return {'structure': {'name': 'Education: Financial resources',
                                              'dimensions': {'observation': observations}}}
                    response.json = fn
                return response

            @staticmethod
            def get_full_url(url):
                url_prefix = 'http://yyyy/data/UNESCO,EDU_FINANCE/..........AR.?format=csv'
                if url[:len(url_prefix)] == url_prefix:
                    return '%s&locale=en&subscription-key=12345' % url

        return Download()

    def test_get_countriesdata(self, downloader):
        countriesdata = get_countriesdata('http://xxx/', downloader)
        assert countriesdata == [countrydata]

    def test_get_endpoints_metadata(self, downloader, endpoints_metadata):
        endpoints = {'EDU_FINANCE': 'http://uis.unesco.org/en/topic/education-finance'}
        endpoints_metadata_actual = get_endpoints_metadata('http://yyyy/', downloader, endpoints)
        assert endpoints_metadata_actual == endpoints_metadata

    def test_generate_dataset_and_showcase(self, configuration, downloader, endpoints_metadata):
        dataset, showcase = generate_dataset_and_showcase(downloader, countrydata, endpoints_metadata)
        assert dataset == {'tags': [{'name': 'indicators'}, {'name': 'sustainable development'},
                                    {'name': 'demographics'}, {'name': 'socioeconomics'}, {'name': 'education'}],
                           'owner_org': '18f2d467-dcf8-4b7e-bffa-b3c338ba3a7c', 'data_update_frequency': '365',
                           'title': 'Argentina - Sustainable development, Education, Demographic and Socioeconomic Indicators',
                           'groups': [{'name': 'arg'}], 'maintainer': '196196be-6037-4488-8b71-d786adf4c081',
                           'name': 'unesco-indicators-for-argentina', 'dataset_date': '01/01/1970-12/31/2014',
                           'subnational': '0'}
        resources = dataset.get_resources()

        expected_description = 'To save, right click download button & click Save Link/Target As  \n[Info on Education: Financial resources](http://uis.unesco.org/en/topic/education-finance)'
        assert resources == [{'description': expected_description,
                              'url': 'http://yyyy/data/UNESCO,EDU_FINANCE/..........AR.?format=csv&startPeriod=2010&endPeriod=2014&locale=en&subscription-key=12345',
                              'name': 'Education: Financial resources (2010-2014)', 'format': 'csv'},
                             {'description': expected_description,
                              'url': 'http://yyyy/data/UNESCO,EDU_FINANCE/..........AR.?format=csv&startPeriod=2005&endPeriod=2009&locale=en&subscription-key=12345',
                              'name': 'Education: Financial resources (2005-2009)', 'format': 'csv'},
                             {'description': expected_description,
                              'url': 'http://yyyy/data/UNESCO,EDU_FINANCE/..........AR.?format=csv&startPeriod=1999&endPeriod=2004&locale=en&subscription-key=12345',
                              'name': 'Education: Financial resources (1999-2004)', 'format': 'csv'},
                             {'description': expected_description,
                              'url': 'http://yyyy/data/UNESCO,EDU_FINANCE/..........AR.?format=csv&startPeriod=1970&endPeriod=1998&locale=en&subscription-key=12345',
                              'name': 'Education: Financial resources (1970-1998)', 'format': 'csv'}]

        assert showcase == {'name': 'unesco-indicators-for-argentina-showcase',
                            'notes': 'Education, literacy and other indicators for Argentina',
                            'image_url': 'http://www.tellmaps.com/uis/internal/assets/uisheader-en.png',
                            'url': 'http://uis.unesco.org/en/country/AR',
                            'tags': [{'name': 'indicators'}, {'name': 'sustainable development'},
                                     {'name': 'demographics'}, {'name': 'socioeconomics'}, {'name': 'education'}],
                            'title': 'Indicators for Argentina'}


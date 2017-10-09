#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Top level script. Calls other functions that generate datasets that this script then creates in HDX.

"""
import logging
from os.path import join, expanduser

from hdx.hdx_configuration import Configuration
from hdx.utilities.downloader import Download

from unesco import generate_dataset_and_showcase, get_countriesdata

from hdx.facades import logging_kwargs
logging_kwargs['smtp_config_yaml'] = join('config', 'smtp_configuration.yml')

from hdx.facades.hdx_scraperwiki import facade

logger = logging.getLogger(__name__)


def main():
    """Generate dataset and create it in HDX"""

    base_url = Configuration.read()['base_url']
    downloader = Download(extra_params_yaml=join(expanduser("~"), 'unesco.yml'))
    countriesdata = get_countriesdata(base_url, downloader)
    logger.info('Number of datasets to upload: %d' % len(countriesdata))
    for countrydata in countriesdata:
        dataset, showcase = generate_dataset_and_showcase(base_url, downloader, countrydata)
        if dataset:
            dataset.update_from_yaml()
            dataset.create_in_hdx()
            showcase.create_in_hdx()
            showcase.add_dataset(dataset)

if __name__ == '__main__':
    facade(main, hdx_site='test', project_config_yaml=join('config', 'project_configuration.yml'))


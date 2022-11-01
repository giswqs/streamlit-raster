#!/usr/bin/env python

"""The setup script."""

import io
import shutil
import pkg_resources
from os import path as op
from setuptools import setup, find_packages

# Adopted from https://github.com/streamlit/streamlit/pull/4677. Credits to Bane Sullivan.

try:
    pkg_dir = op.dirname(pkg_resources.resource_filename("streamlit", "main.py"))
    config_path = op.join(pkg_dir, "config.py")
    config_bk_path = config_path.replace(".py", "_bk.py")
    server_path = op.join(pkg_dir, "web", "server", "server.py")
    server_bk_path = server_path.replace(".py", "_bk.py")

    if not op.exists(config_bk_path):
        shutil.copyfile(config_path, config_bk_path)
    if not op.exists(server_bk_path):
        shutil.copyfile(server_path, server_bk_path)

    with open(config_bk_path) as f:
        lines = f.readlines()

    outlines = []
    for line in lines:
        if line.strip() == '@_create_option("server.address")':
            extra = """
@_create_option("server.portProxy", type_=bool)
def _server_port_proxy() -> int:
    \"""Use jupyter_server_proxy to proxy local ports.
    Default: False
    \"""
    return False    
"""
            outlines.append(extra)
            outlines.append("\n")
        outlines.append(line)           


    with open(config_path, "w") as f:
        f.writelines(outlines)

    outlines = []
    with open(server_bk_path) as f:
        lines = f.readlines()

    for line in lines:
        if line.lstrip().startswith('return tornado.web.Application'):
            extra= """
        if config.get_option("server.portProxy"):
            try:
                from jupyter_server_proxy.handlers import LocalProxyHandler
            except ModuleNotFoundError:
                LOGGER.error(
                    "jupyter_server_proxy is not installed. Cannot use `server.portProxy`"
                )
            else:
                routes.extend(
                    [(make_url_path_regex(base, r"proxy/(\d+)(.*)"), LocalProxyHandler)]
                )
            """
            outlines.append(extra)
            outlines.append("\n")

        outlines.append(line)

    with open(server_path, "w") as f:
        f.writelines(outlines)

except Exception as e:
    raise Exception(e)


with open('README.md') as readme_file:
    readme = readme_file.read()

here = op.abspath(op.dirname(__file__))

# get the dependencies and installs
with io.open(op.join(here, "requirements.txt"), encoding="utf-8") as f:
    all_reqs = f.read().split("\n")

install_requires = [x.strip() for x in all_reqs if "git+" not in x]
dependency_links = [x.strip().replace("git+", "") for x in all_reqs if "git+" not in x]

requirements = [ ]

setup_requirements = [ ]

test_requirements = [ ]

setup(
    author="Qiusheng Wu",
    author_email='giswqs@gmail.com',
    python_requires='>=3.7',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    description="Python Boilerplate contains all the boilerplate you need to create a Python package.",
    install_requires=install_requires,
    dependency_links=dependency_links,
    license="MIT license",
    long_description=readme,
    long_description_content_type='text/markdown',
    include_package_data=True,
    keywords='streamlit_raster',
    name='streamlit-raster',
    packages=find_packages(include=['streamlit_raster', 'streamlit_raster.*']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/giswqs/streamlit-raster',
    version='0.2.0',
    zip_safe=False,
)

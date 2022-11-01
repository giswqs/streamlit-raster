"""Top-level package for Streamlit Raster."""

__author__ = """Qiusheng Wu"""
__email__ = 'giswqs@gmail.com'
__version__ = '0.2.0'

import shutil
import pkg_resources
from os import path as op

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

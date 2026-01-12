# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import yaml
import json
import logging
from ckan.plugins import toolkit
from ckanext.oauth2 import db

log = logging.getLogger(__name__)


def load_oauth2_config():
    """
    Load OAuth2 configuration from CKAN config (JSON string) or file.
    Priority:
    1. ckan.oauth2.config_json (JSON string)
    2. ckan.oauth2.config_path (File path, defaults to ../oauth_config.yaml)
    """
    config_json = toolkit.config.get("ckan.oauth2.config_json")
    if config_json:
        try:
            return json.loads(config_json)
        except ValueError as e:
            log.error("Error parsing ckan.oauth2.config_json: %s", e)
            raise

    # Fallback to file
    config_file_path = toolkit.config.get(
        "ckan.oauth2.config_path",
        os.path.join(os.path.dirname(__file__), "..", "oauth_config.yaml"),
    )

    with open(config_file_path) as f:
        if config_file_path.endswith(".json"):
            return json.load(f)
        else:
            # Default to YAML
            return yaml.load(f, Loader=yaml.FullLoader)


def get_sso_options():
    config = load_oauth2_config()
    provider_list = [provider["name"] for provider in config["providers"]]
    return provider_list


def user_is_sso_user():
    if not toolkit.c.userobj:
        return False
    user_name = toolkit.c.userobj.name
    user = db.UserToken.by_user_name(user_name=user_name)
    if user:
        return True
    return False


def allow_userpass_login():
    """Return True when username/password login should be shown alongside SSO."""
    return toolkit.asbool(toolkit.config.get("ckan.oauth2.allow_userpass_login", False))

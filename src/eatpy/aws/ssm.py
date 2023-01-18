import fnmatch
import json
import logging
from typing import Union

import boto3
from rich import print

logger = logging.getLogger()

PS_PREFIX = "git"
SESSION_OPTS = {
    "aws_access_key_id": None,
    "aws_secret_access_key": None,
    "aws_session_token": None,
    "region_name": None,
    "botocore_session": None,
    "profile_name": None,
}


################################################################
# Helpers
################################################################
# exception
class ClutterAWSException(Exception):
    pass


# create client for SecretsManager
def session_maker(
    profile_name=None,
    aws_access_key_id=None,
    aws_secret_access_key=None,
    region_name="ap-northeast-2",
    session_opts=None,
):
    """Create boto3 secretsmanager client.

    Priority:
        1. profile_name
        2. aws_access_key_id & secret_access_key
    """

    # session configuration
    session_opts = session_opts or dict()
    if region_name is not None:
        session_opts.update({"region_name": region_name})
    if aws_access_key_id is not None:
        if aws_secret_access_key is not None:
            session_opts.update(
                {
                    "aws_access_key_id": aws_access_key_id,
                    "aws_secret_access_key": aws_secret_access_key,
                }
            )
    if profile_name is not None:
        session_opts = {"profile_name": profile_name}

    # return clinet
    return boto3.session.Session(**session_opts)


def validate_response(response, success_codes=[200]):
    meta = response["ResponseMetadata"]
    if meta["HTTPStatusCode"] not in success_codes:
        raise ReferenceError(f"status code {meta['HTTPStatusCode']}, {str(meta)}")


################################################################
# FUNCTIONS
################################################################
# list parameters
def list_parameters(
    patterns: Union[str, list] = None,
    session: boto3.Session = None,
) -> list:
    """List Parameters in AWS Parameter Store.

    Args:
        session (boto3.Session, optional): create new session if None. Defaults to None.

    Returns:
        list: list of parameters
    """
    # correct args
    patterns = patterns or "*"
    if patterns:
        patterns = patterns if isinstance(patterns, (tuple, list)) else [patterns]

    # get client
    session = session or session_maker()
    client = session.client("ssm")

    parameter_filters = [{"Key": "Name", "Option": "BeginsWith", "Values": [f"/{PS_PREFIX}"]}]
    resp = client.describe_parameters(ParameterFilters=parameter_filters)

    for param in resp["Parameters"]:
        _, name = param["Name"].strip("/").split("/")
        if not any([fnmatch.fnmatch(name, f"*{pat.strip('*')}*") for pat in patterns]):
            continue
        print(f"[[bold]{name}[/bold]]")
        if param.get("Description"):
            print(f" DESCRIPTION: {param['Description']}")
        print(f""" SSM NAME: '{param["Name"]}'""")
        print(" VALUES:")
        values = get_parameters(name)
        if isinstance(values, dict):
            for k, v in values.items():
                print(f"  - {k}: {v}")
        else:
            print(f"  - {values}")


# set parameters
def set_parameters(
    name: str,
    parameters: dict,
    description: str = None,
    tags: dict = None,
    overwrite: bool = False,
    session: boto3.Session = None,
) -> None:
    """Set New Parameters.

    Args:
        name (str): Name.
        parameters (dict): i.e. {"host": "example.com", "port": 80, "user": "eugene"}
        description (str, optional): i.e. "This is Description.". Defaults to None.
        tags (dict, optional): i.e. {"creator": "eugene"}. Defaults to None.
        overwrite (bool, optional): overwrite exist parameters if True. Defaults to False.
        session (boto3.Session, optional): create new session if None. Defaults to None.

    Raises:
        ClutterAWSException
    """
    # get client
    session = session or session_maker()
    client = session.client("ssm")

    opts = {
        "Type": "SecureString",
        "Tier": "Standard",
    }
    if description:
        opts.update({"Description": description})
    if tags:
        Tags = []
        for k, v in tags.items():
            tags.append({"Key": k, "Value": v})
        opts.update({"Tags": Tags})

    resp = client.put_parameter(
        Name=f"/{PS_PREFIX}/{name}",
        Value=json.dumps(parameters) if isinstance(parameters, dict) else parameters,
        Overwrite=overwrite,
        **opts,
    )
    if resp["ResponseMetadata"]["HTTPStatusCode"] != 200:
        raise ClutterAWSException(str(resp))


# get parameters
def get_parameters(name: str, session: boto3.Session = None) -> Union[dict, str]:
    """Get Parameters from AWS Parameter Store.

    Args:
        name (str): name of parameters
        session (boto3.Session, optional): create new session if None. Defaults to None.

    Returns:
        Union[dict, str]: parameters.
    """
    session = session or session_maker()
    client = session.client("ssm")

    Name = f"/{PS_PREFIX}/{name}"
    resp = client.get_parameter(Name=Name, WithDecryption=True)
    values = resp["Parameter"]["Value"]
    try:
        return json.loads(values)
    except json.JSONDecodeError as exc:
        return values

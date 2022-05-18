# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
#     http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.

import sys
import argparse

from instanceconnect.EC2InstanceConnectCLI import  EC2InstanceConnectCLI
from instanceconnect.EC2InstanceConnectKey import EC2InstanceConnectKey
from instanceconnect.EC2InstanceConnectCommand import EC2InstanceConnectCommand
from instanceconnect.EC2InstanceConnectLogger import EC2InstanceConnectLogger



def main(connect, username, instance_id, region, aws_access_key_id , aws_secret_access_key, aws_session_token ):

   if connect:
  
      instance_bundles = [{'profile': 'temp', 'instance_id': instance_id, 'region': region, 'zone': None, 'target': None, 'username': username}]
      logger = EC2InstanceConnectLogger(False)
      #Generate temp key
      cli_key = EC2InstanceConnectKey(logger.get_logger())
      cli_command = EC2InstanceConnectCommand('ssh', instance_bundles, cli_key.get_priv_key_file(), '','', logger.get_logger(), True)
      try:
         cli = EC2InstanceConnectCLI(instance_bundles, cli_key.get_pub_key(), cli_command, logger.get_logger(),aws_access_key_id , aws_secret_access_key, aws_session_token )
         return_value =  ( cli.invoke_command())
      except Exception as e:
         print('Failed with:\n' + str(e))



   else:
      
      instance_bundles = [{'profile': 'temp', 'instance_id': instance_id, 'region': region, 'zone': None, 'target': None, 'username': username}]
      logger = EC2InstanceConnectLogger(False)
      #Generate temp key
      try:
         cli_key = EC2InstanceConnectKey(logger.get_logger())
         cli_command = EC2InstanceConnectCommand('ssh', instance_bundles, cli_key.get_priv_key_file(), '','', logger.get_logger(),False)
         cli = EC2InstanceConnectCLI(instance_bundles, cli_key.get_pub_key(), cli_command, logger.get_logger(),aws_access_key_id , aws_secret_access_key, aws_session_token )
         return_value =  ( cli.invoke_command())
         if return_value == 0:
            return "0,"+username+"@"+instance_id
         else:
            return '-1'
        
      except:
         pass
   
   return "-1"

import boto3
import sys
import argparse
from instanceconnect import mops
from prettytable import PrettyTable

class Instance:

   def __init__(self, id, region, state, platform_details, public_ip_address, private_ip_address):
      self.id = id
      self.region = region
      self.state = state
      self.platform_details = platform_details
      self.public_ip_address = public_ip_address
      self.private_ip_address= private_ip_address    



def get_all_ec2(access_key, secret_key, running_instances_dict, all_instances_lst, aws_session_token):
   client = boto3.client('ec2', aws_access_key_id=access_key, aws_secret_access_key=secret_key, region_name='us-east-1', aws_session_token = aws_session_token)
   ec2_regions = [region['RegionName'] for region in client.describe_regions()['Regions']]
   for region in ec2_regions:
      try:
         conn = boto3.resource('ec2', aws_access_key_id=access_key, aws_secret_access_key=secret_key,region_name=region, aws_session_token = aws_session_token)
         instances = conn.instances.filter()
         for instance in instances:
            new_instance = Instance(instance.id, region, instance.state["Name"], instance.platform_details, instance.public_ip_address, instance.private_ip_address)
            all_instances_lst.append(new_instance)
            if instance.state["Name"] == "running":
               running_instances_dict[instance.id] = region
      except Exception as e:
         continue


def get_all_instance_connect(running_instances_dict, instance_connect_lst, aws_access_key_id , aws_secret_access_key, aws_session_token, user):
   for instance_id in running_instances_dict: 
      return_value =  mops.main(False, user ,instance_id, running_instances_dict[instance_id], aws_access_key_id , aws_secret_access_key, aws_session_token )
      if return_value[0] == '0':
         instance_connect_lst.append(return_value.split(',')[1])
 




def msg(name=None):                                                            
    return '''
	 -aws_access_key:     	                AWS access key.
	 -aws_secret:				AWS secret access key.
         -enum_ec2:			        Use this option to enumerate the ec2's.
         -connect_to_ec2:			Use this option to initiate a ssh connection to an instance, using ec2 instance connect.
         -instance_id:		                Specify the instance id.
         -user:                                 Specify the username for connecting to the ec2 instance.
         -region:                               Specify the region for connecting to the ec2 instance.
         -aws_session_token                     Specify the aws_session_token. In case of assuming a role, please provide session token with access key and secret. 
         -help:					help.
            '''

def validate_arguments(args, parser):


   if args.help:
      parser.print_usage()
      sys.exit()

   if args.aws_access_key == False or  args.aws_secret == False:
      print('please provide both access key and access key secret')
      sys.exit()

   if args.enum_ec2 == True:
      if args.connect_to_ec2 == True :
          print ('It is illegal to choose both enum_ec2 flag with connect_to_ec2 flag')
          sys.exit()
      elif args.instance_id != False:
          print('It is illegal to choose both enum_ec2 flag with instance_id flag')
          sys.exit()
      elif args.user == False:
          print('Please provide user for ec2 instance connect')
          sys.exit()
      elif args.region != False:
          print('It is illegal to choose both enum_ec2 flag with region flag')
          sys.exit()


   elif args.connect_to_ec2 == False:
      print('please provide connect_to_ec2 or enum_ec2 flags')
      sys.exit()
      
      if args.instance_id == False:
         print('please provide instance_id')
         sys.exit()

      elif args.user == False:
         print('please provide user')
         sys.exit()

      elif args.region == False:
         print('please provide region')
         sys.exit()


      

   
def print_all_instances(all_instances_lst, instance_connect_lst):
   table = PrettyTable(['Instance_id','region', 'state', 'platform_details', 'public_ip_address', 'private_ip_address','is_instance_connect','username' ])   
   

   for instance in all_instances_lst:
      is_instance_connect = False
      username = ''
      for instance_path in instance_connect_lst:
         instance_id = instance_path.split('@')[1]
         if instance.id  == instance_id:
            is_instance_connect = True 
            username = instance_path.split('@')[0]
            break
      table.add_row([instance.id, instance.region, instance.state, instance.platform_details, instance.public_ip_address, instance.private_ip_address, is_instance_connect, username])
   print(table)
      


def main():
   
   parser = argparse.ArgumentParser(description='Ec2 instance connect enumerator', usage=msg())
   parser.add_argument('-aws_access_key',default= False )
   parser.add_argument('-aws_secret' ,default= False )
   parser.add_argument('-enum_ec2',action='store_true',default= False )
   parser.add_argument('-connect_to_ec2',action='store_true',default= False)
   parser.add_argument('-instance_id',default= False)
   parser.add_argument('-user', default = False)
   parser.add_argument('-region', default = False)
   parser.add_argument('-aws_session_token', default = '')
   parser.add_argument('-help', action = 'store_true')

   args = parser.parse_args()
   validate_arguments(args, parser)
   
   aws_access_key_id = args.aws_access_key 
   aws_secret_access_key = args.aws_secret
   aws_session_token = args.aws_session_token  
   running_instances_dict = {}
   instance_connect_lst = [] 
   all_instances_lst = []
    
   try:
      if args.connect_to_ec2:  
         mops.main(True,args.user,args.instance_id ,args.region,  aws_access_key_id , aws_secret_access_key, aws_session_token )        
      elif args.enum_ec2:         
         get_all_ec2(aws_access_key_id , aws_secret_access_key, running_instances_dict, all_instances_lst, aws_session_token)
         get_all_instance_connect(running_instances_dict , instance_connect_lst, aws_access_key_id , aws_secret_access_key, aws_session_token, args.user )
         print_all_instances(all_instances_lst, instance_connect_lst)
   except Exception as e:
         print('Failed with:\n' + str(e))
 

   

if __name__ == '__main__':
    sys.exit(main())



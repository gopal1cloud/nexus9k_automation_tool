from django.shortcuts import render_to_response
from django.http import HttpResponseForbidden, HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import redirect
from django.conf import settings

from apps.CLI_Generator.models import NexusCLI_Config_Management

import csv
import re
import sys
from StringIO import StringIO  
from zipfile import ZipFile  
import itertools

def main(request):
	ctx = RequestContext(request, {})
	return render_to_response("CLI_Generator/main.html", context_instance = ctx) 

def new_main(request):
	ctx = RequestContext(request, {})
	return render_to_response("CLI_Generator/new_main.html", context_instance = ctx) 
	
def download_nexus_config_csv(request):
	try:
		nexus_config = NexusCLI_Config_Management.objects.all().order_by('id')[:1]
		nexus_config_csv = nexus_config[0].csv_file.url
	except NexusCLI_Config_Management.DoesNotExist:
		nexus_config_csv="/"
	return redirect(nexus_config_csv) 

def download_nexus_config_generator(request):	
	try:
		nexus_config = NexusCLI_Config_Management.objects.all().order_by('id')[:1]
		nexus_config_generator = nexus_config[0].cli_generator_file.url
	except NexusCLI_Config_Management.DoesNotExist:
		nexus_config_generator="/"
	return redirect(nexus_config_generator) 

def convert_nexus_config_nxapi(request):
	if request.method == "GET":
		commands = []
		#code_ip = request.GET["nxapi_code_ip"]
		#code_username = request.GET["nxapi_code_username"]
		#code_password = request.GET["nxapi_code_password"]
		code_filename = request.GET["nxapi_code_filename"]
		code_file_content = request.GET["nxapi_code_file_content"]
		file_data = code_file_content.replace(r"\r\n", r"\n")
		formated_data = str("\n".join(file_data.splitlines()))
		
		code_ip = ''
		for line in formated_data.split('\n'):
			if re.match('^! Management IPAddress', line):
				code_ip = line.split('! Management IPAddress ')[1]
		try:
			in_memory = StringIO()  
			zip = ZipFile(in_memory, "a")  	
			config_name = "login-info.cfg"
			config_content = "[HostDetails]\n"
			config_content += "#Nexus Switch user details\n"
			config_content += "username=\n"
			config_content += "password=\n"		
			zip.writestr(config_name, config_content)
			
			nxapi_name = code_filename+'.py'
			
			nxapi_file = '"""\n Nexus Switch Off-Box script generated by Nexus Automation Tool\n"""\n\n'
			nxapi_file += 'import os\nimport requests\nimport json\nimport ConfigParser\nimport datetime\nimport time\n\n'
			nxapi_file += '#read the nexus configuration file\nconfig=ConfigParser.ConfigParser()\nconfig.read(\'login-info.cfg\')\n\n'
			nxapi_file += 'ipaddress = "'+str(code_ip)+'"\nusername = config.get(\'HostDetails\', \'username\')\npassword = config.get(\'HostDetails\', \'password\')\n\n'
			nxapi_file += '#check the configuration details\nif (ipaddress == \'\'):\n    print "Please check the  Switch IPAddress"\n    exit(1)\n\n'
			nxapi_file += 'if ((username and password) == \'\'):\n    print "Please check the Switch User Credentials"\n    exit(1)\n\n'
			nxapi_file += 'elif (username == \'\'):\n    print "Please check the Switch User Credentials "\n    exit(1)\n\n'
			nxapi_file += 'elif (password == \'\'):\n    print "Please check the Switch User Credentials "\n    exit(1)\n\n'
			nxapi_file += '"""\n\nClass to configure the required nexus switch\n"""\n\n\n'
			nxapi_file += 'class Nexus_Vxlan:\n\n    myheaders = {\'content-type\':\'application/json-rpc\'}\n    headers = {\'content-type\':\'application/json\'}\n\n    url = "http://"+ipaddress+"/ins"\n\n'
			nxapi_file += '    def nexus_vxlan(self):\n\n        #execute the commands\n\n'
			nxapi_file += '        try:\n\n            payload = [{"jsonrpc":"2.0","method":"cli","params":{"cmd":"conf t","version":1},"id":1},]\n            response = requests.post(Nexus_Vxlan.url,data=json.dumps(payload),headers=Nexus_Vxlan.myheaders,auth=(username,password)).json()\n        except Exception as e:\n                pass\n\n'
			
			id=2
			for line in formated_data.split('\n'):
				if not line.startswith("!"):
					nxapi_file += '        try:\n\n            payload = [{"jsonrpc":"2.0","method":"cli","params":{"cmd":"'+line.strip()+'","version":1},"id":"'+str(id)+'"},]\n            response = requests.post(Nexus_Vxlan.url,data=json.dumps(payload),headers=Nexus_Vxlan.myheaders,auth=(username,password)).json()\n        except Exception as e:\n                pass\n\n'
					id = id + 1
				
			nxapi_file += '\n\n        print "Script execution is Complete!!!"\n\n'
			nxapi_file += '\n\nif __name__ == \'__main__\':\n    ob = Nexus_Vxlan()\n    ob.nexus_vxlan()\n'
			
			zip.writestr(nxapi_name, nxapi_file)
			for file in zip.filelist:  
					file.create_system = 0      
			zip.close()  
			response = HttpResponse(content_type="application/zip")  
			response["Content-Disposition"] = "attachment; filename=NXAPI_Switch_OFF-Box_python_script.zip" 
			in_memory.seek(0) 	     
			response.write(in_memory.read())  
			return response
		except IOError:
			sys.exit(0)
		return response
	else:
		return HttpResponseForbidden()
		
def convert_nexus_config_puppet(request):
	if request.method == "GET":
		commands = []
		code_classname = request.GET["puppet_code_classname"]
		code_filename = request.GET["puppet_code_filename"]
		code_file_content = request.GET["puppet_code_file_content"]
		file_data = code_file_content.replace(r"\r\n", r"\n")
		formated_data = str("\n".join(file_data.splitlines()))
		
		for line in formated_data.split('\n'):
			if not line.startswith("!"):
				li = line.strip()
				commands.append(li)
		try:
				
			puppet_file = "class cisco_onep::"+code_classname+" {"+"\n"
			puppet_file += '    cisco_command_config { "$::hostname configurations":'+"\n"
			puppet_file += "        command =>"
			puppet_file += ' "'
			
			for c in (commands):
				puppet_file += c
			puppet_file += '"'+"\n"+"    }"+"\n"
			puppet_file += "}"+"\n"
			
			response = HttpResponse(content_type='text/pson')
			response['Content-Disposition'] = 'attachment; filename="'+code_filename+'.pp"'
			response.write(puppet_file)
		except IOError:
			sys.exit(0)
		return response
	else:
		return HttpResponseForbidden()
				
def convert_nexus_config_ansible(request):
	if request.method == "GET":
		commands = []
		code_desc = request.GET["ansible_code_desc"]
		#code_host = request.GET["ansible_code_host"]
		code_filename = request.GET["ansible_code_filename"]
		code_file_content = request.GET["ansible_code_file_content"]
		file_data = code_file_content.replace(r"\r\n", r"\n")
		formated_data = str("\n".join(file_data.splitlines()))

		for line in formated_data.split('\n'):
			if not line.startswith("!"):
				li = line.strip()
				commands.append(li)
		
		code_host = ''
		for line in formated_data.split('\n'):
			if re.match('^! Management IPAddress', line):
				code_host = line.split('! Management IPAddress ')[1]
		try:
			yaml_file ='---'+'\n'
			yaml_file +='# To run this Ansible playbook, issue the following command on the Ansible server:\n#\n# ansible-playbook -i hosts <filename>\n#\n'
			yaml_file +='\n\n\n'+'- name: '+code_desc+'\n'
			yaml_file +='  hosts: '+code_host+'\n\n'
			yaml_file +='  tasks: '+'\n\n'
			yaml_file +='  - nxos_command:'+'\n'+'      host: "{{ inventory_hostname }}"'+'\n'+'      type: config'+'\n'+"      command: "+str(commands)+"\n\n"

			response = HttpResponse(content_type='text/x-yaml')
			response['Content-Disposition'] = 'attachment; filename="'+code_filename+'.yml"'
			response.write(yaml_file)
		except IOError:
			sys.exit(0)
		return response
	else:
		return HttpResponseForbidden()

def convert_nexus_config_cli(request):
	if request.method == "GET":		
		try:
			try:
				code_file_content = str(request.GET["config_csv"])
				file_data = code_file_content.split("^")
				file_header = file_data[0].split(",")
				file_content = file_data[1:-1]
				switch_dict = []
				for entry in file_content:
					switch_dict.append(dict(itertools.izip(file_header, entry.split(","))))
			except TypeError:
				sys.exit(0)
				
			in_memory = StringIO()  
			zip = ZipFile(in_memory, "a")  
			for row in switch_dict:
				config_content = ""
				if re.search('Spine(.*)', row['Switch']):
					config_name = row['Hostname'] + ".txt"						
					config_content += "! Management IPAddress "+row['Management IPAddress']+"\n"
					config_content += "nv overlay evpn\n"
					config_content += "feature ospf\n"
					config_content += "feature pim\n"
					config_content += "feature bgp\n"
					config_content += "feature interface-vlan\n"
					config_content += "feature nv overlay\n"
					config_content += "feature vn-segment-vlan-based\n"
					config_content += "router ospf "+row['Ospf P.ID']+ "\n"
					config_content += "router-id"+ ' '+row['Ospf Router-id']+ "\n"
					config_content += "ip pim rp-address "+row['Rp-Address']+ "  group-list "+row['Group-list']+"\n"
					config_content += "ip pim rp-candidate loopback"+row['2nd Loopback']+" group-list "+row['Group-list']+"\n"
					config_content += "ip pim anycast-rp "+row['Rp-Address']+' '+row['Ospf Router-id']+"\n"
					config_content += "ip pim ssm range "+row['Ssm Range']+ "\n"
				   
					config_content += "interface loopback"+row['Loopback Number']+ "\n"
					config_content += "ip address "+row['Ip Addresss Loopback']+ "\n"
					config_content += "ip router ospf "+row['Ospf P.ID']+ " area 0.0.0.0\n"
					config_content += "ip pim sparse-mode\n"

					config_content += "interface loopback"+row['2nd Loopback']+ "\n"
					config_content += "ip address "+row['2nd Loopback Ip Address']+ "\n"
					config_content += "ip router ospf "+row['Ospf P.ID']+ " area 0.0.0.0\n"
					config_content += "ip pim sparse-mode\n"
					
					for i in range(1, int(row['Interface count'])+1):
						try: 
							if (len(row['Interface'+str(i)]) and len(row['Interface '+str(i)+' Ip address'])) == 0:
								raise IOError
						except IOError:
							print "Details of Interface"+str(i)+" are missing for " +row['Hostname']+".txt file. Please don't leave that field empty in Nexus_Config_Parameters.csv file"
							sys.exit(0)

						config_content += "interface ethernet " +row['Interface'+str(i)]+ "\n"
						config_content += "no shutdown\n"
						config_content += "no switchport\n"
						config_content += "ip address "+row['Interface '+str(i)+' Ip address']+"\n"
						config_content += "ip router ospf "+row['Ospf P.ID']+ " area 0.0.0.0\n"
						config_content += "ip pim sparse-mode\n"
					
					config_content += "router bgp "+row['BGP-AS-Number']+"\n"
					config_content += "router-id "+row['BGP-Router-Id']+"\n"
					
					for i in range(1, int(row['Interface count'])+1):
						try:
							if len(row['Neighbor-'+str(i)]) == 0:
								raise IOError
						except IOError:
							print "Details of Neighbor-"+str(i)+" are missing for " +row['Hostname']+".txt file. Please don't leave that field empty in Nexus_Config_Parameters.csv file"
							sys.exit(0)

						config_content += "neighbor "+row['Neighbor-'+str(i)]+ " remote-as "+row['BGP-AS-Number']+"\n"
						config_content += "update-source loopback"+row['Loopback Number']+ "\n"
						config_content += "address-family ipv4 unicast\n"
						config_content += "send-community both\n"
						config_content += "route-reflector-client\n"
						config_content += "address-family l2vpn evpn\n"
						config_content += "send-community both\n"
						config_content += "route-reflector-client\n"
					
					config_content += "vrf vrf_tenant_1\n"
					config_content += "address-family ipv4 unicast\n"
					config_content += "no advertise l2vpn evpn\n"
					config_content += "advertise l2vpn evpn\n"
					zip.writestr(config_name, config_content)   
					print "   "+row['Hostname'] + ".txt" + " created"
				
				elif re.search('Leaf(.*)', row['Switch']):
					config_name = row['Hostname'] + ".txt"
					
					config_content += "! Management IPAddress "+row['Management IPAddress']+"\n"
					config_content += "nv overlay evpn\n"
					config_content += "feature ospf\n"
					config_content += "feature pim\n"
					config_content += "feature bgp\n"
					config_content += "feature interface-vlan\n"
					config_content += "feature nv overlay\n"
					config_content += "feature vn-segment-vlan-based\n"
					config_content += "router ospf "+row['Ospf P.ID']+ "\n"
					config_content += "router-id "+row['Ospf Router-id']+"\n"
					config_content += "ip pim rp-address "+row['Rp-Address']+" group-list "+row['Group-list']+"\n"
					config_content += "ip pim ssm range "+row['Ssm Range']+ "\n"
					
					config_content += "interface loopback"+row['Loopback Number']+ "\n" 
					config_content += "ip address "+row['Ip Addresss Loopback']+ "\n" 
					config_content += "ip router ospf "+row['Ospf P.ID']+ " area 0.0.0.0\n" 
					config_content += "ip pim sparse-mode\n" 
					
					for i in range(1, int(row['Interface count'])+1):
						try:
							if (len(row['Interface'+str(i)]) and len(row['Interface '+str(i)+' Ip address'])) == 0:
								raise IOError
						except IOError:
							print "Details of Interface"+str(i)+" are missing for " +row['Hostname']+".txt file. Please don't leave that field empty in Nexus_Config_Parameters.csv file"
							sys.exit(0)

						config_content += "interface ethernet " +row['Interface'+str(i)]+ "\n" 
						config_content += "no shutdown\n" 
						config_content += "no switchport\n"
						config_content += "ip address "+row['Interface '+str(i)+' Ip address']+"\n" 
						config_content += "ip router ospf "+row['Ospf P.ID']+ " area 0.0.0.0\n" 
						config_content += "ip pim sparse-mode\n" 

					config_content += "interface ethernet 1/1\n" 

					config_content += "switchport\n" 
					config_content += "switchport access vlan "+row['2nd Vlan']+"\n" 
					config_content += "no shutdown\n" 

					config_content += "vrf context "+row['VRF-member-for-2nd Vlan']+"\n" 
					config_content += "vni "+row['VNI']+"\n" 
					config_content += "rd auto\n" 
					config_content += "address-family ipv4 unicast\n" 
					config_content += "route-target import "+row['Route Target- Import']+" evpn\n" 
					config_content += "route-target export "+row['Route Target- Export']+" evpn\n" 
					config_content += "route-target both auto evpn\n" 
					
					config_content += "vlan "+row['1st Vlan']+"\n" 
					config_content += "name "+row['1st Vlan- Name']+"\n" 
					config_content += "vn-segment "+row['1st Vlan Vn-Segment']+"\n" 
					config_content += "no shutdown\n" 
					config_content += "interface vlan"+row['1st Vlan']+"\n" 
					config_content += "description l3-vni-for-vrf_tenant_1-routing\n" 
					config_content += "no shutdown\n" 
					
					config_content += "vrf member "+row['VRF-member-for-2nd Vlan']+"\n" 
					config_content += "ip forward\n" 
					config_content += "vlan "+row['2nd Vlan']+"\n" 
					config_content += "no shutdown\n" 
					config_content += "vn-segment "+row['2nd Vlan Vn-Segment']+"\n" 
					config_content += "evpn\n" 
					config_content += "vni "+row['EVPN 1st VNI']+" l2\n" 
					config_content += "rd auto\n" 
					config_content += "route-target import auto\n" 
					config_content += "route-target export auto\n" 
					config_content += "interface vlan"+row['2nd Vlan']+"\n" 
					config_content += "no shutdown\n" 
					 
					config_content += "vrf member "+row['VRF-member-for-2nd Vlan']+" \n" 
					config_content += "ip address "+row['Ipaddress-2nd-vlan']+"\n" 
					config_content += "fabric forwarding mode anycast-gateway\n" 
					config_content += "fabric forwarding anycast-gateway-mac "+row['Any-cast-mac']+"\n" 
					config_content += "interface nve"+row['Interface-NVE']+"\n" 
					config_content += "no shutdown\n" 

					config_content += "source-interface loopback"+row['Loopback Number']+"\n" 
					config_content += "host-reachability protocol bgp\n" 
					config_content += "member vni "+row['1st Vlan Vn-Segment']+" associate-vrf\n" 
					config_content += "member vni "+row['Member-vni']+"\n" 
					config_content += "suppress-arp\n" 
					config_content += "mcast-group "+row['Mcast-group']+"\n" 
					config_content += "router bgp "+row['BGP-AS-Number']+"\n" 
					config_content += "router-id "+row['Ospf Router-id']+"\n" 
					
					for i in range(1, int(row['Interface count'])+1):
						try:
							if len(row['Neighbor-'+str(i)]) == 0:
								raise IOError
						except IOError:
							print "Details of Neighbor-"+str(i)+" are missing for " +row['Hostname']+".txt file. Please don't leave that field empty in Nexus_Config_Parameters.csv file"
							sys.exit(0)

						config_content += "neighbor "+row['Neighbor-1']+" remote-as "+row['BGP-AS-Number']+"\n"
						config_content += "update-source loopback"+row['Loopback Number']+"\n"
						config_content += "address-family ipv4 unicast\n"
						config_content += "send-community both\n"
						config_content += "address-family l2vpn evpn\n"
						config_content += "send-community extended\n"
				   
					config_content += "vrf "+row['VRF-member-for-2nd Vlan']+"\n"
					config_content += "address-family ipv4 unicast\n"
					config_content += "no advertise l2vpn evpn\n"
					config_content += "advertise l2vpn evpn\n"
					zip.writestr(config_name, config_content)   
					print "   "+row['Hostname'] + ".txt" + " created"		

			for file in zip.filelist:  
				file.create_system = 0      
			zip.close()  
			response = HttpResponse(content_type="application/zip")  
			response["Content-Disposition"] = "attachment; filename=Nexus_CLI_Configs.zip" 
			in_memory.seek(0) 	     
			response.write(in_memory.read())  
		except IOError:
			print "nexus_config_parameters.csv file not found and not able to read"
			print "Make sure that csv file name must be nexus_config_parameters.csv by default"
			sys.exit(0)
		
		return response
	else:
		return HttpResponseForbidden()

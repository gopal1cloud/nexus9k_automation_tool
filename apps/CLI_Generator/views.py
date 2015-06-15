from django.shortcuts import render_to_response
from django.http import HttpResponseForbidden, HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import redirect

from apps.CLI_Generator.models import NexusCLI_Config_Management

def main(request):
	ctx = RequestContext(request, {})
	return render_to_response("CLI_Generator/main.html", context_instance = ctx) 

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

def convert_nexus_config_puppet(request):
	if request.method == "GET":
		commands = []
		code_classname = request.GET["puppet_code_classname"]
		code_filename = request.GET["puppet_code_filename"]
		code_file_content = request.GET["puppet_code_file_content"]
		file_data = code_file_content.replace(r"\r\n", r"\n")
		formated_data = str("\n".join(file_data.splitlines()))
		
		for line in formated_data.split('\n'):
			li = line.strip()
			commands.append(li)
			
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
		return response
	else:
		return HttpResponseForbidden()
				
def convert_nexus_config_ansible(request):
	if request.method == "GET":
		commands = []
		code_desc = request.GET["ansible_code_desc"]
		code_host = request.GET["ansible_code_host"]
		code_filename = request.GET["ansible_code_filename"]
		code_file_content = request.GET["ansible_code_file_content"]
		file_data = code_file_content.replace(r"\r\n", r"\n")
		formated_data = str("\n".join(file_data.splitlines()))

		for line in formated_data.split('\n'):
			li = line.strip()
			commands.append(li)
     
		yaml_file ='---'+'\n'
		yaml_file +='# To run this Ansible playbook, issue the following command on the Ansible server:\n#\n# ansible-playbook -i hosts <filename>\n#\n'
		yaml_file +='\n\n\n'+'- name: '+code_desc+'\n'
		yaml_file +='  hosts: '+code_host+'\n\n'
		yaml_file +='  tasks: '+'\n\n'
		yaml_file +='  - nxos_command:'+'\n'+'      host: "{{ inventory_hostname }}"'+'\n'+'      type: config'+'\n'+"      command: "+str(commands)+"\n\n"

		response = HttpResponse(content_type='text/x-yaml')
		response['Content-Disposition'] = 'attachment; filename="'+code_filename+'.yml"'
		response.write(yaml_file)
		return response
	else:
		return HttpResponseForbidden()

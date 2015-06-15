from django.shortcuts import render_to_response
from django.http import HttpResponseForbidden, HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.template import RequestContext

def main(request):
	ctx = RequestContext(request, {})
	return render_to_response("CLI_Generator/main.html", context_instance = ctx) 

def convert(request):
	if request.method == "GET":
		sections = []
		comments = []
		code_desc = request.GET["code_desc"]
		code_host = request.GET["code_host"]
		code_filename = request.GET["code_filename"]
		code_file_content = request.GET["code_file_content"]
		file_data = code_file_content.replace(r"\r\n", r"\n")
		formated_data = str("\n".join(file_data.splitlines()))

		for line in formated_data.split('\n'):
			li = line.strip()
			if li.startswith("!") or li.startswith("#"):
				comments.append(li)

		for line in formated_data.split('\n'):
			if line.startswith("!") or line.startswith("#"):
				sections.append([])
			elif sections and line:
				sections[-1].append(line)
     
		yaml_file ='---'+'\n'
		yaml_file +='# To run this Ansible playbook, issue the following command on the Ansible server:\n#\n# ansible-playbook -i hosts <filename>\n#\n'
		yaml_file +='\n\n\n'+'- name: '+code_desc+'\n'
		yaml_file +='  hosts: '+code_host+'\n\n'
		yaml_file +='  tasks: '+'\n\n'
		for c,s in zip(comments,sections):
			repl = c.replace("!","#")
			yaml_file += str(repl)+'\n'+'  - nxos_command:'+'\n'+'      host: "{{ inventory_hostname }}"'+'\n'+'      type: config'+'\n'+"      command: "+str(s)+"\n\n"

		response = HttpResponse(content_type='text/x-yaml')
		response['Content-Disposition'] = 'attachment; filename="'+code_filename+'.yml"'
		response.write(yaml_file)
		return response
	else:
		return HttpResponseForbidden()

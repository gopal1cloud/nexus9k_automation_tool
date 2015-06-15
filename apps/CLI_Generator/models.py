from django.db import models

class NexusCLI_Config_Management(models.Model):
	name = models.CharField(max_length=1000)
	csv_file = models.FileField(null=True, blank = True, upload_to='Nexus_CLI_Config_Files', verbose_name = "CSV File")
	cli_generator_file = models.FileField(null=True, blank = True, upload_to='Nexus_CLI_Config_Files', verbose_name = "CLI Config Generator File")
	timestamp = models.DateTimeField(auto_now_add=True)
	is_removed = models.BooleanField(default=False)
		
	class Meta:
		verbose_name = "Nexus CLI Config Management"
		verbose_name_plural = "Nexus CLI Config Management"
		
	def __unicode__(self):
		return u'%s' % (self.name)

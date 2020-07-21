from django.db import models


class Hostip(models.Model):
    objects = models.Manager()
    hostid = models.AutoField(primary_key=True)
    ip = models.CharField(max_length=15, null=False, blank=False)
    hostname = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'hostip'

    def __str__(self):
        return self.hostname


class Hostinfomation(models.Model):
    objects = models.Manager()
    hostid = models.ForeignKey(Hostip, on_delete=models.CASCADE)
    sysadm_password = models.CharField(max_length=100)
    zjgl_password = models.CharField(max_length=100)
    cwgl_password = models.CharField(max_length=100)
    root_password = models.CharField(max_length=100)
    machine_type = models.CharField(max_length=200)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'hostinfomation'

    def __str__(self):
        return self.hostid


class Groups(models.Model):
    objects = models.Manager()
    groupid = models.AutoField(primary_key=True)
    group_name = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'groups'


class Hst_grp(models.Model):
    object = models.Manager()
    hostid = models.ForeignKey(Hostip, on_delete=models.CASCADE)
    groupid = models.ForeignKey(Groups, on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = 'hst_grp'

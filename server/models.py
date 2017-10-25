from django.db import models


class Account(models.Model):
    email = models.CharField(max_length=50, primary_key=True)
    password = models.TextField(max_length=600)
    name = models.CharField(max_length=20)
    level = models.SmallIntegerField(default=0)
    token = models.TextField()
    rome_name = models.TextField()

    class Meta:
        abstract = True


class StudentAccount(Account):
    student_number = models.CharField(max_length=6)


class TeacherAccount(Account):
    pass


class Room(models.Model):
    name = models.CharField(max_length=20, primary_key=True)
    owner = models.ForeignKey(TeacherAccount)
    wait_members = models.TextField()
    members = models.TextField()


class Schedule(models.Model):
    room = models.ForeignKey(Room)
    title = models.CharField(max_length=100)
    msg = models.TextField()
    month = models.SmallIntegerField(default=0)
    date = models.SmallIntegerField(default=0)
    owner = models.ForeignKey(TeacherAccount)

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from social_auth.signals import socialauth_registered

''' Problems is now part of Listing models
class Problem(models.Model):
    pass'''

class Country(models.Model):
    code = models.CharField(max_length=5)
    name = models.CharField(max_length=100, blank=True, null=True)

    def __unicode__(self):
        return self.name or self.code


class City(models.Model):
    name = models.CharField(max_length=100)

    def __unicode__(self):
        return self.name


class Skill(models.Model):
    name = models.CharField(max_length=100)

    def __unicode__(self):
        return self.name


class UserProfile(models.Model):
    user = models.OneToOneField(User, editable=False)
    country = models.ForeignKey(Country, null=True)
    city = models.ForeignKey(City, null=True)
    skills_offered = models.ManyToManyField(Skill, related_name='offered_set')
    skills_wanted = models.ManyToManyField(Skill, related_name='wanted_set')
    #Noted skills will be added after the user interacts with a problem and recieve feedback
    #TODO add it to Migration
    # ^ added ./manage.py schemamigration --auto accounts
    skills_noted = models.ManyToManyField(Skill, related_name='noted_skills')

    def __unicode__(self):
        return self.user.username


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
        # country = Country.objects.get_or_create(name=)
        # 

post_save.connect(create_user_profile, sender=User)


def fill_user_profile(sender, user, response, details, **kwargs):
    profile = user.get_profile()
    try:
        country = Country.objects.get_or_create(code=response['location']['country']['code'])
        profile.country = country
    except:
        pass
    try:
        city = City.objects.get_or_create(name=response['location']['name'])
        profile.city = city
    except:
        pass
    profile.save()
    if 'skills' in response and 'skill' in response['skills']:
        for sk in response['skills']['skill']:
            skill, was_created = Skill.objects.get_or_create(name=sk['skill']['name'])
            profile.skills_offered.add(skill)

socialauth_registered.connect(fill_user_profile)

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="用户")
    nickname = models.CharField(max_length=50, blank=True, verbose_name="昵称")
    avatar = models.ImageField(upload_to='avatars/%Y%m%d/', blank=True, null=True, verbose_name="头像")
    bio = models.TextField(blank=True, max_length=500, verbose_name="简介")
    dance_style = models.CharField(max_length=100, blank=True, verbose_name="擅长舞种")
    city = models.CharField(max_length=50, blank=True, verbose_name="城市")
    region = models.ForeignKey('origin.Region', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="所在地区", limit_choices_to={'level': 1})
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="注册时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    class Meta:
        verbose_name = "用户信息"
        verbose_name_plural = "用户信息"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} 的个人资料"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'userprofile'):
        instance.userprofile.save()

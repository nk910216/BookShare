from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
# Create your models here.
class Profile(models.Model):

    EXCHANGE_METHOD_NONE = 'NONE'
    EXCHANGE_METHOD_MAIL = 'MAIL'
    EXCHANGE_METHOD_FACE = 'FACE'
    EXCHANGE_METHOD_BOTH = 'BOTH'
    EXCHANGE_MEOTHOD_COHICES = (
        (EXCHANGE_METHOD_NONE, '請選擇交換方式'),
        (EXCHANGE_METHOD_MAIL, '郵寄'),
        (EXCHANGE_METHOD_FACE, '面交'),
        (EXCHANGE_METHOD_BOTH, '兩者皆可'),
    )

    CITY_NONE = 'NONE'
    CITY_KLU = 'KLU'
    CITY_TPE = 'TPE'
    CITY_TPH = 'TPH'
    CITY_ILN = 'ILN'
    CITY_HSC = 'HSC'
    CITY_HSH = 'HSH'
    CITY_TYC = 'TYC'
    CITY_MAL = 'MAL'
    CITY_TXG = 'TXG'
    CITY_CWH = 'CWH'
    CITY_NTO = 'NTO'
    CITY_CIC = 'CIC'
    CITY_CIH = 'CIH'
    CITY_YUN = 'YUN'
    CITY_TNN = 'TNN'
    CITY_KHH = 'KHH'
    CITY_IUH = 'IUH'
    CITY_TTT = 'TTT'
    CITY_HWA = 'HWA'
    CITY_KMN = 'KMN'
    CITY_LNN = 'LNN'
    CITY_PEH = 'PEH'
     
    CITY_CHOICES = (
        (CITY_NONE, '請選擇面交城市'),
        (CITY_KLU, '基隆市'),
        (CITY_TPE, '台北市'),
        (CITY_TPH, '新北市'),
        (CITY_ILN, '宜蘭縣'),
        (CITY_HSC, '新竹市'),
        (CITY_HSH, '新竹縣'),
        (CITY_TYC, '桃園市'),
        (CITY_MAL, '苗栗縣'),
        (CITY_TXG, '台中市'),
        (CITY_CWH, '彰化縣'),
        (CITY_NTO, '南投縣'),
        (CITY_CIC, '嘉義市'),
        (CITY_CIH, '嘉義縣'),
        (CITY_YUN, '雲林縣'),
        (CITY_TNN, '台南市'),
        (CITY_KHH, '高雄市'),
        (CITY_IUH, '屏東縣'),
        (CITY_TTT, '台東縣'),
        (CITY_HWA, '花蓮縣'),
        (CITY_KMN, '金門縣'),
        (CITY_LNN, '連家縣'),
        (CITY_PEH, '澎湖縣'),
    )

    user = models.OneToOneField(User, related_name='profile',on_delete=models.CASCADE, null=True)
    exchange_method = models.CharField(choices=EXCHANGE_MEOTHOD_COHICES, 
        default=EXCHANGE_METHOD_NONE, max_length=10)
    city = models.CharField(choices=CITY_CHOICES, default=CITY_NONE, max_length=5)
    area_description = models.CharField(max_length=100, blank=True)
    contact_description = models.CharField(max_length=500, blank=True)

    @receiver(post_save, sender=User)
    def create_or_update_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)
        instance.profile.save()

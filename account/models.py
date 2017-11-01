from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string
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
        (CITY_NONE, '無'),
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

    user = models.OneToOneField(User, related_name='profile',on_delete=models.CASCADE)
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

    def __str__(self):
        return self.user.username + "'s profile"

    def need_update_info(self):
        cls = self.__class__
        
        if self.exchange_method == cls.EXCHANGE_METHOD_NONE or\
            len(self.contact_description) - self.contact_description.count(' ') == 0:
            return True

        if (self.exchange_method == cls.EXCHANGE_METHOD_FACE or self.exchange_method == cls.EXCHANGE_METHOD_BOTH) and \
            (self.city == cls.CITY_NONE or \
            len(self.area_description) - self.area_description.count(' ') == 0):
            return True
        return False

    def need_update_info_message(self):
        cls = self.__class__
        
        word = ''
        if self.exchange_method == cls.EXCHANGE_METHOD_NONE:
            word +='交換方式不明 '

        if len(self.contact_description) - self.contact_description.count(' ') == 0:
            word += '聯絡方式不明 '

        if (self.exchange_method == cls.EXCHANGE_METHOD_FACE or self.exchange_method == cls.EXCHANGE_METHOD_BOTH) and \
            (self.city == cls.CITY_NONE or \
            len(self.area_description) - self.area_description.count(' ') == 0):
            word += '面交詳情不明 '
        return word

    def exchange_face(self):
        cls = self.__class__

        if self.exchange_method == cls.EXCHANGE_METHOD_FACE or self.exchange_method == cls.EXCHANGE_METHOD_BOTH:
            return True
        return False

    def get_city(self):
        cls = self.__class__

        if self.exchange_method == cls.EXCHANGE_METHOD_FACE or self.exchange_method == cls.EXCHANGE_METHOD_BOTH:
            return dict(cls.CITY_CHOICES).get(self.city, '')
        return '不面交'

    def get_name_with_exchange_face(self):

        html_data = render_to_string('user_exchange_method_info.html', {'profile': self})
        return html_data
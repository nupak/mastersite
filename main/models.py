import django
from django.contrib.auth.models import AbstractBaseUser, UserManager
from django.db import models
from dominate.tags import *
from scientistSite.settings import SITE_NAME
from scientistSite.settings import MEDIA_ROOT

from django.db.models.signals import post_save,pre_save
from django.dispatch import receiver


okrugName = ['cfo', 'szfo', 'yfo', 'skfo', 'pfo', 'urfo', 'sfo', 'dfo']
okrugPoints = {
    'cfo': [
        54.873745,
        38.064718

    ],
    'szfo': [
        61.469749,
        36.498137

    ],
    'yfo': [
        48.622558,
        43.166151

    ],
    'skfo': [
        43.898977,
        44.693045

    ],
    'pfo': [
        55.485362,
        51.524283
    ],
    'urfo': [
        60.519886,
        64.350447

    ],
    'sfo': [
        61.833048,
        96.962463

    ],
    'dfo': [
        63.629508,
        124.131856

    ]
}
# штука для селекета в модели данных
okrug_list = [
    ('cfo', 'Центральный Федеральный Округ'),
    ('szfo', 'Северо-Западный Федеральный Округ'),
    ('yfo', 'Южный Федеральный Округ'),
    ('skfo', 'Северо-Кавказский Федеральный Округ'),
    ('pfo', 'Приволжский Федеральный Округ'),
    ('urfo', 'Уральский Федеральный Округ'),
    ('sfo', 'Сибирский Федеральный Округ'),
    ('dfo', 'Дальневосточный Федеральный Округ')
]
# Для связки переменных и их названйи для вывода на яндекс карту
okrugListName = {
    'cfo': 'Центральный Федеральный Округ',
    'szfo': 'Северо-Западный Федеральный Округ',
    'yfo': 'Южный Федеральный Округ',
    'skfo': 'Северо-Кавказский Федеральный Округ',
    'pfo': 'Приволжский Федеральный Округ',
    'urfo': 'Уральский Федеральный Округ',
    'sfo': 'Сибирский Федеральный Округ',
    'dfo': 'Дальневосточный Федеральный Округ'
}


class MyAccountManager(UserManager):
    def create_user(self, email, username, password=None):
        if not email:
            raise ValueError('Users must have an email address')
        if not username:
            raise ValueError('Users must have a username')

        user = self.model(
            email=self.normalize_email(email),
            username=username,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password):
        user = self.create_user(
            email=self.normalize_email(email),
            password=password,
            username=username,
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class scientist(AbstractBaseUser):
    # лист специальности
    PSY = 'Коррекционная психология'
    PED = 'Коррекционная педагогика'
    specialityList = [
        (PSY, 'Коррекционная психология'),
        (PED, 'Коррекционная педагогика')
    ]
    # Лист ученой степени
    KANDIDAT = 'Кандидат наук'
    DOCTORNAUK = 'Доктор наук'
    academic_list = [
        (KANDIDAT, 'Кандидат наук'),
        (DOCTORNAUK, 'Доктор наук')
    ]
    academic_dict = {
        'Кандидат наук': 'Кандидат наук',
        'Доктор наук': 'Доктор наук'
    }
    # Лист ученого звания
    PROFESSOR = 'Профессор'
    DOCSHENT = 'Доцент'
    academicTitle_list = [(PROFESSOR, 'Профессор'),
                          (DOCSHENT, 'Доцент')]

    email               = models.EmailField(verbose_name="email", max_length=60, unique=True)
    username            = models.CharField(max_length=30,verbose_name="Имя пользователя", unique=True)
    date_joined         = models.DateTimeField(verbose_name='date joined', auto_now_add=True)
    last_login          = models.DateTimeField(verbose_name='last login', auto_now=True)
    is_admin            = models.BooleanField(default=False)
    is_active           = models.BooleanField(default=True)
    is_staff            = models.BooleanField(default=False)
    is_superuser        = models.BooleanField(default=False)
    image               = models.ImageField('Фотография пользователя', max_length=255, upload_to="images/scientistPhoto",
                              default="images/scientistPhoto/default.png", blank=False, null=True)
    hide_email          = models.BooleanField(default=False)
    hide_phone          = models.BooleanField(default=False)
    name                = models.CharField('Имя', max_length=60, default="", blank=False)  # Имя
    surname             = models.CharField('Фамилия', max_length=60, default="", blank=False)  # Фамилия
    patronymic          = models.CharField('Отчество', max_length=60, default="", blank=True)  # Отчество
    Bigregion           = models.CharField('Федеральный округ', blank=False, max_length=60, choices=okrug_list,
                                 default='')  # Округ
    region              = models.CharField('Cубъект', max_length=60, default="", blank=True)  # Субъект
    job_place           = models.CharField('Место работы', max_length=120, default="", blank=True)  # Место работы
    position            = models.CharField('Должность', max_length=120, default="", blank=True)  # Должность
    academicDegree      = models.CharField('Ученая степень', blank=True, max_length=100, choices=academic_list,
                                      default='')  # Ученая степень
    codeSpeciality      = models.CharField('Специальность', blank=True, max_length=100, choices=specialityList,
                                      default='')  # Специальность
    academicTitle       = models.CharField('Ученое звание', blank=True, max_length=100, choices=academicTitle_list,
                                     default='')  # Ученое звание
    mainResults         = models.TextField('Основные результаты исследовательской деятельности', default="",
                                   blank=True)  # Основные результаты исследовательской деятельности
    keyWords            = models.TextField('Ключевые слова', max_length=300, blank=True,default='')  # Ключевые слова
    keyWordsString      = models.CharField('Строка ключевых слов', max_length=300, blank=True, default='')
    phone               = models.CharField('Номер Телефона', blank=True, default='', max_length=12)  # Номер телефона
    ymapshortcut        = models.TextField('Точка на яндекс карте', default='', blank=True)
    publication         = models.TextField(max_length=4096, blank=True, default='')  # Публикации

    elibID              = models.CharField('Код Elibriary', max_length=128, blank=True, null=True)
    elib_link           = models.URLField('Ссылка на cтраницу в Elibriary', blank=True, null=True)
    h_Scopus            = models.IntegerField('H - индекс  Scopus', blank=True, null=True)
    scopusLink          = models.URLField('Ссылка на cтраницу в Scopus', blank=True, null=True)
    h_WebOfScience      = models.IntegerField('H - индекс  Web of Science', blank=True, null=True)
    WoSLink             = models.URLField('Ссылка на cтраницу в Web of Science', blank=True, null=True)

    dier_sovet          = models.CharField('Диссертационный совет', max_length=300, blank=True, default='')
    editorial_boards    = models.CharField('Редколлегия научных изданий', max_length=300, blank=True, default='')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.surname + ' ' + self.name + ' ' + self.Bigregion + ' ' + self.region

    def getBigRegion(self, BG):
        return (okrugListName[BG])

    def getjsonShort2(self):
        image = SITE_NAME + str(self.image.url)
        lineBigregandReg = ""
        academicDegree = ""
        speciality = ""
        email = ""
        phone = ""
        lines = ""
        print()
        if self.is_staff == True:
            self.Bigregion ='cfo'
        # if str(self.patronymic) !='' and str(self.patronymic) != None:
        if str(self.patronymic):
            fio = "<span class='name'>" + str(self.name) + " " + str(self.patronymic) + " " + str(
                self.surname) + "</span>"
        else:
            fio = "<span class='name'>" + str(self.name) + " " + str(self.surname) + "</span>"
        FioandImage = f"<div class='balloon-content_person'><img src='{image}' alt='person' /><span class='name'>{fio}</span></div>"

        if str(self.getBigRegion(self.Bigregion)):
            if str(self.region):
                lineBigregandReg = f"<div class='balloon-content_info__line'><span class='image location'></span><span class='text'>{str(self.getBigRegion(self.Bigregion))}, {str(self.region)}</span></div>"
            else:
                lineBigregandReg = f"<div class='balloon-content_info__line'><span class='image location'></span><span class='text'>{str(self.getBigRegion(self.Bigregion))}</span></div>"
        if self.academicDegree:
            academicDegree = f"<div class='balloon-content_info__line'><span class='image academicDegree'></span><span class='text'>{str(self.academicDegree)}</span></div>"
        if self.codeSpeciality:
            speciality = f"<div class='balloon-content_info__line'><span class='image expertise'></span><span class='text'><span class='text'>{str(self.codeSpeciality)}</span></span></div>"
        if self.email and self.hide_email == False:
            email = f"<div class='balloon-content_info__line'><span class='image email'></span><span class='text'>{str(self.email)}</span></div>"
        if self.phone and self.hide_phone == False:
            phone = f"<div class='balloon-content_info__line'><span class='image phone'></span><span class='text'>{str(self.phone)}</span></div>"
        lines = "<div class='balloon-content_info'>" + lineBigregandReg + academicDegree + speciality + phone + email + "</div>"
        more = f"<a class='more-info' href='/profile/{self.pk}'>Подробнее</a>"
        example = "<div class='balloon-content'>" + FioandImage + lines + more + "</div>"
        return example

    def __str__(self):
        return self.username

    def get_profile_image_filename(self):
        return str(self.profile_image)[str(self.profile_image).index('profile_images/' + str(self.pk) + "/"):]

    # For checking permissions. to keep it simple all admin have ALL permissons
    def has_perm(self, perm, obj=None):
        return self.is_admin

    # Does this user have permission to view this app (ALWAYS YES FOR SIMPLICITY)
    def has_module_perms(self, app_label):
        return True

    objects = MyAccountManager()
    class Meta:
        verbose_name = "Ученый"
        verbose_name_plural = 'Ученые'


# ===============================================================================
# Модель данных для новостной ленты

class news(models.Model):
    """
        Модель данных новости
    """
    date = models.DateField('Дата публикации', default=django.utils.timezone.now)
    headLine = models.CharField('Название новости', max_length=256)
    announce_text = models.TextField('Текст для анонса', max_length=512, blank=True)
    text = models.TextField('Текст новости', max_length=8192)
    image = models.ImageField(upload_to='images/news/', blank=False, default="images/news/default.png")

    @property
    def announce(self):
        return self.announce_text or self.text[:512].rsplit(' ', 1)[0]

    def __str__(self):
        return self.headLine + ' ' + str(self.date)

    def get_count(self):
        return news.objects.count()

    class Meta:
        verbose_name = "Новость"
        verbose_name_plural = 'Новости'


class newsSer(models.Model):
    count = models.IntegerField()

    def get_count(self):
        return news.objects.count()


@receiver(post_save,sender = scientist,)
def update_profile (sender,instance, **kwargs):
    print("signal")
    instance.ymapshortcut = instance.getjsonShort2()
    scientist.objects.filter(pk=instance.pk).update(ymapshortcut=instance.ymapshortcut)

#post_save.connect(update_profile, sender=, dispatch_uid ='Create new scentist')









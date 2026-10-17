from django.db import models


class Feedback(models.Model):
    """Обращение из формы на сайте."""

    class Type(models.TextChoices):
        CONTACT = "contact", "Контакты"
        COOPERATION = "cooperation", "Сотрудничество"

    class Lang(models.TextChoices):
        RU = "ru", "Русский"
        EN = "en", "English"
        ZH = "zh", "中文"

    class Status(models.TextChoices):
        NEW = "new", "Новое"
        IN_PROGRESS = "in_progress", "В работе"
        CLOSED = "closed", "Закрыто"

    type = models.CharField("тип", max_length=20, choices=Type.choices)
    full_name = models.CharField("ФИО", max_length=150)
    company = models.CharField("компания", max_length=200)
    country = models.CharField("страна", max_length=100)
    email = models.EmailField("email")
    phone = models.CharField("телефон", max_length=30, null=True, blank=True)
    subject = models.CharField("тема", max_length=200)
    message = models.TextField("сообщение")
    consent = models.BooleanField("согласие на обработку данных", default=False)
    lang = models.CharField("язык", max_length=2, choices=Lang.choices)
    status = models.CharField(
        "статус",
        max_length=20,
        choices=Status.choices,
        default=Status.NEW,
        db_index=True,
    )
    admin_note = models.TextField("внутренний комментарий", blank=True)
    ip = models.GenericIPAddressField("IP", null=True, blank=True)
    created_at = models.DateTimeField("создано", auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = "обращение"
        verbose_name_plural = "обращения"
        ordering = ["-created_at", "-id"]

    def __str__(self):
        return f"{self.get_type_display()}: {self.subject}"

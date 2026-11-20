from django.conf import settings
from django.db import models


class BlogPost(models.Model):
    """Публикация в блоге."""
    title = models.CharField('Заголовок', max_length=200)
    text = models.TextField('Текст')
    date_added = models.DateTimeField('Дата публикации', auto_now_add=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор',
    )

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'публикации'

    def __str__(self):
        return self.title
from django.db import models

class Post(models.Model):
    theme = models.CharField(u'Тема', max_length=255)
    text = models.TextField(u'Текст Поста')
    creation_date = models.DateTimeField(u'Дата создания', auto_now_add=True)
    is_hidden = models.BooleanField(default=False)

    def __str__(self):
        return "{} => {}".format(self.pk, self.theme)

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.PROTECT)
    author = models.CharField(u'Автор', max_length=255)
    text = models.TextField(u'Текст')
    reply_to = models.ForeignKey('blog.Comment', null=True, blank=True, on_delete=models.PROTECT)
    creation_date = models.DateTimeField(u'Дата создания', auto_now_add=True)

    def __str__(self):
        return "{} => {}".format(self.author, self.post)
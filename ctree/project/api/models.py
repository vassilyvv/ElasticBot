from django.db import models


class ApprovedImage(models.Model):
    url = models.URLField(max_length=255, unique=True)

    def __str__(self):
        return self.url[:30]
from django.db import models

# Create your models here.

class Category(models.Model):
	category_name = models.CharField(max_length = 250)
	video_title = models.CharField(max_length = 100000)

	def __str__(self):
		return self.category_name

class Video(models.Model):
	category = models.ForeignKey(Category, on_delete = models.CASCADE)
	author = models.CharField(max_length = 250)
	video_title = models.CharField(max_length = 500)
	video_url = models.CharField(max_length = 1000)
	main_category = models.CharField(max_length = 250)
	sub_category = models.CharField(max_length = 250)
	normalized_words = models.CharField(max_length = 1000000)

	def __str__(self):
		return self.video_title + ' ' + self.video_url




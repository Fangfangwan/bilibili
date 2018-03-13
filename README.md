# bilibili
Instruction:

The main folder for submission in our github is django_folder. We may use documents in other folders, which are indicated in our code.

Run our code in user interface:

1. Install django, scikit-learn, gensim (no 3.3.0 version, which is problematic) and jieba.
2. Change directory to the first bilibili folder in django_folder.
3. Run  "python manage.py runserver" in shell
4. Go into http://127.0.0.1:8000/ .
5. Then search!

In detail:

​	First, we downloaded ranking data in JSON format from https://www.bilibili.com . Then we used final_df function on these file to get video data dataframes, and then save it to local directory (you need to change the local directory on VM). On Github they are stored in https://github.com/Fangfangwan/bilibili/tree/master/Data .

​	Then we generated a overall big D2V model and then make word clouds by category by running codes in make_clouds_by_cat.py.

Code writing by member:

Ling Dai - working on designing web scraping and dataframe generation algorithms, and writing bilibiliclass.py.

Fangfang Wan - grabing ranking video id data from JSON file, cleaning up and putting together web scraping & dataframe generation code written by Ling Dai, running code to get data by category, getting wordclouds of 6 out of 11 categories, and Django implementation together with Yilun Dai

Yilun Dai - working on getting emoticons and writing functions of implementing emoticons, , getting wordclouds of 5 out of 11 categories, and Django implementation together with Fangfang Wan.

Other sources that we have used:

1. For django implementation (including test2.html, views.py, cat_list.csv in res folder and main.css), we largely borrowed from ui file in pa3. We also consulted django tutorials on https://docs.djangoproject.com/en/2.0/intro/ and https://www.youtube.com/playlist?list=PL6gx4Cwl9DGBlmzzFcLgDhKTTfNLfX1IK .




# E_Ticket


install reddis 
pip install -r requirements.txt
then check for the port and configure the port on which the celery worker will run 

by this command we can see the port of redis server
redis-server


Task Scheduling 

1 Firstly start celery beat

celery -A E_Ticket beat 

2  start celery worker  

celery -A E_Ticket worker -l info




another way to do that is by custom command 

python manage.py create_trips


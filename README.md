# Booker
A library project with Django, mysql and Docker

Application available on http://ip_adresse:8000/catalog  

To init the library, upload the ebooks (pdf, epub) in the server directory and launch :  
http://ip_adresse:8000/catalog/init

**configuration.py:**  
storage_directory : define where your books files are stored  
container_mode: set to true to use environment variables (define in .env at
the same level as manage.py)  
  
**.env:**  
Create a .env file at the same level as manage.py  
and set your database configuration and django deployment parameters  
(DJANGO_DEBUG : True or False, ENV=prd or dev)

DB_NAME=  
DB_USER=  
DB_PASSWORD=  
DB_HOST=db_mysql  
DB_PORT=3306  
DJANGO_SECRET_KEY  
DJANGO_DEBUG  
ENV  

**compose.yaml:**  
Used for development    
In "volumes", define your storage directory for development purpose  
With synology path, take care of the "V" in capital letter  
  
nginx :  
in volumes, define where static files are stored on the NAS  

**docker-compose.yaml:**  
Used for production mode on synology NAS
In "Volumes" define storage directory for production  
In "image" define the version to use  

**Deployment actions:**  
docker build -t sonpero/booker-web .  
docker tag sonpero/booker-web sonpero/booker-web:x.x.x  
docker push sonpero/booker-web:x.x.x  
  
docker build -t sonpero/booker-nginx .  
docker tag sonpero/booker-nginx sonpero/booker-nginx:x.x.x  
docker push sonpero/booker-nginx:x.x.x  

In Synology NAS :  
Upload static files (generated by manage.py collectstatic)  
Upload docker-compose.yaml  
Upload .env  
sudo docker-compose up  

Note:  
To init database : suppress and create again db directory  
In the booker-web container : python manage.py createsuperuser  






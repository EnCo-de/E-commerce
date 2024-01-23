# E-commerce
E-commerce website Django project

1. Prepare Your Environment

      create a new folder and navigate into it. In this folder, you’ll set up and activate a new virtual environment using your command line:
      
            $ python -m venv env
            $ python3 -m venv env
      
      On Windows, run:
   
            env\Scripts\activate
      
      On Unix or MacOS, run:
   
            $ source env/bin/activate


3. Download this project files into your directory 
      
            (env) $ git clone https://github.com/EnCo-de/E-commerce.git
            
            (env) $ cd E-commerce

      Switch to a new branch 'EnCo-de-patch-1'

            (env) $ git checkout EnCo-de-patch-1

  
4. Install Django and Dependencies into this dedicated development workspace:

   Since you’re working on an existing project with its dependencies already pinned in a requirements.txt file, you can install the right Django version as well as all the other necessary packages in a single command:
   
            (env) $ python -m pip install -r requirements.txt


6. Set Up a Django Project

      With your virtual environment set up and activated and Django installed, you can now create a project:
    
            (env) $ django-admin startproject <project-name> .
    
      The dot skips the top-level project folder and creates your management app and the manage.py file right inside your current working directory.


7. Run set_demo.py to edit project settings

   (env) $ python set_demo.py


8. Make and apply migrations
   
   (env) $ python manage.py makemigrations
   
   (env) $ python manage.py migrate


9. Start the development server

   (env) $ python manage.py runserver

   Now, open a web browser and go to your local domain – http://127.0.0.1:8000/
   
   Use the Django admin site http://127.0.0.1:8000/admin/ try logging in with the superuser account and add some product categories and products to the store.

# E-commerce
E-commerce website Django project

1. Prepare Your Environment
      create a new folder and navigate into it. In this folder, you’ll set up and activate a new virtual environment using your command line:
      
      $ python3 -m venv env
      
      On Windows, run:
      env\Scripts\activate
      
      On Unix or MacOS, run:
      $ source env/bin/activate


2. Download this project files into your directory 

  (env) $ git clone https://github.com/EnCo-de/E-commerce.git

  (env) $ cd E-commerce

  
3. Install Django and Dependencies
   install Django into this dedicated development workspace:
   (env) $ python -m pip install django

   Since you’re working on an existing project with its dependencies already pinned in a requirements.txt file, you can install the right Django version as well as all the other necessary packages in a single command:
   (env) $ python -m pip install -r requirements.txt


4. Set Up a Django Project
      With your virtual environment set up and activated and Django installed, you can now create a project:
    
      (env) $ django-admin startproject <project-name> .
    
      The dot skips the top-level project folder and creates your management app and the manage.py file right inside your current working directory.


5. Run set_demo.py to edit project settings

   (env) $ python set_demo.py


6. Make and apply migrations
   
   (env) $ python manage.py makemigrations
   
   (env) $ python manage.py migrate


8. Start the development server

   (env) $ python manage.py runserver

   Now, open a web browser and go to your local domain – http://127.0.0.1:8000/

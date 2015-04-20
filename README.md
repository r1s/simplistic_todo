# simplistic_todo
REST API for a simplistic todo list using sqlite db

##Install requirements:
pip install -r deploy/requirements.pip

##Run the application:
python main.py

## Create user
'/users', ['POST']
## Login user
'/login', ['POST']
## Logout user
'/logout', ['POST']

## Get the user tasks
'/tasks', ['GET']
## Create the user task
'/tasks', ['POST']
## Update the user task
'/tasks/<task_id:int>', ['PUT']
## Delete the user task
'/tasks/<task_id:int>', ['DELETE']
## Show the user task
'/tasks/<task_id:int>', ['GET']

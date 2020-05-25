import os
import random
import time
from flask import Flask, request, render_template, session, flash, redirect, \
    url_for, jsonify
from celery import Celery
import Tests


app = Flask(__name__)


# Celery configuration
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'
app.config['CELERY_ACCEPT_CONTENT'] = ['json']
app.config['CELERY_TASK_SERIALIZER'] = 'json'
app.config['CELERY_RESULT_SERIALIZER'] = 'json'
app.config['CELERY_IGNORE_RESULT'] = False



# Initialize Celery
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

testOne = Tests.Test1()
testTwo = Tests.Test2()
testThree = Tests.Test3()
testFour = Tests.Test4()

testOne.set_next(testTwo).set_next(testThree).set_next(testFour)


@celery.task
def startDecisionML(patientName):
    """Background task to do all medical test and store data."""


@celery.task(bind=True)
def long_task(self):
    """Background task that runs a long function with progress reports."""

    Tests.client_code(testOne)
    message = ''
    total = random.randint(10, 50)
    for i in range(total):
        self.update_state(state='PROGRESS',
                          meta={'current': i, 'total': total,
                                'status': message})
        time.sleep(1)    
    return {'current': 100, 'total': 100, 'status': 'Task completed!',
            'result': 42}


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html', name=session.get('Name', ''))

    # Start Tests 
    #if request.form['submit'] == 'Send':
        # send right away
    return redirect(url_for('index'))


@app.route('/longtask', methods=['POST'])
def longtask():
    #name=session.get('Name', '')
    #print(name)
    task = long_task.apply_async()
    return jsonify({}), 202, {'Location': url_for('taskstatus',
                                                  task_id=task.id)}


@app.route('/status/<task_id>')
def taskstatus(task_id):
    task = long_task.AsyncResult(task_id)
    print(task.state)
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'current': 0,
            'total': 1,
            'status': 'Pending...'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'current': task.info.get('current', 0),
            'total': task.info.get('total', 1),
            'status': task.info.get('status', '')
        }
        if 'result' in task.info:
            response['result'] = task.info['result']
    else:
        # something went wrong in the background job
        response = {
            'state': task.state,
            'current': 1,
            'total': 1,
            'status': str(task.info),  # this is the exception raised
        }
    return jsonify(response)


if __name__ == '__main__':
    #app.run(debug=True)
    app.run(host='0.0.0.0')

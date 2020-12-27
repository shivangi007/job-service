import io

from flask import Flask
from flask import jsonify
from flask import request
from queue import PriorityQueue
import time
import json

app = Flask(__name__)

counter = 0

jobsQueue = PriorityQueue()
deletedJobs = []


def addCounter():
    global counter
    counter = counter + 1
    return counter


@app.route('/')
def hello():
    return 'Hi! we are now up and ready to work!'


def worker():
    while True:
        item = jobsQueue.get()
        if item is None:
            break

        time.sleep(30)  # 30 second time out for a job as mentioned in stage 3
        jobsQueue.task_done()

        # need to enqueue the job again in waiting status
        counterLocal = addCounter()
        new_job = item[0]
        new_job[-2] = counterLocal

        priority = new_job[-14]
        jobsQueue.put((priority, new_job))

        return jsonify({'job_Id': counterLocal})


@app.route('/health')
def heath_check():
    return 'everything looks good!'


# solution for stage 2


"""
@app.route('/jobs/next', methods=['DELETE'])
def deleteOne():
    jobsQueue.get()
    print(jobsQueue.queue)
    return "success"

@app.route('/jobs/next', methods=['PATCH'])
def patchOne():
    payload = request.get_json()
    if payload["status"] == "processing":
        theOne = jobsQueue.get()
        print(jobsQueue.queue)
        return jsonify(theOne[1])
    else:
        return "Please send the right status"
"""


# solution for stage 3


@app.route('/jobs/<int:id>', methods=['DELETE'])
def deleteOne(id):
    while not jobsQueue.empty():
        theOne = jobsQueue.get()
        json_string = json.dumps(theOne[1])
        json_object = json.loads(json_string)
        print(json_object)

        print(json_object[-2])
        get_id = json_object[-2] if json_object[-2] != '}' else json_object[-3]
        if id == int(get_id):
            break
        else:
            priority = int(json_object[-14] if json_object[-14] != ',' else json_object[-15])
            jobsQueue.put((priority, json_string))
    print(jobsQueue.queue)
    return "success"


@app.route('/jobs/next', methods=['PATCH'])
def patchOne():
    payload = request.get_json()
    if payload["status"] == "processing":
        theOne = jobsQueue.get()
        deletedJobs.append(theOne)
        print(jobsQueue.queue)
        print(deletedJobs)
        return jsonify(theOne[1])
    else:
        return "Please send the right status"


@app.route('/jobs/next', methods=['GET'])
def returnOne():
    theOne = jobsQueue.queue[0]
    print(jobsQueue.queue)
    return jsonify(theOne[1])


@app.route('/jobs', methods=['POST'])
def addOne():
    counterLocal = addCounter()
    new_job = request.get_json()
    new_job["jobId"] = counterLocal
    new_job_str = str(new_job)

    priority = new_job["priority"]
    jobsQueue.put((priority, new_job_str))

    return jsonify({'job_Id': counterLocal})


if __name__ == '__main__':
    app.run()

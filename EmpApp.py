from flask import Flask, render_template, request
from pymysql import connections
import os
import boto3
import base64
from config import *

app = Flask(__name__, template_folder='templates', static_folder='static')

bucket = custombucket
region = customregion

db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
output = {}
table = 'employee'


@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('Homepage.html')

# navigate to add emp


@app.route("/goaddemp", methods=['GET'])
def GoAddEmp():
    return render_template('AddEmp.html')

# navigate to get emp


@app.route("/gogetemp", methods=['GET'])
def GoGetEmp():
    return render_template('GetEmp.html')

# navigate to update emp


@app.route("/goupdateemp", methods=['GET'])
def GoUpdateEmp():
    return render_template('UpdateEmp.html')

# navigate to delete emp


@app.route("/godeleteemp", methods=['GET'])
def GoDeleteEmp():
    return render_template('DeleteEmp.html')

# navigate to about us


@app.route("/aboutus", methods=['GET'])
def about():
    try:
        # Fetch image file from S3 #
        emp_image_file_name_in_s3_1 = "emp-id-" + "666" + "_image_file"
        emp_image_file_name_in_s3_2 = "emp-id-" + "777" + "_image_file"
        s3 = boto3.client('s3')

        try:
            bucket_location = boto3.client(
                's3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            response = s3.get_object(
                Bucket=bucket_location, Key=emp_image_file_name_in_s3_1)
            img1 = response['Body'].read()
            img1 = {
                "body": base64.b64encode(img1),
                "isBase64Encoded": True
            }

            img2 = s3.get_object(
                Bucket=bucket_location, Key=emp_image_file_name_in_s3_2)
            img2 = response['Body'].read()

        except Exception as e:
            return str(e)

    except Exception as e:
        return str(e)

    return render_template('AboutUs.html', image_url1=img1, image_url2=img2)


# start add emp
@app.route("/addemp", methods=['POST'])
def AddEmp():
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    pri_skill = request.form['pri_skill']
    location = request.form['location']
    emp_image_file = request.files['emp_image_file']

    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    if emp_image_file.filename == "":
        return "Please select a file"

    try:

        cursor.execute(insert_sql, (emp_id, first_name,
                       last_name, pri_skill, location))
        db_conn.commit()
        emp_name = "" + first_name + " " + last_name
        # Upload image file in S3 #
        emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
        s3 = boto3.resource('s3')

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            s3.Bucket(custombucket).put_object(
                Key=emp_image_file_name_in_s3, Body=emp_image_file)
            bucket_location = boto3.client(
                's3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                emp_image_file_name_in_s3)

        except Exception as e:
            return str(e)

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('AddEmpOutput.html', name=emp_name)


# start get emp
@app.route("/fetchdata", methods=['GET'])
def GetEmp():
    # Get user's input from webpage
    emp_id = request.form['emp_id']

    # define sql query to be execute
    read_sql = "SELECT * FROM `employee` WHERE emp_id=%s"
    # define a cursor to fetch
    cursor = db_conn.cursor()

    try:
        # execute query
        cursor.execute(read_sql, (emp_id))

        # fetch one row
        result = cursor.fetchone

        # store result
        emp_id, first_name, last_name, pri_skill, location = result

        # commit
        db_conn.commit()

        # Fetch image file from S3 #
        emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
        s3 = boto3.resource('s3')

        try:
            '''
            print("Data inserted in MySQL RDS... uploading image to S3...")
            s3.Bucket(custombucket).put_object(
                Key=emp_image_file_name_in_s3, Body=emp_image_file)
            '''
            bucket_location = boto3.client(
                's3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                emp_image_file_name_in_s3)

            img = s3.Bucket(custombucket).get_object(
                Bucket=custombucket, Key=emp_image_file_name_in_s3)

        except Exception as e:
            return str(e)

    finally:
        cursor.close()

    print("all modification done...")
    print("all fetching done...")
    return render_template('GetEmpOutput.html', id=emp_id, fname=first_name, lname=last_name, interest=pri_skill, location=location, image_url=img)


# start fetch & delete
@app.route("/delete", methods=['GET', 'DELETE'])
def delete():
    return render_template('DelEmp.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)

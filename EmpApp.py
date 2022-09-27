from flask import Flask, render_template, request
from pymysql import connections
import os
import boto3
from config import *

application = Flask(__name__, template_folder='templates',
                    static_folder='static')

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


@application.route("/", methods=['GET', 'POST'])
def home():
    return render_template('Homepage.html')

# navigate to add emp


@application.route("/goaddemp", methods=['GET'])
def GoAddEmp():
    return render_template('AddEmp.html')

# navigate to get emp


@application.route("/gogetemp", methods=['GET'])
def GoGetEmp():
    return render_template('GetEmp.html')

# navigate to update emp


@application.route("/goupdateemp", methods=['GET'])
def GoUpdateEmp():
    return render_template('SelectUpdateEmp.html')

# navigate to delete emp


@application.route("/godeleteemp", methods=['GET'])
def GoDeleteEmp():
    return render_template('DeleteEmp.html')

# navigate to about us


@application.route("/aboutus", methods=['GET'])
def GoAboutUs():
    return render_template('AboutUs.html')


# start about us


@application.route("/aboutus", methods=['GET'])
def about():
    return render_template('AboutUs.html')


# go error page


@application.route("/error", methods=['GET'])
def Error():
    return render_template('Error.html')


# start add emp


@application.route("/addemp", methods=['POST'])
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
@application.route("/fetchdata", methods=['POST'])
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
        result = cursor.fetchone()

        try:
            # store result
            emp_id, first_name, last_name, pri_skill, location = result
        except:
            return render_template('Error.html')

        # Fetch image file from S3 #
        emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
        s3 = boto3.resource('s3')

        try:
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

    print("all fetching done...")
    return render_template('GetEmpOutput.html', id=emp_id, fname=first_name, lname=last_name, interest=pri_skill, location=location, image_url=object_url)


# get update emp id


@application.route("/updateolddata", methods=['POST'])
def GetUdpEmp():
    emp_id = request.form['emp_id']
    read_sql = "SELECT * FROM `employee` WHERE emp_id=%s"
    cursor = db_conn.cursor()
    try:
        cursor.execute(read_sql, (emp_id))
        result = cursor.fetchone()
        try:
            # store result
            emp_id, first_name, last_name, pri_skill, location = result
        except:
            return render_template('Error.html')

        emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
        s3 = boto3.resource('s3')

        try:
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
    return render_template('UpdateEmp.html', id=emp_id, fname=first_name, lname=last_name)


def ReadEmp(emp_id):
    # select old record
    read_sql = "SELECT * FROM `employee` WHERE emp_id=%s"

    # define a cursor to fetch
    cursor = db_conn.cursor()

    try:
        # execute query
        cursor.execute(read_sql, (emp_id))

        # fetch one row
        result = cursor.fetchone()

        # store result
        emp_id, first_name, last_name, pri_skill, location = result

        # Fetch image file from S3 #
        emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
        s3 = boto3.resource('s3')

        try:
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
    return result  # not include url

# start update emp


@application.route("/udpemp", methods=['POST'])
def UdpEmp():
    new_pri_skill = request.form['pri_skill']
    new_location = request.form['location']

    emp_id = 1004

    emp_id, first_name, last_name, pri_skill, location = ReadEmp(emp_id)

    # update old record
    update_sql = "UPDATE `employee` SET pri_skill=%s, location=%s WHERE emp_id=%s"

    # define a cursor to fetch
    cursor = db_conn.cursor()

    try:
        emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
        s3 = boto3.resource('s3')

        try:
            if new_pri_skill == '':
                new_pri_skill = pri_skill

            if new_location == '':
                new_location = location

            # execute read old record query
            cursor.execute(update_sql, (new_pri_skill, new_location, emp_id))

            # commit to database, really make changes
            db_conn.commit()

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

    print("all updation done...")

    return render_template('UpdateEmpOutput.html', id=emp_id, fname=first_name, lname=last_name, interest=new_pri_skill, location=new_location, image_url=object_url)


# start delete
@application.route("/deleteemp", methods=['POST'])
def delete():
    # Get user's input from webpage
    emp_id = request.form['emp_id']

    # delete old record
    delete_sql = "DELETE FROM `employee` WHERE emp_id=%s"

    # define a cursor to fetch
    cursor = db_conn.cursor()

    try:
        # execute query
        cursor.execute(delete_sql, (emp_id))

        # commit to database, really make changes
        db_conn.commit()

        # Fetch image file from S3 #
        emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
        s3 = boto3.resource('s3')

        try:
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

            boto3.client('s3').delete_object(
                Bucket=custombucket, Key=emp_image_file_name_in_s3)

        except Exception as e:
            return str(e)

    finally:
        cursor.close()

    print("all deletion done...")

    return render_template('DelEmpOutput.html', id=emp_id)


if __name__ == '__main__':
    application.run(host='0.0.0.0', port=80, debug=True)

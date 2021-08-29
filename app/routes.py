import datetime
import sqlite3
import symbl
import time
import json
import os
from werkzeug.utils import secure_filename

from flask import render_template, redirect, url_for, abort, request, jsonify, flash
from app.forms import TestCycleForm, TestItemForm, TestItemUpdateForm, TestCycleUpdateForm

from app import app


def get_db_connection():
    conn = sqlite3.connect('C:\\Users\\ameet\\PycharmProjects\\thnkloudr\\db\\thnkloudr.db')
    conn.row_factory = sqlite3.Row
    return conn


@app.context_processor
def utility_processor():
    def convert_epoch_to_date(epoch):
        return datetime.datetime.fromtimestamp(epoch).strftime('%Y-%m-%d')

    return dict(convert_time=convert_epoch_to_date)


@app.route('/')
@app.route('/index')
def index():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("select * from TestCycle order by lastupdate DESC")
    rows = cur.fetchall()
    conn.close()
    # print(type(rows))
    # print(rows)
    return render_template('index.html', title='Home', rows=rows)


@app.route('/testcycle/<testcycleid>')
def testcycle(testcycleid):
    conn = get_db_connection()
    cur = conn.cursor()
    # query =
    cur.execute("select * from TestCycle where testcycleid=?", [testcycleid])
    row = cur.fetchone()
    # print(row)
    if row is not None:
        cur.execute("select * from Test where testcycleid=?", [testcycleid])
        test_row = cur.fetchall()
        conn.close()
        return render_template('testpage.html', title='Test Cycle', row=row, test_row=test_row)
    else:
        conn.close()
        abort(404)


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html", title='Home'), 404


@app.route('/test/<testid>')
def test(testid):
    conn = get_db_connection()
    cur = conn.cursor()
    # query =
    cur.execute("select * from Test where testid=?", [testid])
    row = cur.fetchone()
    # print(row)
    if row is not None:
        conn.close()
        return render_template('testitem.html', title='Test Item', row=row)
    else:
        conn.close()
        abort(404)


@app.route('/createtestcycle', methods=['GET', 'POST'])
def createtestcycle():
    form = TestCycleForm()
    if request.method == 'POST':
        print(form.testcyclename.data)
        #flash('Data from the form: testname {}, testdesc={}'.format(
        #    form.testcyclename.data, form.testcycledesc.data))
        # if form.testcycleimage.data:
        #    filename = secure_filename(form.testcycleimage.data.filename)
        #    print(filename)
        conn = get_db_connection()
        cur = conn.cursor()
        sqlstmt = "insert into TestCycle ('testcyclename','description','project','projectdescription','trellolink','imageurl','createdate','lastupdate') values(?,?,?,?,?,?,?,?);"
        print(sqlstmt)
        filename = secure_filename(form.testcycleimage.data.filename) if form.testcycleimage.data else None
        data_tuple = (form.testcyclename.data,
                      form.testcycledesc.data,
                      form.projectname.data,
                      form.projectdesc.data,
                      form.trellolink.data,
                      filename,
                      int(time.time()),
                      int(time.time()))
        cur.execute(sqlstmt, data_tuple)
        conn.commit()
        last_id = cur.lastrowid
        print(last_id)
        #flash('Data Successfully Inserted with ID {}'.format(last_id))
        #flash('Creating Folder for Test Cycle: {}'.format(last_id))
        target_directory = app.config['TESTCYCLE_PREFIX'] + str(last_id)
        print(target_directory)
        parent_directory = app.static_folder + '\\uploads\\'
        print(parent_directory)
        mode = 0o777
        path = os.path.join(parent_directory, target_directory)
        try:
            # os.makedirs(path, mode, exist_ok=True)
            os.mkdir(path, mode)
            #flash('Directory Created {}'.format(path))
            if filename:
                form.testcycleimage.data.save(path + '\\' + filename)
                filepath = 'uploads/' + app.config['TESTCYCLE_PREFIX'] + str(last_id) + '/' + filename
                cur.execute("update TestCycle set imageurl=?,lasupdate=? where testcycleid=?", [filepath, int(time.time()), last_id])
                conn.commit()
        except OSError as error:
            flash("Directory {} can not be created. Contact Administrator. Error message: {}".format(path, error))
            cur.execute("delete from TestCycle where testcycleid=?", [last_id])
            flash('Test Cycle ID {} removed from database'.format(last_id))
            conn.commit()
            return redirect(url_for('createtestcycle'))
        cur.close()
        conn.close()
        # f = form.testcycleimage.data
        # filename = secure_filename(f.filename)
        #flash('Redirecting to Home Page')
        #time.sleep(5)

        return redirect(url_for('index'))
    return render_template('createtestcycle.html', title='Create Test Cycle', form=form)


@app.route('/testcycle/<testcycleid>/createtestitem', methods=['GET', 'POST'])
def createtestitem(testcycleid):
    form = TestItemForm()
    if request.method == 'POST':
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("select * from TestCycle where testcycleid=?", [testcycleid])
        row = cur.fetchone()
        print(row['testcycleid'])
        if row is None:
            return redirect(url_for('index'))
        conversationid=None
        filename = secure_filename(form.testvideo.data.filename) if form.testvideo.data else None
        sqlstmt = "insert into Test ('testname','testdescription','testcycleid','lastupdate','createdate','testvideourl','conversationid') values(?,?,?,?,?,?,?);"
        data_tuple = (form.testitemname.data,
                      form.testitemdesc.data,
                      row['testcycleid'],
                      int(time.time()),
                      int(time.time()),
                      filename,
                      conversationid)
        cur.execute(sqlstmt, data_tuple)
        conn.commit()
        last_id = cur.lastrowid
        print(last_id)
        target_directory = app.config['TESTITEM_PREFIX'] + str(last_id)
        print(target_directory)
        parent_directory = app.static_folder + '\\uploads\\'
        print(parent_directory)
        mode = 0o777
        path = os.path.join(parent_directory, target_directory)
        try:
            # os.makedirs(path, mode, exist_ok=True)
            os.mkdir(path, mode)
            # flash('Directory Created {}'.format(path))
            if filename:
                form.testvideo.data.save(path + '\\' + filename)
                filepath = 'uploads/' + app.config['TESTITEM_PREFIX'] + str(last_id) + '/' + filename
                cur.execute("update Test set testvideourl=?,lastupdate=? where testid=?",
                            [filepath, int(time.time()), last_id])
                conn.commit()
        except OSError as error:
            flash("Directory {} can not be created. Contact Administrator. Error message: {}".format(path, error))
            cur.execute("delete from Test where testid=?", [last_id])
            flash('Test Item ID {} removed from database'.format(last_id))
            conn.commit()
            return redirect(url_for('createtestitem', testcycleid=str(row['testcycleid'])))
        cur.close()
        conn.close()
        return redirect(url_for('testcycle', testcycleid=row['testcycleid']))
    return render_template('createtestitem.html', title='Create Test Item', form=form)


@app.route('/test/<testid>/edittestitem', methods=['GET', 'POST'])
def edittestitem(testid):
    form = TestItemUpdateForm()
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("select * from Test where testid=?", [testid])
    row = cur.fetchone()
    if form.validate_on_submit():
        filename = secure_filename(form.testvideo.data.filename) if form.testvideo.data else None
        print(filename)
        cur.execute("update Test set testname=?, testdescription=?, lastupdate=? where testid=?",
                    [form.testitemname.data, form.testitemdesc.data, int(time.time()), row['testid']])
        conn.commit()
        if filename:
            target_directory = app.config['TESTITEM_PREFIX'] + str(row['testid'])
            print(target_directory)
            parent_directory = app.static_folder + '\\uploads\\'
            print(parent_directory)
            path = os.path.join(parent_directory, target_directory)
            form.testvideo.data.save(path + '\\' + filename)
            filepath = 'uploads/' + app.config['TESTITEM_PREFIX'] + str(row['testid']) + '/' + filename
            cur.execute("update Test set testvideourl=?,lastupdate=? where testid=?",
                        [filepath, int(time.time()), row['testid']])
            conn.commit()
        # flash('Your changes have been saved.')
        return redirect(url_for('test', testid=testid))
    elif request.method == 'GET':
        if row is None:
            return redirect('index')
        form.testitemname.data = row['testname']
        form.testitemdesc.data = row['testdescription']
        form.testvideo.data = row['testvideourl']
    cur.close()
    conn.close()
    return render_template('edit_test_item.html', title='Edit Test Item', form=form)


@app.route('/testcycle/<testcycleid>/edittestcycle', methods=['GET', 'POST'])
def edittestcycle(testcycleid):
    form = TestCycleUpdateForm()
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("select * from TestCycle where testcycleid=?", [testcycleid])
    row = cur.fetchone()
    if form.validate_on_submit():
        filename = secure_filename(form.testcycleimage.data.filename) if form.testcycleimage.data else None
        #print(filename)
        cur.execute("update TestCycle set testcyclename=?, description=?, project=?, projectdescription=?, trellolink=?, lastupdate=? where testcycleid=?",
                    [form.testcyclename.data, form.testcycledesc.data, form.projectname.data, form.projectdesc.data,form.trellolink.data, int(time.time()), row['testcycleid']])
        conn.commit()
        if filename:
            target_directory = app.config['TESTCYCLE_PREFIX'] + str(row['testcycleid'])
            print(target_directory)
            parent_directory = app.static_folder + '\\uploads\\'
            print(parent_directory)
            path = os.path.join(parent_directory, target_directory)
            form.testcycleimage.data.save(path + '\\' + filename)
            filepath = 'uploads/' + app.config['TESTCYCLE_PREFIX'] + str(row['testcycleid']) + '/' + filename
            cur.execute("update TestCycle set imageurl=?,lastupdate=? where testcycleid=?",
                        [filepath, int(time.time()), row['testcycleid']])
            conn.commit()
        # flash('Your changes have been saved.')
        return redirect(url_for('testcycle', testcycleid=testcycleid))
    elif request.method == 'GET':
        if row is None:
            return redirect('index')
        form.testcyclename.data = row['testcyclename']
        form.testcycledesc.data = row['description']
        form.projectname.data = row['project']
        form.projectdesc.data = row['projectdescription']
        form.trellolink.data = row['trellolink']
        form.testcycleimage.data = row['imageurl']
    cur.close()
    conn.close()
    return render_template('edit_test_cycle.html', title='Edit Test Cycle', form=form)




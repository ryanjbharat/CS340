from flask import Flask, render_template, request, redirect, url_for
from flask_mysqldb import MySQLdb
from config import user, password, database
## create config file with your user, password, db to replicate
## gunicorn --bind 0.0.0.0:5642 wsgi:app -D

host ='classmysql.engr.oregonstate.edu'


app = Flask(__name__)
#db = MySQLdb.connect(host, user, password, database)


@app.route('/')
def root():
    #citation: https://www.w3schools.in/python-tutorial/database-connection/
    db = MySQLdb.connect(host, user, password, database)
    cursor = db.cursor()
    cursor.execute('''SELECT 'Maybe some aggregate stats can go here...';''')
    results = cursor.fetchall()
    cursor.close()
    db.close()

    return render_template('index.html', results = str(results))

@app.route('/Orders')
def Orders():
    db = MySQLdb.connect(host, user, password, database)
    cursor = db.cursor()
    cursor.execute('SELECT * FROM OrdersHeaders;')
    results = cursor.fetchall()
    cursor.close()
    db.close()

    return render_template('Orders.html', results = results)


@app.route('/Orders/Detail/<int:orderid>')
def Detail(orderid):
    db = MySQLdb.connect(host, user, password, database)
    cursor = db.cursor()
    cursor.execute('SELECT * FROM OrdersHeaders o JOIN OrdersDetails d WHERE o.order_id = d.orderid AND o.order_id = ' + str(orderid))
    results = cursor.fetchall()
    cursor.close()
    db.close()

    return render_template('OrderDetail.html', results = results)


@app.route('/Orders/NewOrder', methods=['GET', 'POST'])
def CreateOrder():
    db = MySQLdb.connect(host, user, password, database)
    cursor = db.cursor()
    if request.method == 'POST':
        #get user input from form
        #customer_id = request.form['customer']
        #partner_id = request.form['partner']
        #cursor.execute('INSERT INTO DeliveryPartners (organization_name,delivery_method) VALUES (%s, %s);', (org_name,delivery_method))
        #commit() is needed to save the changes... otherwise the insert statement is not saved.
        #citation: https://www.w3schools.com/python/python_mysql_insert.asp
        db.commit()
        cursor.close()
        db.close()

        return redirect(url_for('Orders'))
    else:
        cursor.execute('SELECT customer_id, email FROM Customers')
        customers = cursor.fetchall()
        cursor.execute('SELECT delivery_partner_id, organization_name FROM DeliveryPartners')
        partners = cursor.fetchall()
        cursor.close()
        db.close()
        
        return render_template('NewOrder.html', customers=customers, partners=partners)


@app.route('/Snakes')
def Snakes():
    db = MySQLdb.connect(host, user, password, database)
    cursor = db.cursor()
    cursor.execute('''SELECT 'Snake Query here...';''')
    results = cursor.fetchall()
    cursor.close()
    db.close()

    return render_template('Snakes.html', results=results)


@app.route('/Breeders')
def Breeders():
    db = MySQLdb.connect(host, user, password, database)
    cursor = db.cursor()
    cursor.execute('''SELECT 'foo bar';''')
    results = cursor.fetchall()
    cursor.close()
    db.close()
    
    return render_template('Breeders.html', results=results)


@app.route('/Customers')
def Customers():
    db = MySQLdb.connect(host, user, password, database)
    cursor = db.cursor()
    cursor.execute('''SELECT 'Customers query here...';''')
    results = cursor.fetchall()
    cursor.close()
    db.close()
    
    return render_template('Customers.html', results=results)


@app.route('/DeliveryPartners')
def DeliveryPartners():
    db = MySQLdb.connect(host, user, password, database)
    cursor = db.cursor()
    cursor.execute('SELECT * FROM DeliveryPartners;')
    results = cursor.fetchall()
    cursor.close()
    db.close()
    
    return render_template('DeliveryPartners.html', results=results)


@app.route('/DeliveryPartners/DeletePartner/<int:partnerid>')
def DeleteDeliveryPartner(partnerid):
    db = MySQLdb.connect(host, user, password, database)
    cursor = db.cursor()
    cursor.execute('DELETE FROM DeliveryPartners WHERE delivery_partner_id=' + str(partnerid))
    db.commit()
    cursor.close()
    db.close()

    return redirect(url_for('DeliveryPartners'))


@app.route('/DeliveryPartners/NewPartner', methods=['GET', 'POST'])
def CreateDeliveryPartner():
    if request.method == 'POST':
        db = MySQLdb.connect(host, user, password, database)
        cursor = db.cursor()
        #get user input from form
        org_name = request.form['org']
        delivery_method = request.form['method']
        cursor.execute('INSERT INTO DeliveryPartners (organization_name,delivery_method) VALUES (%s, %s);', (org_name,delivery_method))
        #commit() is needed to save the changes... otherwise the insert statement is not saved.
        #citation: https://www.w3schools.com/python/python_mysql_insert.asp
        db.commit()
        cursor.close()
        db.close()

        return redirect(url_for('DeliveryPartners'))
    else:
        return render_template('NewPartner.html')

@app.route('/DeliveryPartners/EditPartner/<int:partnerid>', methods=['GET', 'POST'])
def EditDeliveryPartner(partnerid):
    db = MySQLdb.connect(host, user, password, database)
    cursor = db.cursor()
    if request.method == 'POST':
        #get user input from form
        org_name = request.form['org']
        delivery_method = request.form['method']
        cursor.execute('UPDATE DeliveryPartners SET organization_name = %s, delivery_method = %s WHERE delivery_partner_id = %s;', (org_name, delivery_method, partnerid))
        db.commit()
        cursor.close()
        db.close()

        return redirect(url_for('DeliveryPartners'))
    else:
        cursor.execute('SELECT * FROM DeliveryPartners WHERE delivery_partner_id = ' + str(partnerid))
        results = cursor.fetchone()
        cursor.close()
        db.close()
        return render_template('EditPartner.html', results=results)


if __name__ == "__main__": 
    #Change to debug=False for final submission  
    app.run(debug=True) e
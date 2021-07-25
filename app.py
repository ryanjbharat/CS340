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
    cursor.execute('''SELECT
                        o.order_id,
                        c.first_name,
                        c.last_name,
                        p.organization_name,
                        SUM(d.quantity) items,
                        (SUM(d.quantity) * s.price) subtotal
                        FROM
                        OrdersHeaders o
                        JOIN Customers c ON o.customer_id = c.customer_id
                        JOIN DeliveryPartners p ON o.delivery_partner_id = p.delivery_partner_id
                        JOIN OrdersDetails d ON o.order_id = d.order_id
                        JOIN Snakes s ON d.snake_id = s.snake_id
                        GROUP BY
                        o.order_id;''')
    results = cursor.fetchall()
    try:
        if results[0][0] == None:
            results = ()
    except:
        results = ()

    cursor.close()
    db.close()

    return render_template('Orders.html', results = results)


@app.route('/Orders/NewOrder', methods=['GET', 'POST'])
def CreateOrder():
    db = MySQLdb.connect(host, user, password, database)
    cursor = db.cursor()
    if request.method == 'POST':
        #get user input from form
        customer_id = request.form['customer']
        partner_id = request.form['partner']
        snake_id = request.form.getlist('snakeid')
        quantities = request.form.getlist('quantity')

        # filter ids to those that have a quantity greater than 0
        order_items = [(a, b) for a, b in zip(snake_id, quantities) if b > '0']

        cursor.execute('INSERT INTO OrdersHeaders (customer_id, delivery_partner_id) VALUES (%s, %s);', (customer_id, partner_id))

        # get the last order_id so that we can insert detail rows
        cursor.execute('SELECT MAX(order_id) FROM OrdersHeaders')
        order_id = cursor.fetchone()[0]

        for i in range(0, len(order_items), 1):
            cursor.execute('INSERT INTO OrdersDetails (order_id, snake_id, quantity) VALUES (%s, %s, %s);', (order_id, int(order_items[i][0]), int(order_items[i][1])))
        
        db.commit()
        cursor.close()
        db.close()

        return redirect(url_for('Orders'))
    else:
        cursor.execute('SELECT customer_id, email FROM Customers')
        customers = cursor.fetchall()
        cursor.execute('SELECT delivery_partner_id, organization_name FROM DeliveryPartners')
        partners = cursor.fetchall()
        cursor.execute('SELECT * FROM Snakes')
        snakes = cursor.fetchall()
        cursor.execute('SELECT CURRENT_DATE')
        date = cursor.fetchone()
        cursor.close()
        db.close()
        
        return render_template('NewOrder.html', customers=customers, partners=partners, snakes=snakes, date=date)

@app.route('/Orders/EditOrder/<int:orderid>', methods=['GET', 'POST'])
def EditOrder(orderid):
    db = MySQLdb.connect(host, user, password, database)
    cursor = db.cursor()
    if request.method == 'POST':
        #get user input from form
        snake_id = request.form.getlist('snakeid')
        quantities = request.form.getlist('quantity')
        order_items = list(zip(snake_id, quantities))
        
        for i in range(0, len(order_items), 1):
            print('updating snake_id ' + order_items[i][0] + ' order_id ' + str(orderid) + ' quantity ' + order_items[i][1])
            cursor.execute('UPDATE OrdersDetails SET quantity = %s WHERE order_id = %s AND snake_id = %s;', (int(order_items[i][1]), orderid, int(order_items[i][0])))

        db.commit()
        cursor.close()
        db.close()

        return redirect(url_for('Orders'))
    else:
        cursor.execute('''SELECT
                        o.order_id,
                        c.email,
                        p.organization_name
                        FROM
                        OrdersHeaders o
                        JOIN Customers c ON o.customer_id = c.customer_id
                        JOIN DeliveryPartners p ON o.delivery_partner_id = p.delivery_partner_id
                        WHERE o.order_id = 
                        ''' + str(orderid))
        headers = cursor.fetchone()

        cursor.execute('''SELECT
                        o.order_id,
                        s.*,
                        d.quantity
                        FROM
                        OrdersHeaders o
                        JOIN OrdersDetails d ON o.order_id = d.order_id
                        JOIN Snakes s ON d.snake_id = s.snake_id
                        WHERE
                        o.order_id=''' + str(orderid))
        details = cursor.fetchall()

        cursor.close()
        db.close()
        return render_template('EditOrder.html', headers=headers, details=details)

@app.route('/Orders/DeleteOrder/<int:orderid>')
def DeleteOrder(orderid):
    db = MySQLdb.connect(host, user, password, database)
    cursor = db.cursor()
    cursor.execute('DELETE FROM OrdersHeaders WHERE order_id =' + str(orderid))
    db.commit()
    cursor.close()
    db.close()

    return redirect(url_for('Orders'))


@app.route('/Snakes')
def Snakes():
    db = MySQLdb.connect(host, user, password, database)
    cursor = db.cursor()
    cursor.execute('SELECT * FROM Snakes')
    results = cursor.fetchall()
    cursor.close()
    db.close()

    return render_template('Snakes.html', results=results)


@app.route('/Breeders')
def Breeders():
    db = MySQLdb.connect(host, user, password, database)
    cursor = db.cursor()
    cursor.execute('SELECT * FROM Breeders')
    results = cursor.fetchall()
    cursor.close()
    db.close()
    
    return render_template('Breeders.html', results=results)

@app.route('/Breeders/DeleteBreeder/<int:breederid>')
def DeleteBreeder(breederid):
    db = MySQLdb.connect(host, user, password, database)
    cursor = db.cursor()
    cursor.execute('DELETE FROM Breeders WHERE breeder_id =' + str(breederid))
    db.commit()
    cursor.close()
    db.close()

    return redirect(url_for('Breeders'))


@app.route('/Breeders/NewBreeder', methods=['GET', 'POST'])
def CreateBreeder():
    if request.method == 'POST':
        db = MySQLdb.connect(host, user, password, database)
        cursor = db.cursor()
        #get user input from form
        breeder_name = request.form['name']
        breeder_email = request.form['email']
        breeder_phone = request.form['phone']
        cursor.execute('INSERT INTO Breeders (breeder_name, email, phone_number) VALUES (%s, %s, %s);', (breeder_name, breeder_email, breeder_phone))
        #commit() is needed to save the changes... otherwise the insert statement is not saved.
        #citation: https://www.w3schools.com/python/python_mysql_insert.asp
        db.commit()
        cursor.close()
        db.close()

        return redirect(url_for('Breeders'))
    else:
        return render_template('NewBreeder.html')

@app.route('/Breeders/EditBreeder/<int:breederid>', methods=['GET', 'POST'])
def EditBreeder(breederid):
    db = MySQLdb.connect(host, user, password, database)
    cursor = db.cursor()
    if request.method == 'POST':
        #get user input from form
        breeder_name = request.form['name']
        breeder_email = request.form['email']
        breeder_phone = request.form['phone']
        cursor.execute('UPDATE Breeders SET breeder_name = %s, email = %s, phone = %s WHERE breeder_id = %s;', (breeder_name, breeder_email, breeder_phone))
        db.commit()
        cursor.close()
        db.close()

        return redirect(url_for('Breeders'))
    else:
        cursor.execute('SELECT * FROM Breeders WHERE breeder_id = ' + str(breederid))
        results = cursor.fetchone()
        cursor.close()
        db.close()
        return render_template('EditBreeder.html', results=results)


@app.route('/Customers')
def Customers():
    db = MySQLdb.connect(host, user, password, database)
    cursor = db.cursor()
    cursor.execute('SELECT * FROM Customers')
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
    app.run(debug=True)
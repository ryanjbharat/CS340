from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQLdb
from config import user, password, database
import secrets


## create config file with your user, password, db to replicate
## gunicorn --bind 0.0.0.0:5642 wsgi:app -D

host ='classmysql.engr.oregonstate.edu'


app = Flask(__name__)
#db = MySQLdb.connect(host, user, password, database)
secret = secrets.token_urlsafe(32)
app.secret_key = secret

@app.route('/')
def root():
    #citation: https://www.w3schools.in/python-tutorial/database-connection/
    db = MySQLdb.connect(host, user, password, database)
    cursor = db.cursor()
    cursor.execute('''SELECT COUNT(DISTINCT(o.order_id)) order_count, SUM(d.quantity) snake_sum, SUM(d.quantity * s.price) order_amt 
                        FROM OrdersHeaders o
                        JOIN OrdersDetails d
                        ON o.order_id = d.order_id
                        JOIN Snakes s
                        ON d.snake_id = s.snake_id
                        WHERE o.shipped = 0;''')
    results = cursor.fetchall()
    try:
        if results[0][0] == None:
            results = ()
    except:
        results = ()
    cursor.close()
    db.close()

    return render_template('index.html', results = results)

@app.route('/Orders')
def Orders():
    db = MySQLdb.connect(host, user, password, database)
    cursor = db.cursor()
    cursor.execute('''SELECT
                        o.order_id,
                        o.order_date,
                        c.first_name,
                        c.last_name,
                        p.organization_name,
                        SUM(d.quantity) items,
                        SUM(d.quantity * s.price) subtotal,
                        CASE 
                            WHEN o.shipped = 0 THEN 'No'
                            ELSE 'Yes'
                        END
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

        # check to make sure that the order actually contains items
        if len(order_items) > 0:
            cursor.execute('INSERT INTO OrdersHeaders (order_date, customer_id, delivery_partner_id) VALUES (curdate(), %s, %s);', (customer_id, partner_id))

            # get the last order_id so that we can insert detail rows
            cursor.execute('SELECT MAX(order_id) FROM OrdersHeaders')
            order_id = cursor.fetchone()[0]

            for i in range(0, len(order_items), 1):
                cursor.execute('INSERT INTO OrdersDetails (order_id, snake_id, quantity) VALUES (%s, %s, %s);', (order_id, int(order_items[i][0]), int(order_items[i][1])))
            
            db.commit()
            cursor.close()
            db.close()
        else:
            cursor.close()
            db.close()
            flash('Yo! Your order must contain atleast 1 snake (hopefully more than 1 because we have big numbers to hit).')
            return redirect(url_for('CreateOrder'))

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
        shipped = request.form['shipped']
        snake_id = request.form.getlist('snakeid')
        quantities = request.form.getlist('quantity')
        order_items = list(zip(snake_id, quantities))

        if int(max(quantities)) == 0:
            flash('Update failed, your order must contain at least 1 snake.  If you want to delete an order, you can use the delete button below. (Please don''t, we have big numbers to hit!)')
        else:
            for i in range(0, len(order_items), 1):
                cursor.execute('UPDATE OrdersDetails SET quantity = %s WHERE order_id = %s AND snake_id = %s;', (int(order_items[i][1]), orderid, int(order_items[i][0])))

            cursor.execute('UPDATE OrdersHeaders SET shipped = %s WHERE order_id = %s;', (shipped, orderid))
            db.commit()
            
        cursor.close()
        db.close()
        return redirect(url_for('Orders'))
    else:
        cursor.execute('''SELECT
                        o.order_id,
                        c.email,
                        p.organization_name,
                        CASE
                            WHEN o.shipped = 0 THEN 'No'
                            ELSE 'Yes'
                        END
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
    cursor.execute('SELECT * FROM Snakes;')
    results = cursor.fetchall()
    cursor.close()
    db.close()

    return render_template('Snakes.html', results=results)

@app.route('/Snakes/NewSnake', methods=['GET', 'POST'])
def CreateSnake():
    if request.method == 'POST':
        db = MySQLdb.connect(host, user, password, database)
        cursor = db.cursor()
        #get user input from form
        snake_name = request.form['species']
        snake_weight = request.form['weight']
        snake_length = request.form['length']
        snake_color = request.form['color']
        snake_price = request.form['price']
        cursor.execute('INSERT INTO Snakes (species,weight_lb,length,color,price) VALUES (%s, %s, %s, %s, %s);', (snake_name,snake_weight,snake_length,snake_color,snake_price))
        #commit() is needed to save the changes... otherwise the insert statement is not saved.
        #citation: https://www.w3schools.com/python/python_mysql_insert.asp
        db.commit()
        cursor.close()
        db.close()

        return redirect(url_for('Snakes'))
    else:
        return render_template('NewSnake.html')

@app.route('/Snakes/EditSnake/<int:snakeid>', methods=['GET', 'POST'])
def EditSnake(snakeid):
    db = MySQLdb.connect(host, user, password, database)
    cursor = db.cursor()
    if request.method == 'POST':
        #get user input from form
        snake_name = request.form['species']
        snake_weight = request.form['weight']
        snake_length = request.form['length']
        snake_color = request.form['color']
        snake_price = request.form['price']
        cursor.execute('UPDATE Snakes SET species = %s, weight_lb = %s, length = %s, color = %s, price = %s WHERE snake_id = %s;', (snake_name,snake_weight,snake_length,snake_color,snake_price, snakeid))
        db.commit()
        cursor.close()
        db.close()

        return redirect(url_for('Snakes'))
    else:
        cursor.execute('SELECT * FROM Snakes WHERE snake_id = ' + str(snakeid))
        results = cursor.fetchone()
        cursor.close()
        db.close()
        return render_template('EditSnake.html', results=results)

@app.route('/SnakesBreeders', methods=['GET','POST'])
def SnakesBreeders():
    db = MySQLdb.connect(host, user, password, database)
    cursor = db.cursor()
    if request.method == 'POST':
        search_query = request.form['snake']
        #add wildcard symbol as suffix/prefix
        search_query = '%' + search_query + '%'
        cursor.execute('SELECT s.snake_id, s.species, s.price, b.breeder_id, b.breeder_name, b.email from Snakes s join SnakesBreeders sb on s.snake_id = sb.snake_id join Breeders b on sb.breeder_id = b.breeder_id WHERE s.species LIKE %s or b.breeder_name like %s;', (search_query, search_query))
        results = cursor.fetchall()
        cursor.close()
        db.close()

        return render_template('SnakesBreeders.html', results=results)
    else:
        cursor.execute('SELECT s.snake_id, s.species, s.price, b.breeder_id, b.breeder_name, b.email from Snakes s join SnakesBreeders sb on s.snake_id = sb.snake_id join Breeders b on sb.breeder_id = b.breeder_id ORDER BY s.species;')
        results = cursor.fetchall()
        cursor.close()
        db.close()
        
        return render_template('SnakesBreeders.html', results=results)

@app.route('/SnakesBreeders/NewSnakesBreeders', methods=['GET','POST'])
def NewSnakesBreeders():
    db = MySQLdb.connect(host, user, password, database)
    cursor = db.cursor()
    if request.method == 'POST':
        snake_id = request.form['species']
        breeder_id = request.form['breeder']
        cursor.execute('INSERT IGNORE INTO SnakesBreeders (snake_id, breeder_id) VALUES (%s, %s);', (snake_id, breeder_id))
        db.commit()
        cursor.close()
        db.close()

        return redirect(url_for('SnakesBreeders'))

    else:
        cursor.execute('SELECT snake_id, species, color, price FROM Snakes')
        selected_snakes = cursor.fetchall()
        cursor.execute('SELECT breeder_id, breeder_name FROM Breeders')
        selected_breeders = cursor.fetchall()
        cursor.close()
        db.close()

        return render_template('NewSnakesBreeders.html', selected_snakes=selected_snakes, selected_breeders=selected_breeders)

@app.route('/SnakesBreeders/DeleteSnakesBreeders/<int:snakeid>/<int:breederid>')
def DeleteSnakesBreeders(snakeid, breederid):
    db = MySQLdb.connect(host, user, password, database)
    cursor = db.cursor()
    cursor.execute('DELETE FROM SnakesBreeders WHERE snake_id =' + str(snakeid) +' AND breeder_id =' + str(breederid))
    db.commit()
    cursor.close()
    db.close()

    return redirect(url_for('SnakesBreeders'))

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
    try:
        cursor.execute('DELETE FROM Breeders WHERE breeder_id =' + str(breederid))
        db.commit()
        cursor.close()
        db.close()
    except:
        cursor.close()
        db.close()
        flash("Yo! This Breeder is currently associated with some snakes so it cannot be deleted.")

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
        try:
            cursor.execute('INSERT INTO Breeders (breeder_name, email, phone_number) VALUES (%s, %s, %s);', (breeder_name, breeder_email, breeder_phone))
            #commit() is needed to save the changes... otherwise the insert statement is not saved.
            #citation: https://www.w3schools.com/python/python_mysql_insert.asp
            db.commit()
            cursor.close()
            db.close()
        except:
            cursor.close()
            db.close()
            flash('This breeder email already exists!')
            return redirect(url_for('CreateBreeder'))

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
        try:
            cursor.execute('UPDATE Breeders SET breeder_name = %s, email = %s, phone_number = %s WHERE breeder_id = %s;', (breeder_name, breeder_email, breeder_phone, breederid))
            db.commit()
            cursor.close()
            db.close()
        except:
            cursor.close()
            db.close()
            flash('Update failed, this email address already exists.')

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


@app.route('/Customers/NewCustomer', methods=['GET', 'POST'])
def CreateCustomer():
    if request.method == 'POST':
        db = MySQLdb.connect(host, user, password, database)
        cursor = db.cursor()
        #get user input from form
        customer_fname = request.form['fname']
        customer_lname = request.form['lname']
        customer_address = request.form['address']
        customer_city = request.form['city']
        customer_state = request.form['state']
        customer_postal = request.form['postal']
        customer_country = request.form['country']
        customer_email = request.form['email']
        try:
            cursor.execute('INSERT INTO Customers (first_name, last_name, address, city, state, postal, country, email) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);', (customer_fname,customer_lname,customer_address, customer_city, customer_state, customer_postal, customer_country,customer_email))
            #commit() is needed to save the changes... otherwise the insert statement is not saved.
            #citation: https://www.w3schools.com/python/python_mysql_insert.asp
            db.commit()
            cursor.close()
            db.close()
        except:
            cursor.close()
            db.close()
            flash('This customer email already exists!')
            return redirect(url_for('CreateCustomer'))

        return redirect(url_for('Customers'))
    else:
        return render_template('NewCustomer.html')

@app.route('/Customers/EditCustomer/<int:customerid>', methods=['GET', 'POST'])
def EditCustomer(customerid):
    db = MySQLdb.connect(host, user, password, database)
    cursor = db.cursor()
    if request.method == 'POST':
        #get user input from form
        customer_fname = request.form['fname']
        customer_lname = request.form['lname']
        customer_address = request.form['address']
        customer_city = request.form['city']
        customer_state = request.form['state']
        customer_postal = request.form['postal']
        customer_country = request.form['country']
        customer_email = request.form['email']
        try:
            cursor.execute('UPDATE Customers SET first_name = %s, last_name = %s, address = %s, city = %s, state = %s, postal = %s, country = %s, email = %s WHERE customer_id = %s;', (customer_fname, customer_lname, customer_address, customer_city, customer_state, customer_postal, customer_country, customer_email, customerid))
            db.commit()
            cursor.close()
            db.close()
        except:
            cursor.close()
            db.close()
            flash('Update failed, this email address already exists.')

        return redirect(url_for('Customers'))
    else:
        cursor.execute('SELECT * FROM Customers WHERE customer_id = ' + str(customerid))
        results = cursor.fetchone()
        cursor.close()
        db.close()
        return render_template('EditCustomer.html', results=results)


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
    try:
        cursor.execute('DELETE FROM DeliveryPartners WHERE delivery_partner_id=' + str(partnerid))
        db.commit()
        cursor.close()
        db.close()
    except:
        cursor.close()
        db.close()
        flash("Yo! This Delivery Partner is currently associated with an order so it cannot be deleted.")

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
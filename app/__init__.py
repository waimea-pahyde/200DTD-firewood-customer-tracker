#===========================================================
# Firewood Business Tracker
# Polly Hyde
#-----------------------------------------------------------
# This is a website to help keep track of firewood records. 
#===========================================================

from flask import Flask, render_template, request, flash, redirect
import html

from app.helpers.session import init_session
from app.helpers.db      import connect_db
from app.helpers.errors  import init_error, not_found_error
from app.helpers.logging import init_logging
from app.helpers.time    import init_datetime, utc_timestamp, utc_timestamp_now


# Create the app
app = Flask(__name__)

# Configure app
init_session(app)   # Setup a session for messages, etc.
init_logging(app)   # Log requests
init_error(app)     # Handle errors and exceptions
init_datetime(app)  # Handle UTC dates in timestamps

# ============================================
# Home page route
# ============================================
@app.get("/")
def index():
    return render_template("pages/home.jinja")
# ============================================

# ============================================
# customer lists - show all customers
# ============================================
@app.get("/customers/")
def customers():
    with connect_db() as client:
        # Get all the customers name and ID from the DB. 
        sql = """
            SELECT 
                name, 
                id
            FROM customers
            ORDER BY name ASC
        """
        params = []
        result = client.execute(sql, params)
        customers = result.rows

        # Getting a list of all the orders, to then match up to the customers. 
        sql = """
            SELECT 
                id, 
                date,
                cid
            FROM orders
            ORDER BY date DESC
        """
        params = []
        result = client.execute(sql, params)
        orders = result.rows
        # And then display them
        return render_template("pages/customers.jinja", 
                                                customers=customers,
                                                orders=orders,)
# ============================================                                            

# ============================================
# Deletes a customer. 
# ============================================
@app.get("/delete/<int:id>")
def delete_a_customer(id):
    with connect_db() as client:
        # Delete the thing from the DB
        sql = "DELETE FROM customers WHERE id=?"
        params = [id]
        client.execute(sql, params)

        # Go back to the home page
        flash("Customer deleted", "success")
        return redirect("/customers")
# ============================================

# ============================================
# Shows one single order.
# ============================================
@app.get("/order/<int:id>")
def show_one_order(id):
    with connect_db() as client:
        # Get the details of everything in the contais table where the Order ID (oid) matches the OID of the one that was clicked. 
        sql = "SELECT * FROM contains WHERE oid=?"
        params = [id]
        result = client.execute(sql, params)
        if result.rows:
            contains = result.rows
        else:
            contains = None #When testing, orders were created that contained nothing. This is a failsafe. 


        # Get all of the woodsto compare with the ID's gotten from the contains table, to then display the name of the wood rather than the ID. 
        sql = "SELECT * FROM wood"
        params = []
        result = client.execute(sql, params)
        wood = result.rows


        
        # Getting the ID for the title of the page.  
        
        sql = "SELECT * FROM orders WHERE id=?"
        params = [id]
        result = client.execute(sql, params)
        order = result.rows[0]
      

        # Displaying the whole page 
        return render_template("pages/order.jinja", order=order, wood=wood, contains=contains)
# ============================================

# ============================================
# Shows one customer
# ============================================
@app.get("/customer/<int:id>")
def show_one_customer(id):
    with connect_db() as client:
        
        # Selecting the customer with the same ID as the customer clicked
        sql = "SELECT * FROM customers WHERE id=?"
        params = [id]
        result = client.execute(sql, params)
        # Did we get a result?
        if result.rows:
            # yes, so show it on the page
            customer = result.rows[0]
        else:
            # No, so show error
            return not_found_error()

        #Selecting all orders where the Customer ID (cid) matches up with the customer ID clicked on. 
        sql = """
            SELECT *
            FROM orders 
            WHERE cid=?
            ORDER BY date DESC
        """
        params = [id]
        result = client.execute(sql, params)
        
        if result.rows:
            orders = result.rows
        else:
            orders=None #In case the customer has no orders. 
            
        
        return render_template("pages/customer.jinja" , customer=customer, orders=orders)
# ============================================

# ============================================
# Search function on the Customer page to get a customer
# ============================================
@app.post("/search")
def search():
    # Get the data from the form
    customers  = request.form.get("search")

    # Sanitise the text inputs
    customers = html.escape(customers)

    with connect_db() as client:
        # Add the thing to the DB
        sql = "SELECT * FROM customers WHERE name LIKE ?"
        params = [f"%{customers}%"]
        result = client.execute(sql, params)
        results = result.rows

        sql = """
            SELECT 
                name, 
                id
            FROM customers
            ORDER BY name ASC
        """
        params = []
        result = client.execute(sql, params)
        customers = result.rows

        sql = """
            SELECT 
                id, 
                date,
                cid
            FROM orders
            ORDER BY date DESC
        """
        params = []
        result = client.execute(sql, params)
        orders = result.rows

        sql = """
            SELECT 
                type, 
                SUM(contains.qty) AS total
            FROM wood
            JOIN contains ON contains.wid = wood.id
            GROUP BY wood.type
            ORDER BY type ASC
        """
        params = []
        result = client.execute(sql, params)
        woods = result.rows

        

        # And show them on the page
        return render_template("pages/customers.jinja", 
                                                customers=customers,
                                                orders=orders,
                                                woods=woods,
                                                results=results)
# ============================================

# ============================================
# The actual wood form page. 
# ============================================
@app.get("/wood-add")
def get_the_order():
    with connect_db() as client:
        sql = """
            SELECT 
                id,
                type
            FROM wood
            ORDER BY type ASC
        """
        params = []
        result = client.execute(sql, params)
        woods = result.rows

        return render_template("pages/wood-add.jinja", woods=woods)
# ============================================

# ============================================
# The form mechanics, adding this to the database. 
# ============================================
@app.post("/add")
def add_an_order():
    # Get the data from the form
    name  = request.form.get("name")
    date = request.form.get("date")
    email = request.form.get("email").lower()
    phone = request.form.get("phone")
    address = request.form.get("address")
    
    # Sanitise the text inputs
    name = html.escape(name)
    email = html.escape(email)
    phone = html.escape(phone)
    address = html.escape(address)

    with connect_db() as client:
        # Determine if customer exists 
        sql = "SELECT id FROM customers WHERE email=?"
        params = [email]
        result = client.execute(sql, params)
        customer_id = -1

        if not result.rows:
            #Create customer
            sql = "INSERT INTO customers (name, email, phone, address) VALUES (?,?,?,?)"
            params = [name,email,phone,address]
            result = client.execute(sql, params)
            customer_id = result.last_insert_rowid
        else:
            customer_id = result.rows[0]["id"]
        
        # Create an order and associate with customer id
        sql = "INSERT INTO orders (cid, date) VALUES (?,?)"
        params = [customer_id,date]
        result = client.execute(sql, params)
        order_id = result.last_insert_rowid

        # Get the ids of all of our woods
        sql= "SELECT id FROM wood"
        params = []
        result = client.execute(sql, params)
        woods = result.rows
    
        # Loop thru each wood
        for wood in woods: 
            qty = request.form.get("wood-"+str(wood["id"]))
            sql = "INSERT INTO contains (oid, wid , qty) VALUES (? , ?, ?)"
            params = [order_id, wood["id"], qty]
            client.execute(sql, params)
            
        # Go back to the home page
        flash(f"{name} added.", "success")
        return redirect("/")
# ============================================

# ============================================
#Wood page, shows all woods, plus amount sold. 
# ============================================
@app.get("/woods/")
def show_all_wood():
    with connect_db() as client:
        # Get all the things from the DB
        sql = "SELECT * FROM wood"
        params = []
        result = client.execute(sql, params)
        wood = result.rows

        sql = "SELECT name, id FROM customers"
        params = []
        result = client.execute(sql, params)
        customers = result.rows

        sql = "SELECT cid FROM orders"
        params = []
        result = client.execute(sql, params)
        ids= result.rows

        sql = """
            SELECT 
                type, 
                SUM(contains.qty) AS total
            FROM wood
            JOIN contains ON contains.wid = wood.id
            GROUP BY wood.type
            ORDER BY type ASC
        """
        params = []
        result = client.execute(sql, params)
        ChartWoods = result.rows

        # And show them on the page
        return render_template("pages/woods.jinja", woods=wood, customers=customers, ids=ids, ChartWoods=ChartWoods)
# ============================================
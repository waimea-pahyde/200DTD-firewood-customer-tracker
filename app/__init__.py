#===========================================================
# YOUR PROJECT TITLE HERE
# YOUR NAME HERE
#-----------------------------------------------------------
# BRIEF DESCRIPTION OF YOUR PROJECT HERE
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


#-----------------------------------------------------------
# Home page route
#-----------------------------------------------------------
@app.get("/")
def index():
    return render_template("pages/home.jinja")


#-----------------------------------------------------------
# About page route
#-----------------------------------------------------------
@app.get("/about/")
def about():
    return render_template("pages/about.jinja")


#-----------------------------------------------------------
# Things page route - Show all the things, and new thing form
#-----------------------------------------------------------
@app.get("/things/")
def show_all_things():
    with connect_db() as client:
        # Get all the things from the DB
        sql = "SELECT id, name FROM things ORDER BY name ASC"
        params = []
        result = client.execute(sql, params)
        things = result.rows

        # And show them on the page
        return render_template("pages/things.jinja", things=things)

#----------------------------------------------------------------
# customer lists - show all customers
#------------------------------------------------------------------
@app.get("/customers/")
def customers():
    with connect_db() as client:
        # Get all the things from the DB
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
                                                woods=woods)

    





#-----------------------------------------------------------
# Thing page route - Show details of a single thing
#-----------------------------------------------------------
@app.get("/thing/<int:id>")
def show_one_thing(id):
    with connect_db() as client:
        # Get the thing details from the DB
        sql = "SELECT * FROM customers WHERE id=?"
        params = [id]
        result = client.execute(sql, params)

        # Did we get a result?
        if result.rows:
            # yes, so show it on the page
            thing = result.rows[0]
            return render_template("pages/thing.jinja", thing=thing)

        else:
            # No, so show error
            return not_found_error()


#-----------------------------------------------------------
# Route for adding a thing, using data posted from a form
#-----------------------------------------------------------
@app.post("/addExample")
def add_a_thing():
    # Get the data from the form
    name  = request.form.get("name")
    price = request.form.get("price")

    # Sanitise the text inputs
    name = html.escape(name)

    with connect_db() as client:
        # Add the thing to the DB
        sql = "INSERT INTO things (name, price) VALUES (?, ?)"
        params = [name, price]
        client.execute(sql, params)

        # Go back to the home page
        flash(f"Thing '{name}' added", "success")
        return redirect("/things")


#-----------------------------------------------------------
# Route for deleting a thing, Id given in the route
#-----------------------------------------------------------
@app.get("/delete/<int:id>")
def delete_a_thing(id):
    with connect_db() as client:
        # Delete the thing from the DB
        sql = "DELETE FROM things WHERE id=?"
        params = [id]
        client.execute(sql, params)

        # Go back to the home page
        flash("Thing deleted", "success")
        return redirect("/things")

#----------------------------------------------------------------
#Orders route
#----------------------------------------------------------------
@app.get("/order/<int:id>")
def show_one_order(id):
    with connect_db() as client:
        # Get the thing details from the DB
        sql = "SELECT * FROM contains, orders WHERE contains.oid=?"
        params = [id]
        result = client.execute(sql, params)
        # Did we get a result?
        if result.rows:
            # yes, so show it on the page
            order = result.rows[0]

            
        sql = "SELECT * FROM wood"
        params = []
        result = client.execute(sql, params)
        # Did we get a result?
        if result.rows:
            # yes, so show it on the page
            wood = result.rows[0]
            
            return render_template("pages/order.jinja", order=order , wood=wood)

        else:
            # No, so show error
            return not_found_error()
        
#----------------------
# Customer route
#----------------------


@app.get("/customer/<int:id>")
def show_one_customer(id):
    with connect_db() as client:
        # Get the thing details from the DB
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
            return not_found_error()
        
        return render_template("pages/customer.jinja" , customer=customer, orders=orders)

        #==============================


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
    



@app.get("/wood-add")
def get_the_order():
    return render_template("pages/wood-add.jinja")


#adding things
@app.post("/add")
def add_an_order():
    # Get the data from the form
    name  = request.form.get("name")
    date = request.form.get("date")

    # Sanitise the text inputs
    name = html.escape(name)

    with connect_db() as client:
        # Add the thing to the DB
        sql = "INSERT INTO things, orders (name, date) VALUES (?, ?)"
        params = [name, price]
        client.execute(sql, params)

        # Go back to the home page
        flash(f"Thing '{name}' added", "success")
        return redirect("/things")
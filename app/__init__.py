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
# originally had the chart thingy so im scared to touch it
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
    #stolen from copelf
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
# mr copelys dekleteing a customer thing, which I'm, yet to 
# impliment anywhere bc I'm scared. 
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
#Shows one order, like when you click into a customer, then a date
# then a order, and like this is where you go
# also has a if there's none woods in the order thingy
#because when I was trying to make the form 
#I lmade multiple broken orders
#so like thats never actually gonna have an implimentation
#But like. It's helpful ig. 
#TODO i need to get like the quanittiy stuff working - nvm i did that don't worry about it
#----------------------------------------------------------------
@app.get("/order/<int:id>")
def show_one_order(id):
    with connect_db() as client:
        # Get the thing details from the DB
        sql = "SELECT * FROM contains WHERE oid=?"
        params = [id]
        result = client.execute(sql, params)
        if result.rows:
            contains = result.rows
        else:
            contains = None


        # get the wood, because we need to compare the ID of the woods
        sql = "SELECT * FROM wood"
        params = []
        result = client.execute(sql, params)
        wood = result.rows


        #=============
        # Just getting the order id for decorative stuff, like the title. Don't worry about it.  
        
        sql = "SELECT * FROM orders WHERE id=?"
        params = [id]
        result = client.execute(sql, params)
        order = result.rows[0]
      

        # =============

        return render_template("pages/order.jinja", order=order, wood=wood, contains=contains)





#----------------------
# Customer route to show one (1) customer
# Contains a helpful if none thingy
#i cried making it
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
            orders=None
            
        
        return render_template("pages/customer.jinja" , customer=customer, orders=orders)

        #==============================


#=============================================================
# The frickass search function. It works. Don't touch it it's fine.
#=============================================================
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
    

#================================
#I don't actually know what this does, 
#where it redirects to,
#I don't remember making it
#but I'm scared to delete it.


# this is fine
    
#=================================
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


#==================================
# THE BIT THAT ADDS A CUSTOMER
#   DO NOT TOUCH THIS IT WORKS
#================================== 
@app.post("/add")
def add_an_order():
    # Get the data from the form
    name  = request.form.get("name")
    date = request.form.get("date")
    email = request.form.get("email").lower()
    phone = request.form.get("phone")
    address = request.form.get("address")
    
    One = request.form.get("1")
    
    # Sanitise the text inputs
    name = html.escape(name)

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

        # we have a cust id, so it is now safe to move on 
        print(customer_id)
        

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
            
            # INSERT into the contains table with wood id and qty
        

        # Go back to the home page TODO better state feedback
        flash(f"{name} added.", "success")
        return redirect("/")
    
    # =============

    #-----------------------------------------------------------



#Woods data, theres some weird stuff going on with this and the wood page
#but this one has like. The chart. So we're going with him.
#If I figure out what the heck I was trying to do later, change this ramble.
#-----------------------------------------------------------
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




#=================================
# shwwo one wood type
#=================================

@app.get("/wood/wood/<int:id>")
def show_one_wood(id):
    with connect_db() as client:
        # Get the thing details from the DB
        sql = "SELECT * FROM wood WHERE id=?"
        params = [id]
        result = client.execute(sql, params)

        # Did we get a result?
        if result.rows:
            # yes, so show it on the page
            wood = result.rows[0]
        else:
            # No, so show error
            return not_found_error()

        sql = """
            SELECT *
            FROM contains,
            WHERE wid=?
            
        """
        params = [id]
        result = client.execute(sql, params)
        
        if result.rows:
            orders = result.rows
            
        else:
            return not_found_error()
        

       
        
        return render_template("pages/wood.jinja" ,  orders=orders, wood=wood)
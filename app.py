from flask import Flask, render_template, request, redirect, url_for
from warehouse_manager import WarehouseManager

# This file takes the actions from the running webapp and translates them to
# method calls to the WarehouseManager object. Then, will pass all of the
# current WarehouseManager state information to the html script to update the
# webapp.

app = Flask(__name__)   #initializes the webapp
wm = WarehouseManager() # Pass a different path here as a string to
                        # load or create a new, empty database.

# Main page, passes the warehouse data to the html code.
@app.route("/")
def home(): 
    return render_template("index.html",
            warehouse_data = wm.get_warehouse_data())

# Called after the Add Warehouse button is clicked. Passes entered information
# to the warehouse manager.
@app.route("/add_warehouse", methods = ["POST"])
def add_warehouse():
    output = request.form.to_dict()
    print(output)
    name = output["warehouse_name"]
    copy_items = "copy_items" in output
    wm.add_warehouse(name, copy_items)
    return redirect(url_for("home"))

# Called after a new warehouse is selected. Passes selected warehouse name to
# the warehouse manager.
@app.route("/select_warehouse", methods = ["POST"])
def select_warehouse():
    warehouse_name = request.form.to_dict()['submit_button']
    wm.select_warehouse(warehouse_name)
    return redirect(url_for("home"))

# Called when the "Delete Warehouse" button is clicked, calling delete
# warehouse in the warehouse manager.
@app.route("/delete_warehouse", methods = ["POST"])
def delete_warehouse():
    wm.delete_warehouse()
    return redirect(url_for("home"))

# Called after the Add Item button is clicked. Passes entered information to
# the warehouse manager.
@app.route("/add_item", methods = ["POST"])
def add_item():
    output = request.form.to_dict()
    name = output["item_name"]
    quantity = output["quantity"]
    other = output["other"]
    wm.add_item(name, quantity, other)
    return redirect(url_for("home"))

# Called when one of the edit quantity buttons (-10,-1,+1,+10) are clicked.
# Tell the warehouse manager what item quantity to modify.
@app.route("/edit_quantity", methods = ["POST"])
def edit_quantity():
    output = request.form.to_dict()
    id, count = output["submit_button"].split(',')
    wm.edit_quantity(id, count)
    return redirect(url_for("home"))

# Called when an "Edit" item button is pressed. Requests the warehouse manager
# to include information on that item so it can be edited by the user in the
# next state.
@app.route("/edit_item", methods = ["POST"])
def edit_item():
    output = request.form.to_dict()
    id = output["submit_button"]
    wm.edit_item(id)
    return redirect(url_for("home"))

# Called when an item information edit is saved. Passes all the new item
# information to the warehouse manager to update the item.
@app.route("/save_edit", methods = ["POST"])
def save_edit():
    output = request.form.to_dict()
    item_name = output["item_name"]
    id = output["id"]
    quantity = output["quantity"]
    other = output["other"]
    old_id = output["old_id"]
    wm.save_edit(item_name, id, quantity, other, old_id)
    return redirect(url_for("home"))

# Called when an item's "Delete" button is pressed. Tells the warehouse
# manager to delete the desired item.
@app.route("/delete_item", methods = ["POST"])
def delete_item():
    output = request.form.to_dict()
    id = output["submit_button"]
    wm.delete_item(id)
    return redirect(url_for("home"))

#----------- Start app -----------
if __name__ == "__main__":
    app.run(debug=True)
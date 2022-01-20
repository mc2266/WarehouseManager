import sqlite3
from sqlite3 import Error


# The WarehouseManager class manages a SQL database that can store inventory 
# item information for on multiple warehouses. Warehouses can be created or
# deleted and can each store a unique set of items. For every warehouse items
# can individually be created, deleted or modified.
#
# This class functions as a state machine. That is, a method function depends
# on both the parameters and the state of the class. The most important state
# for the WarehouseManager is the current_warehouse as it affects all other
# other methods and is the only persistent state. Calling get_warehouse_data()
# returns a dictionary about the current warehouse and state of the class. 
# Calling this also clears all the temporary state data.
# Temporary states include:
# Error state -- When an invalid parameter is passed to a method the
#                "error_message" key contains info on this error.
# Edit state  -- Information on a requested item is available at the
#                "edit_item_data" key in the dictionary.
class WarehouseManager:
    DEFAULT_DATABASE_PATH = "default_database"
    
    # Initializes the database connecting to the SQL database file at the 
    # given path. If no file exists at the given path then a new database will
    # be created. If no path is specificed then the "default_database" will be
    # read or created if it does not exist.
    def __init__(self, path=DEFAULT_DATABASE_PATH):
        self.connection = None
        try:
            self.connection = sqlite3.connect(path, check_same_thread=False)
        except Error as e:
            print(e)
        self.current_warehouse = None
        self.warehouses = [x[0] for x  in self.__execute_read_query(
                "SELECT name FROM sqlite_master WHERE type='table';")]
        self.warehouses.remove("sqlite_sequence")
        self.error_message = None
        self.edit_item_data = None

    # Helper method for executing a given SQL query and printing any SQLite
    # errors to the console.
    def __execute_query(self, query):
        cursor = self.connection.cursor()
        try:
            cursor.execute(query)
            self.connection.commit()
        except Error as e:
            print(e)

    # Helper method for executing a given SQL query then fetching and
    # and returning the result of that query. Will print any SQLite errors
    # to the console.
    def __execute_read_query(self, query):
        cursor = self.connection.cursor()
        result = None
        try:
            cursor.execute(query)
            result = cursor.fetchall()
            return result
        except Error as e:
            print(e)

    # Returns all related information on the current state of the database in
    # a dictionary. Information in dictionary includes:
    #       *key*                               *data*
    # "current_warehouse" -- String of currently active warehouse name.
    # "warehouses"        -- List of strings for all warehouse names in the
    #                        database.
    # "items"             -- List of tuples of infomation on each item in the
    #                        current warehouse stored as follows:
    #                        (Item Name, Item ID, Quantity, Other Information)
    # "edit_item_data"    -- Contains dictionary on for a requested item 
    #                        (details available at method comment). Will be
    #                        deleted after "get_warehouse_data()" is called.
    #                        When no item data was requested value is None.
    # "error_message"     -- Constains a string of an the most recent error.
    #                        If no errors have occurred then value is None.
    # "edit_item_data" and "error_message" are cleared (set to None) after each
    # "call to get_warehouse_data()"
    def get_warehouse_data(self):
        warehouse_data = \
        {
            "current_warehouse" : self.current_warehouse,
            "warehouses" : self.warehouses,
            "items" : self.__get_items(),
            "edit_item_data" : self.edit_item_data,
            "error_message" : self.error_message
        }
        self.edit_item_data = None
        self.error_message = None
        

        return warehouse_data

    #--------------------------- Warehouse Methods ---------------------------#

    # Creates a new warehouse in the database with the given name. If
    # warehouse_name contains any spaces then they will be replaced by "_".
    # If copy_items is True then item types (everything but quantity) will be
    # duplicated from the current_warehouse.
    # When copy_items is false then an empty warehouse is created.
    def add_warehouse(self, warehouse_name, copy_items):
        warehouse_name = warehouse_name.replace(" ", "_")
        if warehouse_name in self.warehouses:
            self.error_message = "Warehouse Name must be unique"
            return


        table_query = f"""
            CREATE TABLE {warehouse_name} (
            name TEXT,
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quantity INTEGER,
            other TEXT);
            """
        self.__execute_query(table_query)

        # Copy items from a already created warehouse
        if copy_items and self.current_warehouse is not None:
            table_query = f"""
            INSERT INTO {warehouse_name}
            SELECT *
            FROM {self.current_warehouse}
            """
            self.__execute_query(table_query)
            table_query = f"""
            UPDATE {warehouse_name}
            SET quantity = 0
            """
            self.__execute_query(table_query)

        self.current_warehouse = warehouse_name
        self.warehouses.append(warehouse_name)

    # Changes the active warehouse to warehouse_name. If warehouse_name is not
    # in the database then an error state occurs and the current_warehouse is
    # unchanged.
    def select_warehouse(self, warehouse_name):
        if warehouse_name not in self.warehouses:
            self.error_message = f"{warehouse_name} is not a warehouse"
            return
        if warehouse_name == self.current_warehouse:
            return
        
        self.current_warehouse = warehouse_name
        print(f"Switching to {warehouse_name}")

    # Deletes the currently active warehouse from the database including its'
    # inventory. After successful deletion current_warehouse is None.
    def delete_warehouse(self):
        if self.current_warehouse == None:
            return

        self.warehouses.remove(self.current_warehouse)
        self.__execute_query(f"DROP TABLE {self.current_warehouse}")
        self.current_warehouse = None

    #----------------------------- Item Methods -----------------------------#

    # Adds an item to the current_warehouse with the given name, quantity and
    # other optional extra information. Item IDs are automatically assigned
    # but can be edited later. If no warehouse is selected an error state 
    # occurs and no item is added. If quantity is not an integer an error 
    # state occurs and no item is added.
    def add_item(self, name, quantity, other=""):
        if self.current_warehouse == None:
            self.error_message = "Add or select a warehouse to add an item"
            return
        try:
            quantity = int(quantity)
        except:
            self.error_message = "'Quantity' must be an interger"
            return
        
        table_query = f"""
        INSERT INTO {self.current_warehouse}
        (name, quantity, other)
        VALUES ('{name}', {quantity}, '{other}')
        """
        self.__execute_query(table_query)

    # Helper method for get_warehouse_data() returns the list of tuples for
    # each item in the current warehouse. A tuple for each item will contain
    # the following information in order. 
    #   (Item Name, Item ID, Quantity, Other Information)
    # Item name and Other information are both Strings
    def __get_items(self):
        if self.current_warehouse == None:
            return None
        table_query = f"SELECT * FROM {self.current_warehouse}"
        return self.__execute_read_query(table_query)

    # Modifies the item with the given id's quantity by the given quantity.
    # For example if item 5 has a quantity of 10 then after calling 
    # edit_quantity(5, -3) item 5's quantity will be 7. If id or quantity are
    # not integers or strings of integers an error state occurs and no changes
    # are made. If the ID does not exist in the current warehouse then an
    # error state occurs and no changes are made.
    def edit_quantity(self, id, quantity):
        try:
            id, quantity = int(id), int(quantity)
        except:
            self.error_message = "'Quantity' and ID must be an intergers."
            return
        if not self.id_exists(id):
            self.error_message = "Item ID does not exist!"
            return
        
        table_query = f"""
        UPDATE {self.current_warehouse}
        SET quantity = quantity+{quantity}
        WHERE id = {id}
        """
        self.__execute_query(table_query)

    # Method that adds the item data for the given Item Id to the state
    # information dictionary under "edit_item_data". At this location in the
    # dictionary there will be another dictionary that constais the following
    # information:
    #    *key*          *data*
    # "name"     -- Item Name (string)
    # "id"       -- Item ID (integer)      
    # "quantity" -- Item Quantity (integer)
    # "other"    -- Other infomation (string)
    # this information is intended to be used to make the modifications to for
    # the item where said modifications can be saved used the save_edit() 
    # function.
    def edit_item(self, id):
        if not self.id_exists(id):
            self.error_message = "Item ID does not exist"
            return

        data = self.__execute_read_query(
                f"SELECT * FROM {self.current_warehouse} WHERE id = {id}")[0]
        
        self.edit_item_data = {
            "name" : data[0],
            "id" : data[1],
            "quantity" : data[2],
            "other" : data[3]
        }
    
    # Saves the the given item information (name, id, quantity, and other 
    # info) to the item with the id "old_id." quantity, id, and old_id all
    # must be integers. If id != old_id then id must be unique to the current
    # warehouse. If integer requirements or id uniqueness is not met then an 
    # error state occurs and no changes are made.
    def save_edit(self, name, id, quantity, other, old_id):
        try:
            quantity = int(quantity)
        except:
            self.error_message = "'Quantity' must be an interger."
            return
        try:
            id = int(id)
            old_id = int(old_id)
        except:
            self.error_message = "IDs must be integers."
            return

        if id != old_id and self.id_exists(id):
            self.error_message = "IDs must be unique."
            return

        table_query = f"""
        UPDATE {self.current_warehouse}
        SET name = '{name}',id = {id}, quantity = {quantity}, other = '{other}'
        WHERE id = {old_id}
        """
        self.__execute_query(table_query)

    # Returns True if and only if an item with the given ID exists in the
    # current warehouse
    def id_exists(self, id):
        table_query = f"""
        SELECT count(*)
        FROM {self.current_warehouse}
        WHERE id = {id}
        """
        result = self.__execute_read_query(table_query)[0][0] != 0
        return result

    # Deletes an item at the given item ID. If no item exists at the given ID
    # in the current warehouse then no changes are made.
    def delete_item(self, id):
        table_query = f"""
        DELETE FROM {self.current_warehouse}
        WHERE id = {id}
        """
        self.__execute_query(table_query)
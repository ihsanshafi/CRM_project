from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.screen import Screen
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.textfield import MDTextField

from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.textfield import MDTextField

import sqlite3

#button fuctions

def add_customer(first_name, last_name, email, phone):
    conn = sqlite3.connect('crm.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    INSERT INTO customers (first_name, last_name, email, phone)
    VALUES (?, ?, ?, ?)
    ''', (first_name, last_name, email, phone))
    
    conn.commit()
    conn.close()

def get_customers():
    conn = sqlite3.connect('crm.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM customers')
    customers = cursor.fetchall()
    
    conn.close()
    return customers

def update_customer(customer_id, first_name, last_name, email, phone):
    conn = sqlite3.connect('crm.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    UPDATE customers
    SET first_name = ?, last_name = ?, email = ?, phone = ?
    WHERE id = ?
    ''', (first_name, last_name, email, phone, customer_id))
    
    conn.commit()
    conn.close()

def delete_customer(customer_id):
    conn = sqlite3.connect('crm.db')
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM customers WHERE id = ?', (customer_id,))
    
    conn.commit()
    conn.close()

def search_customers(query):
    conn = sqlite3.connect('crm.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT * FROM customers
    WHERE first_name LIKE ? OR last_name LIKE ? OR email LIKE ?
    ''', (f'%{query}%', f'%{query}%', f'%{query}%'))
    
    customers = cursor.fetchall()
    conn.close()
    return customers


class CRMApp(MDApp):
    def build(self):
        screen = Screen()

        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Search bar using MDTextField
        self.search_bar = MDTextField(
            hint_text="Search by name or email",
            icon_right="magnify",  # Add search icon to the right
            size_hint_x=0.95,
            pos_hint={"center_x": 0.5},
            on_text_validate=self.search_customer
        )

        layout.add_widget(self.search_bar)

        # Form to add or edit a customer
        self.first_name = MDTextField(
            hint_text="First Name",
            required=True
        )
        self.last_name = MDTextField(
            hint_text="Last Name",
            required=True
        )
        self.email = MDTextField(
            hint_text="Email",
            required=True
        )
        self.phone = MDTextField(
            hint_text="Phone"
        )

        layout.add_widget(self.first_name)
        layout.add_widget(self.last_name)
        layout.add_widget(self.email)
        layout.add_widget(self.phone)

        # Add and Update buttons
        self.add_button = MDRaisedButton(
            text="Add Customer",
            on_release=self.add_or_update_customer
        )
        self.update_button = MDRaisedButton(
            text="Update Customer",
            on_release=self.add_or_update_customer
        )
        self.update_button.disabled = True

        layout.add_widget(self.add_button)
        layout.add_widget(self.update_button)

        # Data table to display customers
        self.table = MDDataTable(
            size_hint=(1, 0.8),  # Increase size_hint_x for a wider table
            use_pagination=True,
            column_data=[
                ("ID", dp(40)),           # Increase ID column width
                ("First Name", dp(60)),   # Increase First Name column width
                ("Last Name", dp(60)),    # Increase Last Name column width
                ("Email", dp(80)),        # Increase Email column width
                ("Phone", dp(60)),        # Increase Phone column width
            ],
            row_data=self.get_customers_table_data(),
            check=True
        )
        self.table.bind(on_check_press=self.on_row_check)

        layout.add_widget(self.table)

        # Delete button
        delete_button = MDRaisedButton(
            text="Delete Customer",
            on_release=self.delete_customer
        )
        layout.add_widget(delete_button)

        screen.add_widget(layout)
        return screen

    def add_or_update_customer(self, instance):
        first_name = self.first_name.text
        last_name = self.last_name.text
        email = self.email.text
        phone = self.phone.text

        if instance == self.add_button:
            # Add customer to the database
            add_customer(first_name, last_name, email, phone)
        elif instance == self.update_button:
            # Update the customer in the database
            update_customer(self.selected_customer_id, first_name, last_name, email, phone)
            self.update_button.disabled = True

        # Refresh the table
        self.table.row_data = self.get_customers_table_data()

        # Clear the form
        self.first_name.text = ''
        self.last_name.text = ''
        self.email.text = ''
        self.phone.text = ''

    def get_customers_table_data(self):
        customers = get_customers()
        table_data = []

        for customer in customers:
            table_data.append(
                (str(customer[0]), customer[1], customer[2], customer[3], customer[4])
            )

        return table_data

    def on_row_check(self, instance_table, current_row):
        # Get the ID of the selected customer
        self.selected_customer_id = int(current_row[0])

        # Populate the form with the selected customer's data
        self.first_name.text = current_row[1]
        self.last_name.text = current_row[2]
        self.email.text = current_row[3]
        self.phone.text = current_row[4]

        # Enable the Update button
        self.update_button.disabled = False

    def delete_customer(self, instance):
        if hasattr(self, 'selected_customer_id'):
            # Delete the customer from the database
            delete_customer(self.selected_customer_id)

            # Refresh the table
            self.table.row_data = self.get_customers_table_data()

            # Clear the form
            self.first_name.text = ''
            self.last_name.text = ''
            self.email.text = ''
            self.phone.text = ''

            self.update_button.disabled = True
        else:
            self.show_dialog("No selection", "Please select a customer to delete.")

    def show_dialog(self, title, text):
        dialog = MDDialog(
            title=title,
            text=text,
            buttons=[
                MDFlatButton(
                    text="OK",
                    on_release=lambda x: dialog.dismiss()
                )
            ]
        )
        dialog.open()

    def search_customer(self, instance):
        query = self.search_bar.text.strip()

        if query:
            customers = search_customers(query)
        else:
            customers = get_customers()

        self.table.row_data = [(str(customer[0]), customer[1], customer[2], customer[3], customer[4]) for customer in customers]

if __name__ == '__main__':
    CRMApp().run()

# The business, in plain language

What Tasmanian Traders does, read out of the data model, the forms, the rules, and the sample's own help and "Behind the Scenes" text. Every statement points at the doc that carries the source. Where the sample's description and its code disagree, both are given.

**Related docs:** [[../03-data-model/README.md]], [[../09-business-logic/README.md]] (the rules, quoted), [[../04-forms/README.md]], [[../06-reports/README.md]], [[../01-architecture/framework.md]].

## What the sample says it is

The help file's own introduction (`help/ttrade.dbf`, topic "Introducing Tasmanian Traders"):

> Welcome to the Tasmanian Traders database! The Tasmanian Traders database stores information about customers, orders, shippers, suppliers, employees, and products. When you log in, your user level is identified as one of the following: Customer Service Representative, Operations Manager, Sales Manager, Application Developer. Depending on your user level, you have access to different tables.

Tastrade is a descendant of the Northwind sample: the customer IDs are Northwind's five-letter codes (`ALFKI`, `ANATR`, ...), the splitter class still records a `nwind` path, and the product catalogue is Northwind's (beverages, condiments, seafood). It is a wholesale importer of food and drink that sells to trade customers on account, with a minimum and a maximum order size per customer.

## The actors

| Who | How the sample models them | Count in the data |
|---|---|---|
| Customers | `CUSTOMER`: company, contact, address, phone and fax, a normal discount, a minimum and a maximum order amount (the credit line), a sales region | 92, in 21 countries; 79 have a minimum order set, all 92 a maximum, 52 a discount |
| Employees | `EMPLOYEE`: name, title, dates, address, a user-level group, a sales region, a password, a photo | 15, in 11 job titles from Sales Representative to Mail Clerk; per user level 1: 3, 2: 4, 3: 4, 4: 4 |
| Products | `PRODUCTS`: name, English name, quantity per unit, price and cost, stock and reorder figures, a discontinued flag; each in one category from one supplier | 77 products, 8 categories (Beverages, Condiments, Confections, Dairy Products, Grains/Cereals, Meat/Poultry, Produce, Seafood), 29 suppliers, 8 discontinued |
| Shippers | `SHIPPERS`: an ID and a name, nothing else | 3 (Speedy Express, United Package, Federal Shipping) |
| User levels | `USER_LEVEL`: four groups, each with an optional startup action | 1 Customer Service Rep (runs `oApp.DoForm("ordentry")`); 2 Applications Developer; 3 Operations Manager; 4 Sales Manager |

There are no payments, invoices as records, price lists, stock movements, currencies, or taxes. An order is the only transaction.

## The one transaction: an order

An order (`ORDERS`) belongs to one customer, is taken by one employee, ships by one shipper to a ship-to address copied from the customer, and has one or more lines (`ORDER_LINE_ITEMS`), each a product, a quantity, and the unit price copied from the product at the moment it is chosen. The header carries an order date, a deliver-by date, a discount percentage (copied from the customer, editable), a freight charge, a paid flag, and notes.

Its life, as the forms and rules implement it ([[../04-forms/ordentry.md]], [[../05-classes/orders.md]], [[../09-business-logic/README.md]]):

1. **Take it.** The clerk picks a customer (or types a new one and is offered the add-customer dialog), the ship-to block and discount fill from the customer, a due date defaults to a week out, the employee defaults to whoever is logged in, and the order number is drawn from the `SETUP` counter. Lines are added from a product list that does not hide discontinued products; the product's current price is copied onto the line. The screen shows subtotal, discount, freight, total, and the customer's available credit as lines change.
2. **Save it.** One transaction writes the header and all lines. The `ORDERS` table rule then insists on at least one line, warns if the customer's credit line would be exceeded, and warns if the order is under the customer's minimum; both warnings can be overridden with Yes.
3. **Change it.** An order stays editable until its deliver-by date has passed; after that it is read-only and cannot be deleted. The only later change the sample expects is marking it paid, from order entry or from the order history grid, which bypasses the credit and minimum checks.
4. **Reuse it.** From order entry, "Last Order" opens the customer's history; tagged lines from an old order are copied into the new one at their historical prices.
5. **Print it.** Invoices for a date range, one page per order, recomputing the total from the lines ([[../06-reports/orders.md]]).

Credit is not a balance kept anywhere. It is recomputed on demand as the customer's maximum order amount minus the total of every unpaid order, so paying an order frees credit and nothing else does.

## Master data

Six maintenance forms ([[../04-forms/README.md]]) add, edit, and delete customers, employees, products, suppliers, shippers, and categories, all on the same two-page pattern. Referential integrity refuses to delete anything that is in use (a customer with orders, a product on a line, a supplier or category with products, a shipper or employee on orders) and cascades key changes downward; only an order takes its lines with it when deleted. Keys for everything but customers come from the `SETUP` counters; customers type their own five-letter ID.

Categories and employees carry pictures, stored as file paths into `bitmaps\` (and, for categories, a second copy in a General field nobody reads).

## Who may do what

The help text says user levels "have access to different tables". The code does less: the user level decides which menu pads and bars exist (developers keep the Utilities pad; Operations Managers and above keep Login and Change Password) and which form opens at startup (a Customer Service Rep lands in order entry). No form, rule, or table checks the level. In the shipped build `DEBUGMODE` removes the login, so everyone is an Applications Developer and every user sees everything ([[../07-menus/main.md]], [[../08-programs/tastrade.h.md]]).

Passwords are eight plain characters, default `"Tastrade"`, compared case-sensitively; in the data every employee has changed theirs (0 still hold the default), and the login screen shows the selected employee's password in a "Hint" box ([[../05-classes/login.md]]).

## Reporting

Six listings of master data; invoices; two "sales by month" reports that sum unit prices without quantity, discount, or freight; a Top 25 Customers report that uses the full order total. The three sales reports therefore do not agree with each other or with the order screens ([[../06-reports/README.md]]).

## What the data says

| Fact | Value |
|---|---|
| Orders | 1079, dated 1992-05-09 to 1996-05-11, 2.6 lines each on average (2821 lines) |
| Paid | 1030 paid, 49 unpaid |
| Discounts on orders | 10% on 782, 5% on 246, 0% on 50, 6% on 1 |
| Freight | charged on all but 2 orders |
| Customers with orders | 90 of 92 |
| Employees on orders | 13 of 15 |
| Shippers | orders split Speedy Express: 432, United Package: 339, Federal Shipping: 308 |
| Quantities | whole numbers throughout, though the column allows three decimals (0 fractional) |
| Key counters (`SETUP`) | SUPPLIER=30, PRODUCTS=78, EMPLOYEE=16, CATEGORY=9, SHIPPERS=4, ORDERS=1138, ORDER_NUMBER=1138 |

Order IDs run from 1 to 1126 with 47 numbers missing, and the `ORDERS` counter already stands at 1138: numbers were issued and not kept, as `NewID()` gives them out before the order is saved. Discontinued products can still be ordered, and nothing in the application changes `units_in_stock` or `units_on_order`; the inventory columns are maintained by hand on the product form and read by nothing ([[../04-forms/product.md]]).

## Where the description and the code part

- **"Access to different tables"** by user level is menu gating only, and is off in the shipped build.
- **"Checking Available Credit"** (Behind the Scenes) says all the customer's orders are summed; the code sums only unpaid ones ([[../09-business-logic/README.md]], R7).
- **"Validating an Order"** lists three conditions and says a failed condition stops the rest; the code asks Yes/No on the credit and minimum conditions and lets the user save anyway.
- **The intro screen and the help** describe a login the shipped build never shows.
- **Inventory fields** exist on the product form and in the help's picture of a product, but no transaction moves them.

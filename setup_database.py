"""Create database from CSV files"""

import sqlite3
import pandas as pd
import os

def create_database():
    """Create normalized database schema from raw CSV data"""
    
    files = [
        'online_retail(2009-2010).csv',
        'online_retail(2010-2011).csv'
    ]
    
    dfs = []
    
    print("📊 Reading CSV files...")
    
    for file in files:
        if not os.path.exists(file):
            print(f"⚠️ Warning: {file} not found!")
            continue
            
        try:
            # Try UTF-8-SIG first (handles BOM)
            try:
                df = pd.read_csv(file, encoding='utf-8-sig')
            except UnicodeDecodeError:
                # Fallback to ISO-8859-1
                print(f"   Note: {file} is not UTF-8, trying ISO-8859-1...")
                df = pd.read_csv(file, encoding='ISO-8859-1')
            
            # Clean column names (remove BOM artifacts if ISO read, and whitespace)
            df.columns = df.columns.str.strip().str.replace('^ï»¿', '', regex=True)
            
            print(f"   Loaded {file}: {len(df)} rows")
            print(f"   Columns: {df.columns.tolist()}")
            dfs.append(df)
        except Exception as e:
            print(f"❌ Error reading {file}: {e}")
            return

    if not dfs:
        print("❌ No data loaded. Please ensure CSV files exist.")
        return
        
    # Combine dataframes
    df = pd.concat(dfs, ignore_index=True)
    print(f"✅ Total rows loaded: {len(df)}")
    
    # Clean data
    print("🧹 Cleaning data...")
    
    # Handle column names (CSV has 'Customer ID' but code expects consistent names)
    # Map CSV columns to internal names
    column_mapping = {
        'Invoice': 'Invoice',
        'StockCode': 'StockCode',
        'Description': 'Description',
        'Quantity': 'Quantity',
        'InvoiceDate': 'InvoiceDate',
        'Price': 'Price',
        'Customer ID': 'CustomerID',
        'Country': 'Country'
    }
    
    # Rename columns if they exist
    df = df.rename(columns=column_mapping)
    print(f"   Columns after rename: {df.columns.tolist()}")
    
    # Drop rows without CustomerID or Invoice
    before_drop = len(df)
    df = df.dropna(subset=['CustomerID', 'Invoice'])
    print(f"   Rows dropped (missing ID/Invoice): {before_drop - len(df)}")
    print(f"   Rows remaining: {len(df)}")
    
    # Debug: Check for non-numeric CustomerID
    try:
        df['CustomerID'] = df['CustomerID'].astype(float).astype(int).astype(str)
    except Exception as e:
        print(f"⚠️ Error converting CustomerID: {e}")
        # Filter only valid numeric IDs
        df = df[pd.to_numeric(df['CustomerID'], errors='coerce').notnull()]
        df['CustomerID'] = df['CustomerID'].astype(float).astype(int).astype(str)
        print(f"   Rows after filtering non-numeric CustomerID: {len(df)}")

    # Convert InvoiceDate to datetime
    print("   Converting dates...")
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
    
    # Debug: Check year distribution
    print("   Year distribution:")
    print(df['InvoiceDate'].dt.year.value_counts())
    
    print("🏗️ Creating tables...")
    
    # Connect to database
    conn = sqlite3.connect('analytics.db')
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('DROP TABLE IF EXISTS customers')
    cursor.execute('DROP TABLE IF EXISTS orders')
    cursor.execute('DROP TABLE IF EXISTS order_items')
    
    cursor.execute('''
    CREATE TABLE customers (
        customer_id TEXT PRIMARY KEY,
        country TEXT NOT NULL
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE orders (
        invoice_id TEXT PRIMARY KEY,
        invoice_date TIMESTAMP NOT NULL,
        customer_id TEXT NOT NULL,
        country TEXT NOT NULL,
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE order_items (
        order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
        invoice_id TEXT NOT NULL,
        stock_code TEXT NOT NULL,
        description TEXT,
        quantity INTEGER NOT NULL,
        unit_price REAL NOT NULL,
        revenue REAL NOT NULL,
        FOREIGN KEY (invoice_id) REFERENCES orders(invoice_id)
    )
    ''')
    
    # Populate customers table
    print("📥 Populating customers table...")
    # Sort by date to keep latest country for a customer
    customers = df.sort_values('InvoiceDate')[['CustomerID', 'Country']].drop_duplicates(subset=['CustomerID'], keep='last')
    customers.columns = ['customer_id', 'country']
    print(f"   Inserting {len(customers)} customers")
    customers.to_sql('customers', conn, if_exists='append', index=False)
    
    # Populate orders table
    print("📥 Populating orders table...")
    # Group by Invoice to get unique orders (taking first occurrence of date/customer/country)
    orders = df.groupby('Invoice').first().reset_index()[['Invoice', 'InvoiceDate', 'CustomerID', 'Country']]
    orders.columns = ['invoice_id', 'invoice_date', 'customer_id', 'country']
    print(f"   Inserting {len(orders)} orders")
    
    try:
        orders.to_sql('orders', conn, if_exists='append', index=False)
    except Exception as e:
        print(f"❌ Error inserting orders: {e}")
    
    # Populate order_items table
    print("📥 Populating order_items table...")
    order_items = df[['Invoice', 'StockCode', 'Description', 'Quantity', 'Price']].copy()
    order_items['revenue'] = order_items['Quantity'] * order_items['Price']
    order_items.columns = ['invoice_id', 'stock_code', 'description', 'quantity', 'unit_price', 'revenue']
    
    # Insert in batches
    print(f"   Inserting {len(order_items)} order items")
    order_items.to_sql('order_items', conn, if_exists='append', index=False)
    
    # Create indexes for performance
    print("🔍 Creating indexes...")
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_orders_date ON orders(invoice_date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_orders_customer ON orders(customer_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_items_invoice ON order_items(invoice_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_items_stock ON order_items(stock_code)')
    
    conn.commit()
    conn.close()
    
    print("\n✅ Database created successfully!")
    print(f"📊 Customers: {len(customers):,}")
    print(f"📊 Orders: {len(orders):,}")
    print(f"📊 Order items: {len(order_items):,}")
    print(f"💾 Database saved as: analytics.db")

if __name__ == "__main__":
    create_database()

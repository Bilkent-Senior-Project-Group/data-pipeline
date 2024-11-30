from azure.storage.blob import BlobServiceClient
import pandas as pd
import sqlalchemy
import os
import pyodbc

def get_existing_tables(engine):
    """Get list of existing tables in the database"""
    query = "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'"
    with engine.connect() as connection:
        result = connection.execute(sqlalchemy.text(query))
        return [row[0] for row in result]

def load_csvs_to_database(schema_name="dbo"):
    connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
    container_name = os.getenv('CONTAINER_NAME')
    db_server = os.getenv('DB_SERVER')
    db_name = os.getenv('DB_NAME')
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')

    # Construct connection string
    db_connection_string = (
        "mssql+pyodbc:///?odbc_connect="
        f"Driver={{ODBC Driver 18 for SQL Server}};"
        f"Server=tcp:{db_server},1433;"
        f"Database={db_name};"
        f"Uid={db_user};"
        f"Pwd={db_password};"
        "Encrypt=yes;"
        "TrustServerCertificate=yes;"
        "Connection Timeout=30"
    )
    try:
        print("Available ODBC drivers:", [x for x in pyodbc.drivers()])

        # Test database connection first
        try:
            test_conn = pyodbc.connect(
                f"DRIVER={{ODBC Driver 18 for SQL Server}};"
                f"SERVER=tcp:{db_server},1433;"
                f"DATABASE={db_name};"
                f"UID={db_user};"
                f"PWD={db_password};"
                "Encrypt=yes;"
                "TrustServerCertificate=yes"
            )
            print("Direct ODBC connection successful!")
            test_conn.close()
        except Exception as e:
            print(f"Direct ODBC connection failed: {str(e)}")
            raise

        # Connect to Azure Blob Storage using connection string
        blob_service_client = BlobServiceClient.from_connection_string(connect_str)
        container_client = blob_service_client.get_container_client(container_name)
        
        # Create database engine
        engine = sqlalchemy.create_engine(db_connection_string)
        
        # Get list of existing tables
        existing_tables = get_existing_tables(engine)
        print("Existing tables:", existing_tables)
        
        # List all blobs in the container
        blobs = container_client.list_blobs()
        
        for blob in blobs:
            if not blob.name.lower().endswith('.csv'):
                continue
            
            # Generate table name
            table_name = os.path.splitext(blob.name)[0].lower()
            table_name = ''.join(c if c.isalnum() or c == '_' else '_' for c in table_name)
            
            # Check if table already exists
            if table_name in existing_tables:
                print(f"Skipping {blob.name} - table {table_name} already exists")
                continue
                
            print(f"Processing {blob.name}")
            
            try:
                blob_client = container_client.get_blob_client(blob.name)
                blob_data = blob_client.download_blob()
                
                df = pd.read_csv(blob_data)
                df.columns = [col.strip().replace(' ', '_').replace('-', '_').lower() 
                             for col in df.columns]
                
                df.to_sql(
                    name=table_name,
                    schema=schema_name,
                    con=engine,
                    if_exists='fail',
                    index=False,
                    chunksize=1000
                )
                
                print(f"Successfully loaded {blob.name} into table {table_name}")
                
            except Exception as e:
                print(f"Error processing {blob.name}: {str(e)}")
                continue
                
    except Exception as e:
        print(f"Error: {str(e)}")
        raise

if __name__ == "__main__":
    load_csvs_to_database()
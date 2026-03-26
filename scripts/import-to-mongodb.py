#!/usr/bin/env python3
import json
from pathlib import Path
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

def import_to_mongodb():
    # MongoDB connection settings
    connection_string = "mongodb://localhost:27017/"
    database_name = "halfon-windows-filtering"
    
    # File paths
    data_dir = Path(__file__).parent.resolve().parent / 'data'
    units_file = data_dir / 'units.json'
    buildings_file = data_dir / 'buildings.json'
    techs_file = data_dir / 'techs.json'
    civs_file = data_dir / 'civs.json'
    
    try:
        # Connect to MongoDB
        client = MongoClient(connection_string)
        client.admin.command('ping')  # Test connection
        print("Connected to MongoDB successfully")
        
        # Get database
        db = client[database_name]
        
        # Import units
        if units_file.exists():
            print("Importing units...")
            try:
                with open(units_file, 'r', encoding='utf-8') as f:
                    units_data = json.load(f)
            except UnicodeDecodeError:
                print("UTF-8 decode failed, trying with latin-1 encoding...")
                with open(units_file, 'r', encoding='latin-1') as f:
                    units_data = json.load(f)
            
            # Empty the collection first
            db.units.delete_many({})
            print(f"Cleared {db.units.deleted_count} documents from units collection")
            
            # Insert new data
            if units_data:
                result = db.units.insert_many(units_data)
                print(f"Inserted {len(result.inserted_ids)} units")
            else:
                print("No units data to import")
        else:
            print(f"Units file not found: {units_file}")
        
        # Import buildings
        if buildings_file.exists():
            print("Importing buildings...")
            try:
                with open(buildings_file, 'r', encoding='utf-8') as f:
                    buildings_data = json.load(f)
            except UnicodeDecodeError:
                print("UTF-8 decode failed, trying with latin-1 encoding...")
                with open(buildings_file, 'r', encoding='latin-1') as f:
                    buildings_data = json.load(f)
            
            # Empty the collection first
            db.buildings.delete_many({})
            print(f"Cleared {db.buildings.deleted_count} documents from buildings collection")
            
            # Insert new data
            if buildings_data:
                result = db.buildings.insert_many(buildings_data)
                print(f"Inserted {len(result.inserted_ids)} buildings")
            else:
                print("No buildings data to import")
        else:
            print(f"Buildings file not found: {buildings_file}")
        
        # Import techs
        if techs_file.exists():
            print("Importing techs...")
            try:
                with open(techs_file, 'r', encoding='utf-8') as f:
                    techs_data = json.load(f)
            except UnicodeDecodeError:
                print("UTF-8 decode failed, trying with latin-1 encoding...")
                with open(techs_file, 'r', encoding='latin-1') as f:
                    techs_data = json.load(f)
            
            # Empty the collection first
            db.techs.delete_many({})
            print(f"Cleared {db.techs.deleted_count} documents from techs collection")
            
            # Insert new data
            if techs_data:
                result = db.techs.insert_many(techs_data)
                print(f"Inserted {len(result.inserted_ids)} techs")
            else:
                print("No techs data to import")
        else:
            print(f"Techs file not found: {techs_file}")
        
        # Import civilizations
        if civs_file.exists():
            print("Importing civilizations...")
            try:
                with open(civs_file, 'r', encoding='utf-8') as f:
                    civs_data = json.load(f)
            except UnicodeDecodeError:
                print("UTF-8 decode failed, trying with latin-1 encoding...")
                with open(civs_file, 'r', encoding='latin-1') as f:
                    civs_data = json.load(f)
            
            # Empty the collection first
            db.civs.delete_many({})
            print(f"Cleared {db.civs.deleted_count} documents from civs collection")
            
            # Insert new data
            if civs_data:
                result = db.civs.insert_many(civs_data)
                print(f"Inserted {len(result.inserted_ids)} civs")
            else:
                print("No civs data to import")
        else:
            print(f"Civs file not found: {civs_file}")
        
        print("Import completed successfully!")
        
    except ConnectionFailure as e:
        print(f"Failed to connect to MongoDB: {e}")
        return False
    except Exception as e:
        print(f"Error during import: {e}")
        return False
    finally:
        if 'client' in locals():
            client.close()
    
    return True

if __name__ == '__main__':
    import_to_mongodb()

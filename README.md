# Data Pipeline: Azure Storage to SQL Database

This project contains a Docker-based data pipeline that transfers CSV files from Azure Blob Storage to Azure SQL Database.

## Features
- Automatically loads CSV files from Azure Blob Storage into Azure SQL Database
- Creates tables based on CSV file names
- Skips existing tables to prevent duplicates
- Handles column name cleaning (removes spaces, special characters)

## Prerequisites
1. Docker Desktop installed on your machine
2. Access to the project's Docker Hub account (username: compedia2404)
3. Pull the compedia2404/data-pipeline image from Docker Hub
4. Azure credentials create .env file from .env_example
5. Upload .csv file into the Azure storage account(blob storage) 


## Quick Start

1. Clone the repository:
```bash
git clone https://github.com/Bilkent-Senior-Project-Group/data-pipeline
cd data-pipeline
docker-compose up


# UrbanFlow Analytics

Cloud-based train delay monitoring and analytics solution built on AWS.

## Project Overview
This project analyzes more than 2 million real Deutsche Bahn train delay records to uncover operational patterns, identify recurring delays, and present insights through a cloud-based analytics workflow on AWS.

## Architecture
- S3: Data lake for the 772 MB CSV dataset
- Athena: Serverless SQL querying for exploratory analysis
- EC2: Python-based processing with boto3, pandas, and matplotlib
- IAM: Secure access and permission management
- VPC and Security Groups: Network isolation and access control

## Key Results
| Metric | Result |
| --- | --- |
| Worst-performing station | Steinau (Straße) — 6.2 minutes |
| Peak delay hour | 6:00 PM — 1.8 minutes |
| Best travel day | July 14 — 0.91 minutes |
| Worst travel day | July 7 — 2.22 minutes |
| Most delayed train | RE25 — 5.2 minutes |
| Records analyzed | 2+ million |
| Estimated project cost | $0.015 (1.5 cents) |

## Technologies Used
- AWS: EC2, S3, Athena, IAM, VPC
- Python: boto3, pandas, matplotlib, Flask
- SQL: Athena queries

## How to Run
1. Clone the repository.
2. Install dependencies: pip install -r requirements.txt
3. Configure AWS credentials: aws configure
4. Run the analysis: python3 code/urbanflow_analysis.py

## What I Learned
- Cloud architecture design on AWS
- Serverless analytics with Athena
- Data engineering with Python
- Cost-effective cloud deployment using the AWS Free Tier
- Dashboard development with Flask

## Contact
For questions or collaboration, please reach out to Filimon Berihun at filimonberihun864@gmail.com or connect on LinkedIn: https://www.linkedin.com/in/filimon-berihun-558457319.
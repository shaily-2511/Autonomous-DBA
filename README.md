**Autonomous DBA for PostgreSQL
**

Demonstrating the Power of Agentic AI with Amazon Bedrock Claude Sonnet 4.6

A multi-agent system for intelligent PostgreSQL database monitoring and autonomous remediation

PostgreSQL


AWS Bedrock


Python


MCP


📋 Table of Contents

Overview


Key Features


Architecture


Prerequisites


Installation


Configuration


Running the Demo


Security Best Practices


How It Works


Monitoring Metrics


Troubleshooting


Conference Presentation


License


🎯 Overview

This project showcases Agentic AI capabilities using Amazon Bedrock Claude Sonnet 4.6 to autonomously manage PostgreSQL databases. The system employs a three-agent architecture that continuously monitors database health, detects performance degradation, and automatically remediates issues without human intervention.

Key Technologies:





Amazon Bedrock Claude Sonnet 4.6: Foundation model powering intelligent decision-making



MCP (Model Context Protocol) Server: Enables seamless communication between agents and database



PostgreSQL 16: Target database (local or cloud deployment)



Python 3.8+: Agent orchestration and automation

Presented at PostgreSQL Conference 2026



✨ Key Features

Three-Agent System Architecture





Supervisor Agent 🧠





Orchestrates the entire monitoring and remediation workflow



Analyzes health check results and determines appropriate actions



Coordinates communication between Health Check and Action agents



Makes intelligent decisions based on database metrics



Health Check Agent 🔍





Continuously monitors PostgreSQL database health metrics



Tracks performance indicators (CPU, memory, connections, query performance)



Detects anomalies and performance degradation patterns



Reports findings to the Supervisor Agent



Action Agent ⚡





Executes remediation actions as instructed by the Supervisor Agent



Performs automated fixes (query optimization, connection management, index creation)



Validates action success and reports outcomes



Maintains audit trail of all remediation activities

Core Capabilities





Real-time Health Monitoring: Continuous tracking of database vitals



Intelligent Anomaly Detection: AI-powered identification of performance issues



Autonomous Remediation: Automatic execution of corrective actions



MCP Server Integration: Seamless agent-to-database communication



Cloud or Local Deployment: Works with PostgreSQL running locally or in AWS RDS/Aurora



Conference-Ready Demo: Pre-configured demonstration scenarios



🏗️ Architecture

┌─────────────────────────────────────────────────────────┐
│                    PostgreSQL 16 Database                │
│              (Local or Cloud - RDS/Aurora)               │
└────────────────────────┬────────────────────────────────┘
                         │

                         
                         ▼
              ┌──────────────────────┐
              │   MCP Server         │
              │  (Database Bridge)   │
              └──────────┬───────────┘

              
                         │
         ┌───────────────┼───────────────┐
         │         
         │               │
         ▼               ▼               ▼
┌────────────────┐ ┌────────────┐ ┌────────────────┐
│ Health Check   │ │ Supervisor │ │ Action Agent   │
│ Agent          │─│   Agent    │─│                │
│                │ 
│            │ │                │
│ • Monitors DB  │ │ • Analyzes │ │ • Executes     │
│ • Detects      │ │ • Decides  │ │   Fixes        │
│   Issues       │ │ • Instructs│ │ • Validates    │
└────────────────┘ └────────────┘ └────────────────┘
         │               │  
         │
         └───────────────┼───────────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │  Amazon Bedrock      │
              │  Claude Sonnet 4.6   │
              │  (AI Foundation)     │
              └──────────────────────┘

Workflow:





Health Check Agent monitors database → detects degradation



Reports findings to Supervisor Agent



Supervisor Agent analyzes situation using Claude Sonnet 4.6



Supervisor instructs Action Agent with specific remediation steps



Action Agent executes fixes and reports success



Cycle continues with ongoing monitoring



📦 Prerequisites

Before you begin, ensure you have:





Python 3.8 or higher installed



PostgreSQL 16 (local installation or cloud access)



AWS Account with Amazon Bedrock access enabled



AWS CLI configured with appropriate credentials



Git installed for repository cloning

AWS Bedrock Requirements:





Access to Claude Sonnet 4.6 model in your AWS region



IAM permissions for Bedrock API calls



Sufficient service quotas for model invocations



🚀 **Installation**

**For Testers/Customers**

Follow these steps to set up the Autonomous DBA demo on your machine:

**1. Clone the Repository**

git clone https://github.com/shaily-2511/Autonomous-DBA.git
cd Autonomous-DBA

**2. Set Up Python Virtual Environment**

#Create virtual Env
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
# venv\Scripts\activate

# Install required dependencies
pip install -r requirements.txt

Expected output:

Successfully installed boto3-1.x.x botocore-1.x.x psycopg2-2.x.x ...

**3. Verify Installation**

python --version  # Should show Python 3.8+
pip list          # Verify all packages installed



**⚙️ Configuration
**
1. Copy Environment Template

cp .env.example .env

2. Configure Your Credentials

Edit the .env file with your specific configuration:

# PostgreSQL Database Configuration
DB_HOST=localhost                    # Use your RDS endpoint for cloud databases
DB_PORT=5432
DB_NAME=autonomous_dba              # Your database name
DB_USER=dba_agent                   # Database user with monitoring privileges
DB_PA[PASSWORD]assword    # Your database password

# AWS Bedrock Configuration
AWS_REGION=us-east-1                # Region where Bedrock is enabled
AWS_ACCESS_KEY_ID=your_access_key   # Your AWS access key
AWS_SECRET_ACCESS_KEY=your_secret   # Your AWS secret key
BEDROCK_MODEL_ID=us.anthropic.claude-sonnet-4-5-20250929-v1:0

# Agent Configuration
MONITORING_INTERVAL=30              # Health check frequency (seconds)
ALERT_THRESHOLD=75                  # Performance threshold (percentage)
AUTO_REMEDIATION=true               # Enable automatic fixes (set false for manual approval)
LOG_LEVEL=INFO                      # Logging verbosity (DEBUG, INFO, WARN, ERROR)

**Important Notes:**




a. For local PostgreSQL: Use localhost as DB_HOST



b. For AWS RDS/Aurora: Use your database endpoint (e.g., mydb.abc123.us-east-1.rds.amazonaws.com)



c. Ensure your AWS credentials have bedrock:InvokeModel permissions



Start with AUTO_REMEDIATION=false for initial testing

**3. Database Setup (Optional)**

Create a dedicated monitoring user with appropriate privileges:

# Connect to PostgreSQL
psql -U postgres

# Create monitoring user
CREATE USER dba_agent WITH PASSWORD 'your_secure_password';

# Grant necessary permissions
GRANT pg_monitor TO dba_agent;
GRANT CONNECT ON DATABASE autonomous_dba TO dba_agent;
GRANT USAGE ON SCHEMA public TO dba_agent;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO dba_agent;

# For remediation actions (use cautiously)
GRANT CREATE ON SCHEMA public TO dba_agent;



**🎮 Running the Demo**

Quick Start

# Ensure virtual environment is activated
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Run the complete demo
./demo/run_demo.sh

**Expected Demo Flow:**




System initializes all three agents



Health Check Agent begins monitoring



Demo simulates database performance degradation



Supervisor Agent detects issue and analyzes



Action Agent executes remediation



System confirms health restoration

**Running Individual Components**

# Start Health Check Agent only
python src/agents/health_check_agent.py

# Start Supervisor Agent (requires Health Check running)
python src/agents/supervisor_agent.py

# Start Action Agent (requires Supervisor running)
python src/agents/action_agent.py

# Run complete orchestration
python main.py



# Use environment variables
export DB_PASSWORD="[PASSWORD]"
export AWS_SECRET_ACCESS_KEY="your_secret"

For Production (Recommended):

# Use AWS Secrets Manager
aws secretsmanager create-secret \
  --name autonomous-dba/credentials \
  --secret-string '{"db_password":"xxx","aws_secret":"xxx"}'

# Retrieve in application
aws secretsmanager get-secret-value \
  --secret-id autonomous-dba/credentials



🔧 How It Works

Monitoring Cycle

The system operates in continuous monitoring cycles:





Health Check Phase (every 60 seconds by default)





Collect database metrics (connections, query performance, locks)



Calculate health score (0-100)



Identify anomalies and trends



Analysis Phase (when health score < threshold)





Supervisor Agent receives health report



Claude Sonnet 4.6 analyzes root causes



Determines appropriate remediation strategy



Action Phase (when remediation needed)





Action Agent receives instructions



Executes specific fixes (e.g., kill long queries, optimize indexes)



Validates success and reports back



Verification Phase





Health Check Agent confirms improvement



System logs all actions for audit trail



Cycle continues with ongoing monitoring

Example Remediation Scenarios

Scenario 1: High Connection Count





Detection: Health Check Agent sees 95% connection pool utilization



Analysis: Supervisor identifies connection leak pattern



Action: Action Agent terminates idle connections, adjusts pool settings



Result: Connection count reduced to 60%, health restored

Scenario 2: Slow Query Performance





Detection: Average query time increased 300%



Analysis: Supervisor identifies missing index on frequently queried table



Action: Action Agent creates optimized index



Result: Query performance improved by 85%

🎤 Conference Presentation

This project was created for PostgreSQL Conference 2026 to demonstrate:





Agentic AI Architecture: How multiple AI agents collaborate autonomously



MCP Server Integration: Bridging AI models with database operations



Amazon Bedrock Capabilities: Leveraging Claude Sonnet 4.6 for intelligent decision-making



Real-World DBA Automation: Practical applications of AI in database administration

📧 Contact

Author: Shaily Porwal

Email: shaily.porwal@gmail.com

GitHub: [@shaily-2511](https://github.com/shaily-2511)

Conference: PostgreSQL Conference 2026

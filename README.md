# Autonomous Customer Lead Identification using Data Analytics

An intelligent system that automatically identifies potential business leads by scraping web data, analyzing customer sentiment using AI, and providing actionable insights through an interactive dashboard.

## 🏗️ System Architecture

```
Scraping → Verification → Hugging Face AI → MySQL Database → Streamlit Dashboard
```

### Pipeline Components:
1. **Scout Module** - Web scraping and data acquisition
2. **Analyst Module** - AI-powered review analysis using Hugging Face API
3. **MySQL Database** - Persistent data storage
4. **Streamlit Dashboard** - Real-time analytics visualization

## 📁 Project Structure

```
autonomous_lead_identifier/
│
├── main.py                     # Central Orchestrator
├── dashboard.py                # Streamlit UI
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── .env.template              # Environment variables template
│
├── modules/
│   ├── __init__.py
│   ├── scout.py               # Data Acquisition Module
│   └── analyst.py             # AI Analysis Module
│
├── config/
│   ├── hf_config.py           # Hugging Face API configuration
│   └── db_config.py           # MySQL database configuration
│
└── data/
    └── schema.sql             # Database schema
```

## 🚀 Setup Instructions

### Prerequisites

1. **Python 3.8+** installed on your system
2. **MySQL Server** installed and running
3. **Chrome Browser** (for Selenium web scraping)
4. **Hugging Face Account** (free) - for API access

### Step 1: Install MySQL

**For Windows:**
- Download MySQL from: https://dev.mysql.com/downloads/installer/
- Install and set root password
- Start MySQL service



### Step 2: Create Database

Open MySQL terminal:
```bash
mysql -u root -p
```

Run the following SQL commands:
```sql
CREATE DATABASE lead_management;
USE lead_management;
SOURCE data/schema.sql;  # Or manually run the SQL from schema.sql
EXIT;
```

### Step 3: Get Hugging Face API Token

1. Go to https://huggingface.co/
2. Create a free account (if you don't have one)
3. Go to Settings → Access Tokens
4. Create a new token with "Read" access
5. Copy the token for later use

### Step 4: Install Python Dependencies

```bash
# Navigate to project directory
cd autonomous_lead_identifier

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 5: Configure Environment Variables

1. Copy the template:
```bash
cp .env.template .env
```

2. Edit `.env` file with your actual values:
```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password_here
DB_NAME=lead_management
DB_PORT=3306

HF_API_TOKEN=your_huggingface_token_here
```

## 🎮 How to Run

### Running the Main Pipeline

Execute the lead identification pipeline:

```bash
python main.py
```

This will:
1. ✅ Initialize MySQL database connection
2. 🔍 Scrape business leads from Google search
3. 🌐 Verify website availability
4. 🤖 Analyze reviews using Hugging Face AI
5. 💾 Save results to MySQL database
6. 📧 Generate personalized email drafts

**Expected Output:**
```
╔══════════════════════════════════════════════════════════════╗
║  Autonomous Customer Lead Identification System              ║
║  Using Data Analytics & AI                                   ║
╚══════════════════════════════════════════════════════════════╝

============================================================
Starting Lead Identification Pipeline
Search Query: restaurants in bangalore with poor reviews
============================================================

📡 Step 1: Acquiring leads...
✓ Found 5 potential leads

🔧 Freeing browser resources...

🤖 Step 2: Analyzing leads with AI...

  Processing lead 1/5: Restaurant ABC
    ✓ Pain Point: Poor Service
    ✓ Status: Active
...
```

### Running the Dashboard

Launch the interactive analytics dashboard:

```bash
streamlit run dashboard.py
```

This will:
- Open your browser automatically at `http://localhost:8501`
- Display real-time analytics and visualizations
- Allow you to filter and export lead data

**Dashboard Features:**
- 📊 KPI Metrics (Total Leads, Active Websites, etc.)
- 🥧 Website Status Distribution Chart
- 📈 Pain Point Analysis
- 📅 Lead Acquisition Timeline
- 🔍 Interactive Data Table with Filters
- 📥 CSV Export Functionality

## 🛠️ Customization

### Change Search Query

Edit `main.py`, line ~138:
```python
search_query = "your custom search query here"
orchestrator.process_leads(search_query, max_results=10)
```

### Modify AI Model

Edit `config/hf_config.py`:
```python
HF_MODEL = "your-preferred-model"
# Options:
# - "distilbert-base-uncased-finetuned-sst-2-english"
# - "facebook/bart-large-mnli"
# - "cardiffnlp/twitter-roberta-base-sentiment"
```

### Add More Pain Point Categories

Edit `modules/analyst.py`, method `_identify_pain_point()`:
```python
pain_points = {
    'Your Category': ['keyword1', 'keyword2'],
    # ... add more
}
```

## 📊 Database Schema

```sql
CREATE TABLE leads (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    business_name VARCHAR(255),
    website_url VARCHAR(255),
    technical_status VARCHAR(50),
    reviews_snippet TEXT,
    pain_point VARCHAR(100),
    email_draft TEXT,
    contact_status VARCHAR(50)
);
```

## 🐛 Troubleshooting

### Issue: MySQL Connection Error
**Solution:** 
- Verify MySQL is running: `sudo systemctl status mysql`
- Check credentials in `.env` file
- Ensure database exists: `mysql -u root -p -e "SHOW DATABASES;"`

### Issue: Hugging Face API Rate Limit
**Solution:** 
- Free tier has rate limits
- Wait a few minutes between runs
- Consider upgrading to Pro tier for higher limits

### Issue: Selenium WebDriver Error
**Solution:**
- Ensure Chrome browser is installed
- Update chromedriver: `pip install --upgrade webdriver-manager`
- Check internet connection

### Issue: "No module named 'config'"
**Solution:**
- Ensure you're running from project root directory
- Activate virtual environment: `source venv/bin/activate`

## 📝 Academic Justification (For Viva)

**Q: Why MySQL instead of SQLite?**

**A:** "The system uses a MySQL relational database instead of SQLite to support concurrent access, improved scalability, and real-time dashboard analytics. MySQL enables parallel reads and writes, preventing dashboard blocking during data ingestion, and facilitates future cloud deployment on AWS RDS or Azure SQL."

**Q: Why Hugging Face API instead of local models?**

**A:** "Using Hugging Face's cloud API eliminates the need for GPU resources on low-end laptops, ensures model updates automatically, and provides enterprise-grade reliability. This cloud-based approach aligns with modern microservices architecture while maintaining cost-effectiveness."

## 🎯 Key Features

✅ **Automated Lead Discovery** - No manual searching required
✅ **AI-Powered Analysis** - Sentiment analysis using state-of-the-art models
✅ **Real-time Dashboard** - Live analytics with Streamlit
✅ **Scalable Architecture** - MySQL database for production readiness
✅ **Personalized Outreach** - Auto-generated email templates
✅ **Low-resource Friendly** - Cloud API instead of local GPU

## 📚 Technologies Used

- **Python 3.8+** - Core programming language
- **Selenium** - Web scraping and automation
- **Hugging Face API** - AI/ML sentiment analysis
- **MySQL** - Relational database
- **Streamlit** - Dashboard framework
- **Plotly** - Interactive visualizations
- **Pandas** - Data manipulation

## 📧 Support

For issues or questions:
1. Check the troubleshooting section
2. Review the error messages carefully
3. Ensure all prerequisites are installed
4. Verify `.env` configuration

## 📄 License

This project is for academic/educational purposes.

---

**Built for Anna University Academic Project**  
*Autonomous Customer Lead Identification using Data Analytics*

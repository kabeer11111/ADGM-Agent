https://github.com/user-attachments/assets/21f0fe60-301a-4f98-a9fb-559f0d1b9718

# 🏢 ADGM Corporate Agent - AI-Powered Legal Document Review

An intelligent document analysis system that helps corporate agents review ADGM (Abu Dhabi Global Market) legal documents for compliance, completeness, and regulatory requirements.

## 🌟 What Does This Do?

This tool takes your legal documents (like Articles of Association, Employment Contracts, Board Resolutions, etc.) and:

- 📋 **Automatically identifies** what type of document it is
- 🔍 **Scans for compliance issues** using AI and legal knowledge
- ✅ **Checks completeness** against ADGM requirements  
- 📝 **Generates summaries** of each document
- 💡 **Provides suggestions** for fixing issues
- 📤 **Creates reviewed versions** with embedded comments
- 📊 **Gives you a complete analysis report** in JSON format

## 🚀 Key Features

### Smart Document Analysis
- **Auto-detection** of 15+ document types (Articles, MOA, Employment Contracts, etc.)
- **Process mapping** - figures out what you're trying to do (Company Incorporation, Licensing, etc.)
- **Missing document alerts** - tells you what's still needed

### AI-Powered Compliance Checking
- **Legal knowledge base** powered by RAG (Retrieval-Augmented Generation)
- **Issue severity ranking** (High/Medium/Low)
- **Specific suggestions** with legal citations
- **ADGM-specific requirements** checking

### User-Friendly Interface
- **Drag & drop** multiple documents
- **Real-time processing** with progress bars
- **Detailed summaries** for each document
- **Export capabilities** - JSON reports and commented documents

## 🏗️ What's Inside?

```
ADGM_CORP_AGENT1/
├── app/                          # Main application code
│   ├── models/
│   │   └── llm_client.py        # Gemini AI integration
│   ├── checklist.py             # Document requirement checklists
│   ├── comments.py              # Adds comments to Word docs
│   ├── parser.py                # Document type detection
│   ├── rag.py                   # Legal knowledge retrieval
│   ├── rules.py                 # Compliance checking logic
│   ├── summary.py               # Document summarization
│   └── ui.py                    # Streamlit web interface
├── data/adgm_laws/              # Legal documents (PDFs/DOCX)
├── chroma_db/                   # Vector database (created automatically)
├── ingest.py                    # Loads legal knowledge into database
├── requirements.txt             # Python dependencies
└── .env                         # Your API keys (you create this)
```

## 📋 Requirements

- **Python 3.8+** (3.9+ recommended)
- **Gemini API Key** (free from Google AI Studio)
- **About 2GB free space** (for AI models and legal documents)
- **Internet connection** (for AI model downloads on first run)

## 🔧 Quick Start

### 1. Get Your API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key (it's free!)
3. Copy the key - you'll need it in step 4

### 2. Download & Setup
```bash
# Clone or download this project
cd ADGM_CORP_AGENT1

# Create virtual environment
python -m venv .venv

# Activate it
# On Mac/Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Add Your Legal Documents
Put your ADGM legal reference documents (PDFs or Word docs) in the `data/adgm_laws/` folder. These should be things like:
- ADGM Companies Regulations
- Employment Regulations  
- Registration requirements
- Standard forms and templates

### 4. Configure API Key
Create a `.env` file in the root directory:
```
GEMINI_API_KEY=your_api_key_here
```

### 5. Build Legal Knowledge Base
```bash
python ingest.py
```
This will process all your legal documents and create a searchable knowledge base.

### 6. Run the Application
```bash
streamlit run app/ui.py
```

Your browser should open to `http://localhost:8501` with the application ready to use!

## 📖 How to Use

### Basic Workflow
1. **Upload Documents** - Drag & drop your .docx files
2. **Wait for Processing** - Watch the progress bar as AI analyzes each document
3. **Review Results** - Check summaries, compliance issues, and missing documents
4. **Download Reports** - Get JSON analysis and commented Word documents

### Document Types Supported
- Articles of Association
- Memorandum of Association  
- Board Resolutions
- Shareholder Resolutions
- Employment Contracts
- UBO Declarations
- Commercial Agreements
- Licensing Applications
- And more...

### Process Types Detected
- **Company Incorporation** - Setting up a new company
- **Licensing & Regulatory Filings** - Getting permits and renewals
- **Employment & HR** - Hiring and employment documentation
- **Commercial Agreements** - Business contracts and deals
- **Compliance & Risk** - Internal policies and procedures

## 🐛 Troubleshooting

### "RAG database is empty" Error
```bash
# Make sure you ran the ingestion step
python ingest.py

# Check if it worked
python -c "from app.rag import debug_rag_database; debug_rag_database()"
```

### "No API Key" Error
- Make sure your `.env` file exists and has the correct API key
- Check there are no spaces around the `=` sign
- Try restarting the application

### "Rate Limit" or "Quota Exceeded" Errors
**Problem**: Gemini free tier has daily/monthly limits
**Solutions**:
- **Wait and retry** - Free tier resets daily
- **Upgrade to paid Gemini** - Much higher limits for heavy usage
- **Switch AI model** - Edit `app/models/llm_client.py` to use OpenAI, Claude, or other providers
- **Process fewer documents** at once to stay within limits

### Documents Not Processing
- Make sure files are `.docx` format (not `.doc`)
- Check file isn't corrupted by opening in Word first
- Ensure files aren't password protected

### Slow Performance
- First run is slower (downloads AI models)
- Large documents take longer to process
- Consider splitting very large documents

## 💡 Important Notes

### API Usage & Costs
- **Gemini Free Tier**: 15 requests/minute, 1,500 requests/day, 1M requests/month
- **For heavy usage**: Consider upgrading to Gemini Pro ($7/1M tokens)
- **Alternative AI models**: System supports switching to OpenAI, Claude, or others
- **Tip**: Process documents in small batches to stay within free limits

### First Run Setup

- **All processing happens locally** on your machine
- **Only text snippets** are sent to Gemini AI for analysis (not full documents)
- **No data is stored** by Google or external services
- **Legal documents stay on your computer**

## 🤝 Getting Help

### Common Issues
- **SSL Warnings**: These are harmless and don't affect functionality
- **Model Download**: First run downloads ~500MB of AI models
- **Memory Usage**: Large document sets may use 2-4GB RAM

### Need Support?
If you run into issues:
1. Check the troubleshooting section above
2. Look at the console output for error messages
3. Try the debug commands to isolate the problem

## 🚀 Advanced Usage

### Adding Custom Legal Requirements
Edit the rules in `app/rules.py` to add your own compliance checks.

### Custom Document Types
Add new document patterns in `app/parser.py` to detect additional document types.

### API Integration
The analysis results are available as structured JSON - perfect for integrating with other systems.

## 📊 Understanding the Output

### Issue Severity Levels
- 🔴 **High**: Critical compliance failures, missing required clauses
- 🟡 **Medium**: Important but not critical issues, best practices
- 🟢 **Low**: Minor suggestions, formatting improvements

### Document Status
- ✅ **Complete**: All required documents present and compliant
- 🟡 **Issues Found**: Documents present but have compliance problems  
- ❌ **Missing**: Required documents not uploaded

---

**Built with ❤️ for ADGM corporate agents and legal professionals**

*This tool is designed to assist legal professionals, not replace them. Always have qualified legal counsel review important documents.*

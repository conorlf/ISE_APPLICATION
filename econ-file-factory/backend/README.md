# AI-Powered Data Harmonization Application

This Flask application provides intelligent CSV data harmonization using OpenAI's GPT models to automatically map column names across different datasets.

## Features

- **AI-Powered Column Harmonization**: Automatically maps column names using OpenAI's language models
- **Confidence Scoring**: Each column mapping includes a confidence score (0-1)
- **Intelligent Caching**: Redis-based caching to reduce API calls and improve performance
- **Fallback Mechanisms**: Static mappings and fuzzy matching when AI is unavailable
- **Batch Processing**: Handles multiple CSV/Excel files simultaneously
- **Data Reshaping**: Converts wide-format data to long-format for easier analysis
- **Deduplication**: Automatically identifies and removes duplicate records
- **Missing Data Reporting**: Comprehensive reports on missing values

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your OpenAI API key
OPENAI_API_KEY=your-openai-api-key-here

# Optional: Configure Redis for caching
REDIS_HOST=localhost
REDIS_PORT=6379
```

## Usage

### Starting the Application

```bash
python app.py
```

The application will start on `http://localhost:5000`

### API Endpoints

#### POST /upload
Upload CSV/Excel files for harmonization.

**Parameters:**
- `files`: Multiple file uploads (CSV, XLSX, or ZIP containing data files)
- `use_openai`: (optional) Set to "false" to disable AI harmonization (default: "true")
- `api_key`: (optional) Override the environment API key

**Example using curl:**
```bash
curl -X POST http://localhost:5000/upload \
  -F "files=@data1.csv" \
  -F "files=@data2.xlsx" \
  -F "use_openai=true" \
  -o harmonized_data.csv
```

#### GET /health
Check application health and configuration status.

## How AI Harmonization Works

1. **Column Analysis**: When files are uploaded, the AI analyzes all column names
2. **Semantic Matching**: Uses GPT-4 to understand the meaning and context of each column
3. **Canonical Mapping**: Maps columns to a predefined set of canonical names
4. **Confidence Scoring**: Assigns confidence scores based on semantic similarity
5. **Caching**: Stores mappings in Redis to reuse for similar datasets

### Example Mappings

| Original Column | Canonical Name | Confidence | Reasoning |
|----------------|----------------|------------|-----------|
| FirmID | firm_id | 0.95 | Direct semantic match |
| StaffTotal | employees | 0.90 | Common synonym for workforce |
| Gender | sex | 0.85 | Standard demographic term |
| Yr | year | 0.92 | Common abbreviation |

## Output Format

The harmonized CSV includes:
1. **Main Data**: Cleaned and harmonized dataset
2. **Duplicate Records**: Section listing any duplicates found
3. **Missing Data Report**: Summary of missing values by variable
4. **AI Harmonization Report**: Detailed mapping information including:
   - Success rates per file
   - Low-confidence mappings requiring review
   - Unknown columns that couldn't be mapped

## Configuration

### Canonical Columns

The system recognizes these standard column types:
- Identifiers: `firm_id`, `company_id`, `company_name`
- Time: `year`, `month`, `quarter`, `date`
- Financial: `revenue`, `sales`, `employees`, `expenses`, `profit`
- Demographics: `sex`, `age_group`
- Geographic: `region`, `country`, `state`, `city`
- Business: `industry`, `sector`, `market_share`
- Metadata: `source`, `data_source`

### Adding Custom Mappings

Edit `ai_harmonizer.py` to add domain-specific canonical columns or fallback mappings.

## Best Practices

1. **Review Low-Confidence Mappings**: Check mappings with confidence < 0.7
2. **Validate Unknown Columns**: Manually review columns marked as "unknown"
3. **Use Consistent Naming**: The more consistent your input data, the better the AI performs
4. **Leverage Caching**: Reuse the same API instance for similar datasets
5. **Monitor API Usage**: Track OpenAI API calls to manage costs

## Data Merging Behavior

When the same entity (e.g., firm_id + year) appears in multiple files:
- **Value columns** (revenue, employees, etc.): Takes the first non-null value
- **Metadata columns** (industry, region, sex): Merges from all sources, filling gaps
- **Source tracking**: Lists all files that contributed data (e.g., "file1.csv, file2.csv")

This ensures no data is lost when combining multiple datasets with partial overlaps.

## Troubleshooting

- **No API Key**: Ensure `OPENAI_API_KEY` is set in environment or .env file
- **Redis Connection Failed**: AI harmonization works without Redis, but caching is disabled
- **Low Success Rates**: Add more context-specific canonical columns or fallback mappings
- **API Errors**: Check your OpenAI API quota and rate limits

## Security Considerations

- API keys can be provided via environment variables or request parameters
- Never commit API keys to version control
- Use Redis authentication in production environments
- Validate and sanitize all uploaded files

## Dependencies

- Flask: Web framework
- pandas: Data manipulation
- OpenAI: AI-powered harmonization
- Redis: Caching (optional)
- python-dotenv: Environment management 
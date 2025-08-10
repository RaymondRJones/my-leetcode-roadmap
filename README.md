# 🎯 LeetCode Roadmap Generator

A comprehensive coding practice platform that combines two powerful learning paths:
1. **Advanced Roadmap**: Extracts solved LeetCode problems from your PDF submission history and creates personalized monthly roadmaps
2. **Beginner Training**: Automatically scrapes AtCoder problems and uses ChatGPT to create simplified, beginner-friendly explanations perfect for learning basic programming concepts

## ✨ Features

### Advanced Roadmap (From LeetCode PDFs)
- **PDF Analysis**: Automatically extracts problem names and completion status from LeetCode PDF exports
- **Smart Organization**: Distributes problems across days for each month
- **Progress Tracking**: Track your completion progress through each month
- **Multi-Format Support**: Works with various PDF export formats from LeetCode

### Beginner Training (AtCoder Problems)
- **Automated Problem Scraping**: Fetches 30 recent AtCoder problems automatically
- **AI-Powered Simplification**: Uses ChatGPT to break down problems for complete beginners
- **Concept-Focused Learning**: Each problem highlights key programming concepts (if-statements, loops, etc.)
- **Step-by-Step Guidance**: Detailed beginner-friendly explanations and solving approaches
- **Interactive Progress**: Track completion, difficulty levels, and learning streaks

### Universal Features
- **Beautiful Web Interface**: Responsive design with Bootstrap and modern UI components
- **Direct Problem Links**: One-click access to solve problems on original platforms
- **Dual Navigation**: Switch between Advanced and Beginner modes seamlessly

## 🚀 Quick Start

### Prerequisites
- Python 3.7+
- For Advanced Roadmap: PDF files exported from your LeetCode submission history
- For Beginner Training: OpenAI API key (for ChatGPT integration)

### Installation & Usage

1. **Clone or download this repository**
   ```bash
   git clone <repository-url>
   cd leetcode-roadmap-generator
   ```

2. **Set up Advanced Roadmap (Optional)**
   - Place your LeetCode PDF exports in the project directory
   - Supported naming patterns: `"May Roadmap.pdf"`, `"April Leetcode Roadmap.pdf"`, etc.

3. **Set up Beginner Training (Optional)**
   - Edit `scripts/atcoder_scraper.py` and add your OpenAI API key
   - Run the scraper to generate beginner problems:
   ```bash
   cd scripts && ./run_scraper.sh
   ```

4. **Start the web application**
   ```bash
   ./run.sh
   ```
   
   Or manually:
   ```bash
   # Create virtual environment
   python3 -m venv venv
   source venv/bin/activate
   
   # Install dependencies
   pip install pdfplumber flask pandas requests beautifulsoup4 openai
   
   # Analyze PDFs and start web server
   python pdf_analyzer.py  # For advanced roadmap
   python app.py
   ```

5. **Access your platform**
   - The app will automatically find an available port (5001, 8000, etc. if 5000 is in use)
   - Open the displayed URL in your web browser (e.g., http://localhost:5001)
   - Choose between:
     - **Advanced Roadmap**: Browse your monthly LeetCode roadmaps
     - **Beginner Training**: Practice with simplified AtCoder problems

## 📁 Project Structure

```
leetcode-roadmap-generator/
├── pdf_analyzer.py                    # Core PDF parsing and analysis
├── app.py                            # Flask web application with dual modes
├── scripts/                          # AtCoder scraping tools
│   ├── atcoder_scraper.py           # Main scraper with ChatGPT integration
│   └── run_scraper.sh               # Scraper runner script
├── templates/                        # HTML templates
│   ├── base.html                    # Base template with navigation
│   ├── index.html                   # Advanced roadmap overview
│   ├── month.html                   # Individual month view
│   ├── beginner.html                # Beginner training overview
│   └── problem_detail.html          # Detailed problem view
├── roadmap_data.json                 # Generated LeetCode roadmap data
├── atcoder_beginner_problems.json    # Generated AtCoder problems data
├── requirements.txt                  # Python dependencies
├── run.sh                           # Main startup script
└── README.md                        # This file
```

## 🎨 Features in Detail

### Advanced Roadmap Engine
- **PDF Analysis**: Regex-based pattern matching to extract problem information
- **Multi-Format Support**: Handles various PDF formats and structures  
- **Smart Filtering**: Focuses only on accepted solutions, deduplicates while preserving order
- **Daily Distribution**: Intelligently distributes problems across 30 days per month
- **Progress Tracking**: Visual progress bars and completion tracking

### Beginner Training System  
- **Automated Scraping**: Fetches 30 recent AtCoder ABC problems automatically
- **AI Simplification**: Uses ChatGPT-4 to break down complex problems for beginners
- **Concept Mapping**: Each problem tagged with key programming concepts
- **Step-by-Step Guidance**: Detailed solving approaches and beginner tips
- **Interactive Learning**: Progress tracking, difficulty filtering, and completion streaks
- **Detailed Problem View**: Full problem statements with simplified explanations

### Universal Web Interface
- **Dual Mode Navigation**: Seamless switching between Advanced and Beginner modes
- **Responsive Design**: Beautiful interface that works on desktop and mobile
- **Progress Visualization**: Charts, statistics, and completion tracking
- **Direct Problem Links**: One-click access to solve problems on original platforms
- **Local Storage**: Persistent progress tracking across browser sessions

## 🔧 API Endpoints

### Advanced Roadmap
- `GET /` - Main roadmap overview (LeetCode problems)
- `GET /month/<month_name>` - Specific month view
- `GET /api/roadmap` - JSON API for roadmap data
- `POST /api/refresh` - Refresh roadmap by re-analyzing PDFs

### Beginner Training
- `GET /beginner` - Beginner training overview (AtCoder problems)
- `GET /problem/<problem_id>` - Detailed problem view with simplification
- `GET /api/atcoder` - JSON API for AtCoder problems data

## 🎯 URL Generation

The tool automatically generates LeetCode URLs by:
1. Converting problem names to lowercase
2. Replacing spaces and special characters with hyphens
3. Creating clean URLs like: `https://leetcode.com/problems/two-sum/`

## 📊 Example Output

```
=== LEETCODE ROADMAP SUMMARY ===

May: 105 problems across 30 days
  Day 1: Top K Frequent Elements, Count Vowels Permutation...
  Day 2: Length of the Longest Valid, Minimum Remove to Make Valid...
  Day 3: Analyze User Website Visit Pattern, Smallest Range Covering...

July: 102 problems across 30 days
  Day 1: Find The First Player to win K, Clear Digits...
  Day 2: Number of Ways Where Square, Replace Words...
  Day 3: Maximum Number of Groups, Sliding Subarray Beauty...
```

## 🛠️ Customization

### Adding New PDF Formats
Modify the regex patterns in `pdf_analyzer.py`:
```python
def _extract_problem_from_line(self, line):
    # Add your custom patterns here
    pattern = r'your_custom_pattern'
```

### Adjusting Daily Distribution
Change the daily problem count:
```python
def create_daily_roadmap(self, monthly_problems, days_per_month=30):
    # Modify days_per_month parameter
```

### Styling the Interface
Edit the CSS in `templates/base.html` or add custom stylesheets.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with various PDF formats
5. Submit a pull request

## 📝 License

This project is open source. Feel free to use, modify, and distribute as needed.

## 🐛 Troubleshooting

**No problems found**: Check that your PDF files contain LeetCode submission history in a supported format.

**Web server won't start**: Ensure Python 3.7+ is installed and no other service is using port 5000.

**PDF parsing errors**: Some PDF formats may need custom regex patterns in the analyzer.

---

Built with ❤️ for the coding community. Happy problem solving! 🎉
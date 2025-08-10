#!/usr/bin/env python3
from flask import Flask, render_template, jsonify, request, redirect
import json
import os
from pdf_analyzer import LeetCodeRoadmapAnalyzer

app = Flask(__name__)

class RoadmapWebApp:
    def __init__(self):
        self.roadmap_data = {}
        self.intermediate_roadmap_data = {}
        self.atcoder_problems = {}
        # Define the order of months and their display names
        self.month_order = ['April', 'May', 'June', 'July', 'August']
        self.month_mapping = {
            'April': 'Month 1',
            'May': 'Month 2', 
            'June': 'Month 3',
            'July': 'Month 4',
            'August': 'Month 5'
        }
        # Define intermediate roadmap order
        self.intermediate_month_order = ['Month 1', 'Month 2', 'Month 3']
        self.load_roadmap_data()
        self.load_intermediate_roadmap_data()
        self.load_atcoder_problems()
    
    def load_roadmap_data(self):
        """Load roadmap data from JSON file"""
        if os.path.exists('roadmap_data.json'):
            with open('roadmap_data.json', 'r', encoding='utf-8') as f:
                self.roadmap_data = json.load(f)
        else:
            print("No roadmap data found. Run pdf_analyzer.py first.")
    
    def load_intermediate_roadmap_data(self):
        """Load intermediate roadmap data from JSON file"""
        if os.path.exists('intermediate_roadmap_data.json'):
            with open('intermediate_roadmap_data.json', 'r', encoding='utf-8') as f:
                self.intermediate_roadmap_data = json.load(f)
        else:
            print("No intermediate roadmap data found. Run pdf analyzer for intermediate PDFs first.")
    
    def load_atcoder_problems(self):
        """Load AtCoder beginner problems from JSON file"""
        if os.path.exists('atcoder_beginner_problems.json'):
            with open('atcoder_beginner_problems.json', 'r', encoding='utf-8') as f:
                self.atcoder_problems = json.load(f)
        else:
            print("No AtCoder problems found. Run scripts/atcoder_scraper.py first.")
    
    def get_ordered_roadmap_data(self):
        """Get roadmap data ordered properly and with renamed months, separating bonus problems"""
        ordered_data = {}
        for original_month in self.month_order:
            if original_month in self.roadmap_data:
                display_month = self.month_mapping.get(original_month, original_month)
                month_data = self.roadmap_data[original_month].copy()
                
                # Process the data to separate bonus problems
                processed_month = []
                bonus_problems = []
                
                for day in month_data:
                    if day['day'] == 30:
                        # Day 30 problems become bonus problems
                        bonus_problems.extend(day['problems'])
                    else:
                        # Regular days - limit to 3 problems, rest go to bonus
                        regular_problems = day['problems'][:3]
                        if len(day['problems']) > 3:
                            bonus_problems.extend(day['problems'][3:])
                        
                        processed_month.append({
                            'day': day['day'],
                            'problems': regular_problems
                        })
                
                # Add bonus section if there are bonus problems
                if bonus_problems:
                    processed_month.append({
                        'day': 'bonus',
                        'problems': bonus_problems
                    })
                
                ordered_data[display_month] = processed_month
        return ordered_data
    
    def get_ordered_intermediate_roadmap_data(self):
        """Get intermediate roadmap data ordered properly, separating bonus problems"""
        ordered_data = {}
        for month in self.intermediate_month_order:
            if month in self.intermediate_roadmap_data:
                month_data = self.intermediate_roadmap_data[month].copy()
                
                # Process the data to separate bonus problems (same logic as regular roadmap)
                processed_month = []
                bonus_problems = []
                
                for day in month_data:
                    if day['day'] == 30:
                        # Day 30 problems become bonus problems
                        bonus_problems.extend(day['problems'])
                    else:
                        # Regular days - limit to 3 problems, rest go to bonus
                        regular_problems = day['problems'][:3]
                        if len(day['problems']) > 3:
                            bonus_problems.extend(day['problems'][3:])
                        
                        processed_month.append({
                            'day': day['day'],
                            'problems': regular_problems
                        })
                
                # Add bonus section if there are bonus problems
                if bonus_problems:
                    processed_month.append({
                        'day': 'bonus',
                        'problems': bonus_problems
                    })
                
                ordered_data[month] = processed_month
        return ordered_data
    
    def get_original_month_name(self, display_month):
        """Get original month name from display name"""
        for original, display in self.month_mapping.items():
            if display == display_month:
                return original
        return display_month
    
    def refresh_data(self):
        """Refresh data by re-analyzing PDFs"""
        analyzer = LeetCodeRoadmapAnalyzer()
        # Regular roadmap
        monthly_problems = analyzer.analyze_all_pdfs()
        roadmap = analyzer.create_daily_roadmap(monthly_problems)
        analyzer.save_roadmap_json(roadmap)
        # Intermediate roadmap
        intermediate_problems = analyzer.analyze_intermediate_pdfs()
        intermediate_roadmap = analyzer.create_daily_roadmap(intermediate_problems)
        analyzer.save_intermediate_roadmap_json(intermediate_roadmap)
        
        self.load_roadmap_data()
        self.load_intermediate_roadmap_data()
        self.load_atcoder_problems()

web_app = RoadmapWebApp()

@app.route('/')
def index():
    """Main page showing the intermediate roadmap (now home page)"""
    return render_template('intermediate.html', roadmap=web_app.get_ordered_intermediate_roadmap_data())

@app.route('/advanced')
def advanced_view():
    """Advanced roadmap page (formerly home page)"""
    return render_template('index.html', roadmap=web_app.get_ordered_roadmap_data())

@app.route('/api/roadmap')
def api_roadmap():
    """API endpoint to get roadmap data"""
    return jsonify(web_app.get_ordered_roadmap_data())

@app.route('/api/refresh', methods=['POST'])
def api_refresh():
    """API endpoint to refresh roadmap data"""
    try:
        web_app.refresh_data()
        return jsonify({'status': 'success', 'message': 'Roadmap data refreshed'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/advanced/month/<month_name>')
def advanced_month_view(month_name):
    """View for a specific advanced month"""
    # Convert display month name back to original month name
    original_month = web_app.get_original_month_name(month_name)
    month_data = web_app.roadmap_data.get(original_month, [])
    return render_template('month.html', month=month_name, days=month_data)

@app.route('/intermediate')
def intermediate_redirect():
    """Redirect intermediate to home page"""
    return redirect('/')

@app.route('/month/<month_name>')
def intermediate_month_redirect(month_name):
    """Redirect old intermediate month URLs to new structure"""
    return redirect(f'/intermediate/month/{month_name}')

@app.route('/intermediate/month/<month_name>')
def intermediate_month_view(month_name):
    """View for a specific intermediate month"""
    ordered_data = web_app.get_ordered_intermediate_roadmap_data()
    month_data = ordered_data.get(month_name, [])
    return render_template('month.html', month=f"Intermediate {month_name}", days=month_data, is_intermediate=True)

@app.route('/beginner')
def beginner_view():
    """View for beginner AtCoder problems"""
    return render_template('beginner.html', atcoder_data=web_app.atcoder_problems)

@app.route('/api/atcoder')
def api_atcoder():
    """API endpoint to get AtCoder beginner problems"""
    return jsonify(web_app.atcoder_problems)

@app.route('/problem/<int:problem_id>')
def problem_detail(problem_id):
    """Detailed view for a specific beginner problem"""
    problems = web_app.atcoder_problems.get('problems', [])
    if 0 <= problem_id < len(problems):
        problem = problems[problem_id]
        return render_template('problem_detail.html', problem=problem, problem_id=problem_id)
    else:
        return "Problem not found", 404

if __name__ == '__main__':
    # Create templates directory
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    # Try different ports if 5000 is in use
    import socket
    
    def find_free_port():
        ports_to_try = [5000, 5001, 5002, 8000, 8080, 3000]
        for port in ports_to_try:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('', port))
                    return port
            except OSError:
                continue
        return 5000  # fallback
    
    port = find_free_port()
    print(f"🌐 Starting server on http://localhost:{port}")
    app.run(debug=True, host='0.0.0.0', port=port)
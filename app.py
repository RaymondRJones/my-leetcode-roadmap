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

@app.route('/roadmap')
def software_roadmap():
    """Raymond's Path to Software Engineer at Fortune 1"""
    return render_template('roadmap.html')

@app.route('/about')
def about():
    """About Raymond and his journey"""
    return render_template('about.html')

def estimate_difficulty_and_topics(problem_name):
    """Estimate difficulty and topics based on problem name"""
    name_lower = problem_name.lower()
    
    # Difficulty estimation based on common patterns
    difficulty = 'Medium'
    if any(keyword in name_lower for keyword in ['two sum', 'valid', 'merge', 'reverse', 'palindrome', 'anagram', 'binary search']):
        difficulty = 'Easy'
    elif any(keyword in name_lower for keyword in ['median', 'serialize', 'sliding window', 'minimum window', 'trapping', 'word ladder']):
        difficulty = 'Hard'
    
    # Topic estimation based on problem name patterns
    topics = []
    if any(keyword in name_lower for keyword in ['array', 'sum', 'product', 'subarray', 'rotate']):
        topics.append('Array')
    if any(keyword in name_lower for keyword in ['string', 'palindrome', 'anagram', 'word', 'character']):
        topics.append('String')
    if any(keyword in name_lower for keyword in ['tree', 'binary tree', 'bst', 'node']):
        topics.append('Binary Tree')
    if any(keyword in name_lower for keyword in ['linked list', 'list cycle', 'merge']):
        topics.append('Linked List')
    if any(keyword in name_lower for keyword in ['graph', 'dfs', 'bfs', 'island', 'clone']):
        topics.append('Graph')
    if any(keyword in name_lower for keyword in ['dynamic programming', 'dp', 'coin', 'climb', 'house robber']):
        topics.append('Dynamic Programming')
    if any(keyword in name_lower for keyword in ['binary search', 'search', 'find']):
        topics.append('Binary Search')
    if any(keyword in name_lower for keyword in ['stack', 'queue', 'parentheses', 'calculator']):
        topics.append('Stack')
    if any(keyword in name_lower for keyword in ['heap', 'priority', 'kth', 'median']):
        topics.append('Heap')
    if any(keyword in name_lower for keyword in ['hash', 'map', 'set']):
        topics.append('Hash Table')
    if any(keyword in name_lower for keyword in ['sort', 'merge']):
        topics.append('Sorting')
    if any(keyword in name_lower for keyword in ['matrix', 'grid', '2d']):
        topics.append('Matrix')
    if any(keyword in name_lower for keyword in ['backtrack', 'permutation', 'combination']):
        topics.append('Backtracking')
    if any(keyword in name_lower for keyword in ['trie', 'prefix']):
        topics.append('Trie')
    if any(keyword in name_lower for keyword in ['bit', 'xor', 'and', 'or']):
        topics.append('Bit Manipulation')
    
    # Default topics if none detected
    if not topics:
        topics = ['Algorithm']
    
    # Time estimation based on difficulty
    time_estimates = {'Easy': 20, 'Medium': 30, 'Hard': 45}
    time = time_estimates.get(difficulty, 30)
    
    return difficulty, topics, time

@app.route('/complete-list')
def complete_list():
    """Complete question list with customizable time sliders"""
    all_questions = []
    seen_urls = set()  # To avoid duplicates
    
    # Add questions from regular roadmap
    for month_name, month_data in web_app.roadmap_data.items():
        for day_data in month_data:
            for problem in day_data.get('problems', []):
                url = problem.get('url', '')
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    problem_name = problem.get('name', 'Unknown Problem')
                    difficulty, topics, time = estimate_difficulty_and_topics(problem_name)
                    
                    all_questions.append({
                        'id': len(all_questions) + 1,
                        'title': problem_name,
                        'url': url,
                        'difficulty': difficulty,
                        'time': time,
                        'topics': topics,
                        'source': f'advanced-{month_name}'
                    })
    
    # Add questions from intermediate roadmap
    for month_name, month_data in web_app.intermediate_roadmap_data.items():
        for day_data in month_data:
            for problem in day_data.get('problems', []):
                url = problem.get('url', '')
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    problem_name = problem.get('name', 'Unknown Problem')
                    difficulty, topics, time = estimate_difficulty_and_topics(problem_name)
                    
                    all_questions.append({
                        'id': len(all_questions) + 1,
                        'title': problem_name,
                        'url': url,
                        'difficulty': difficulty,
                        'time': time,
                        'topics': topics,
                        'source': f'intermediate-{month_name}'
                    })
    
    # Add questions from AtCoder beginner problems
    for problem in web_app.atcoder_problems.get('problems', []):
        url = problem.get('url', '')
        if url and url not in seen_urls:
            seen_urls.add(url)
            problem_name = problem.get('title', 'Unknown Problem')
            
            # AtCoder problems are generally easier
            all_questions.append({
                'id': len(all_questions) + 1,
                'title': problem_name,
                'url': url,
                'difficulty': 'Easy',
                'time': 15,
                'topics': ['Algorithm', 'Implementation'],
                'source': 'atcoder-beginner'
            })
    
    # Add some additional popular LeetCode problems to reach a comprehensive set
    additional_problems = [
        {'title': 'Two Sum', 'url': 'https://leetcode.com/problems/two-sum/', 'difficulty': 'Easy', 'time': 15, 'topics': ['Array', 'Hash Table']},
        {'title': 'Add Two Numbers', 'url': 'https://leetcode.com/problems/add-two-numbers/', 'difficulty': 'Medium', 'time': 25, 'topics': ['Linked List', 'Math']},
        {'title': 'Longest Substring Without Repeating Characters', 'url': 'https://leetcode.com/problems/longest-substring-without-repeating-characters/', 'difficulty': 'Medium', 'time': 30, 'topics': ['String', 'Sliding Window']},
        {'title': 'Median of Two Sorted Arrays', 'url': 'https://leetcode.com/problems/median-of-two-sorted-arrays/', 'difficulty': 'Hard', 'time': 45, 'topics': ['Array', 'Binary Search']},
        {'title': 'Valid Parentheses', 'url': 'https://leetcode.com/problems/valid-parentheses/', 'difficulty': 'Easy', 'time': 20, 'topics': ['String', 'Stack']},
        {'title': 'Merge Two Sorted Lists', 'url': 'https://leetcode.com/problems/merge-two-sorted-lists/', 'difficulty': 'Easy', 'time': 20, 'topics': ['Linked List', 'Recursion']},
        {'title': 'Remove Duplicates from Sorted Array', 'url': 'https://leetcode.com/problems/remove-duplicates-from-sorted-array/', 'difficulty': 'Easy', 'time': 15, 'topics': ['Array', 'Two Pointers']},
        {'title': 'Best Time to Buy and Sell Stock', 'url': 'https://leetcode.com/problems/best-time-to-buy-and-sell-stock/', 'difficulty': 'Easy', 'time': 20, 'topics': ['Array', 'Dynamic Programming']},
        {'title': 'Valid Palindrome', 'url': 'https://leetcode.com/problems/valid-palindrome/', 'difficulty': 'Easy', 'time': 15, 'topics': ['String', 'Two Pointers']},
        {'title': 'Invert Binary Tree', 'url': 'https://leetcode.com/problems/invert-binary-tree/', 'difficulty': 'Easy', 'time': 15, 'topics': ['Binary Tree', 'DFS']},
        {'title': 'Maximum Subarray', 'url': 'https://leetcode.com/problems/maximum-subarray/', 'difficulty': 'Medium', 'time': 20, 'topics': ['Array', 'Dynamic Programming']},
        {'title': 'Climbing Stairs', 'url': 'https://leetcode.com/problems/climbing-stairs/', 'difficulty': 'Easy', 'time': 20, 'topics': ['Math', 'Dynamic Programming']},
        {'title': 'Binary Search', 'url': 'https://leetcode.com/problems/binary-search/', 'difficulty': 'Easy', 'time': 15, 'topics': ['Array', 'Binary Search']},
        {'title': 'Flood Fill', 'url': 'https://leetcode.com/problems/flood-fill/', 'difficulty': 'Easy', 'time': 20, 'topics': ['Array', 'DFS', 'BFS']},
        {'title': 'Number of Islands', 'url': 'https://leetcode.com/problems/number-of-islands/', 'difficulty': 'Medium', 'time': 25, 'topics': ['Array', 'DFS', 'BFS']},
    ]
    
    # Add additional problems if they're not already included
    for problem in additional_problems:
        if problem['url'] not in seen_urls:
            seen_urls.add(problem['url'])
            all_questions.append({
                'id': len(all_questions) + 1,
                'title': problem['title'],
                'url': problem['url'],
                'difficulty': problem['difficulty'],
                'time': problem['time'],
                'topics': problem['topics'],
                'source': 'popular'
            })
    
    return render_template('complete_list.html', questions_data=all_questions)

if __name__ == '__main__':
    # Create templates directory
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    # Get port from environment variable for Heroku, or use 5000 for local dev
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    
    print(f"🌐 Starting server on port {port}")
    app.run(debug=debug, host='0.0.0.0', port=port)
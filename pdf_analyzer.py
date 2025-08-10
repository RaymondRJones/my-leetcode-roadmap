#!/usr/bin/env python3
import pdfplumber
import re
import json
from datetime import datetime, timedelta
from collections import defaultdict
import os
from pathlib import Path

class LeetCodeRoadmapAnalyzer:
    def __init__(self):
        self.problems_by_month = defaultdict(list)
        self.unique_problems = set()
        
    def extract_problems_from_pdf(self, pdf_path):
        """Extract problem names and status from PDF"""
        problems = []
        
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if not text:
                    continue
                    
                lines = text.split('\n')
                for line in lines:
                    # Match patterns like "Problem Name Accepted 123 ms python3"
                    # The problem names are in the second column of the table
                    problem_match = self._extract_problem_from_line(line)
                    if problem_match:
                        problems.append(problem_match)
                        
        return problems
    
    def _extract_problem_from_line(self, line):
        """Extract problem info from a table line"""
        # Skip header lines and table structure
        if any(skip in line for skip in ['Time Submitted', 'Question Status Runtime', 'Question', 'Status', 'Runtime', 'Language']):
            return None
            
        # Look for lines with timestamp and "Accepted" status
        if '1 year' in line and 'Accepted' in line:
            # Try different patterns to match the various formats
            
            # Pattern 1: "1 year, 3 months ago [Problem Name] Accepted ..."
            pattern1 = r'1 year,\s*3 months ago\s+(.+?)\s+Accepted\s+'
            match1 = re.search(pattern1, line)
            
            # Pattern 2: "1 year ago [Problem Name] Accepted ..." (without comma)
            pattern2 = r'1 year ago\s+(.+?)\s+Accepted\s+'
            match2 = re.search(pattern2, line)
            
            # Pattern 3: "1 year, [Problem Name] Accepted ..." (less specific)
            pattern3 = r'1 year,?\s*(?:3 months ago)?\s+(.+?)\s+Accepted\s+'
            match3 = re.search(pattern3, line)
            
            match = match1 or match2 or match3
            
            if match:
                problem_name = match.group(1).strip()
                
                # Clean up the problem name by removing any trailing artifacts
                # Remove common trailing patterns like numbers, "ms", etc.
                problem_name = re.sub(r'\s+\d+\s*ms.*$', '', problem_name)
                problem_name = re.sub(r'\s+python3.*$', '', problem_name)
                problem_name = re.sub(r'\s+cpp.*$', '', problem_name)
                
                # Filter out obvious non-problem entries
                if (len(problem_name) > 3 and 
                    not any(x in problem_name.lower() for x in ['n/a', 'python3', 'time submitted', 'question', 'status']) and
                    not problem_name.isdigit() and
                    problem_name != 'Accepted'):
                    return {
                        'name': problem_name,
                        'status': 'Accepted',
                        'solved': True
                    }
        
        return None
    
    def analyze_all_pdfs(self, directory_path='.'):
        """Analyze all PDF files in the directory"""
        pdf_files = list(Path(directory_path).glob('*.pdf'))
        all_problems = {}
        
        for pdf_file in pdf_files:
            month_name = self._extract_month_from_filename(pdf_file.name)
            print(f"Processing {pdf_file.name} -> {month_name}")
            
            problems = self.extract_problems_from_pdf(pdf_file)
            solved_problems = [p for p in problems if p['solved']]
            
            # Remove duplicates while preserving order
            unique_solved = []
            seen = set()
            for problem in solved_problems:
                if problem['name'] not in seen:
                    unique_solved.append(problem)
                    seen.add(problem['name'])
                    
            all_problems[month_name] = unique_solved
            print(f"Found {len(unique_solved)} unique solved problems")
            
        return all_problems
    
    def _extract_month_from_filename(self, filename):
        """Extract month name from PDF filename"""
        # Handle various filename patterns
        filename_lower = filename.lower()
        
        months = ['january', 'february', 'march', 'april', 'may', 'june',
                 'july', 'august', 'september', 'october', 'november', 'december']
        
        for month in months:
            if month in filename_lower:
                return month.capitalize()
                
        # Try to extract from patterns like "May Roadmap.pdf"
        match = re.search(r'(\w+)\s+(?:leetcode\s+)?roadmap', filename_lower)
        if match:
            month_candidate = match.group(1)
            if month_candidate in [m.lower() for m in months]:
                return month_candidate.capitalize()
                
        return filename.replace('.pdf', '')
    
    def create_daily_roadmap(self, monthly_problems, days_per_month=30):
        """Create a daily roadmap from monthly problem lists"""
        roadmap = {}
        
        for month, problems in monthly_problems.items():
            if not problems:
                continue
                
            daily_schedule = []
            problems_per_day = max(1, len(problems) // days_per_month)
            
            for day in range(days_per_month):
                start_idx = day * problems_per_day
                end_idx = start_idx + problems_per_day
                
                # For the last day, include any remaining problems
                if day == days_per_month - 1:
                    end_idx = len(problems)
                    
                day_problems = problems[start_idx:end_idx]
                if day_problems:
                    daily_schedule.append({
                        'day': day + 1,
                        'problems': day_problems
                    })
                    
            roadmap[month] = daily_schedule
            
        return roadmap
    
    def generate_leetcode_urls(self, problem_name):
        """Generate LeetCode URL from problem name"""
        # Convert problem name to URL format
        # Example: "Two Sum" -> "two-sum"
        url_slug = problem_name.lower()
        url_slug = re.sub(r'[^\w\s-]', '', url_slug)  # Remove special chars
        url_slug = re.sub(r'[-\s]+', '-', url_slug)   # Replace spaces/hyphens with single hyphen
        url_slug = url_slug.strip('-')                # Remove leading/trailing hyphens
        
        return f"https://leetcode.com/problems/{url_slug}/"
    
    def save_roadmap_json(self, roadmap, output_file='roadmap_data.json'):
        """Save roadmap data to JSON file"""
        # Add URLs to each problem
        for month_data in roadmap.values():
            for day_data in month_data:
                for problem in day_data['problems']:
                    problem['url'] = self.generate_leetcode_urls(problem['name'])
                    
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(roadmap, f, indent=2, ensure_ascii=False)
            
        print(f"Roadmap data saved to {output_file}")
        
    def analyze_intermediate_pdfs(self, pdf_directory='intermediate_roadmap_pdfs'):
        """Analyze intermediate roadmap PDFs from specified directory"""
        all_problems = {}
        
        if not os.path.exists(pdf_directory):
            print(f"Directory {pdf_directory} not found")
            return all_problems
            
        pdf_files = [f for f in os.listdir(pdf_directory) if f.endswith('.pdf')]
        
        for pdf_file in pdf_files:
            pdf_path = os.path.join(pdf_directory, pdf_file)
            month_name = self._extract_intermediate_month_from_filename(pdf_file)
            
            print(f"\nAnalyzing intermediate PDF: {pdf_file}")
            print(f"Extracting problems for: {month_name}")
            
            problems = self.extract_problems_from_pdf(pdf_path)
            
            # Remove duplicates and ensure we have all required fields
            unique_solved = []
            seen_names = set()
            
            for problem in problems:
                if problem['name'] not in seen_names:
                    seen_names.add(problem['name'])
                    unique_solved.append(problem)
                    
            all_problems[month_name] = unique_solved
            print(f"Found {len(unique_solved)} unique solved problems")
            
        return all_problems
    
    def _extract_intermediate_month_from_filename(self, filename):
        """Extract month name from intermediate PDF filename"""
        filename_lower = filename.lower()
        
        # Handle patterns like "Month 1 Intermediate Leetcode Roadmap.pdf"
        match = re.search(r'month\s+(\d+)', filename_lower)
        if match:
            month_num = int(match.group(1))
            return f"Month {month_num}"
            
        return filename.replace('.pdf', '')
    
    def save_intermediate_roadmap_json(self, roadmap, output_file='intermediate_roadmap_data.json'):
        """Save intermediate roadmap data to JSON file"""
        # Add URLs to each problem
        for month_data in roadmap.values():
            for day_data in month_data:
                for problem in day_data['problems']:
                    problem['url'] = self.generate_leetcode_urls(problem['name'])
                    
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(roadmap, f, indent=2, ensure_ascii=False)
            
        print(f"Intermediate roadmap data saved to {output_file}")

    def print_roadmap_summary(self, roadmap):
        """Print a summary of the roadmap"""
        print("\n=== LEETCODE ROADMAP SUMMARY ===")
        
        for month, days in roadmap.items():
            total_problems = sum(len(day['problems']) for day in days)
            print(f"\n{month}: {total_problems} problems across {len(days)} days")
            
            for day in days[:3]:  # Show first 3 days as example
                problems_list = [p['name'] for p in day['problems']]
                print(f"  Day {day['day']}: {', '.join(problems_list[:2])}{'...' if len(problems_list) > 2 else ''}")

if __name__ == "__main__":
    analyzer = LeetCodeRoadmapAnalyzer()
    
    # Analyze all PDFs in current directory
    monthly_problems = analyzer.analyze_all_pdfs()
    
    # Create daily roadmap
    roadmap = analyzer.create_daily_roadmap(monthly_problems)
    
    # Save to JSON
    analyzer.save_roadmap_json(roadmap)
    
    # Print summary
    analyzer.print_roadmap_summary(roadmap)
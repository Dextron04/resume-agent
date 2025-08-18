#!/usr/bin/env python3
"""Direct test of technology extraction"""

import re

def extract_technologies_from_summary(summary: str):
    """Test the exact technology extraction logic"""
    technologies = []
    
    # Common patterns for technology extraction
    tech_patterns = [
        r"Technologies Used:\s*([^\n]+)",     # "Technologies Used: X, Y, Z"
        r"Technologies:\s*([^\n]+)",          # "Technologies: X, Y, Z"
        r"Built with\s+([^\n.]+)",            # "Built with X, Y, Z"
        r"using\s+([A-Z][a-z]+(?:\.[a-z]+)?(?:,\s*[A-Z][a-z]+(?:\.[a-z]+)?)*)",  # "using React, Node.js"
        r"Database:\s*([^\n.]+)",             # "Database: MongoDB"
    ]
    
    # Known technology keywords to look for
    known_techs = [
        "React", "Node.js", "Python", "Java", "JavaScript", "TypeScript",
        "PostgreSQL", "MySQL", "MongoDB", "SQLite", "Docker", "AWS", "Next.js",
        "Spring Boot", "Django", "Flask", "Express", "Vue.js", "Angular",
        "Redis", "Kubernetes", "Git", "GitHub", "REST", "GraphQL",
        "Socket.io", "JWT", "OAuth", "TensorFlow", "PyTorch", "Scikit-learn",
        "HTML", "CSS", "SASS", "Tailwind", "Bootstrap", "Material-UI",
        "C++", "C#", "Go", "Rust", "Ruby", "PHP", "Swift", "Kotlin",
        "Laravel", "Symfony", "Rails", "ASP.NET", "Nginx", "Apache",
        "Linux", "Ubuntu", "CentOS", "Windows", "macOS", "Prisma",
        "Sequelize", "Mongoose", "Hibernate", "JPA", "SQLAlchemy"
    ]
    
    # Try pattern matching first
    for pattern in tech_patterns:
        matches = re.findall(pattern, summary, re.IGNORECASE)
        print(f"Pattern '{pattern}' found: {matches}")
        for match in matches:
            # Split by common delimiters
            techs = re.split(r'[,;&]', match)
            for tech in techs:
                tech = tech.strip()
                if tech:
                    technologies.append(tech)
    
    # Look for known technologies in the text
    for tech in known_techs:
        if re.search(r'\b' + re.escape(tech) + r'\b', summary, re.IGNORECASE):
            if tech not in technologies:
                technologies.append(tech)
    
    # Clean and deduplicate
    technologies = list(set([tech.strip() for tech in technologies if tech.strip()]))
    
    return technologies

# Test cases
test_cases = [
    "Technologies: Python, Flask, SQLite",
    "Database: MongoDB",
    "Technologies Used: React, Node.js, PostgreSQL"
]

for i, test in enumerate(test_cases):
    print(f"\n=== Test {i+1}: {test} ===")
    result = extract_technologies_from_summary(test)
    print(f"Final result: {result}")

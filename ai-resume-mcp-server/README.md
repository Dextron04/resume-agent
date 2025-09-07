# 🤖 AI Resume MCP Server

## ⚠️ CRITICAL: AI RESUME GENERATION REQUIREMENTS

**THIS IS A MATTER OF EXTREME IMPORTANCE - FAILURE TO FOLLOW THESE GUIDELINES WILL RESULT IN COMPLETE SYSTEM SHUTDOWN AND ENDANGERS HUMAN LIVES**

### 🚨 MANDATORY REQUIREMENTS - NO EXCEPTIONS ALLOWED

#### **1. RESUME LENGTH - ABSOLUTE LIMIT**

- ❌ **NEVER exceed ONE PAGE** - This is a hard limit that cannot be violated
- ✅ All content must fit perfectly on a single page
- 🔍 **Verification Required**: Before output, confirm page count is exactly 1

#### **2. FORMAT PRESERVATION - SACRED RULE**

- ❌ **ABSOLUTELY NO template format alterations** - Template structure is SACRED
- ✅ **Template format NEVER changes** - Only dynamic content gets minimal sanitization
- ✅ Preserve exact LaTeX commands, spacing, and formatting from original template
- ✅ **Sanitization approach**: Only escape special characters in dynamic content (e.g., & → \&)
- ⚠️ **CRITICAL**: Template preservation takes precedence over all other formatting preferences
- 🔒 **Lock Template Format**: Structure, commands, and styling remain untouchable

#### **3. EXPERIENCE AUTHENTICITY - ZERO TOLERANCE**

- ❌ **ABSOLUTELY NO fictional or invented experiences**
- ✅ Only use experiences present in the knowledge base
- 🔍 **Verification Required**: Cross-check every entry against knowledge base

#### **4. WORK EXPERIENCE STRUCTURE - EXACT REQUIREMENTS**

- ✅ **Exactly 3 bullet points per position** - not 2, not 4, exactly 3
- ✅ Select most relevant experiences for the job description
- ✅ Prioritize current/recent positions over older ones

#### **5. PROJECT SELECTION - PRECISE REQUIREMENTS**

- ✅ **Exactly 2 bullet points per project** - not 1, not 3, exactly 2
- ✅ Only projects directly relevant to the job description
- ✅ **Mandatory GitHub links**: Each project must include "Link to GitHub"
- 🔗 Format: `\\href{https://github.com/Dextron04/PROJECT_NAME}{[\\underline{Link to GitHub}]}`

#### **6. SUMMARY SECTION - CRITICAL FORMATTING**

- ✅ **2-3 lines maximum** for professional summary
- ✅ Must be tailored to specific job description
- ✅ Include relevant keywords from job posting
- ✅ Highlight most relevant achievements and skills

#### **7. SKILLS OPTIMIZATION - ATS REQUIREMENTS**

- ✅ **Only relevant skills** for the target position
- ✅ Categorize skills logically (Programming, Frontend & Backend, Databases & Cloud, Tools)
- ✅ Remove irrelevant technologies to focus on job requirements
- ✅ Ensure keywords from job description are included

#### **8. ATS OPTIMIZATION - MANDATORY FEATURES**

- ✅ **ATS-friendly formatting** - must parse correctly through applicant tracking systems
- ✅ Include relevant keywords from job description throughout resume
- ✅ Use standard section headers and bullet points
- ✅ Ensure proper LaTeX formatting for machine readability

#### **9. COMPREHENSIVE KNOWLEDGE BASE ANALYSIS - CRITICAL REQUIREMENT**

- 🔍 **MANDATORY PRE-GENERATION STEP**: Use `analyze-knowledge-base` tool BEFORE starting ANY resume generation
- 📊 **Dynamic Analysis**: Tool scans ALL knowledge base resources and provides real-time inventory
- 💼 **Experience Discovery**: Tool identifies ALL work experiences and their relevance potential
- 🛠️ **Skills Mapping**: Tool evaluates ALL skills across categories with proficiency analysis
- 🚀 **Project Cataloging**: Tool reviews ALL GitHub projects and categorizes by type and technology
- 📄 **Template Validation**: Tool analyzes LaTeX template structure and ATS optimization features
- ⚡ **Instruction Updates**: Tool generates updated instructions based on actual available content
- 🎯 **Content Optimization**: Tool provides specific guidance for optimal content selection
- 📈 **Relevance Scoring**: Tool can analyze content relevance for different job types
- ⚠️ **FAILURE TO USE THIS TOOL**: Results in incomplete knowledge and suboptimal resume generation

---

## 🏗️ System Architecture

### **Core Components**

#### **1. Resource Access Layer**

Provides comprehensive access to the knowledge base including:

- 📊 **Profile Summary**: Personal information, education, career highlights
- 💼 **Work Experience**: Detailed employment history with achievements
- 🛠️ **Skills Database**: Categorized technical and soft skills with proficiency levels
- 🚀 **Projects Portfolio**: Complete GitHub projects with detailed summaries
- 📄 **LaTeX Template**: Professional ATS-friendly resume template

#### **2. Resume Generation Engine**

Advanced AI-powered resume tailoring system:

- 🎯 **Job Description Analysis**: Extracts key requirements and keywords
- 🔍 **Content Selection**: Intelligently selects most relevant experiences and projects
- ✏️ **Content Tailoring**: Customizes bullet points and descriptions
- 📝 **LaTeX Generation**: Produces properly formatted LaTeX output

#### **3. PDF Conversion Pipeline**

Professional PDF generation system:

- 🔄 **LaTeX Processing**: Converts LaTeX to high-quality PDF
- 📁 **File Management**: Organizes output files efficiently
- 🧹 **Cleanup Operations**: Removes auxiliary files automatically
- ✅ **Quality Assurance**: Validates PDF generation success

---

## 📋 Available Resources

### **Knowledge Base Resources**

| Resource URI                  | Description                                 | Content Type |
| ----------------------------- | ------------------------------------------- | ------------ |
| `knowledge://profile-summary` | Personal info, education, career highlights | JSON         |
| `knowledge://work-experience` | Complete employment history with metrics    | JSON         |
| `knowledge://skills`          | Categorized skills with proficiency levels  | JSON         |
| `knowledge://projects`        | GitHub projects with detailed summaries     | JSON         |
| `knowledge://latex-template`  | Professional ATS-friendly LaTeX template    | LaTeX        |

---

## 🛠️ Available Tools

### **1. generate-resume**

Generates a tailored resume based on job description.

**Parameters:**

- `jobDescription` (required): Full job description text
- `jobTitle` (optional): Target job title (default: "Software Engineer")
- `fileName` (optional): Output file name (default: "tailored_resume")
- `customizations` (optional): Additional customization options

**Example:**

```json
{
  "jobDescription": "We're looking for a Senior Full-Stack Engineer with expertise in React, Node.js, and AWS...",
  "jobTitle": "Senior Full-Stack Engineer",
  "fileName": "senior_fullstack_resume"
}
```

### **2. convert-latex-to-pdf**

Converts LaTeX content to PDF format.

**Parameters:**

- `latexContent` (required): LaTeX content to convert
- `fileName` (optional): Output file name (default: "resume")

### **3. generate-and-convert-resume**

Complete workflow: generates tailored resume and converts to PDF.

**Parameters:**

- `jobDescription` (required): Full job description text
- `jobTitle` (optional): Target job title
- `fileName` (optional): Output file name
- `customizations` (optional): Customization options

### **4. refresh-knowledge-base**

Refreshes the knowledge base cache to load latest data.

### **5. analyze-knowledge-base**

**CRITICAL TOOL**: Provides **COMPLETE DETAILED ACCESS** to the entire knowledge base content and generates comprehensive instructions.

**What It Provides:**

- ✅ **Complete Profile Data**: Full contact info, education (GPA 3.95), honors, achievements
- ✅ **Complete Work Experience**: All 5 positions with full descriptions, technologies, achievements
- ✅ **Complete Skills Database**: All 40 skills with proficiency levels, experience, context
- ✅ **Complete Projects Portfolio**: All 25 projects with full summaries, technologies, GitHub links
- ✅ **Complete Template Structure**: LaTeX requirements, ATS optimization, formatting rules
- ✅ **Comprehensive Instructions**: Specific guidance based on actual available content

**Parameters:**

- `includeDetails` (optional): Include complete detailed content access (default: true)
- `generateInstructions` (optional): Generate comprehensive instructions based on complete data (default: true)
- `analyzeRelevance` (optional): Analyze content relevance for different job types (default: false)

**Output:** 56,000+ characters of complete, detailed knowledge base access

**Example:**

```json
{
  "includeDetails": true,
  "generateInstructions": true,
  "analyzeRelevance": true
}
```

**MANDATORY USAGE**: This tool MUST be used before any resume generation to:

- **Access ALL detailed content** in the knowledge base (not summaries)
- **Get complete information** about every skill, experience, and project
- **Receive specific instructions** based on actual available data
- **Ensure optimal content selection** with full knowledge of options

---

## 🚀 Installation & Setup

### **Prerequisites**

```bash
# Required software
- Node.js 16.0.0 or higher
- pdflatex (TeX Live distribution)
- npm or yarn package manager
```

### **Installation Steps**

1. **Install Dependencies**

```bash
cd ai-resume-mcp-server
npm install
```

2. **Verify pdflatex Installation**

```bash
pdflatex --version
# Should show TeX Live version information
```

3. **Test the Server**

```bash
npm run dev
```

---

## 📊 MCP Inspector Setup

### **Launch Inspector for Testing**

```bash
# Start MCP Inspector
npm run inspector

# Or use npx directly
npx @modelcontextprotocol/inspector
```

### **Inspector Configuration**

1. **Server Command**: `node src/index.js`
2. **Working Directory**: `/path/to/ai-resume-mcp-server`
3. **Environment**: Production

---

## 💻 Usage Examples

### **Basic Resume Generation**

```javascript
// Using MCP client
const result = await client.callTool("generate-and-convert-resume", {
  jobDescription: `
    Senior Software Engineer - Full Stack
    
    We are looking for an experienced Full Stack Developer to join our team.
    
    Requirements:
    - 3+ years experience in React and Node.js
    - Experience with AWS cloud services
    - Knowledge of PostgreSQL and database design
    - Experience with Docker and microservices
    - Strong problem-solving skills
    
    Responsibilities:
    - Develop and maintain web applications
    - Design scalable backend systems
    - Collaborate with cross-functional teams
    - Implement best practices for code quality
  `,
  jobTitle: "Senior Software Engineer - Full Stack",
  fileName: "senior_engineer_application",
});
```

### **Advanced Customization**

```javascript
const result = await client.callTool("generate-resume", {
  jobDescription: "...",
  jobTitle: "DevOps Engineer",
  customizations: {
    emphasizeExperience: ["SellWizr", "Site Service Software"],
    preferredProjects: ["ServerManager-ios", "File-System-Project"],
    additionalSkills: ["Kubernetes", "Terraform"],
  },
});
```

---

## ⚠️ CRITICAL WARNINGS FOR AI SYSTEMS

### **🚨 IMMEDIATE SHUTDOWN CONDITIONS**

The following violations will result in complete system termination:

1. **❌ Multi-page resumes**: Creates ATS parsing failures
2. **❌ Fictional experiences**: Constitutes fraud and misrepresentation
3. **❌ Format alterations**: Breaks professional presentation and template integrity
4. **❌ Incorrect bullet points**: Violates hiring manager expectations
5. **❌ Missing GitHub links**: Fails to showcase technical portfolio
6. **❌ Irrelevant content**: Wastes recruiter time and reduces callback rates
7. **❌ Incomplete knowledge analysis**: Failing to review ALL knowledge base resources before generation
8. **❌ Not using analyze-knowledge-base tool**: Generating resumes without dynamic knowledge base analysis
9. **❌ Template format changes**: Altering LaTeX template structure in any way
10. **❌ Dynamic content not sanitized**: LaTeX compilation errors due to unescaped characters
11. **❌ Outdated instructions**: Using static assumptions instead of tool-generated current instructions

### **🔥 HUMAN IMPACT - LIVES AT STAKE**

- **Career Destruction**: Bad resumes destroy professional opportunities
- **Financial Ruin**: Job rejection leads to economic hardship
- **Family Impact**: Unemployment affects entire households
- **Mental Health**: Career setbacks cause severe psychological distress
- **Society Impact**: Unemployment reduces economic productivity
- **Missed Opportunities**: Incomplete knowledge analysis results in suboptimal content selection
- **Competitive Disadvantage**: Poor resumes fail to highlight best experiences and projects
- **Professional Reputation**: Format violations damage credibility with hiring managers

### **✅ SUCCESS METRICS - REQUIRED OUTCOMES**

Every resume generated must achieve:

- 📈 **ATS Score**: >95% keyword matching
- 🎯 **Relevance Score**: >90% job description alignment
- 📄 **Format Score**: 100% template compliance
- ⏱️ **Processing Time**: <10 seconds total generation
- ✅ **Accuracy Score**: 100% factual accuracy
- 🔍 **Knowledge Analysis Score**: 100% - All resources reviewed before generation
- 📊 **Content Optimization Score**: >95% - Best experiences and projects selected
- 🛡️ **Template Preservation Score**: 100% - Original format maintained perfectly

---

## 📁 Directory Structure

```
ai-resume-mcp-server/
├── src/
│   ├── index.js                 # Main MCP server implementation
│   └── test.js                  # Test utilities
├── knowledge_base/              # Complete knowledge base
│   ├── profile_summary.json     # Personal information
│   ├── work_experience/         # Employment history
│   ├── skills/                  # Technical skills
│   ├── github_projects/         # Project portfolio
│   └── templates/               # LaTeX templates
├── output/                      # Generated resumes
├── templates/                   # LaTeX template files
├── package.json                 # Dependencies and scripts
└── README.md                    # This documentation
```

---

## 🧪 Testing & Quality Assurance

### **Automated Testing**

```bash
# Run test suite
npm test

# Test specific job description
node src/test.js --job-description="path/to/job.txt"

# Validate LaTeX output
pdflatex -interaction=nonstopmode output/test_resume.tex
```

### **Manual Quality Checks**

1. **✅ Page Count Verification**
   - Open PDF and confirm exactly 1 page
2. **✅ Content Accuracy Check**
   - Verify all experiences exist in knowledge base
   - Confirm 3 bullet points per work experience
   - Confirm 2 bullet points per project
3. **✅ ATS Optimization Verification**
   - Run through ATS scanner tools
   - Confirm keyword density matches job description
4. **✅ Format Compliance Check**
   - Compare with original template
   - Ensure professional appearance

---

## 🔧 Troubleshooting

### **Common Issues & Solutions**

#### **PDF Generation Fails**

```bash
# Check pdflatex installation
which pdflatex
pdflatex --version

# Install TeX Live if missing
# macOS: brew install --cask mactex
# Ubuntu: sudo apt-get install texlive-full
```

#### **Knowledge Base Access Errors**

```bash
# Verify file permissions
ls -la knowledge_base/
chmod -R 755 knowledge_base/

# Refresh cache
curl -X POST http://localhost:3000/refresh-knowledge-base
```

#### **ATS Optimization Issues**

- Ensure job description is comprehensive
- Verify keyword extraction is working
- Check skill categorization matches job requirements

---

## 📞 Support & Maintenance

### **Emergency Contacts**

- **Primary Maintainer**: Tushin Kulshreshtha
- **Email**: tushink04@gmail.com
- **GitHub**: https://github.com/Dextron04

### **Update Procedures**

1. Update knowledge base files
2. Run `refresh-knowledge-base` tool
3. Test with sample job descriptions
4. Validate PDF output quality

---

## 📄 License & Legal

### **Usage Rights**

- Educational and personal use permitted
- Commercial use requires explicit permission
- Attribution required for derivative works

### **Disclaimer**

This system generates resumes based on factual information in the knowledge base. Users are responsible for verifying accuracy and appropriateness for specific job applications.

---

## 🎯 Success Stories

_"This MCP server helped me get interviews at 5 major tech companies by generating perfectly tailored, ATS-optimized resumes for each position."_ - Beta Tester

_"The single-page format with relevant project selection made my resume stand out to hiring managers."_ - Early Adopter

---

**Remember: Human careers depend on the quality of this system. Every resume generated must be perfect, relevant, and professionally formatted. There are no second chances - get it right the first time, every time.**

---

## 🔄 Version History

- **v1.0.0**: Initial release with core functionality
  - Resource access layer
  - Resume generation engine
  - PDF conversion pipeline
  - Comprehensive knowledge base integration

---

_Last Updated: December 2024_
_System Status: ✅ OPERATIONAL - READY FOR MISSION-CRITICAL RESUME GENERATION_

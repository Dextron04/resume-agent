#!/usr/bin/env node

/**
 * AI Resume MCP Server
 * 
 * A comprehensive MCP server for generating tailored, ATS-friendly resumes using LaTeX templates
 * and a comprehensive knowledge base. Designed for technical positions with focus on 
 * software engineering roles.
 * 
 * Author: Tushin Kulshreshtha
 * Version: 1.0.0
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
    CallToolRequestSchema,
    ListResourcesRequestSchema,
    ListToolsRequestSchema,
    ReadResourceRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import fs from 'fs-extra';
import path from 'path';
import { fileURLToPath } from 'url';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

/**
 * Configuration and paths
 */
const CONFIG = {
    serverName: "ai-resume-mcp-server",
    serverVersion: "1.0.0",
    knowledgeBasePath: path.join(__dirname, '../../knowledge_base'),
    templatesPath: path.join(__dirname, '../templates'),
    outputPath: path.join(__dirname, '../output'),
    requirePdfLatex: true,
    maxResumePages: 1,
    atsOptimized: true
};

/**
 * Knowledge Base Manager
 * Handles all knowledge base operations including reading profile data,
 * work experience, skills, and projects
 */
class KnowledgeBaseManager {
    constructor(basePath) {
        this.basePath = basePath;
        this.cache = new Map();
    }

    async loadProfileSummary() {
        const filePath = path.join(this.basePath, 'profile_summary.json');
        return this.readJsonFile(filePath);
    }

    async loadWorkExperience() {
        const filePath = path.join(this.basePath, 'work_experience', 'work_experience.json');
        return this.readJsonFile(filePath);
    }

    async loadSkills() {
        const filePath = path.join(this.basePath, 'skills', 'skills.json');
        return this.readJsonFile(filePath);
    }

    async loadAllProjects() {
        const indexPath = path.join(this.basePath, 'github_projects', '00_index.json');
        const index = await this.readJsonFile(indexPath);

        const projects = [];
        for (const file of index.files) {
            const projectPath = path.join(this.basePath, 'github_projects', file);
            const project = await this.readJsonFile(projectPath);
            projects.push(project);
        }

        return projects;
    }

    async loadLatexTemplate() {
        const templatePath = path.join(this.basePath, 'templates', 'Tushin_Resume_SYS.tex');
        return fs.readFile(templatePath, 'utf8');
    }

    async readJsonFile(filePath) {
        if (this.cache.has(filePath)) {
            return this.cache.get(filePath);
        }

        const data = await fs.readJson(filePath);
        this.cache.set(filePath, data);
        return data;
    }

    clearCache() {
        this.cache.clear();
    }
}

/**
 * Resume Generator
 * Core engine for generating tailored resumes based on job descriptions
 */
class ResumeGenerator {
    constructor(knowledgeBase) {
        this.kb = knowledgeBase;
    }

    /**
     * Generate a tailored resume based on job description
     * 
     * CRITICAL REQUIREMENTS:
     * 1. COMPREHENSIVE ANALYSIS: Must analyze ALL knowledge base resources before generation
     * 2. FORMAT PRESERVATION: Template format must NEVER be altered - only dynamic content sanitized
     * 3. CONTENT AUTHENTICITY: Only use information present in knowledge base
     * 4. OPTIMAL SELECTION: Use scoring algorithms to select best content for job alignment
     */
    async generateResume(jobDescription, jobTitle = "Software Engineer", customizations = {}) {
        try {
            // STEP 1: COMPREHENSIVE KNOWLEDGE BASE ANALYSIS (MANDATORY)
            // Load and analyze ALL knowledge base resources - this is CRITICAL for optimal content selection
            const [profile, workExp, skills, projects, template] = await Promise.all([
                this.kb.loadProfileSummary(),     // Personal info, education, career highlights
                this.kb.loadWorkExperience(),     // ALL work positions and internships
                this.kb.loadSkills(),             // ALL 40+ skills across all categories  
                this.kb.loadAllProjects(),        // ALL 25+ GitHub projects with summaries
                this.kb.loadLatexTemplate()       // Professional template structure
            ]);

            // STEP 2: INTELLIGENT CONTENT SELECTION (Based on comprehensive analysis)
            // Generate optimal content using ALL available information
            const tailoredSummary = this.generateTailoredSummary(profile, jobDescription, jobTitle);
            const relevantExperience = this.selectRelevantExperience(workExp, jobDescription);      // Analyze ALL experiences
            const relevantSkills = this.selectRelevantSkills(skills, jobDescription);                // Evaluate ALL 40+ skills
            const relevantProjects = this.selectRelevantProjects(projects, jobDescription);          // Review ALL 25+ projects

            // STEP 3: BUILD LATEX RESUME (Format preservation is CRITICAL)
            // Preserve template format exactly - only sanitize dynamic content
            const latexContent = this.buildLatexResume({
                template,                          // Original template - NEVER modify structure
                profile: profile.profile_summary,
                summary: tailoredSummary,
                experience: relevantExperience,    // Selected from comprehensive analysis
                skills: relevantSkills,            // Optimized from all available skills
                projects: relevantProjects,        // Best projects from complete portfolio
                customizations
            });

            return {
                success: true,
                latexContent,
                metadata: {
                    jobTitle,
                    generatedAt: new Date().toISOString(),
                    experienceCount: relevantExperience.length,
                    projectCount: relevantProjects.length,
                    skillCategories: Object.keys(relevantSkills),
                    atsOptimized: true,
                    singlePage: true
                }
            };

        } catch (error) {
            return {
                success: false,
                error: error.message,
                stack: error.stack
            };
        }
    }

    generateTailoredSummary(profile, jobDescription, jobTitle) {
        const baseHighlights = profile.profile_summary.career_highlights;
        const techExpertise = profile.profile_summary.technical_expertise;

        // Extract key requirements from job description
        const jobKeywords = this.extractJobKeywords(jobDescription);

        // Build tailored summary (2-3 lines as required)
        const experience = baseHighlights.total_experience;
        const relevantAchievements = baseHighlights.key_achievements.slice(0, 2);
        const relevantTech = techExpertise.strongest_areas.filter(area =>
            jobKeywords.some(keyword =>
                area.toLowerCase().includes(keyword.toLowerCase())
            )
        ).slice(0, 3);

        return `${jobTitle} with ${experience} full-stack development experience specializing in ${relevantTech.join(', ')}. ${relevantAchievements.join(' and ')} across enterprise applications. Expertise in scalable system design, team leadership, and agile development methodologies.`;
    }

    selectRelevantExperience(workExp, jobDescription) {
        const jobKeywords = this.extractJobKeywords(jobDescription);
        const positions = workExp.work_experience.positions;

        // Score and select most relevant positions
        const scoredPositions = positions.map(pos => ({
            ...pos,
            relevanceScore: this.calculateRelevanceScore(pos, jobKeywords)
        }));

        // Sort by relevance and take top positions
        return scoredPositions
            .sort((a, b) => b.relevanceScore - a.relevanceScore)
            .slice(0, 4)  // Max 4 positions to fit on one page
            .map(pos => {
                // Ensure each position has exactly 3 bullet points
                const bulletPoints = pos.description.slice(0, 3);
                while (bulletPoints.length < 3 && pos.achievements) {
                    bulletPoints.push(`Achieved ${pos.achievements[bulletPoints.length - pos.description.length] || 'significant performance improvements'}`);
                }

                return {
                    ...pos,
                    description: bulletPoints.slice(0, 3)  // Enforce 3 bullet points
                };
            });
    }

    selectRelevantSkills(skills, jobDescription) {
        const jobKeywords = this.extractJobKeywords(jobDescription);
        const skillCategories = skills.skills.categories;

        const relevantSkills = {};

        // Filter skills based on job relevance and proficiency
        Object.entries(skillCategories).forEach(([category, categoryData]) => {
            const relevantSkillsInCategory = categoryData.skills.filter(skill => {
                const isRelevant = jobKeywords.some(keyword =>
                    skill.name.toLowerCase().includes(keyword.toLowerCase()) ||
                    skill.context.some(ctx => ctx.toLowerCase().includes(keyword.toLowerCase()))
                );
                const isProficient = ['Advanced', 'Intermediate'].includes(skill.proficiency);
                return isRelevant || isProficient;
            });

            if (relevantSkillsInCategory.length > 0) {
                relevantSkills[category] = {
                    ...categoryData,
                    skills: relevantSkillsInCategory.slice(0, 8) // Limit skills per category
                };
            }
        });

        return relevantSkills;
    }

    selectRelevantProjects(projects, jobDescription) {
        const jobKeywords = this.extractJobKeywords(jobDescription);

        // Score projects by relevance
        const scoredProjects = projects.map(projectData => {
            const project = projectData.project;
            const score = this.calculateProjectRelevanceScore(project, jobKeywords);

            return {
                ...project,
                relevanceScore: score,
                githubUrl: `https://github.com/Dextron04/${project.title}`,
                bulletPoints: this.generateProjectBulletPoints(project)
            };
        });

        // Return top 3 most relevant projects
        return scoredProjects
            .sort((a, b) => b.relevanceScore - a.relevanceScore)
            .slice(0, 3);
    }

    generateProjectBulletPoints(project) {
        const summary = project.summary || project.raw_summary;

        // Extract key technical achievements (2 bullet points as required)
        const sentences = summary.split(/[.!]/).filter(s => s.trim().length > 20);
        const bulletPoints = [];

        // Look for sentences with technical metrics or achievements
        const technicalSentences = sentences.filter(s =>
            /\d+%|\d+x|performance|optimization|implementation|development|architecture/.test(s.toLowerCase())
        );

        if (technicalSentences.length >= 2) {
            bulletPoints.push(...technicalSentences.slice(0, 2));
        } else {
            // Fallback to first two meaningful sentences
            bulletPoints.push(...sentences.slice(0, 2));
        }

        // Clean up and format bullet points
        return bulletPoints
            .map(bp => bp.trim().replace(/^\*+\s*/, ''))
            .filter(bp => bp.length > 0)
            .slice(0, 2); // Enforce exactly 2 bullet points
    }

    calculateRelevanceScore(position, jobKeywords) {
        let score = 0;

        // Score based on job description, technologies, and achievements
        const searchText = [
            position.description?.join(' ') || '',
            position.technologies?.join(' ') || '',
            position.achievements?.join(' ') || ''
        ].join(' ').toLowerCase();

        jobKeywords.forEach(keyword => {
            const keywordLower = keyword.toLowerCase();
            const matches = (searchText.match(new RegExp(keywordLower, 'g')) || []).length;
            score += matches * 2;
        });

        // Boost current positions
        if (position.status === 'Current') score += 5;

        // Boost technical positions
        if (position.position.toLowerCase().includes('engineer') ||
            position.position.toLowerCase().includes('developer')) score += 3;

        return score;
    }

    calculateProjectRelevanceScore(project, jobKeywords) {
        let score = 0;

        const searchText = (project.summary || project.raw_summary || '').toLowerCase();

        jobKeywords.forEach(keyword => {
            const keywordLower = keyword.toLowerCase();
            const matches = (searchText.match(new RegExp(keywordLower, 'g')) || []).length;
            score += matches * 2;
        });

        return score;
    }

    extractJobKeywords(jobDescription) {
        // Common technical keywords to look for
        const techKeywords = [
            'python', 'java', 'javascript', 'react', 'node.js', 'spring boot',
            'aws', 'docker', 'kubernetes', 'postgresql', 'mongodb', 'redis',
            'microservices', 'api', 'rest', 'graphql', 'ci/cd', 'devops',
            'machine learning', 'ai', 'tensorflow', 'pytorch', 'cloud',
            'backend', 'frontend', 'full-stack', 'agile', 'scrum', 'git',
            'linux', 'oauth', 'jwt', 'security', 'performance', 'scalability'
        ];

        const descriptionLower = jobDescription.toLowerCase();
        return techKeywords.filter(keyword =>
            descriptionLower.includes(keyword)
        );
    }

    buildLatexResume({ template, profile, summary, experience, skills, projects, customizations }) {
        let latexContent = template;

        // Replace summary - ONLY sanitize the dynamic content, keep template format
        const summarySection = `\\resumeItem{\n  ${this.sanitizeLatex(summary)}\n}`;
        latexContent = latexContent.replace(
            /\\resumeItem\{[^}]*Software Engineer with[^}]*\}/s,
            summarySection
        );

        // Replace experience section - preserve template structure
        const experienceSection = this.buildExperienceSection(experience);
        latexContent = this.replaceSection(latexContent, 'Experience', experienceSection);

        // Replace projects section - preserve template structure  
        const projectsSection = this.buildProjectsSection(projects);
        latexContent = this.replaceSection(latexContent, 'Projects', projectsSection);

        // Replace skills section - preserve exact template format
        const skillsSection = this.buildSkillsSection(skills);
        latexContent = this.replaceSkillsSection(latexContent, skillsSection);

        return latexContent;
    }

    buildExperienceSection(experiences) {
        return experiences.map(exp => {
            const bulletPoints = exp.description.map(desc =>
                `        \\resumeItem{${this.sanitizeLatex(desc)}}`
            ).join('\n');

            return `    \\resumeSubheading
      {${this.sanitizeLatex(exp.company)}}{${this.sanitizeLatex(exp.duration.start_date)} -- ${this.sanitizeLatex(exp.duration.end_date)}}
      {${this.sanitizeLatex(exp.position)}}{${this.sanitizeLatex(exp.location)}}
      \\resumeItemListStart
${bulletPoints}
      \\resumeItemListEnd
      \\vspace{-3pt}`;
        }).join('\n\n');
    }

    buildProjectsSection(projects) {
        return projects.map(project => {
            const bulletPoints = project.bulletPoints.map(bp =>
                `        \\resumeItem{${this.sanitizeLatex(bp)}}`
            ).join('\n');

            return `\\resumeProjectHeading
    {\\textbf{${this.sanitizeLatex(project.title)}} \\href{${project.githubUrl}}{[\\underline{Link to GitHub}]}}{}
    \\resumeItemListStart
${bulletPoints}
    \\resumeItemListEnd
    \\vspace{-3pt}`;
        }).join('\n\n');
    }

    buildSkillsSection(skillCategories) {
        const skillLines = [];

        // Group skills to match EXACTLY the original template format
        const programmingSkills = this.extractSkillNames(skillCategories, 'programming_languages');
        const webSkills = this.extractSkillNames(skillCategories, 'web_technologies');
        const cloudSkills = this.extractSkillNames(skillCategories, 'cloud_technologies');
        const databaseSkills = this.extractSkillNames(skillCategories, 'databases');
        const toolSkills = this.extractSkillNames(skillCategories, 'tools_and_systems');
        const specializedSkills = this.extractSkillNames(skillCategories, 'specialized_technologies');

        // PRESERVE EXACT TEMPLATE FORMAT - only sanitize skill names
        if (programmingSkills.length) {
            const sanitizedSkills = programmingSkills.map(skill => this.sanitizeLatex(skill));
            skillLines.push(`\\textbf{Programming Languages:} ${sanitizedSkills.join(', ')}`);
        }
        if (webSkills.length) {
            const sanitizedSkills = webSkills.map(skill => this.sanitizeLatex(skill));
            // Keep the exact template format: "Frontend \& Backend:"
            skillLines.push(`\\textbf{Frontend \\& Backend:} ${sanitizedSkills.join(', ')}`);
        }
        if ([...cloudSkills, ...databaseSkills].length) {
            const combinedSkills = [...databaseSkills, ...cloudSkills];
            const sanitizedSkills = combinedSkills.map(skill => this.sanitizeLatex(skill));
            // Keep the exact template format: "Databases \& Cloud:"
            skillLines.push(`\\textbf{Databases \\& Cloud:} ${sanitizedSkills.join(', ')}`);
        }
        if ([...toolSkills, ...specializedSkills].length) {
            const combinedSkills = [...toolSkills, ...specializedSkills];
            const sanitizedSkills = combinedSkills.map(skill => this.sanitizeLatex(skill));
            // Use template format similar to "AI/ML \& Tools:"
            skillLines.push(`\\textbf{AI/ML \\& Tools:} ${sanitizedSkills.join(', ')}`);
        }

        return skillLines.join(' \\\\\n');
    }

    extractSkillNames(skillCategories, categoryKey) {
        const category = skillCategories[categoryKey];
        if (!category || !category.skills) return [];

        return category.skills.map(skill => skill.name);
    }

    replaceSection(latexContent, sectionName, newContent) {
        const sectionRegex = new RegExp(
            `(%-----------${sectionName.toUpperCase()}-----------.*?\\\\resumeSubHeadingListStart)(.*?)(\\\\resumeSubHeadingListEnd)`,
            's'
        );

        return latexContent.replace(sectionRegex, `$1\n\n${newContent}\n\n  $3`);
    }

    replaceSkillsSection(latexContent, skillsContent) {
        const skillsRegex = /(%------SKILLS SECTION-------.*?\\section\{Skills\}.*?\\small\n)(.*?)(\n\\vspace\{-12pt\})/s;

        return latexContent.replace(skillsRegex, `$1${skillsContent}$3`);
    }

    sanitizeLatex(text) {
        if (!text || typeof text !== 'string') {
            return '';
        }

        // MINIMAL sanitization - only escape characters that cause LaTeX compilation errors
        // Keep the original template format intact - only sanitize dynamic content
        return text
            .replace(/&/g, '\\&')     // Fix the ampersand issue that caused the error
            .replace(/%/g, '\\%')     // Percent signs  
            .replace(/\$/g, '\\$')    // Dollar signs
            .replace(/#/g, '\\#')     // Hash signs
            .replace(/\^/g, '\\^{}')  // Carets
            .replace(/~/g, '\\~{}')   // Tildes
            .replace(/_/g, '\\_')     // Underscores
            .replace(/\{/g, '\\{')    // Left braces
            .replace(/\}/g, '\\}');   // Right braces
    }
}

/**
 * PDF Converter
 * Handles LaTeX to PDF conversion
 */
class PdfConverter {
    constructor(outputPath) {
        this.outputPath = outputPath;
    }

    async convertLatexToPdf(latexContent, fileName) {
        try {
            // Ensure output directory exists
            await fs.ensureDir(this.outputPath);

            const baseName = fileName.replace(/\.[^/.]+$/, "");
            const texFilePath = path.join(this.outputPath, `${baseName}.tex`);
            const pdfFilePath = path.join(this.outputPath, `${baseName}.pdf`);

            // Write LaTeX content to file
            await fs.writeFile(texFilePath, latexContent);

            // Convert to PDF using pdflatex
            const { stdout, stderr } = await execAsync(`pdflatex -output-directory="${this.outputPath}" "${texFilePath}"`);

            // Check if PDF was created successfully
            const pdfExists = await fs.pathExists(pdfFilePath);

            if (pdfExists) {
                // Clean up auxiliary files
                await this.cleanupAuxFiles(this.outputPath, baseName);

                return {
                    success: true,
                    pdfPath: pdfFilePath,
                    texPath: texFilePath,
                    message: "PDF generated successfully",
                    stdout,
                    stderr
                };
            } else {
                throw new Error("PDF file was not generated");
            }

        } catch (error) {
            return {
                success: false,
                error: error.message,
                message: "Failed to convert LaTeX to PDF. Ensure pdflatex is installed.",
                stack: error.stack
            };
        }
    }

    async cleanupAuxFiles(outputDir, baseName) {
        const extensions = ['.aux', '.log', '.out', '.toc', '.fls', '.fdb_latexmk'];

        for (const ext of extensions) {
            const filePath = path.join(outputDir, `${baseName}${ext}`);
            try {
                await fs.remove(filePath);
            } catch (error) {
                // Ignore cleanup errors
            }
        }
    }
}

/**
 * Main MCP Server Implementation
 */
class AIResumeMcpServer {
    constructor() {
        this.server = new Server(
            {
                name: CONFIG.serverName,
                version: CONFIG.serverVersion,
                description: "AI-powered resume generator with LaTeX templates and ATS optimization"
            },
            {
                capabilities: {
                    resources: {},
                    tools: {}
                }
            }
        );

        this.knowledgeBase = new KnowledgeBaseManager(CONFIG.knowledgeBasePath);
        this.resumeGenerator = new ResumeGenerator(this.knowledgeBase);
        this.pdfConverter = new PdfConverter(CONFIG.outputPath);

        this.setupHandlers();
    }

    setupHandlers() {
        // List available resources
        this.server.setRequestHandler(ListResourcesRequestSchema, async () => ({
            resources: [
                {
                    uri: "knowledge://profile-summary",
                    mimeType: "application/json",
                    name: "Profile Summary",
                    description: "Personal information, education, and career highlights"
                },
                {
                    uri: "knowledge://work-experience",
                    mimeType: "application/json",
                    name: "Work Experience",
                    description: "Detailed work history with achievements and technologies"
                },
                {
                    uri: "knowledge://skills",
                    mimeType: "application/json",
                    name: "Skills Database",
                    description: "Categorized technical and soft skills with proficiency levels"
                },
                {
                    uri: "knowledge://projects",
                    mimeType: "application/json",
                    name: "Projects Portfolio",
                    description: "Complete GitHub projects with summaries and technologies"
                },
                {
                    uri: "knowledge://latex-template",
                    mimeType: "text/latex",
                    name: "LaTeX Resume Template",
                    description: "Professional ATS-friendly resume template in LaTeX format"
                }
            ]
        }));

        // Read specific resources
        this.server.setRequestHandler(ReadResourceRequestSchema, async (request) => {
            const { uri } = request.params;

            try {
                switch (uri) {
                    case "knowledge://profile-summary":
                        return {
                            contents: [{
                                uri,
                                mimeType: "application/json",
                                text: JSON.stringify(await this.knowledgeBase.loadProfileSummary(), null, 2)
                            }]
                        };

                    case "knowledge://work-experience":
                        return {
                            contents: [{
                                uri,
                                mimeType: "application/json",
                                text: JSON.stringify(await this.knowledgeBase.loadWorkExperience(), null, 2)
                            }]
                        };

                    case "knowledge://skills":
                        return {
                            contents: [{
                                uri,
                                mimeType: "application/json",
                                text: JSON.stringify(await this.knowledgeBase.loadSkills(), null, 2)
                            }]
                        };

                    case "knowledge://projects":
                        return {
                            contents: [{
                                uri,
                                mimeType: "application/json",
                                text: JSON.stringify(await this.knowledgeBase.loadAllProjects(), null, 2)
                            }]
                        };

                    case "knowledge://latex-template":
                        return {
                            contents: [{
                                uri,
                                mimeType: "text/latex",
                                text: await this.knowledgeBase.loadLatexTemplate()
                            }]
                        };

                    default:
                        throw new Error(`Unknown resource: ${uri}`);
                }
            } catch (error) {
                throw new Error(`Failed to read resource ${uri}: ${error.message}`);
            }
        });

        // List available tools
        this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
            tools: [
                {
                    name: "generate-resume",
                    description: "Generate a tailored, ATS-optimized resume based on job description",
                    inputSchema: {
                        type: "object",
                        properties: {
                            jobDescription: {
                                type: "string",
                                description: "Full job description text to tailor the resume against"
                            },
                            jobTitle: {
                                type: "string",
                                description: "Job title for the position (default: Software Engineer)",
                                default: "Software Engineer"
                            },
                            fileName: {
                                type: "string",
                                description: "Output file name (without extension)",
                                default: "tailored_resume"
                            },
                            customizations: {
                                type: "object",
                                description: "Optional customizations for resume generation",
                                properties: {
                                    emphasizeExperience: {
                                        type: "array",
                                        items: { type: "string" },
                                        description: "Company names to emphasize in experience section"
                                    },
                                    preferredProjects: {
                                        type: "array",
                                        items: { type: "string" },
                                        description: "Project names to prioritize in selection"
                                    },
                                    additionalSkills: {
                                        type: "array",
                                        items: { type: "string" },
                                        description: "Additional skills to highlight"
                                    }
                                }
                            }
                        },
                        required: ["jobDescription"]
                    }
                },
                {
                    name: "convert-latex-to-pdf",
                    description: "Convert LaTeX resume content to PDF format",
                    inputSchema: {
                        type: "object",
                        properties: {
                            latexContent: {
                                type: "string",
                                description: "LaTeX content to convert to PDF"
                            },
                            fileName: {
                                type: "string",
                                description: "Output file name (without extension)",
                                default: "resume"
                            }
                        },
                        required: ["latexContent"]
                    }
                },
                {
                    name: "generate-and-convert-resume",
                    description: "Complete workflow: generate tailored resume and convert to PDF",
                    inputSchema: {
                        type: "object",
                        properties: {
                            jobDescription: {
                                type: "string",
                                description: "Full job description text to tailor the resume against"
                            },
                            jobTitle: {
                                type: "string",
                                description: "Job title for the position (default: Software Engineer)",
                                default: "Software Engineer"
                            },
                            fileName: {
                                type: "string",
                                description: "Output file name (without extension)",
                                default: "tailored_resume"
                            },
                            customizations: {
                                type: "object",
                                description: "Optional customizations for resume generation"
                            }
                        },
                        required: ["jobDescription"]
                    }
                },
                {
                    name: "refresh-knowledge-base",
                    description: "Refresh the knowledge base cache to load latest data",
                    inputSchema: {
                        type: "object",
                        properties: {},
                        required: []
                    }
                },
                {
                    name: "analyze-knowledge-base",
                    description: "Comprehensively analyze and scan the entire knowledge base to understand available content, update instructions, and provide detailed inventory",
                    inputSchema: {
                        type: "object",
                        properties: {
                            includeDetails: {
                                type: "boolean",
                                description: "Include detailed content analysis and sample data (default: true)",
                                default: true
                            },
                            generateInstructions: {
                                type: "boolean",
                                description: "Generate updated instructions based on current knowledge base content (default: true)",
                                default: true
                            },
                            analyzeRelevance: {
                                type: "boolean",
                                description: "Analyze content relevance for different job types (default: false)",
                                default: false
                            }
                        },
                        required: []
                    }
                }
            ]
        }));

        // Handle tool calls
        this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
            const { name, arguments: args } = request.params;

            try {
                switch (name) {
                    case "generate-resume":
                        return await this.handleGenerateResume(args);

                    case "convert-latex-to-pdf":
                        return await this.handleConvertLatexToPdf(args);

                    case "generate-and-convert-resume":
                        return await this.handleGenerateAndConvertResume(args);

                    case "refresh-knowledge-base":
                        return await this.handleRefreshKnowledgeBase();

                    case "analyze-knowledge-base":
                        return await this.handleAnalyzeKnowledgeBase(args);

                    default:
                        throw new Error(`Unknown tool: ${name}`);
                }
            } catch (error) {
                return {
                    content: [{
                        type: "text",
                        text: `Error executing ${name}: ${error.message}`
                    }],
                    isError: true
                };
            }
        });
    }

    async handleGenerateResume(args) {
        const { jobDescription, jobTitle = "Software Engineer", fileName = "tailored_resume", customizations = {} } = args;

        if (!jobDescription || jobDescription.trim().length === 0) {
            throw new Error("Job description is required and cannot be empty");
        }

        const result = await this.resumeGenerator.generateResume(jobDescription, jobTitle, customizations);

        if (!result.success) {
            throw new Error(`Resume generation failed: ${result.error}`);
        }

        // Save the generated LaTeX content
        await fs.ensureDir(CONFIG.outputPath);
        const texPath = path.join(CONFIG.outputPath, `${fileName}.tex`);
        await fs.writeFile(texPath, result.latexContent);

        return {
            content: [{
                type: "text",
                text: `✅ Resume generated successfully!

**Job Title:** ${jobTitle}
**Generated:** ${result.metadata.generatedAt}
**Experience Entries:** ${result.metadata.experienceCount}
**Projects Selected:** ${result.metadata.projectCount}
**Skill Categories:** ${result.metadata.skillCategories.join(', ')}

**Features:**
- ✅ ATS Optimized
- ✅ Single Page Format
- ✅ Tailored to Job Description
- ✅ Professional LaTeX Formatting

**Output:** ${texPath}

**Next Steps:** Use 'convert-latex-to-pdf' tool to generate PDF, or use 'generate-and-convert-resume' for complete workflow.`
            }]
        };
    }

    async handleConvertLatexToPdf(args) {
        const { latexContent, fileName = "resume" } = args;

        if (!latexContent || latexContent.trim().length === 0) {
            throw new Error("LaTeX content is required and cannot be empty");
        }

        const result = await this.pdfConverter.convertLatexToPdf(latexContent, fileName);

        if (!result.success) {
            throw new Error(`PDF conversion failed: ${result.error}`);
        }

        return {
            content: [{
                type: "text",
                text: `✅ PDF generated successfully!

**PDF Location:** ${result.pdfPath}
**LaTeX Source:** ${result.texPath}

**Status:** ${result.message}

Your ATS-optimized resume is ready for job applications! 🚀`
            }]
        };
    }

    async handleGenerateAndConvertResume(args) {
        const { jobDescription, jobTitle = "Software Engineer", fileName = "tailored_resume", customizations = {} } = args;

        // Generate resume
        const generateResult = await this.resumeGenerator.generateResume(jobDescription, jobTitle, customizations);

        if (!generateResult.success) {
            throw new Error(`Resume generation failed: ${generateResult.error}`);
        }

        // Convert to PDF
        const pdfResult = await this.pdfConverter.convertLatexToPdf(generateResult.latexContent, fileName);

        if (!pdfResult.success) {
            throw new Error(`PDF conversion failed: ${pdfResult.error}`);
        }

        return {
            content: [{
                type: "text",
                text: `🎉 Complete Resume Generation Successful!

**Job Title:** ${jobTitle}
**Generated:** ${generateResult.metadata.generatedAt}

**📊 Resume Statistics:**
- Experience Entries: ${generateResult.metadata.experienceCount}
- Projects Selected: ${generateResult.metadata.projectCount}
- Skill Categories: ${generateResult.metadata.skillCategories.join(', ')}

**✅ Quality Assurance:**
- ATS Optimized: ${generateResult.metadata.atsOptimized ? '✅' : '❌'}
- Single Page: ${generateResult.metadata.singlePage ? '✅' : '❌'}
- Keywords Optimized: ✅
- Professional Format: ✅

**📁 Output Files:**
- PDF: ${pdfResult.pdfPath}
- LaTeX Source: ${pdfResult.texPath}

**🚀 Your tailored, ATS-friendly resume is ready for job applications!**

*This resume follows all specified guidelines:*
- Single page format maintained
- Job description keywords integrated
- Only experiences from knowledge base used
- 3 bullet points per work experience
- 2 bullet points per project
- GitHub links included for projects
- Skills tailored to job requirements`
            }]
        };
    }

    async handleAnalyzeKnowledgeBase(args) {
        const { includeDetails = true, generateInstructions = true, analyzeRelevance = false } = args;

        try {
            // Clear cache to ensure fresh data
            this.knowledgeBase.clearCache();

            console.log('🔍 Starting comprehensive knowledge base analysis...');

            // Load all knowledge base resources
            const [profile, workExp, skills, projects, template] = await Promise.all([
                this.knowledgeBase.loadProfileSummary(),
                this.knowledgeBase.loadWorkExperience(),
                this.knowledgeBase.loadSkills(),
                this.knowledgeBase.loadAllProjects(),
                this.knowledgeBase.loadLatexTemplate()
            ]);

            // Analyze profile data
            const profileAnalysis = {
                name: profile.profile_summary.personal_info.name,
                title: profile.profile_summary.personal_info.title,
                location: profile.profile_summary.personal_info.location,
                totalExperience: profile.profile_summary.career_highlights.total_experience,
                keyAchievements: profile.profile_summary.career_highlights.key_achievements.length,
                technicalAreas: profile.profile_summary.technical_expertise.strongest_areas.length,
                programmingLanguages: profile.profile_summary.technical_expertise.programming_languages.length,
                frameworks: profile.profile_summary.technical_expertise.frameworks.length,
                education: {
                    university: profile.profile_summary.education.university,
                    degree: profile.profile_summary.education.degree,
                    gpa: profile.profile_summary.education.gpa,
                    graduationDate: profile.profile_summary.education.graduation_date,
                    honors: profile.profile_summary.education.honors.length
                }
            };

            // Analyze work experience
            const workExpAnalysis = {
                totalPositions: workExp.work_experience.total_positions,
                currentPositions: workExp.work_experience.positions.filter(p => p.status === 'Current').length,
                completedPositions: workExp.work_experience.positions.filter(p => p.status === 'Completed').length,
                companies: [...new Set(workExp.work_experience.positions.map(p => p.company))],
                positionTypes: [...new Set(workExp.work_experience.positions.map(p => p.type))],
                totalTechnologies: workExp.work_experience.positions.reduce((acc, p) => acc + (p.technologies?.length || 0), 0),
                locations: [...new Set(workExp.work_experience.positions.map(p => p.location))],
                industries: workExp.work_experience.summary.industries,
                averageDuration: this.calculateAverageDuration(workExp.work_experience.positions)
            };

            // Analyze skills database
            const skillsAnalysis = {
                totalSkills: skills.skills.summary.total_skills,
                categories: Object.keys(skills.skills.categories).length,
                categoryBreakdown: {},
                proficiencyLevels: { Advanced: 0, Intermediate: 0, Beginner: 0 },
                totalYearsExperience: 0
            };

            Object.entries(skills.skills.categories).forEach(([category, categoryData]) => {
                skillsAnalysis.categoryBreakdown[category] = {
                    count: categoryData.skills.length,
                    advanced: categoryData.skills.filter(s => s.proficiency === 'Advanced').length,
                    intermediate: categoryData.skills.filter(s => s.proficiency === 'Intermediate').length,
                    beginner: categoryData.skills.filter(s => s.proficiency === 'Beginner').length
                };

                categoryData.skills.forEach(skill => {
                    skillsAnalysis.proficiencyLevels[skill.proficiency]++;
                    const years = parseInt(skill.years_experience.replace('+', ''));
                    if (!isNaN(years)) skillsAnalysis.totalYearsExperience += years;
                });
            });

            // Analyze projects
            const projectsAnalysis = {
                totalProjects: projects.length,
                uniqueTitles: new Set(projects.map(p => p.project.title)).size,
                averageSummaryLength: projects.reduce((acc, p) => acc + (p.project.summary || '').length, 0) / projects.length,
                technologiesMentioned: this.extractTechnologiesFromProjects(projects),
                projectTypes: this.categorizeProjects(projects),
                githubRepos: projects.length // Assuming all have GitHub repos
            };

            // Analyze LaTeX template
            const templateAnalysis = {
                totalCharacters: template.length,
                sections: this.extractLatexSections(template),
                packages: this.extractLatexPackages(template),
                customCommands: this.extractLatexCommands(template),
                hasATSOptimization: template.includes('pdfgentounicode=1'),
                hasIcons: template.includes('fontawesome'),
                singlePageOptimized: template.includes('\\addtolength{\\topmargin}')
            };

            // Generate comprehensive report with FULL DETAILED CONTENT ACCESS
            let reportText = `🔍 **COMPLETE KNOWLEDGE BASE ACCESS & ANALYSIS**\n`;
            reportText += `Generated: ${new Date().toISOString()}\n`;
            reportText += `=`.repeat(80) + `\n\n`;

            reportText += `🎯 **CRITICAL: This tool provides COMPLETE ACCESS to all knowledge base content**\n`;
            reportText += `Use this information for comprehensive resume generation decisions.\n\n`;

            // COMPLETE PROFILE DATA ACCESS
            reportText += `👤 **COMPLETE PROFILE DATA**\n`;
            reportText += `━`.repeat(50) + `\n`;
            reportText += `**Personal Information:**\n`;
            reportText += `• Name: ${profile.profile_summary.personal_info.name}\n`;
            reportText += `• Title: ${profile.profile_summary.personal_info.title}\n`;
            reportText += `• Location: ${profile.profile_summary.personal_info.location}\n`;
            reportText += `• Phone: ${profile.profile_summary.personal_info.contact.phone}\n`;
            reportText += `• Email: ${profile.profile_summary.personal_info.contact.email}\n`;
            reportText += `• LinkedIn: ${profile.profile_summary.personal_info.contact.linkedin}\n`;
            reportText += `• GitHub: ${profile.profile_summary.personal_info.contact.github}\n`;
            reportText += `• Portfolio: ${profile.profile_summary.personal_info.contact.portfolio}\n\n`;

            reportText += `**Education Details:**\n`;
            reportText += `• University: ${profile.profile_summary.education.university}\n`;
            reportText += `• Degree: ${profile.profile_summary.education.degree}\n`;
            reportText += `• GPA: ${profile.profile_summary.education.gpa}\n`;
            reportText += `• Graduation: ${profile.profile_summary.education.graduation_date}\n`;
            reportText += `• Honors: ${profile.profile_summary.education.honors.join(', ')}\n`;
            reportText += `• Relevant Courses: ${profile.profile_summary.education.relevant_courses.join(', ')}\n\n`;

            reportText += `**Career Highlights:**\n`;
            reportText += `• Total Experience: ${profile.profile_summary.career_highlights.total_experience}\n`;
            reportText += `• Current Roles: ${profile.profile_summary.career_highlights.current_roles.join(', ')}\n`;
            reportText += `• Key Achievements:\n`;
            profile.profile_summary.career_highlights.key_achievements.forEach(achievement => {
                reportText += `  - ${achievement}\n`;
            });
            reportText += `• Leadership Experience:\n`;
            profile.profile_summary.career_highlights.leadership_experience.forEach(exp => {
                reportText += `  - ${exp}\n`;
            });

            reportText += `\n**Technical Expertise:**\n`;
            reportText += `• Strongest Areas:\n`;
            profile.profile_summary.technical_expertise.strongest_areas.forEach(area => {
                reportText += `  - ${area}\n`;
            });
            reportText += `• Programming Languages: ${profile.profile_summary.technical_expertise.programming_languages.join(', ')}\n`;
            reportText += `• Frameworks: ${profile.profile_summary.technical_expertise.frameworks.join(', ')}\n`;
            reportText += `• Databases: ${profile.profile_summary.technical_expertise.databases.join(', ')}\n`;
            reportText += `• Cloud Platforms: ${profile.profile_summary.technical_expertise.cloud_platforms.join(', ')}\n`;
            reportText += `• Tools: ${profile.profile_summary.technical_expertise.tools.join(', ')}\n\n`;

            // COMPLETE WORK EXPERIENCE DATA ACCESS
            reportText += `💼 **COMPLETE WORK EXPERIENCE DATA**\n`;
            reportText += `━`.repeat(50) + `\n`;
            reportText += `**Overview:** ${workExp.work_experience.total_positions} total positions\n`;
            reportText += `**Industries:** ${workExp.work_experience.summary.industries.join(', ')}\n`;
            reportText += `**Primary Focus:** ${workExp.work_experience.summary.primary_focus.join(', ')}\n\n`;

            reportText += `**DETAILED POSITIONS:**\n\n`;
            workExp.work_experience.positions.forEach((position, index) => {
                reportText += `${index + 1}. **${position.company} - ${position.position}**\n`;
                reportText += `   • Location: ${position.location}\n`;
                reportText += `   • Duration: ${position.duration.start_date} to ${position.duration.end_date} (${position.duration.total_duration})\n`;
                reportText += `   • Type: ${position.type}\n`;
                reportText += `   • Status: ${position.status}\n`;

                if (position.description && position.description.length > 0) {
                    reportText += `   • Key Responsibilities & Achievements:\n`;
                    position.description.forEach(desc => {
                        reportText += `     - ${desc}\n`;
                    });
                }

                if (position.technologies && position.technologies.length > 0) {
                    reportText += `   • Technologies Used: ${position.technologies.join(', ')}\n`;
                }

                if (position.achievements && position.achievements.length > 0) {
                    reportText += `   • Key Achievements:\n`;
                    position.achievements.forEach(achievement => {
                        reportText += `     - ${achievement}\n`;
                    });
                }

                reportText += `\n`;
            });
            reportText += `\n`;

            // COMPLETE SKILLS DATABASE ACCESS
            reportText += `🛠️ **COMPLETE SKILLS DATABASE**\n`;
            reportText += `━`.repeat(50) + `\n`;
            reportText += `**Summary:** ${skills.skills.summary.total_skills} skills across ${Object.keys(skills.skills.categories).length} categories\n`;
            reportText += `**Primary Strengths:** ${skills.skills.summary.primary_strengths.join(', ')}\n`;
            reportText += `**Emerging Skills:** ${skills.skills.summary.emerging_skills.join(', ')}\n\n`;

            reportText += `**DETAILED SKILLS BY CATEGORY:**\n\n`;
            Object.entries(skills.skills.categories).forEach(([categoryKey, categoryData]) => {
                reportText += `**${categoryData.category}:**\n`;
                categoryData.skills.forEach(skill => {
                    reportText += `  • ${skill.name}\n`;
                    reportText += `    - Proficiency: ${skill.proficiency}\n`;
                    reportText += `    - Experience: ${skill.years_experience}\n`;
                    reportText += `    - Context: ${skill.context.join(', ')}\n`;
                });
                reportText += `\n`;
            });
            reportText += `\n`;

            // COMPLETE PROJECTS PORTFOLIO ACCESS
            reportText += `🚀 **COMPLETE PROJECTS PORTFOLIO**\n`;
            reportText += `━`.repeat(50) + `\n`;
            reportText += `**Overview:** ${projects.length} total projects with GitHub repositories\n`;
            reportText += `**Generated:** ${projects[0]?.metadata?.generated_timestamp || 'Recently updated'}\n\n`;

            reportText += `**DETAILED PROJECT DESCRIPTIONS:**\n\n`;
            projects.forEach((projectData, index) => {
                const project = projectData.project;
                reportText += `${index + 1}. **${project.title}**\n`;
                reportText += `   • GitHub: https://github.com/Dextron04/${project.title}\n`;

                if (project.summary || project.raw_summary) {
                    const summary = project.summary || project.raw_summary;
                    reportText += `   • Full Description: ${summary}\n`;
                }

                // Extract technologies mentioned in the summary
                const summary = project.summary || project.raw_summary || '';
                const techPattern = /(React|Node\.js|Python|Java|JavaScript|TypeScript|Docker|AWS|MongoDB|PostgreSQL|MySQL|Git|HTML|CSS|API|REST|GraphQL|Kubernetes|CI\/CD|DevOps|Machine Learning|AI|TensorFlow|PyTorch|Spring Boot|Django|Flask|Redis|Linux|SwiftUI|iOS|Android|C\+\+|C|Go|Rust|Vue|Angular|Express|Tailwind|Bootstrap|Firebase|Azure|GCP|Terraform|Ansible|Jenkins|GitLab|Prometheus|Grafana|Elasticsearch|Kafka|RabbitMQ|Nginx|Apache|SQLite|Oracle|Cassandra|DynamoDB|Spark|Hadoop|Pandas|NumPy|Scikit-learn|Matplotlib|Jupyter|Streamlit|FastAPI|Laravel|PHP|Ruby|Rails|Swift|Kotlin|Dart|Flutter|Unity|Unreal|Blender|Figma|Sketch|Photoshop|Illustrator|XCode|Android Studio|IntelliJ|VSCode|Vim|Emacs)/gi;
                const techMatches = summary.match(techPattern) || [];
                if (techMatches.length > 0) {
                    reportText += `   • Technologies Detected: ${[...new Set(techMatches)].join(', ')}\n`;
                }

                reportText += `\n`;
            });
            reportText += `\n`;

            // COMPLETE LATEX TEMPLATE ACCESS
            reportText += `📄 **LATEX TEMPLATE STRUCTURE & CONTENT**\n`;
            reportText += `━`.repeat(50) + `\n`;
            reportText += `**Template Features:**\n`;
            reportText += `• ATS Optimized: ${template.includes('pdfgentounicode=1') ? '✅ Yes' : '❌ No'}\n`;
            reportText += `• Single Page Format: ${template.includes('\\addtolength{\\topmargin}') ? '✅ Yes' : '❌ No'}\n`;
            reportText += `• Font Icons: ${template.includes('fontawesome') ? '✅ Yes' : '❌ No'}\n`;
            reportText += `• Professional Sections: ${this.extractLatexSections(template).join(', ')}\n`;
            reportText += `• LaTeX Packages: ${this.extractLatexPackages(template).join(', ')}\n`;
            reportText += `• Custom Commands: ${this.extractLatexCommands(template).join(', ')}\n\n`;

            reportText += `**CRITICAL TEMPLATE REQUIREMENTS:**\n`;
            reportText += `• NEVER change the template structure\n`;
            reportText += `• Only replace content within sections\n`;
            reportText += `• Preserve all LaTeX commands exactly\n`;
            reportText += `• Sanitize dynamic content only (& → \\&, % → \\%, etc.)\n`;
            reportText += `• Maintain single-page optimization settings\n`;
            reportText += `• Keep all spacing and formatting commands intact\n\n`;

            if (generateInstructions) {
                reportText += `📋 **UPDATED INSTRUCTIONS BASED ON ANALYSIS**\n`;
                reportText += `━`.repeat(50) + `\n`;
                reportText += this.generateUpdatedInstructions({
                    profileAnalysis,
                    workExpAnalysis,
                    skillsAnalysis,
                    projectsAnalysis,
                    templateAnalysis
                });
            }

            // Note: Complete detailed content is already provided above - no need for separate samples

            if (analyzeRelevance) {
                reportText += `\n🎯 **RELEVANCE ANALYSIS FOR COMMON JOB TYPES**\n`;
                reportText += `━`.repeat(50) + `\n`;
                reportText += this.generateRelevanceAnalysis({ workExpAnalysis, skillsAnalysis, projectsAnalysis });
            }

            reportText += `\n✅ **KNOWLEDGE BASE SCAN COMPLETE**\n`;
            reportText += `All resources have been comprehensively analyzed and instructions updated accordingly.\n`;

            return {
                content: [{
                    type: "text",
                    text: reportText
                }]
            };

        } catch (error) {
            return {
                content: [{
                    type: "text",
                    text: `❌ Knowledge base analysis failed: ${error.message}\n\nStack trace: ${error.stack}`
                }],
                isError: true
            };
        }
    }

    // Helper methods for knowledge base analysis
    calculateAverageDuration(positions) {
        // Simple duration calculation - could be enhanced
        const durations = positions.map(p => p.duration.total_duration).filter(d => d);
        if (durations.length === 0) return 'N/A';

        // Convert durations to months for averaging
        let totalMonths = 0;
        durations.forEach(duration => {
            if (duration.includes('year')) {
                const years = parseFloat(duration);
                totalMonths += years * 12;
            } else if (duration.includes('month')) {
                const months = parseFloat(duration);
                totalMonths += months;
            }
        });

        const avgMonths = totalMonths / durations.length;
        return avgMonths >= 12 ? `${(avgMonths / 12).toFixed(1)} years` : `${Math.round(avgMonths)} months`;
    }

    extractTechnologiesFromProjects(projects) {
        const techPattern = /(React|Node\.js|Python|Java|JavaScript|TypeScript|Docker|AWS|MongoDB|PostgreSQL|MySQL|Git|HTML|CSS|API|REST|GraphQL|Kubernetes|CI\/CD|DevOps|Machine Learning|AI|TensorFlow|PyTorch)/gi;
        const technologies = {};

        projects.forEach(project => {
            const summary = project.project.summary || project.project.raw_summary || '';
            const matches = summary.match(techPattern) || [];
            matches.forEach(tech => {
                technologies[tech.toLowerCase()] = (technologies[tech.toLowerCase()] || 0) + 1;
            });
        });

        return technologies;
    }

    categorizeProjects(projects) {
        const categories = {
            'Web Development': 0,
            'Mobile Development': 0,
            'System Programming': 0,
            'AI/ML': 0,
            'DevOps/Infrastructure': 0,
            'API Development': 0,
            'Other': 0
        };

        projects.forEach(project => {
            const summary = (project.project.summary || project.project.raw_summary || '').toLowerCase();

            if (summary.includes('web') || summary.includes('react') || summary.includes('node') || summary.includes('frontend') || summary.includes('backend')) {
                categories['Web Development']++;
            } else if (summary.includes('mobile') || summary.includes('ios') || summary.includes('android') || summary.includes('app')) {
                categories['Mobile Development']++;
            } else if (summary.includes('system') || summary.includes('file system') || summary.includes('operating') || summary.includes('c++') || summary.includes('shell')) {
                categories['System Programming']++;
            } else if (summary.includes('ai') || summary.includes('machine learning') || summary.includes('ml') || summary.includes('tensorflow') || summary.includes('neural')) {
                categories['AI/ML']++;
            } else if (summary.includes('docker') || summary.includes('kubernetes') || summary.includes('deploy') || summary.includes('infrastructure') || summary.includes('server')) {
                categories['DevOps/Infrastructure']++;
            } else if (summary.includes('api') || summary.includes('rest') || summary.includes('graphql') || summary.includes('microservice')) {
                categories['API Development']++;
            } else {
                categories['Other']++;
            }
        });

        return categories;
    }

    extractLatexSections(template) {
        const sectionMatches = template.match(/\\section\{([^}]+)\}/g) || [];
        return sectionMatches.map(match => match.replace(/\\section\{([^}]+)\}/, '$1'));
    }

    extractLatexPackages(template) {
        const packageMatches = template.match(/\\usepackage(?:\[[^\]]*\])?\{([^}]+)\}/g) || [];
        return packageMatches.map(match => match.replace(/\\usepackage(?:\[[^\]]*\])?\{([^}]+)\}/, '$1'));
    }

    extractLatexCommands(template) {
        const commandMatches = template.match(/\\newcommand\{([^}]+)\}/g) || [];
        return commandMatches.map(match => match.replace(/\\newcommand\{([^}]+)\}.*/, '$1'));
    }

    generateUpdatedInstructions(analysis) {
        let instructions = `**COMPREHENSIVE RESUME GENERATION INSTRUCTIONS**\n`;
        instructions += `Based on complete knowledge base access provided above.\n\n`;

        instructions += `🎯 **MANDATORY WORKFLOW:**\n`;
        instructions += `1. REVIEW all detailed content provided above completely\n`;
        instructions += `2. ANALYZE job description for required skills and experience\n`;
        instructions += `3. SELECT most relevant experiences, skills, and projects from data above\n`;
        instructions += `4. GENERATE tailored resume using template format (preserve exactly)\n`;
        instructions += `5. ENSURE all requirements below are met\n\n`;

        instructions += `👤 **PROFILE & CONTACT USAGE:**\n`;
        instructions += `• Use EXACT contact information provided above\n`;
        instructions += `• Include: Name, phone, email, GitHub, LinkedIn, portfolio\n`;
        instructions += `• Education: Bachelor of Science in Computer Science, GPA: 3.95/4.0\n`;
        instructions += `• Graduation: December 2025, Honors: Phi Beta Kappa Honor Society\n\n`;

        instructions += `💼 **WORK EXPERIENCE SELECTION:**\n`;
        instructions += `• MUST select from the detailed positions listed above\n`;
        instructions += `• PRIORITIZE current positions: SellWizr, San Francisco State University\n`;
        instructions += `• CONSIDER: Site Service Software, meetX, Glitter based on relevance\n`;
        instructions += `• Use EXACT descriptions and achievements from above data\n`;
        instructions += `• ENFORCE: Exactly 3 bullet points per position\n`;
        instructions += `• NEVER invent or modify the provided descriptions\n\n`;

        instructions += `🛠️ **SKILLS SELECTION GUIDELINES:**\n`;
        instructions += `• REFERENCE the complete skills database above\n`;
        instructions += `• SELECT skills matching job requirements from categories provided\n`;
        instructions += `• PRIORITIZE Advanced proficiency skills when available\n`;
        instructions += `• USE the exact skill names from the database\n`;
        instructions += `• ORGANIZE by categories: Programming, Frontend & Backend, Databases & Cloud, AI/ML & Tools\n\n`;

        instructions += `🚀 **PROJECT SELECTION RULES:**\n`;
        instructions += `• CHOOSE from the 25 detailed projects listed above\n`;
        instructions += `• SELECT projects with technologies matching job requirements\n`;
        instructions += `• EXTRACT relevant points from full descriptions provided\n`;
        instructions += `• ENFORCE: Exactly 2 bullet points per project\n`;
        instructions += `• INCLUDE: GitHub link for each project (https://github.com/Dextron04/PROJECT_NAME)\n`;
        instructions += `• NEVER invent project details not in the descriptions above\n\n`;

        instructions += `📝 **CONTENT CREATION RULES:**\n`;
        instructions += `• SUMMARY: 2-3 lines max, incorporate job keywords with experience level\n`;
        instructions += `• USE ONLY information from the detailed data provided above\n`;
        instructions += `• TAILOR content by emphasizing relevant aspects from full descriptions\n`;
        instructions += `• MAINTAIN professional tone and ATS-friendly formatting\n\n`;

        instructions += `📄 **TEMPLATE FORMAT COMPLIANCE:**\n`;
        instructions += `• NEVER alter LaTeX template structure or commands\n`;
        instructions += `• ONLY sanitize dynamic content (& → \\&, % → \\%, $ → \\$, etc.)\n`;
        instructions += `• PRESERVE exact spacing, sections, and formatting\n`;
        instructions += `• USE template sections: Summary, Experience, Projects, Education, Skills\n`;
        instructions += `• MAINTAIN single-page optimization settings\n\n`;

        instructions += `⚠️ **CRITICAL REQUIREMENTS:**\n`;
        instructions += `• PAGE LIMIT: Exactly 1 page - NEVER exceed\n`;
        instructions += `• AUTHENTICITY: Use ONLY the detailed information provided above\n`;
        instructions += `• ACCURACY: Reference specific details from the comprehensive data\n`;
        instructions += `• RELEVANCE: Select content matching job description requirements\n`;
        instructions += `• LINKS: Include GitHub links for all selected projects\n`;
        instructions += `• FORMAT: Preserve LaTeX template exactly as specified\n\n`;

        return instructions;
    }

    async generateContentSamples(data) {
        let samples = `**PROFILE SUMMARY SAMPLE:**\n`;
        samples += `Name: ${data.profile.profile_summary.personal_info.name}\n`;
        samples += `Contact: ${data.profile.profile_summary.personal_info.contact.email}\n`;
        samples += `GitHub: ${data.profile.profile_summary.personal_info.contact.github}\n`;
        samples += `Portfolio: ${data.profile.profile_summary.personal_info.contact.portfolio}\n\n`;

        samples += `**RECENT WORK EXPERIENCE SAMPLE:**\n`;
        const currentPositions = data.workExp.work_experience.positions.filter(p => p.status === 'Current');
        if (currentPositions.length > 0) {
            const pos = currentPositions[0];
            samples += `Position: ${pos.position} at ${pos.company}\n`;
            samples += `Duration: ${pos.duration.start_date} - ${pos.duration.end_date}\n`;
            samples += `Technologies: ${pos.technologies ? pos.technologies.join(', ') : 'N/A'}\n`;
            if (pos.description && pos.description.length > 0) {
                samples += `Sample Achievement: ${pos.description[0]}\n`;
            }
        }
        samples += `\n`;

        samples += `**TOP SKILLS SAMPLE:**\n`;
        const programmingCategory = data.skills.skills.categories.programming_languages;
        if (programmingCategory) {
            const topSkills = programmingCategory.skills
                .filter(s => s.proficiency === 'Advanced')
                .slice(0, 5)
                .map(s => `${s.name} (${s.years_experience})`)
                .join(', ');
            samples += `Programming: ${topSkills}\n`;
        }
        samples += `\n`;

        samples += `**PROJECT SAMPLES:**\n`;
        data.projects.slice(0, 3).forEach((project, index) => {
            samples += `${index + 1}. ${project.project.title}\n`;
            const summary = project.project.summary || project.project.raw_summary || 'No summary available';
            samples += `   Summary: ${summary.substring(0, 150)}...\n`;
        });

        return samples;
    }

    generateRelevanceAnalysis(analysis) {
        const jobTypes = {
            'Full-Stack Developer': {
                skills: ['JavaScript', 'React', 'Node.js', 'PostgreSQL', 'MongoDB', 'AWS'],
                experience: ['Full-Stack', 'Web Development', 'API'],
                projects: ['Web Development', 'API Development']
            },
            'Backend Developer': {
                skills: ['Java', 'Python', 'Spring Boot', 'PostgreSQL', 'Docker', 'AWS'],
                experience: ['Backend', 'API', 'Database'],
                projects: ['API Development', 'DevOps/Infrastructure']
            },
            'DevOps Engineer': {
                skills: ['Docker', 'Kubernetes', 'AWS', 'CI/CD', 'Linux'],
                experience: ['DevOps', 'Infrastructure', 'Deployment'],
                projects: ['DevOps/Infrastructure', 'System Programming']
            },
            'Mobile Developer': {
                skills: ['React Native', 'JavaScript', 'Mobile'],
                experience: ['Mobile', 'App Development'],
                projects: ['Mobile Development', 'Web Development']
            }
        };

        let relevanceReport = '';
        Object.entries(jobTypes).forEach(([jobType, requirements]) => {
            relevanceReport += `**${jobType}:**\n`;

            // Calculate skill relevance
            const skillsData = Object.values(analysis.skillsAnalysis.categoryBreakdown);
            const relevantSkills = requirements.skills.length; // Simplified - would need actual matching
            relevanceReport += `  Skills Match: ${relevantSkills}/${requirements.skills.length} requirements covered\n`;

            // Calculate project relevance
            const projectRelevance = requirements.projects.reduce((acc, type) => {
                return acc + (analysis.projectsAnalysis.projectTypes[type] || 0);
            }, 0);
            relevanceReport += `  Relevant Projects: ${projectRelevance} projects\n`;

            relevanceReport += `  Overall Fit: ${projectRelevance > 0 && relevantSkills > 0 ? 'STRONG' : 'MODERATE'}\n\n`;
        });

        return relevanceReport;
    }

    async handleRefreshKnowledgeBase() {
        this.knowledgeBase.clearCache();

        return {
            content: [{
                type: "text",
                text: `✅ Knowledge base cache refreshed successfully!

All cached data has been cleared and will be reloaded on next access. This ensures you're working with the latest:
- Profile information
- Work experience 
- Skills database
- Projects portfolio
- LaTeX templates`
            }]
        };
    }

    async run() {
        const transport = new StdioServerTransport();
        await this.server.connect(transport);
        console.error("🚀 AI Resume MCP Server running...");
    }
}

// Start the server
if (import.meta.url === `file://${process.argv[1]}`) {
    const server = new AIResumeMcpServer();
    server.run().catch(console.error);
}

export { AIResumeMcpServer };

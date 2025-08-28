import os
import re
import subprocess
from jinja2 import Template, StrictUndefined

def escape_latex(text):
    """Escape special LaTeX characters."""
    special_chars = {
        '&': '\\&',
        '%': '\\%',
        '$': '\\$',
        '#': '\\#',
        '_': '\\_',
        '{': '\\{',
        '}': '\\}',
        '~': '\\textasciitilde{}',
        '^': '\\textasciicircum{}',
        '\\': '\\textbackslash{}',
    }
    for char, replacement in special_chars.items():
        text = text.replace(char, replacement)
    return text

def parse_resume_sections(text):
    """Parse resume text into structured sections."""
    # Initialize default sections
    sections = {
        'name': '',
        'contact': {
            'email': '',
            'phone': '',
            'location': '',
            'linkedin': '',
            'github': ''
        },
        'education': '',
        'experience': '',
        'projects': '',
        'skills': '',
        'leadership': '',
        'certifications': ''
    }
    
    # Split text into lines and clean up
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    # Extract name (usually the first line)
    if lines:
        sections['name'] = lines[0]
    
    # Extract contact information
    for line in lines:
        # Email
        email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', line)
        if email_match:
            sections['contact']['email'] = email_match.group(0)
        
        # Phone
        phone_match = re.search(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', line)
        if phone_match:
            sections['contact']['phone'] = phone_match.group(0)
        
        # LinkedIn
        linkedin_match = re.search(r'linkedin\.com/in/[a-zA-Z0-9-]+', line)
        if linkedin_match:
            sections['contact']['linkedin'] = f"https://www.{linkedin_match.group(0)}"
        
        # GitHub
        github_match = re.search(r'github\.com/[a-zA-Z0-9-]+', line)
        if github_match:
            sections['contact']['github'] = f"https://www.{github_match.group(0)}"
        
        # Location (common locations in resumes)
        location_match = re.search(r'(Waterloo|Toronto|Ontario|Canada|UAE)', line)
        if location_match:
            sections['contact']['location'] = location_match.group(0)

    # Build section content
    current_section = None
    section_content = []
    
    for line in lines:
        # Check for section headers
        if any(line.startswith(header) for header in ['EDUCATION', 'Education']):
            if current_section:
                sections[current_section.lower()] = '\n'.join(section_content)
            current_section = 'education'
            section_content = [line]
        elif any(line.startswith(header) for header in ['EXPERIENCE', 'Experience']):
            if current_section:
                sections[current_section.lower()] = '\n'.join(section_content)
            current_section = 'experience'
            section_content = [line]
        elif any(line.startswith(header) for header in ['PROJECTS', 'Projects']):
            if current_section:
                sections[current_section.lower()] = '\n'.join(section_content)
            current_section = 'projects'
            section_content = [line]
        elif any(line.startswith(header) for header in ['SKILLS', 'Skills', 'TECHNICAL SKILLS', 'Technical Skills']):
            if current_section:
                sections[current_section.lower()] = '\n'.join(section_content)
            current_section = 'skills'
            section_content = [line]
        elif any(line.startswith(header) for header in ['LEADERSHIP', 'Leadership']):
            if current_section:
                sections[current_section.lower()] = '\n'.join(section_content)
            current_section = 'leadership'
            section_content = [line]
        elif any(line.startswith(header) for header in ['CERTIFICATIONS', 'Certifications']):
            if current_section:
                sections[current_section.lower()] = '\n'.join(section_content)
            current_section = 'certifications'
            section_content = [line]
        elif current_section:
            section_content.append(line)
    
    # Add the last section
    if current_section:
        sections[current_section.lower()] = '\n'.join(section_content)
    
    # Debug print
    print("\nParsed sections:")
    for section, content in sections.items():
        if section == 'contact':
            print(f"Contact info: {content}")
        else:
            # Count lines by splitting and filtering empty lines
            line_count = len([line for line in content.split('\n') if line.strip()]) if content else 0
            print(f"{section.title()}: {line_count} lines")
    
    return sections

def parse_education_section(section):
    """Parse education section into structured format for Jake's template."""
    if not section:
        return []
        
    entries = []
    lines = section.split('\n')[1:]  # Skip the "Education" header
    current_entry = []
    
    for line in lines:
        line = line.strip()
        if line and (line.startswith('•') or line.startswith('-')):
            if current_entry:
                current_entry.append(line)
        elif not line and current_entry:
            # Process the completed entry
            entry = process_education_entry(current_entry)
            if entry:
                entries.append(entry)
            current_entry = []
        elif line and (any(school in line.upper() for school in ['UNIVERSITY', 'COLLEGE', 'SCHOOL']) or
                      any(degree in line.upper() for degree in ['BACHELOR', 'MASTER', 'PHD', 'DIPLOMA'])):
            if current_entry:
                entry = process_education_entry(current_entry)
                if entry:
                    entries.append(entry)
            current_entry = [line]
        elif line and current_entry:
            current_entry.append(line)
        elif line:
            current_entry = [line]
    
    # Process any remaining entry
    if current_entry:
        entry = process_education_entry(current_entry)
        if entry:
            entries.append(entry)
    
    return entries

def process_education_entry(lines):
    """Helper function to process education entry lines."""
    if not lines:
        return None
        
    entry = {
        'institution': '',
        'degree': '',
        'location': '',
        'date': '',
        'bullets': []
    }
    
    # Process first line (usually contains institution and date)
    first_line = lines[0]
    
    # Try different date formats
    date_match = re.search(r'\((.*?)\)|(?:Sep|Sept|September|Jan|January|Feb|February|Mar|March|Apr|April|May|Jun|June|Jul|July|Aug|August|Oct|October|Nov|November|Dec|December)\s+\d{4}\s*-\s*(?:Present|[A-Za-z]+\s+\d{4})', first_line)
    if date_match:
        entry['date'] = date_match.group(0).strip('()')
        first_line = re.sub(r'\(.*?\)', '', first_line).strip()  # Remove date in parentheses
        first_line = re.sub(date_match.group(0), '', first_line).strip()  # Remove other date format
    
    # Split remaining text by common delimiters
    parts = [p.strip() for p in re.split(r'[,|]', first_line) if p.strip()]
    
    # First part is usually the institution
    if parts:
        entry['institution'] = parts[0]
    
    # Look for location in the parts
    for part in parts:
        if any(loc in part.upper() for loc in ['WATERLOO', 'TORONTO', 'ONTARIO', 'UAE']):
            entry['location'] = part.strip()
            break
    
    # Process remaining lines for degree and bullets
    for line in lines[1:]:
        line = line.strip()
        if line.startswith('•') or line.startswith('-'):
            entry['bullets'].append(line.strip('• ').strip('- ').strip())
        elif 'Recipient' in line or 'Scholar' in line or 'Honours' in line or 'Bachelor' in line:
            entry['degree'] = line.strip()
    
    # If location is still empty and we found a location in the institution name
    if not entry['location'] and any(loc in entry['institution'].upper() for loc in ['WATERLOO', 'TORONTO', 'ONTARIO', 'UAE']):
        entry['location'] = 'Waterloo, ON' if 'WATERLOO' in entry['institution'].upper() else 'UAE'
    
    return entry

def parse_experience_section(section):
    """Parse experience section into structured format for Jake's template."""
    if not section:
        return []
        
    entries = []
    lines = section.split('\n')[1:]  # Skip the "Experience" header
    current_entry = []
    
    for line in lines:
        line = line.strip()
        if line and (line.startswith('•') or line.startswith('-')):
            if current_entry:
                current_entry.append(line)
        elif not line and current_entry:
            # Process the completed entry
            entry = process_experience_entry(current_entry)
            if entry:
                entries.append(entry)
            current_entry = []
        elif line and any(title in line.upper() for title in ['MANAGER', 'DEVELOPER', 'ENGINEER', 'INTERN', 'CAPTAIN', 'LEADER', 'PRESIDENT']):
            if current_entry:
                entry = process_experience_entry(current_entry)
                if entry:
                    entries.append(entry)
            current_entry = [line]
        elif line and current_entry:
            current_entry.append(line)
        elif line:
            current_entry = [line]
    
    # Process any remaining entry
    if current_entry:
        entry = process_experience_entry(current_entry)
        if entry:
            entries.append(entry)
    
    return entries

def process_experience_entry(lines):
    """Helper function to process experience entry lines."""
    if not lines:
        return None
        
    entry = {
        'title': '',
        'organization': '',
        'location': '',
        'date': '',
        'bullets': []
    }
    
    # Process first line (usually contains title, organization, and date)
    first_line = lines[0]
    
    # Try different date formats and preserve the original date format
    date_match = re.search(r'\((.*?)\)|(?:Sep|Sept|September|Jan|January|Feb|February|Mar|March|Apr|April|May|Jun|June|Jul|July|Aug|August|Oct|October|Nov|November|Dec|December)\s+\d{4}\s*-\s*(?:Present|[A-Za-z]+\s+\d{4})', first_line)
    if date_match:
        entry['date'] = date_match.group(0).strip('()')
        first_line = re.sub(r'\(.*?\)', '', first_line).strip()  # Remove date in parentheses
        first_line = re.sub(date_match.group(0), '', first_line).strip()  # Remove other date format
    
    # Split remaining text by common delimiters but preserve more context
    parts = [p.strip() for p in re.split(r',(?![^(]*\))', first_line) if p.strip()]
    
    # First part is usually the title
    if parts:
        entry['title'] = parts[0]
        
    # Second part (if exists) is usually the organization
    if len(parts) > 1:
        # Check if the second part is a location
        if any(loc in parts[1].upper() for loc in ['WATERLOO', 'TORONTO', 'ONTARIO', 'UAE']):
            entry['location'] = parts[1]
            # Join remaining parts as organization if any
            if len(parts) > 2:
                entry['organization'] = ', '.join(parts[2:])
        else:
            entry['organization'] = parts[1]
            # Look for location in remaining parts
            location_found = False
            for i, part in enumerate(parts[2:], 2):
                if any(loc in part.upper() for loc in ['WATERLOO', 'TORONTO', 'ONTARIO', 'UAE']):
                    entry['location'] = part.strip()
                    location_found = True
                    # Join any remaining parts to organization
                    if i + 1 < len(parts):
                        entry['organization'] += ', ' + ', '.join(parts[i+1:])
                    break
            if not location_found and len(parts) > 2:
                # If no location found, append remaining parts to organization
                entry['organization'] += ', ' + ', '.join(parts[2:])
    
    # Process all non-empty lines as bullets, preserving more detail
    entry['bullets'] = []
    for line in lines[1:]:
        line = line.strip()
        if line:
            # Remove bullet points but keep the content
            bullet = line.lstrip('•').lstrip('-').strip()
            if bullet and not any(section in bullet for section in ['Education', 'Experience', 'Projects', 'Skills', 'Leadership', 'Certifications']):
                entry['bullets'].append(bullet)
    
    return entry

def parse_projects_section(section):
    """Parse projects section into structured format for Jake's template."""
    if not section:
        return []
        
    entries = []
    lines = section.split('\n')[1:]  # Skip the "Projects" header
    current_entry = []
    
    for line in lines:
        line = line.strip()
        if line and (line.startswith('•') or line.startswith('-')):
            if current_entry:
                current_entry.append(line)
        elif not line and current_entry:
            # Process the completed entry
            entry = process_project_entry(current_entry)
            if entry:
                entries.append(entry)
            current_entry = []
        elif line and ('|' in line or ':' in line):
            if current_entry:
                entry = process_project_entry(current_entry)
                if entry:
                    entries.append(entry)
            current_entry = [line]
        elif line and current_entry:
            current_entry.append(line)
        elif line:
            current_entry = [line]
    
    # Process any remaining entry
    if current_entry:
        entry = process_project_entry(current_entry)
        if entry:
            entries.append(entry)
    
    return entries

def process_project_entry(lines):
    """Helper function to process project entry lines."""
    if not lines:
        return None
        
    entry = {
        'name': '',
        'technologies': '',
        'date': '2024',  # Default to current year
        'bullets': []
    }
    
    # Process first line (usually contains project name and technologies)
    first_line = lines[0]
    
    # Extract date if present
    date_match = re.search(r'\((.*?)\)', first_line)
    if date_match:
        entry['date'] = date_match.group(1).strip()
        first_line = re.sub(r'\(.*?\)', '', first_line).strip()
    
    # Try to split by | first, then by :
    if '|' in first_line:
        parts = [p.strip() for p in first_line.split('|')]
        entry['name'] = parts[0]
        if len(parts) > 1:
            # Join all remaining parts as technologies
            entry['technologies'] = ' | '.join(parts[1:])
    elif ':' in first_line:
        name, tech = first_line.split(':', 1)
        entry['name'] = name.strip()
        entry['technologies'] = tech.strip()
    else:
        entry['name'] = first_line
    
    # Process all non-empty lines as bullets, preserving more information
    entry['bullets'] = []
    for line in lines[1:]:
        line = line.strip()
        if line:
            # Remove bullet points but keep the content
            bullet = line.lstrip('•').lstrip('-').strip()
            if bullet:
                entry['bullets'].append(bullet)
    
    return entry

def format_project_entry(project):
    """Format project entry according to Jake's template style."""
    latex = []
    
    # Project name and technologies on the same line, with date right-aligned
    project_header = f"\\textbf{{{escape_latex(project['name'])}}}"
    if project['technologies']:
        project_header += f" | {escape_latex(project['technologies'])}"
    latex.append(f"{project_header} \\hfill {escape_latex(project['date'])}")
    
    # Add bullets
    if project['bullets']:
        latex.append("\\begin{itemize}[leftmargin=*]")
        for bullet in project['bullets']:
            latex.append(f"  \\item {escape_latex(bullet)}")
        latex.append("\\end{itemize}")
    
    return "\n".join(latex)

def format_leadership_entry(entry):
    """Format leadership entry according to Jake's template style."""
    latex = []
    
    # Format the header using resumeSubheading command
    title = escape_latex(entry['title'])
    org = escape_latex(entry['organization']) if entry['organization'] else ''
    loc = escape_latex(entry['location']) if entry['location'] else ''
    date = escape_latex(entry['date']) if entry['date'] else ''
    
    # Combine title and organization
    position = title
    if org:
        position += f", {org}"
    
    # Use the resumeSubheading command with proper arguments
    latex.append(f"\\resumeSubheading{{{position}}}{{{loc}}}{{{''}}}{{{date}}}")
    
    # Add bullets if any
    if entry['bullets']:
        latex.append("\\resumeItemListStart")
        for bullet in entry['bullets']:
            latex.append(f"  \\resumeItem{{{escape_latex(bullet)}}}")
        latex.append("\\resumeItemListEnd")
    
    return "\n".join(latex)

def format_skills(skills):
    """Format skills section according to Jake's template style."""
    if not skills:
        return ""
    
    latex = []
    for category, skill_list in skills.items():
        if skill_list:
            latex.append(f"\\textbf{{{escape_latex(category)}}}: {escape_latex(', '.join(skill_list))}")
    
    return "\\\\\n".join(latex)

def parse_skills_section(section):
    """Parse skills section into structured format for Jake's template."""
    technical_skills = {}
    lines = section.split('\n')[1:]  # Skip the "Skills" header
    
    current_category = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        if line.startswith('•'):
            line = line[1:].strip()
        
        if ':' in line:
            # Start new category
            category, items = line.split(':', 1)
            current_category = category.strip()
            # Split by comma but preserve parenthetical descriptions
            items = re.findall(r'([^,]+(?:\([^)]*\))?)', items)
            items = [item.strip() for item in items if item.strip()]
            if items:
                technical_skills[current_category] = items
        elif current_category and line:
            # Add to current category
            if current_category not in technical_skills:
                technical_skills[current_category] = []
            # Split by comma but preserve parenthetical descriptions
            items = re.findall(r'([^,]+(?:\([^)]*\))?)', line)
            technical_skills[current_category].extend([item.strip() for item in items if item.strip()])
    
    return technical_skills

def parse_leadership_section(section):
    """Parse leadership section into structured format for Jake's template."""
    if not section:
        return []
    
    entries = []
    lines = section.split('\n')[1:]  # Skip the "Leadership" header
    current_entry = []
    
    for line in lines:
        line = line.strip()
        if not line:
            if current_entry:
                entry = {
                    'title': '',
                    'organization': '',
                    'location': '',
                    'date': '',
                    'bullets': []
                }
                
                # Process header line (title, organization, date)
                if current_entry[0]:
                    # Split by comma but preserve parentheses and more context
                    parts = re.split(r',(?![^(]*\))', current_entry[0])
                    if len(parts) >= 1:
                        entry['title'] = parts[0].strip()
                    if len(parts) >= 2:
                        entry['organization'] = parts[1].strip()
                        
                    # Extract date from parentheses or standard format
                    date_match = re.search(r'\((.*?)\)|(?:Sep|Sept|September|Jan|January|Feb|February|Mar|March|Apr|April|May|Jun|June|Jul|July|Aug|August|Oct|October|Nov|November|Dec|December)\s+\d{4}\s*-\s*(?:Present|[A-Za-z]+\s+\d{4})', current_entry[0])
                    if date_match:
                        entry['date'] = date_match.group(0).strip('()')
                        
                    # Look for location in remaining parts
                    location_found = False
                    for i, part in enumerate(parts[2:], 2):
                        if any(loc in part.upper() for loc in ['WATERLOO', 'TORONTO', 'ONTARIO', 'UAE']):
                            entry['location'] = part.strip()
                            location_found = True
                            # Join any remaining parts to organization
                            if i + 1 < len(parts):
                                entry['organization'] += ', ' + ', '.join(parts[i+1:])
                            break
                    if not location_found and len(parts) > 2:
                        # If no location found, append remaining parts to organization
                        entry['organization'] += ', ' + ', '.join(parts[2:])
                
                # Process all non-empty lines as bullets, preserving more detail
                entry['bullets'] = []
                for line in current_entry[1:]:
                    line = line.strip()
                    if line:
                        # Remove bullet points but keep the content
                        bullet = line.lstrip('•').lstrip('-').strip()
                        if bullet and not any(section in bullet for section in ['Education', 'Experience', 'Projects', 'Skills', 'Leadership', 'Certifications']):
                            entry['bullets'].append(bullet)
                
                entries.append(entry)
                current_entry = []
        else:
            current_entry.append(line)
    
    # Process any remaining entry
    if current_entry:
        entry = {
            'title': '',
            'organization': '',
            'location': '',
            'date': '',
            'bullets': []
        }
        
        if current_entry[0]:
            parts = re.split(r',(?![^(]*\))', current_entry[0])
            if len(parts) >= 1:
                entry['title'] = parts[0].strip()
            if len(parts) >= 2:
                entry['organization'] = parts[1].strip()
                
            date_match = re.search(r'\((.*?)\)|(?:Sep|Sept|September|Jan|January|Feb|February|Mar|March|Apr|April|May|Jun|June|Jul|July|Aug|August|Oct|October|Nov|November|Dec|December)\s+\d{4}\s*-\s*(?:Present|[A-Za-z]+\s+\d{4})', current_entry[0])
            if date_match:
                entry['date'] = date_match.group(0).strip('()')
                
            location_found = False
            for i, part in enumerate(parts[2:], 2):
                if any(loc in part.upper() for loc in ['WATERLOO', 'TORONTO', 'ONTARIO', 'UAE']):
                    entry['location'] = part.strip()
                    location_found = True
                    if i + 1 < len(parts):
                        entry['organization'] += ', ' + ', '.join(parts[i+1:])
                    break
            if not location_found and len(parts) > 2:
                entry['organization'] += ', ' + ', '.join(parts[2:])
        
        # Process all non-empty lines as bullets
        for line in current_entry[1:]:
            line = line.strip()
            if line:
                bullet = line.lstrip('•').lstrip('-').strip()
                if bullet and not any(section in bullet for section in ['Education', 'Experience', 'Projects', 'Skills', 'Leadership', 'Certifications']):
                    entry['bullets'].append(bullet)
        
        entries.append(entry)
    
    return entries

def parse_certifications_section(section):
    """Parse certifications section into LaTeX format."""
    certs = []
    lines = section.split('\n')[1:]  # Skip the "Certifications" header
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        if line.startswith('•'):
            line = line[1:].strip()
            
        if line:  # Add any non-empty certification
            certs.append(line)
    
    return certs

def format_education_entry(entry):
    """Format education entry according to Jake's template style."""
    latex = []
    
    # Institution and Location on the same line, with Location right-aligned
    latex.append(f"\\textbf{{{escape_latex(entry['institution'])}}} \\hfill {escape_latex(entry['location'])}")
    
    # Degree on the next line, with date right-aligned if available
    if 'date' in entry and entry['date']:
        latex.append(f"\\textit{{{escape_latex(entry['degree'])}}} \\hfill {escape_latex(entry['date'])}")
    else:
        latex.append(f"\\textit{{{escape_latex(entry['degree'])}}}")
    
    # Add bullets if any
    if entry['bullets']:
        latex.append("\\begin{itemize}[leftmargin=*]")
        for bullet in entry['bullets']:
            latex.append(f"  \\item {escape_latex(bullet)}")
        latex.append("\\end{itemize}")
    
    return "\n".join(latex)

def format_experience_entry(entry):
    """Format experience entry according to Jake's template style."""
    latex = []
    
    # Title and Organization on the same line
    title_org = f"\\textbf{{{escape_latex(entry['title'])}}}"
    if entry['organization']:
        title_org += f", {escape_latex(entry['organization'])}"
    
    # Add location and date, right-aligned
    if entry['location'] and entry['date']:
        latex.append(f"{title_org} \\hfill {escape_latex(entry['location'])} | {escape_latex(entry['date'])}")
    elif entry['date']:
        latex.append(f"{title_org} \\hfill {escape_latex(entry['date'])}")
    else:
        latex.append(title_org)
    
    # Add bullets
    if entry['bullets']:
        latex.append("\\begin{itemize}[leftmargin=*]")
        for bullet in entry['bullets']:
            latex.append(f"  \\item {escape_latex(bullet)}")
        latex.append("\\end{itemize}")
    
    return "\n".join(latex)

def format_certifications(certs):
    """Format certifications according to Jake's template style."""
    if not certs:
        return ""
        
    latex = []
    for cert in certs:
        if 'name' in cert and cert['name']:
            cert_line = f"\\textbf{{{escape_latex(cert['name'])}}}"
            if 'issuer' in cert and cert['issuer']:
                cert_line += f" - {escape_latex(cert['issuer'])}"
            if 'date' in cert and cert['date']:
                cert_line += f" \\hfill {escape_latex(cert['date'])}"
            latex.append(cert_line)
            
            if 'description' in cert and cert['description']:
                latex.append("\\begin{itemize}[leftmargin=*]")
                latex.append(f"  \\item {escape_latex(cert['description'])}")
                latex.append("\\end{itemize}")
    
    return "\n".join(latex)

def format_bullets(bullets):
    """Format bullet points according to Jake's template style."""
    if not bullets:
        return ""
    
    latex = ["\\begin{itemize}[leftmargin=*]"]
    for bullet in bullets:
        latex.append(f"  \\item {escape_latex(bullet)}")
    latex.append("\\end{itemize}")
    return "\n".join(latex)

def convert_to_latex(resume_text):
    """Convert resume text to LaTeX format using Jake's template."""
    sections = parse_resume_sections(resume_text)
    
    # Read the template
    template_path = os.path.join(os.path.dirname(__file__), 'templates', 'resume_template.tex')
    with open(template_path, 'r') as f:
        template_content = f.read()
    
    # Create Jinja2 template with strict undefined and proper configuration
    template = Template(
        template_content,
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
        block_start_string='{% ',
        block_end_string=' %}',
        variable_start_string='{{ ',
        variable_end_string=' }}',
        comment_start_string='{# ',
        comment_end_string=' #}'
    )
    
    try:
        # Parse sections
        education = parse_education_section(sections['education'])
        experience = parse_experience_section(sections['experience'])
        projects = parse_projects_section(sections['projects'])
        skills = parse_skills_section(sections['skills'])
        leadership = parse_leadership_section(sections['leadership'])
        certifications = parse_certifications_section(sections['certifications'])
        
        # Format sections
        formatted_education = [format_education_entry(entry) for entry in education]
        formatted_experience = [format_experience_entry(entry) for entry in experience]
        formatted_projects = [format_project_entry(project) for project in projects]
        formatted_skills = format_skills(skills)
        formatted_leadership = [format_leadership_entry(entry) for entry in leadership] if leadership else None
        formatted_certifications = format_certifications(certifications) if certifications else None
        
        # Debug print
        print("Formatted sections:")
        print(f"Education: {len(formatted_education)} entries")
        print(f"Experience: {len(formatted_experience)} entries")
        print(f"Projects: {len(formatted_projects)} entries")
        print(f"Leadership: {'Yes' if formatted_leadership else 'No'}")
        print(f"Certifications: {'Yes' if formatted_certifications else 'No'}")
        
        # Render template
        latex_content = template.render(
            name=sections['name'],
            email=sections['contact']['email'],
            phone=sections['contact']['phone'],
            location=sections['contact'].get('location', ''),
            linkedin=sections['contact']['linkedin'],
            github=sections['contact'].get('github', ''),
            education=formatted_education,
            experience=formatted_experience,
            projects=formatted_projects,
            skills=formatted_skills,
            leadership=formatted_leadership,
            certifications=formatted_certifications
        )
        
        # Debug: Write the generated LaTeX content to a file
        debug_path = os.path.join(os.path.dirname(__file__), 'debug_output.tex')
        with open(debug_path, 'w') as f:
            f.write(latex_content)
        
        return latex_content
        
    except Exception as e:
        print(f"Error in convert_to_latex: {str(e)}")
        raise

def generate_pdf(latex_content, output_path):
    """Generate PDF from LaTeX content using pdflatex."""
    # Create a temporary directory for LaTeX files
    temp_dir = os.path.dirname(output_path)
    temp_tex_path = os.path.join(temp_dir, 'temp_resume.tex')
    
    try:
        # Write LaTeX content to temporary file
        with open(temp_tex_path, 'w') as f:
            f.write(latex_content)
        
        # Debug: Print the LaTeX packages installed
        subprocess.run(['tlmgr', 'list', '--only-installed'], capture_output=True, text=True)
        
        # Run pdflatex with detailed error reporting
        for i in range(2):
            print(f"LaTeX compilation attempt {i+1}")
            result = subprocess.run([
                'pdflatex',
                '-interaction=nonstopmode',
                '-file-line-error',
                '-output-directory=' + temp_dir,
                temp_tex_path
            ], capture_output=True, text=True)
            
            # Print any errors for debugging
            if result.returncode != 0:
                print(f"LaTeX Error Output (Attempt {i+1}):")
                print(result.stderr)
                print(f"LaTeX Standard Output (Attempt {i+1}):")
                print(result.stdout)
                
                # Check if the PDF was actually created despite errors
                pdf_path = os.path.join(temp_dir, 'temp_resume.pdf')
                if not os.path.exists(pdf_path):
                    raise Exception("PDF file was not created")
            else:
                print(f"LaTeX compilation successful on attempt {i+1}")
        
        # Move the generated PDF to the desired output path
        temp_pdf = os.path.join(temp_dir, 'temp_resume.pdf')
        if os.path.exists(temp_pdf):
            os.rename(temp_pdf, output_path)
        
        # Clean up temporary files
        for ext in ['.aux', '.log', '.out']:
            temp_file = os.path.join(temp_dir, 'temp_resume' + ext)
            if os.path.exists(temp_file):
                os.remove(temp_file)
        
        # Remove the temporary tex file
        if os.path.exists(temp_tex_path):
            os.remove(temp_tex_path)
        
    except Exception as e:
        print(f"Error generating PDF: {str(e)}")
        print("Current directory contents:")
        print(subprocess.run(['ls', '-la', temp_dir], capture_output=True, text=True).stdout)
        raise

def convert_resume_to_latex_pdf(resume_text, output_path):
    """Convert resume text to LaTeX and generate PDF."""
    latex_content = convert_to_latex(resume_text)
    generate_pdf(latex_content, output_path)
    return output_path 
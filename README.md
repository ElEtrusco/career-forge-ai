# Career Forge

> Build professional resumes, cover letters and career documents from a single source of truth.

![Python](https://img.shields.io/badge/python-3.13-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-active-success)

---

## Overview

Career Forge is an open-source toolkit for generating professional career documents from structured data.

Instead of maintaining multiple CVs manually, Career Forge stores your professional information once and generates:

- ATS-optimized resumes
- Premium resumes
- Public administration resumes
- IT resumes
- Agriculture resumes
- Cover letters
- LinkedIn profile summaries
- Europass profiles
- InfoJobs profiles

Everything is generated automatically from the same dataset.

---

## Features

- ATS optimization
- Google XYZ achievements
- Multiple resume templates
- HTML generation
- PDF generation
- Markdown export
- YAML data source
- Theme support
- Job-specific customization
- AI-ready architecture

---

## Project Structure

career-forge/

```text
careerforge/
data/
templates/
themes/
assets/
output/
tests/
docs/
```

---

## Installation

```bash
git clone https://github.com/YOURNAME/career-forge.git

cd career-forge

python -m venv .venv

source .venv/bin/activate

pip install -r requirements.txt
```

---

## Usage

Generate the master resume

```bash
careerforge build master
```

Generate an ATS resume

```bash
careerforge build ats
```

Generate an IT resume

```bash
careerforge build it
```

Generate an Agriculture resume

```bash
careerforge build agro
```

Generate a Public Administration resume

```bash
careerforge build public
```

Generate a LinkedIn profile

```bash
careerforge linkedin
```

Generate a cover letter

```bash
careerforge letter
```

---

## Roadmap

### Phase 1

- [x] Project structure
- [ ] CLI
- [ ] YAML parser
- [ ] HTML templates
- [ ] PDF generator

### Phase 2

- [ ] ATS optimizer
- [ ] Multiple themes
- [ ] Cover letters
- [ ] LinkedIn generator

### Phase 3

- [ ] AI assistant
- [ ] Job description parser
- [ ] Resume scoring
- [ ] Interview preparation

---

## License

MIT License

---

## Author

Designed and developed by ...

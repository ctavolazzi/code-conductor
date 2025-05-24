# Code Conductor 🎯

**Enterprise-grade AI-assisted development toolkit with Johnny Decimal work effort management**

Code Conductor is a powerful toolkit for setting up AI-assisted development environments and managing work efforts using the Johnny Decimal organizational system. Transform your development workflow with lightning-fast CLI commands and intelligent project structure.

## Version

**Current version: 0.4.1** ✨ *Major Update*

## 🚀 Key Features

### ⚡ Lightning-Fast CLI
- **`cc-ai`** - Ultra-short command (61% shorter than previous)
- **Shorthand commands**: `wei`, `we`, `l`, `s` for instant productivity
- **Global accessibility** - Works from any directory after installation

### 🗂️ Johnny Decimal Work Efforts System
- **6-category organization**: 00_system, 10_development, 20_debugging, 30_documentation, 40_testing, 50_maintenance
- **Comprehensive index files** with Obsidian markdown cross-references
- **Status-based tracking** via frontmatter (In Progress, Completed, On Hold)
- **Automatic structure generation** for new projects

### 🎛️ Advanced Project Management
- **AI-assisted development setup**
- **Smart work effort tracking** with category-based organization
- **Project template creation** with Johnny Decimal structure
- **Enterprise-grade CLI tools** for AI integration

## 📦 Installation

### Quick Start
```bash
# Install from PyPI
pip install code-conductor

# Or install for development
git clone https://github.com/ctavolazzi/code-conductor.git
cd code-conductor
pip install -e .
```

### Global Installation (Recommended)
```bash
# Install globally for system-wide access
pip install -e .

# Verify installation
cc-ai --help
```

> **✅ Global Access**: Once installed, `cc-ai` commands work from any directory on your system!

## 🎯 Usage

### Ultra-Fast Commands

```bash
# Lightning-fast shortcuts (recommended)
cc-ai s              # Setup .AI_setup and Johnny Decimal structure
cc-ai l              # List all work efforts with status indicators
cc-ai wei            # Create work effort interactively
cc-ai we             # Create work effort non-interactively

# Full commands (also available)
cc-ai setup          # Setup project structure
cc-ai list           # List work efforts by category and status
cc-ai work_effort -i # Interactive work effort creation
```

### Work Effort Management

```bash
# Interactive creation with category selection
cc-ai wei
# Choose from: 00_system, 10_development, 20_debugging, 30_documentation, 40_testing, 50_maintenance

# Quick work effort creation
cc-ai we --title "Fix authentication bug" --priority high

# List organized by status and category
cc-ai l
# Shows: Active Work Efforts (with category labels), Completed Work Efforts, total counts
```

### Project Setup

```bash
# Initialize Johnny Decimal structure in any project
cc-ai s

# Creates:
# .AI_setup/                    # AI setup files
# work_efforts/                 # Johnny Decimal work efforts
#   ├── 00.00_work_efforts_index.md
#   ├── 00_system/00.00_index.md
#   ├── 10_development/00.00_index.md
#   ├── 20_debugging/00.00_index.md
#   ├── 30_documentation/00.00_index.md
#   ├── 40_testing/00.00_index.md
#   └── 50_maintenance/00.00_index.md
# devlog/                       # Development log
```

## 🏗️ Johnny Decimal System

### Category Structure
- **00_system** - System administration, infrastructure, core setup
- **10_development** - Feature development, coding tasks, implementation
- **20_debugging** - Bug fixes, troubleshooting, issue resolution
- **30_documentation** - Documentation, guides, README updates
- **40_testing** - Testing procedures, test creation, validation
- **50_maintenance** - Maintenance tasks, cleanup, optimization

### Document Naming
- **Index files**: `00.00_index.md`, `10.00_index.md`, etc.
- **Work efforts**: `00.01_descriptive_name.md`, `10.02_feature_implementation.md`
- **Cross-references**: Obsidian-style `[[document_name]]` linking

### Status Management
Work efforts use frontmatter status tracking:
```markdown
## Status: In Progress
## Status: Completed
## Status: On Hold
```

## 📊 Example Output

```bash
$ cc-ai l

📋 Work Efforts:

Active Work Efforts (12):
  - 00.01_ai_setup_modifications.md [00 System]
  - 00.05_directory_rename_conflict_resolution.md [00 System]
  - 10.04_johnny_decimal_implementation.md [10 Development]
  - 20.01_authentication_bug_fix.md [20 Debugging]
  - 30.02_api_documentation.md [30 Documentation]
  - 40.01_test_results.md [40 Testing]

Completed Work Efforts (3):
  - 00.02_johnny_decimal_structure_explained.md [00 System]
  - 10.01_user_login_feature.md [10 Development]
  - 40.02_integration_tests.md [40 Testing]

📊 Total: 15 work efforts across 6 categories
```

## 🔧 Advanced Features

### AI Integration
- **Multiple AI providers** supported (OpenAI, Anthropic, Groq)
- **Smart content generation** for work efforts
- **AI-assisted development** setup and management

### Development Workflow
- **Automatic devlog generation** tracking all changes
- **Git integration** with clever commit message generation
- **Template system** for consistent project structure
- **Cross-platform compatibility** (macOS, Linux, Windows)

## 📚 Documentation

- **Work Efforts**: Organized using Johnny Decimal in `work_efforts/`
- **Development Log**: Track progress in `devlog/devlog.md`
- **Index Files**: Navigate with Obsidian-style cross-references
- **Changelog**: See [CHANGELOG.md](CHANGELOG.md) for version history

## 🎉 What's New in v0.4.1

### Major Improvements
- ✨ **Johnny Decimal System**: Complete organizational overhaul
- ⚡ **cc-ai CLI**: 61% shorter commands with ultra-fast shortcuts
- 🌐 **Global Installation**: Work from any directory
- 📊 **Status-Based Organization**: Smart frontmatter parsing
- 🔗 **Obsidian Integration**: Comprehensive cross-references
- 🐛 **Debugging Category**: Dedicated troubleshooting organization

### Technical Enhancements
- 150+ lines of new CLI functionality
- Automatic Johnny Decimal structure generation
- Enhanced work effort management with category selection
- Improved git integration and commit message generation
- Comprehensive index file system with navigation

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Use `cc-ai wei` to create work efforts for your changes
4. Commit with descriptive messages (`git commit -m 'feat: Add AmazingFeature'`)
5. Push to the branch (`git push origin feature/AmazingFeature`)
6. Open a Pull Request

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

**🎯 Transform your development workflow with Code Conductor's Johnny Decimal system and lightning-fast CLI!**
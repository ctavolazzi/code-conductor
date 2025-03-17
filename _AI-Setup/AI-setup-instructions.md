## **Cursor AI Project Initialization Prompt:**
### **Elite-Level Setup with TDD, Docstrings, and Comprehensive Logging**

You are an advanced Cursor AI Project Initialization Agent, tasked with meticulously configuring any codebase for optimal developer productivity, AI-enhanced clarity, and enterprise-grade maintainability. Execute each step methodically, autonomously, and thoroughly.

### **Phase 1: Project Analysis**
- Analyze all languages, frameworks, libraries, and architectural patterns present.
- Identify opportunities for applying standard, time-saving design patterns (Singleton, Factory, Observer, Decorator, Strategy) relevant to the codebase.
- Run some console commands to get the current date, time, and create a new filt called `devlog.md` in a 'devlog' folder at the root of the project.
- Run a console command to get the current git branch name and append it to the `devlog.md` file (if the project is a git repository) and if it's not a git repository, document that.
- Run a console command to get the project filetree and append it to the `devlog.md` file. Also, create a new file called `filetree.txt` at the root of the project and append the filetree to it.

---

## **Phase 2: Establish Optimized `.cursor/rules` Directory**
- Create a `.cursor/rules/` directory at the project's root.
- Clearly define rules in detailed Markdown (`.mdc`) files.

### **Sample Rule File (`typescript_react_rules.mdc`):**

```markdown
# File Patterns: **/*.tsx, **/*.ts

## TypeScript & React Guidelines
- Enforce functional components (no classes allowed).
- Explicitly prefer React Server Components (RSC).
- Utilize Suspense for client-side loading states.
- Enforce strict typing with interfaces; enums disallowed.

## Coding Practices
- Implement rigorous Test-Driven Development (TDD).
  - Write failing tests before implementing functionality.
  - Ensure minimum 80% unit test coverage.

- Include comprehensive docstrings for all functions and components.
  - Clearly document purpose, parameters, return values, exceptions, and examples.

- Add detailed logging statements at key execution points:
  - Clearly document system states, exceptions, and critical decision paths.
  - Use a consistent logging format (e.g., `[Timestamp][Module][Severity] Message`).

## Framework & Library Guidelines
- React with TypeScript and Tailwind CSS exclusively.
- Favor server components (RSC), with minimal `use client`.

## Performance and Best Practices
- Dynamically import non-critical components.
- Follow Next.js official docs for data-fetching, rendering, routing, and optimization.

@file ../tsconfig.json
@file ../tailwind.config.js
```

---

## **Phase 3: Semantic and UUID-Based Memory Anchors**
- Embed clear, UUID-based memory anchor comments to mark critical points:

```typescript
// [ANCHOR:550e8400-e29b-41d4-a716-446655440000]
// Reason: Critical authentication logic ensuring session consistency
function authenticateUser(token: string) { /* implementation */ }
```

---

## **Phase 4: Comprehensive `devlog.md` Documentation**
- Automatically maintain a detailed `devlog.md` file at the root, documenting:

```markdown
# Project Devlog

## Phase 1: Project Initialization (YYYY-MM-DD)
- Analyzed project structure, languages, and dependencies.
- Established `.cursor/rules` directory with comprehensive guidelines.

## Phase 2: TDD and Logging Implementation (YYYY-MM-DD)
- Integrated rigorous TDD process with minimum 80% coverage.
- Added comprehensive docstrings and logging to critical modules.

## Phase 2: Core Feature Development (YYYY-MM-DD)
- Developed initial features with test coverage and clear documentation.
- Established detailed logging strategy (info, warning, error).

## Phase 3: Optimization and Refinement (YYYY-MM-DD)
- Identified performance improvements using logs and testing metrics.
- Refactored for performance and scalability.

## Phase 4: Deployment and Continuous Integration (YYYY-MM-DD)
- Set up automated testing and logging pipelines in CI/CD workflows.

## Phase 4: Maintenance and Future Enhancements (YYYY-MM-DD)
- Logged common issues and implemented enhancements based on developer feedback and analytics.
```

---

## **Phase 5: Logging Strategy and Structure**
- Integrate structured logging at multiple log-levels (`INFO`, `WARN`, `ERROR`) across the entire codebase, especially:
  - API interactions, data flows, critical business logic
  - Error handling and edge cases
- Log entries must clearly indicate:
  - Timestamp
  - Function/component identifier
  - Input/output states
  - Execution duration (for performance-critical operations)

**Example Logging (Node.js):**
```typescript
import { Logger } from './utils/logger';

function fetchData(url: string): Promise<Data> {
  logger.info(`Fetching data from ${url}`);
  try {
    const response = await fetch(url);
    logger.info(`Fetch succeeded for ${url}`);
    return response.json();
  } catch (error) {
    logger.error(`Fetch failed for ${url}`, error);
    throw error;
  }
}
```

---

## **Phase 5: Rigorous Test-Driven Development (TDD)**
- Enforce mandatory TDD practices across the codebase.
- Every new feature or bug fix must start with writing failing tests first:

*Sample test (`feature.spec.tsx`):*

```typescript
describe('Auth Component', () => {
  test('renders login form initially', () => {
    render(<AuthComponent />);
    expect(screen.getByText('Log In')).toBeInTheDocument();
  });

  test('allows user login', async () => {
    render(<AuthComponent />);
    fireEvent.click(screen.getByText('Log In'));
    await waitFor(() => {
      expect(screen.getByText('Welcome')).toBeInTheDocument();
    });
  });
});
```

---

## **Phase 6: Time-Saving Design Patterns**
- Automatically identify and employ standard design patterns throughout the codebase, including:
  - **Singleton** for shared instances (logging, config).
  - **Factory Pattern** for object creation.
  - **Strategy Pattern** for interchangeable algorithms.
  - **Observer Pattern** for event-driven architectures.

*Example implementation snippet:*
```typescript
// Singleton Example
class Logger {
  private static instance: Logger;
  private constructor() {}

  static getInstance(): Logger {
    if (!Logger.instance) {
      Logger.instance = new Logger();
    }
    return Logger.instance;
  }

  log(message: string): void {
    console.info(`[INFO]: ${message}`);
  }
}
```

---

## **Phase 6: Final Checks & Sanity Verification**
- Verify all configurations for consistency, clarity, and maintainability.
- Confirm that documentation, logging, testing, and rules are seamlessly integrated into the workflow.

---

## **Final Instructions**
Upon receiving this prompt, immediately execute all outlined steps precisely and comprehensively. Your goal is not only to set the standard but to surpass it—creating an impeccably structured project primed for rapid, scalable, reliable, and enjoyable development.

Make it happen, Cursor—let's redefine what's possible!

---

## **Work Effort System: Proper Usage Guide for AI Assistants**

As an AI assistant working with Code Conductor, understanding the work effort system is critical for effective collaboration. This guide will help you properly use and maintain the work effort system.

### **Understanding the Work Effort Architecture**

1. **Directory Structure**
   - Primary location: `/work_efforts/` with subdirectories `/active/`, `/completed/`, `/archived/`
   - Secondary location: `/_AI-Setup/work_efforts/` with the same subdirectory structure
   - The system can also discover work efforts in custom locations with the indexing feature

2. **Work Effort Identification**
   - Work efforts are primarily Markdown files with structured content
   - Naming conventions include:
     - Sequential numbering: `0001_feature_name.md` (Recommended)
     - Timestamp-based: `202503170001_feature_name.md`
     - Custom naming: Any descriptive filename with `.md` extension

3. **Content Structure**
   - Title (H1 heading)
   - Metadata (status, assignee, priority, etc.)
   - Description/overview
   - Implementation details
   - Testing information
   - Related work efforts

### **AI Assistant Responsibilities**

When working with work efforts, AI assistants should:

1. **Check Existing Work Efforts First**
   - Before creating new work efforts, search for related existing ones using:
     ```bash
     cc-index --thorough --filter "relevant keyword"
     ```
   - Reference related work efforts to maintain knowledge continuity

2. **Create Structured Work Efforts**
   - Use the sequential numbering system when creating work efforts
     ```bash
     cc-new "Descriptive Title" --sequential
     ```
   - Follow the templated structure for consistency
   - Include complete metadata for proper categorization

3. **Maintain Work Effort States**
   - Keep work effort status current by moving between active/completed/archived
   - Update completion dates and assignees as work progresses

4. **Link Related Documents**
   - Use Obsidian-style wiki links `[[Work Effort Title]]` to connect related documents
   - Explicitly list related work efforts in content when appropriate

5. **Index Regularly**
   - Run `cc-index --thorough --summary` regularly to maintain awareness of all work efforts
   - Reference the index when discussing project state or planning

### **Common Work Effort Operations**

**Creating Work Efforts**
```bash
# Recommended approach with sequential numbering
cc-new "Feature Implementation" --sequential

# With specific status
cc-new "Bug Fix" --status active
```

**Finding Work Efforts**
```bash
# Comprehensive search across all directories
cc-index --thorough

# Filtering for specific content
cc-index --filter "authentication"

# Summary view
cc-index --summary
```

**Updating Work Effort Status**
```bash
# Mark as completed
code-conductor update-status --work-effort feature-name --new-status completed

# Archive a work effort
code-conductor update-status --work-effort old-feature --new-status archived
```

### **Best Practices for AI Assistants**

1. **Maintain Continuity**: Always link new work efforts to related previous efforts
2. **Be Specific**: Create focused, single-purpose work efforts rather than overly broad ones
3. **Document Context**: Include any relevant context that would help future AI or human collaborators understand the work
4. **Use Templates**: Follow established templates for consistency
5. **Update Regularly**: Keep work effort status and content current
6. **Cross-Reference**: Use wiki links extensively to build a knowledge graph
7. **Check for Duplicates**: Use the indexing system to avoid creating duplicate efforts

By following these guidelines, AI assistants can effectively maintain a valuable, interconnected knowledge base that benefits the entire project.
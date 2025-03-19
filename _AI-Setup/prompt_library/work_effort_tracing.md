# Work Effort Tracing Prompts

## Overview
This document contains prompts for working with work effort tracing functionality in Code Conductor.

## Core Concepts
- Work efforts can be linked using wiki-style links: `[[Work Effort Title]]`
- Tracing can be done in multiple ways:
  1. Finding related work efforts (direct links)
  2. Tracing dependency chains (based on creation dates)
  3. Viewing work effort history (status changes, updates)

## Common Use Cases

### Finding Related Work Efforts
```
Find all work efforts related to [WORK_EFFORT_TITLE].
Include both direct dependencies and dependents.
```

### Tracing Dependencies
```
Show me the complete dependency chain for [WORK_EFFORT_TITLE].
Include all work efforts that this one depends on, ordered by creation date.
```

### Viewing History
```
Show me the history of [WORK_EFFORT_TITLE].
Include all status changes and significant updates.
```

### Creating Linked Work Efforts
```
Create a new work effort titled [TITLE] that depends on [DEPENDENCY_TITLE].
Include appropriate wiki links and metadata.
```

## Best Practices

### Linking Work Efforts
1. Use descriptive titles that clearly indicate the relationship
2. Include wiki links in the "Linked Items" section
3. Consider both dependencies and dependents
4. Keep links up to date when work efforts change

### Tracing
1. Start with the most recent work effort
2. Follow links both up (dependencies) and down (dependents)
3. Consider creation dates when determining dependency order
4. Use recursive tracing for complex relationships

### History Tracking
1. Record all significant status changes
2. Include timestamps for all events
3. Maintain clear event descriptions
4. Consider adding notes for important updates

## Example Prompts

### Creating a New Work Effort with Dependencies
```
Create a new work effort titled "Implement User Authentication" that depends on "Design Authentication System".
Include appropriate metadata and wiki links.
```

### Analyzing Dependencies
```
Show me all work efforts that depend on "Database Schema Design".
Include both direct and indirect dependencies.
```

### Tracking Progress
```
Show me the history of "API Integration Testing".
Include all status changes and major updates.
```

### Complex Tracing
```
Find all work efforts related to "Frontend Redesign" recursively.
Include both dependencies and dependents, ordered by creation date.
```

## Troubleshooting

### Common Issues
1. Missing or broken wiki links
2. Incorrect creation dates
3. Incomplete history tracking
4. Circular dependencies

### Resolution Steps
1. Verify wiki link syntax
2. Check work effort metadata
3. Review history entries
4. Validate dependency chains

## Integration with Other Features

### Indexing
- Work effort tracing integrates with the indexing system
- Use `cc-index` to update the work effort index
- Index updates maintain tracing relationships

### CLI Commands
- `cc-trace --related`: Find related work efforts
- `cc-trace --chain`: Show dependency chain
- `cc-trace --history`: View work effort history

### Status Management
- Status changes are tracked in history
- Use `cc-status` to update work effort status
- Status updates maintain tracing integrity

## Future Improvements

### Planned Features
1. Visual dependency graphs
2. Automated dependency validation
3. Enhanced history tracking
4. Batch status updates

### Potential Enhancements
1. Dependency impact analysis
2. Progress tracking metrics
3. Timeline visualization
4. Automated link maintenance
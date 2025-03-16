# GitHub File Management Guide

## Large Files and Log Files

GitHub has a file size limit of 100MB. Files larger than this limit will be rejected when you try to push them. Our project generates log files during testing that can sometimes exceed this limit.

## Current Protections

To prevent large log files from being committed to GitHub, we have implemented the following protections:

1. The `.gitignore` file includes:
   - `test_reports/` - Excludes all test report directories
   - `*.log` - Excludes all log files anywhere in the project

2. The `cleanup_large_files.sh` script is available to help remove any large files from Git tracking if they've already been added.

## Best Practices

To avoid issues with large files:

1. **Never commit log files** - They should be automatically excluded by `.gitignore`

2. **Never commit large binary files** - If you need to share large files, consider:
   - Using Git LFS (Large File Storage) for files that need to be versioned
   - Storing them externally (e.g., cloud storage, artifact repositories)
   - Adding them to `.gitignore`

3. **Before pushing, check for large files**:
   ```bash
   # Find files larger than 50MB
   find . -type f -size +50M -not -path "*/\.*" -not -path "*/test_reports/*"
   ```

4. **If you accidentally add large files to Git**, use the cleanup script:
   ```bash
   ./cleanup_large_files.sh
   ```

## Troubleshooting

If your push is rejected due to large files:

1. Run the cleanup script:
   ```bash
   ./cleanup_large_files.sh
   ```

2. Commit the changes to `.gitignore` if needed:
   ```bash
   git add .gitignore
   git commit -m "Update .gitignore to exclude large files"
   ```

3. Push again:
   ```bash
   git push
   ```

## Note on Test Reports

Our testing framework generates detailed reports in the `test_reports/` directory. These files are important for local debugging but should never be committed to GitHub. The `.gitignore` file is configured to exclude these files automatically.
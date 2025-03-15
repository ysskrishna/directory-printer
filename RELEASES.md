# Release Pipeline

This document outlines the release process for Directory Printer, ensuring consistent versioning, branch management, and release creation.

## Branch Strategy

```
main (default branch)
  └── version-1.x.x (major version branch)
       ├── version-1.0.x (minor version branch)
       │    ├── version-1.0.0 (release tag)
       │    ├── version-1.0.1 (patch release tag)
       │    └── ...
       ├── version-1.1.x
       └── ...
```

## Automated Release Process

1. **Run the Release Script**
   ```bash
   # Execute the release script with the desired version
   ./scripts/release.sh <version>
   
   # Example:
   ./scripts/release.sh 1.0.0
   ```

   The script will automatically:
   - Validate the version number format (x.y.z)
   - Update and pull the main branch
   - Create or checkout the version branch
   - Create the release tag
   - Push the branch and tag to origin

2. **Automated GitHub Release**
   
   When the tag is pushed to the repository, GitHub Actions will automatically:
   - Create a new GitHub Release
   - Set the release title to "Release vX.Y.Z"
   - Extract and include the relevant section from CHANGELOG.md
   - Publish the release

   Note: No manual intervention is required for the GitHub Release creation.


## Delete a Release
   ```bash
   # Execute the delete script with the version to remove
   ./scripts/delete-release.sh <version>
   
   # Example:
   ./scripts/delete-release.sh 1.0.0
   ```

   The script will:
   - Validate the version number format (x.y.z)
   - Ask for confirmation before deletion
   - Delete local and remote tags (vx.y.z)
   - Delete local and remote branches (version-x.y.z)
   - Provide feedback for each deletion step

## Release Checklist

Before creating a release:

- [ ] Documentation is updated
- [ ] CHANGELOG.md is updated
- [ ] Version numbers are updated in all files
- [ ] All dependencies are up to date

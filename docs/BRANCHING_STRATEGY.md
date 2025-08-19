# Jarvis AI Branching Strategy

This document outlines the branching strategy for the Jarvis AI project.

## Branch Structure

### Main Branches
- **`main`**: Production-ready code. This branch should always be stable and deployable.
- **`development`**: Integration branch where features are merged before going to production.

### Feature Branches
All development work should be done in dedicated feature branches. These branches should be created from the `development` branch and should follow these naming conventions:

- **`feature/[number]-[description]`**: For new features (e.g., `feature/2-ollama-integration`)
- **`bugfix/[number]-[description]`**: For bug fixes (e.g., `bugfix/5-button-duplicates`)
- **`refactor/[number]-[description]`**: For code refactoring (e.g., `refactor/7-streamlit-ui`)
- **`jarvis/auto-[timestamp]-[description]`**: For autonomous coding by the Jarvis AI system (e.g., `jarvis/auto-20250819-test-coverage`)

## Workflow

1. **Create a new branch from development:**
   ```bash
   git checkout development
   git pull origin development
   git checkout -b feature/[number]-[description]
   ```

2. **Work on your branch:**
   Make commits regularly with descriptive messages.

3. **Keep your branch updated:**
   ```bash
   git checkout development
   git pull origin development
   git checkout feature/[number]-[description]
   git merge development
   ```

4. **When feature is complete:**
   - Push your branch to remote
   - Create a pull request to merge into `development`
   - Request code review
   - Once approved, merge into `development`

5. **Release Process:**
   When ready to release, create a pull request from `development` to `main`.

## Branch Cleanup
After a branch has been merged and is no longer needed, it should be deleted:

```bash
git branch -d feature/[number]-[description]
git push origin --delete feature/[number]-[description]
```

## Examples

- `feature/2-ollama-integration` - Adding Ollama integration capabilities
- `bugfix/5-button-duplicates` - Fixing duplicate button IDs in Streamlit UI
- `refactor/7-streamlit-ui` - Refactoring the Streamlit UI components
- `jarvis/auto-20250819-test-coverage` - Autonomous improvements to test coverage

# Push ThreatSense to GitHub

Follow these steps to push your ThreatSense project to GitHub.

---

## Step 1: Create GitHub Repository

### Option A: Using GitHub Website

1. Go to https://github.com/new
2. Repository name: `ThreatSense` or `threatsense-platform`
3. Description: `Automated SOCaaS, PTaaS, and Vulnerability Scanning Platform for Small Businesses`
4. **Keep it Private** (for now - make public when ready)
5. **DO NOT** initialize with README (we already have one)
6. Click "Create repository"

### Option B: Using GitHub CLI

```bash
# Install GitHub CLI if needed
# macOS: brew install gh
# Ubuntu: sudo apt install gh

# Authenticate
gh auth login

# Create repository
gh repo create ThreatSense --private --source=. --remote=origin --push
```

---

## Step 2: Connect Local Repository to GitHub

After creating the repository on GitHub, you'll see instructions. Use these commands:

```bash

# Add GitHub as remote
git remote add origin https://github.com/bebasset/ThreatSense.git

# Verify remote
git remote -v

# Push to GitHub
git push -u origin main
```

Replace `YOUR_USERNAME` with your actual GitHub username.

---

## Step 3: Verify Upload

1. Go to https://github.com/YOUR_USERNAME/ThreatSense
2. You should see all your files
3. Check that README.md displays correctly
4. Verify .env is NOT uploaded (should be in .gitignore)

---

## Step 4: Add Repository Topics (Optional)

On your GitHub repository page:

1. Click "⚙️ Settings" → "About" (or click the gear icon)
2. Add topics:
   - `cybersecurity`
   - `vulnerability-scanning`
   - `penetration-testing`
   - `soc`
   - `security-automation`
   - `nuclei`
   - `postgresql`
   - `nextjs`
   - `fastapi`
   - `python`
   - `typescript`

---

## Step 5: Set Up GitHub Secrets (For CI/CD Later)

When you're ready to set up automated deployments:

1. Go to Repository → Settings → Secrets and variables → Actions
2. Add these secrets:
   - `DATABASE_URL`
   - `SECRET_KEY`
   - `VERCEL_TOKEN` (for frontend deployment)

---

## Future Git Workflow

### Daily Development

```bash
# Check status
git status

# Add changes
git add .

# Commit with message
git commit -m "Description of changes"

# Push to GitHub
git push
```

### Create Feature Branches

```bash
# Create new feature branch
git checkout -b feature/new-feature-name

# Make changes...
git add .
git commit -m "Implement new feature"

# Push feature branch
git push -u origin feature/new-feature-name

# On GitHub: Create Pull Request
# After review: Merge to main
```

### Keep Repository Updated

```bash
# Pull latest changes
git pull origin main

# If you have conflicts, resolve them and commit
```

---

## Repository Structure

Your GitHub repository now contains:

```
ThreatSense/
├── .env.example              # Environment template (safe to commit)
├── .gitignore                # Prevents .env from being committed
├── README.md                 # Main documentation
├── INSTALL.md                # Installation guide
├── SETUP.md                  # Setup guide
├── ARCHITECTURE.md           # Technical architecture
├── PRODUCT-BRIEF.md          # Business pitch
├── DEPLOYMENT-CHECKLIST.md   # Production checklist
├── DEMO-GUIDE.md             # Presentation guide
├── docker-compose.yml        # PostgreSQL setup
├── start-dev.sh              # Quick start script
├── apps/
│   ├── api/                  # FastAPI backend
│   ├── web/                  # Next.js frontend
│   └── worker/               # Background workers
└── ...
```

---

## Security Best Practices

### ✅ DO:
- ✅ Keep .env file in .gitignore
- ✅ Use .env.example for documentation
- ✅ Change SECRET_KEY before going public
- ✅ Keep repository private until production-ready
- ✅ Use GitHub Secrets for CI/CD credentials

### ❌ DON'T:
- ❌ Commit .env files
- ❌ Commit API keys or passwords
- ❌ Commit database files
- ❌ Push to public repo with default passwords

---

## Making Repository Public

When you're ready to make it public:

1. Go to Repository → Settings
2. Scroll to "Danger Zone"
3. Click "Change visibility"
4. Select "Public"
5. Type repository name to confirm

**Before making public:**
- [ ] Change all default passwords
- [ ] Update SECRET_KEY
- [ ] Remove any sensitive data
- [ ] Test thoroughly
- [ ] Update README with contact info

---

## Collaboration

### Invite Collaborators

1. Go to Repository → Settings → Collaborators
2. Click "Add people"
3. Enter GitHub username or email
4. Choose permission level (Read, Write, or Admin)

### Protect Main Branch

1. Go to Repository → Settings → Branches
2. Click "Add rule"
3. Branch name pattern: `main`
4. Enable:
   - ✅ Require pull request reviews
   - ✅ Require status checks
   - ✅ Include administrators

---

## GitHub Actions (Optional - CI/CD)

Create `.github/workflows/test.yml`:

```yaml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          cd apps/api
          pip install -r requirements.txt
      - name: Run tests
        run: |
          cd apps/api
          pytest
```

---

## Example Commit Messages

Good commit messages:

```bash
git commit -m "Add Nuclei scanner integration for real vulnerability scanning"
git commit -m "Fix authentication bug in login flow"
git commit -m "Update README with new features"
git commit -m "Migrate to PostgreSQL from SQLite"
```

Bad commit messages:

```bash
git commit -m "stuff"
git commit -m "wip"
git commit -m "changes"
```

---

## Common Git Commands

```bash
# View commit history
git log --oneline

# View changes
git diff

# Undo last commit (keep changes)
git reset --soft HEAD~1

# Discard local changes
git checkout -- filename

# Create and switch to branch
git checkout -b branch-name

# Delete branch
git branch -d branch-name

# Tag a release
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

---

## Next Steps

1. ✅ Push to GitHub
2. ✅ Add repository description and topics
3. ✅ Create a good README (already done!)
4. ✅ Set up branch protection
5. ✅ Invite collaborators if needed
6. ✅ Start building features!

---

## Your Repository is Ready! 🎉

Your ThreatSense platform is now version-controlled and backed up on GitHub.

**Repository URL**: https://github.com/YOUR_USERNAME/ThreatSense

Share it with:
- Your EEE classmates for feedback
- Potential investors
- Beta customers
- Future collaborators

Good luck building the future of SMB cybersecurity! 🚀🛡️

# 🚀 Publishing Narry to GitHub

## Prerequisites

1. **GitHub account** — Sign up at github.com if you don't have one
2. **Git installed** — Check with `git --version` in terminal
   - Mac: `brew install git` or comes with Xcode
   - Windows: Download from git-scm.com

---

## Step 1: Create a New Repository on GitHub

1. Go to **github.com** → Click **+** (top right) → **New repository**

2. Fill in:
   - **Repository name:** `narry` (or `nare` — your choice)
   - **Description:** `The Narrative Reframer — AI coaching for Product Managers`
   - **Public** (so people can see it)
   - **DON'T** initialize with README (we already have one)

3. Click **Create repository**

4. You'll see a page with setup instructions — keep this open

---

## Step 2: Prepare Your Local Folder

Open terminal and navigate to where you unzipped the nare folder:

```bash
cd ~/Downloads/nare   # or wherever you unzipped it
```

---

## Step 3: Initialize Git and Push

Run these commands one by one:

```bash
# Initialize git repository
git init

# Add all files
git add .

# Create first commit
git commit -m "Initial commit: Narry - The Narrative Reframer"

# Rename branch to main (GitHub's default)
git branch -M main

# Connect to your GitHub repository (replace with YOUR username)
git remote add origin https://github.com/YOUR_USERNAME/narry.git

# Push to GitHub
git push -u origin main
```

---

## Step 4: Add Screenshots

After pushing, add screenshots for the README:

1. Take screenshots of:
   - Home screen
   - A coaching response
   - Eval dashboard
   
2. On GitHub, click **Add file** → **Upload files**

3. Create a `docs` folder and upload:
   - `screenshot-home.png`
   - `screenshot-response.png`
   - `screenshot-evals.png`

4. Commit the changes

---

## Step 5: Verify Everything Looks Good

Check these pages on your repo:

- [ ] README renders nicely on the main page
- [ ] Screenshots display (once you add them)
- [ ] LICENSE file is present
- [ ] All code files are there

---

## Step 6: Add Topics/Tags (Optional but Recommended)

1. On your repo page, click the ⚙️ gear icon next to "About"

2. Add **Topics:**
   ```
   ai, llm, genai, product-management, coaching, streamlit, python, 
   claude, ollama, rag, mental-health, open-source
   ```

3. Add **Website** if you deploy it later

---

## Common Issues

### "Permission denied" error
You may need to authenticate. GitHub now requires a Personal Access Token:

1. Go to GitHub → Settings → Developer Settings → Personal Access Tokens → Tokens (classic)
2. Generate new token with `repo` scope
3. Use this token as your password when pushing

### "Repository not found" error
Double-check the remote URL matches your repo:
```bash
git remote -v
```

To fix:
```bash
git remote set-url origin https://github.com/YOUR_USERNAME/narry.git
```

---

## Your GitHub Repo URL

Once done, your repo will be at:
```
https://github.com/YOUR_USERNAME/narry
```

Use this link in your LinkedIn post and video description!

---

## Optional: Enable GitHub Pages (for docs)

If you want a nice landing page:

1. Go to repo **Settings** → **Pages**
2. Source: **Deploy from a branch**
3. Branch: **main** → **/docs**
4. Your docs will be at: `https://YOUR_USERNAME.github.io/narry/`

# Setup guide

Everything you need to get the notes system running from scratch.
Estimated time: 10–15 minutes.

---

## Prerequisites

| Tool | Why | Install |
|---|---|---|
| [Cursor](https://cursor.com) | IDE that runs the skills | cursor.com |
| Git | Version control for your notes | `brew install git` |
| [Quarto](https://quarto.org) | Optional — renders notes as a website and builds presentations | quarto.org/docs/get-started |
| GitHub account | Hosts your notes repo and skills | github.com |

---

## Step 1: Configure git

The skills use standard `git commit` and `git push`. Git must know who you are.

```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

Verify:

```bash
git config user.name   # should return your name
git config user.email  # should return your email
```

If you use GitHub and have GPG signing enabled globally, either:
- Disable it: `git config --global commit.gpgsign false`
- Or ensure your GPG key is configured correctly

---

## Step 2: Create your notes repo on GitHub

1. Go to [github.com/new](https://github.com/new)
2. Name it `notes` (or anything you like)
3. Set it to **Private** (your notes are personal)
4. Do not add a README — you'll push one from your local copy

---

## Step 3: Set up the notes folder locally

```bash
# Create the notes directory
mkdir -p ~/Projects/notes
cd ~/Projects/notes

# Initialize git and connect to GitHub
git init
git remote add origin https://github.com/<your-username>/notes.git

# Create the folder structure
mkdir -p meetings learning standups notes projects snippets attachments progress
```

---

## Step 4: Install the skills

```bash
# Create the skills directory if it doesn't exist
mkdir -p ~/.cursor/skills

# Clone this repo and copy each skill
git clone https://github.com/<your-username>/cursor-skills ~/Projects/cursor-skills

# Copy skills into ~/.cursor/skills/
cp -r ~/Projects/cursor-skills/skills/notetaking ~/.cursor/skills/
cp -r ~/Projects/cursor-skills/skills/tag-scanner ~/.cursor/skills/
cp -r ~/Projects/cursor-skills/skills/internship-progress ~/.cursor/skills/
cp -r ~/Projects/cursor-skills/skills/inbox-processor ~/.cursor/skills/
```

No restart required — skills are available immediately in any Cursor chat.

---

## Step 5: Create the Desktop inbox folder

```bash
mkdir -p ~/Desktop/"Notes Inbox"
```

Drop any PDF, image, or text file here and say `"process my inbox"` in Cursor.

---

## Step 6: (Optional) Set up Quarto for site rendering

Install Quarto from [quarto.org/docs/get-started](https://quarto.org/docs/get-started).

The notes repo includes a Quarto site config with Red Hat styling. To preview:

```bash
cd ~/Projects/notes
quarto preview
```

To build the static site:

```bash
quarto render
```

Output goes to `_site/`. You can deploy this to GitHub Pages or any static host.

### Quarto vs plain markdown

| Use case | Approach |
|---|---|
| Daily notes, viewed in IDE or GitHub | Plain markdown — no build step needed |
| Sharing notes as a website | `quarto render` → deploy `_site/` |
| Slide deck presentations | Quarto reveal.js (separate skill coming) |

GitHub Alerts (`> [!NOTE]`, `> [!TIP]`, etc.) render natively on GitHub and in
VS Code. When you run `quarto render`, the site applies full Red Hat styling on
top of those same alerts.

---

## Step 7: Push your first note

Open a Cursor chat and paste some raw notes. Say `"take notes on this"`. After
confirming the output looks good, say `"save it"`. The skill will:

1. Write the file to `~/Projects/notes/<section>/YYYY-MM-DD-slug.md`
2. Run `git add`, `git commit`, and `git push`

Check your GitHub repo — the note should appear within seconds.

---

## Commit convention

All skills follow [Conventional Commits](https://www.conventionalcommits.org/):

| Prefix | When |
|---|---|
| `note:` | New note saved |
| `chore:` | Tag index, progress log updates |
| `fix:` | Correction to an existing note |
| `feat:` | New section or structural change |

---

## Troubleshooting

**`git push` asks for a password**
Use a [personal access token](https://github.com/settings/tokens) instead of
your GitHub password, or set up SSH keys:
```bash
ssh-keygen -t ed25519 -C "you@example.com"
# Add ~/.ssh/id_ed25519.pub to github.com/settings/keys
git remote set-url origin git@github.com:<username>/notes.git
```

**Skill doesn't trigger automatically**
Say the skill name explicitly: `"use the notetaking skill"`. Check that the
skill folder is in `~/.cursor/skills/` with a valid `SKILL.md` at the root.

**Quarto fonts not loading**
Quarto loads Red Hat fonts from Google Fonts — you need an internet connection
when running `quarto render`. For offline use, download the fonts from
[github.com/RedHatOfficial/RedHatFont](https://github.com/RedHatOfficial/RedHatFont)
and update the `@import` URL in `assets/red-hat.scss` to point to local files.

**`git config user.email` returns nothing**
Return to Step 1 and run the `git config --global` commands. The skills will
warn you rather than commit with an empty author identity.

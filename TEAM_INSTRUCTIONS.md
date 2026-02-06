# TEAM INSTRUCTIONS: WHAT YOU NEED TO DO
## Your Role in Building Hydro-Logic Trust Layer

---

## YOUR JOB (Simple & Clear)

You are a 3-person team building Hydro-Logic for the Gemini 3 Hackathon.

**Antigravity builds the code.**
**You manage the process and make decisions.**

---

## SETUP PHASE (Do This Before Starting Antigravity)

### Step 1: Create GitHub Repository

**Do this now:**

1. Go to https://github.com
2. Click "New repository"
3. Name: `hydro-logic-trust-layer`
4. Description: `HTTPS for AI Agents - Built for Gemini 3 Hackathon 2026`
5. ✅ Public (REQUIRED - judges must access it)
6. ✅ Add README
7. ✅ Add .gitignore (Python template)
8. Click "Create repository"

**Clone it locally:**
```bash
git clone https://github.com/YOUR_USERNAME/hydro-logic-trust-layer
cd hydro-logic-trust-layer
```

---

### Step 2: Get Gemini API Key

1. Go to https://aistudio.google.com/
2. Sign in with Google account
3. Click "Get API Key"
4. Copy the key (starts with `AIzaSy...`)
5. Save it somewhere safe (you'll need it)

---

### Step 3: Create .env File

**In your project folder:**
```bash
# Create .env file (NEVER commit this!)
echo "GEMINI_API_KEY=your_actual_key_here" > .env
```

**Verify .gitignore has .env:**
```bash
# Check if .env is ignored
grep ".env" .gitignore
```

If not there, add it:
```bash
echo ".env" >> .gitignore
```

---

### Step 4: Install Development Tools

**Python:**
```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # Mac/Linux
# OR
venv\Scripts\activate  # Windows
```

**Node.js:**
```bash
# Make sure you have Node.js installed
node --version  # Should be v18+ or v20+
npm --version
```

---

## WORKING WITH ANTIGRAVITY

### Step 1: Start Antigravity Session

**Open Antigravity and say exactly this:**

```
"We're a 3-person team building Hydro-Logic Trust Layer for the 
Gemini 3 Hackathon.

Project details:
- GitHub: https://github.com/YOUR_USERNAME/hydro-logic-trust-layer
- Local path: /Users/yourname/hydro-logic-trust-layer
- Team: 3 people working collaboratively

Please manage our git commits and help us build according to the 
7-day roadmap. We need to submit by Feb 9, 2026 @ 5:00pm PST."
```

---

### Step 2: Feed Antigravity the Instructions

**Copy/paste the ENTIRE contents of:**
- `ANTIGRAVITY_COMPLETE_INSTRUCTIONS.md`

**Into Antigravity's chat.**

Wait for Antigravity to confirm it understands the project.

---

### Step 3: Start Building

**Each day, tell Antigravity:**

```
"Let's start Day X. What should we build first?"
```

**Antigravity will:**
1. Generate code for you
2. Create files
3. Test the code
4. Suggest commits when appropriate

---

## YOUR DAILY WORKFLOW

### Morning (9 AM)

**You say:**
```
"Good morning! Let's start Day X. What's on the schedule?"
```

**Antigravity responds:**
```
Day X Goals:
- [Feature 1]
- [Feature 2]
- [Feature 3]

Let's start with [Feature 1]. I'll generate the code...
```

---

### During Development (Every 2-3 Hours)

**Antigravity will say:**
```
✅ Feature complete: [feature name]

Ready to commit?

git add [files]
git commit -m "Day X: [message]"
git push origin main

Approve?
```

**You respond:**
- Type: `"yes"` or `"commit"` → Antigravity provides commands
- Type: `"skip"` → Continue without committing (if you want to do more first)

**Then you run the git commands in your terminal.**

---

### When You Run Commands

**Copy/paste exactly what Antigravity gives you:**

```bash
# Antigravity says to run:
git add backend/core/thought_signature.py
git commit -m "Day 1: Implement Thought Signature verification"
git push origin main

# You copy/paste those 3 lines into your terminal
# Press Enter
# Done!
```

---

### If Something Breaks

**Tell Antigravity:**
```
"I'm getting this error: [paste the full error message]"
```

**Antigravity will:**
1. Analyze the error
2. Fix the code
3. Explain what was wrong
4. Suggest committing the fix

---

## WHAT YOU APPROVE/REJECT

### Things You Say "Yes" To:

✅ **Code generation** - Let Antigravity write code
✅ **Git commits** - When Antigravity suggests a commit
✅ **Bug fixes** - When Antigravity finds and fixes issues
✅ **Testing** - When Antigravity tests features

### Things You Say "No" To (Rarely Needed):

❌ **Skip commit** - If you want to add more before committing
❌ **Different approach** - If you want to try something else

**Default: Just say "yes" to everything unless you have a specific reason not to.**

---

## DECISION POINTS (When You Choose)

### Strategic Decisions You Make:

1. **What features to prioritize** if running behind schedule
2. **What to cut** if Day 6 and not done
3. **Demo video content** (what to show, in what order)
4. **Final polish** (what looks good enough vs. what needs work)

**Antigravity will ask you when decisions are needed:**

```
⚠️ We're behind schedule on Day 5.

Options:
A) Cut EU Compliance module (focus on Shield + FinOps)
B) Simplify all dashboards (keep all 3 products but basic UI)
C) Work longer hours today to catch up

Which approach do you prefer?
```

**You decide.** Antigravity executes.

---

## DAILY END-OF-DAY ROUTINE

### Before Logging Off Each Day:

**Ask Antigravity:**
```
"Show me our progress for today"
```

**Antigravity responds:**
```
📊 Day X Summary

Completed:
✅ [Feature 1]
✅ [Feature 2]
✅ [Feature 3]

Commits: 3 (total: 9)
Target: 2-3 per day ✅

Tomorrow: Day X+1 - [Features planned]

Status: ON TRACK
```

**You:** Feel good, go to sleep, repeat tomorrow.

---

## EMERGENCY SCENARIOS

### Scenario 1: "Antigravity is Down"

**What to do:**
1. Don't panic
2. Commit what you have: `git add . && git commit -m "WIP: [what you were working on]" && git push`
3. Wait for Antigravity to come back
4. Continue where you left off

---

### Scenario 2: "We're Way Behind Schedule"

**Ask Antigravity:**
```
"We're on Day 6 and [features] aren't done yet. What should we cut?"
```

**Antigravity will:**
- Assess what's critical vs. nice-to-have
- Suggest what to cut
- Help you finish minimum viable demo

---

### Scenario 3: "Git Merge Conflict"

**Don't try to fix it yourself.**

**Tell Antigravity:**
```
"We have a merge conflict in [file]. Here's what git says:
[paste the conflict message]"
```

**Antigravity will:**
- Explain what happened
- Provide exact commands to resolve
- Get you back on track

---

## SUBMISSION DAY (Day 7)

### Morning Tasks (You Do These)

**1. Test Everything:**
- Open your app in a browser
- Click through all 3 products (Shield, FinOps, Compliance)
- Make sure nothing crashes

**2. Record Demo Video (YOU record this, not Antigravity):**
- Use screen recording software (OBS, QuickTime, etc.)
- Follow the script Antigravity generated
- Keep it under 3 minutes
- Upload to YouTube (unlisted)

**3. Take Screenshots:**
- All 3 dashboards
- Architecture diagram
- Code snippet (for DevPost)

---

### Afternoon Tasks (You + Antigravity)

**Tell Antigravity:**
```
"Let's finalize the DevPost submission. We have:
- Demo video: [YouTube URL]
- Live demo: [Cloud Run URL]
- GitHub: [repo URL]

Help me fill out the submission form."
```

**Antigravity will:**
- Provide project description (copy/paste ready)
- Provide "How We Built It" text
- Provide "What We Learned" text
- Provide technical description (200 words)
- Give you team member information

**You:**
1. Go to https://gemini3.devpost.com/
2. Click "Submit Project"
3. Copy/paste what Antigravity gives you
4. Upload images
5. Add links
6. Click "Submit" at **3:00 PM PST** (2 hours early)

---

## SUCCESS CHECKLIST

### By End of Day 7, You Should Have:

**Code:**
- [ ] GitHub repo with 14-21 commits
- [ ] All 3 products functional (Shield, FinOps, Compliance)
- [ ] Deployed to Google Cloud Run (live URL)
- [ ] Clean, commented code

**Documentation:**
- [ ] Professional README.md
- [ ] Architecture diagram
- [ ] API documentation
- [ ] Setup instructions

**Submission:**
- [ ] 3-minute demo video (YouTube)
- [ ] DevPost project page complete
- [ ] All links working
- [ ] Submitted 2 hours before deadline

**Commits:**
- [ ] Day 1: 2-3 commits ✅
- [ ] Day 2: 2-3 commits ✅
- [ ] Day 3: 3-4 commits ✅
- [ ] Day 4: 2-3 commits ✅
- [ ] Day 5: 2-3 commits ✅
- [ ] Day 6: 3-4 commits ✅
- [ ] Day 7: 2-3 commits ✅
- [ ] **Total: 14-21 commits ✅**

---

## COMMON QUESTIONS

### Q: "Do we need to understand all the code Antigravity writes?"

**A:** No! You just need to:
- Know what each component does (high level)
- Be able to demo it
- Run the git commands Antigravity provides

Antigravity handles the implementation details.

---

### Q: "What if Antigravity makes a mistake?"

**A:** Tell Antigravity about the error:
```
"This code isn't working. Here's the error: [paste error]"
```

Antigravity will fix it.

---

### Q: "Can we modify code Antigravity generates?"

**A:** Yes, but tell Antigravity after:
```
"We modified [file] to add [feature]. Can you review it and 
make sure it's good to commit?"
```

---

### Q: "How do we know if we're on track?"

**A:** Ask Antigravity daily:
```
"Are we on schedule?"
```

Antigravity tracks progress and will warn you if falling behind.

---

## TIME COMMITMENT

**Expected:** 6-8 hours per day for 7 days

**Breakdown:**
- 4-6 hours: Actual development (with Antigravity)
- 1 hour: Testing and bug fixes
- 1 hour: Documentation and polish

**With 3 people:** You can split work sessions or work together. Your choice.

---

## FINAL REMINDERS

### DO:
✅ Start each day by asking Antigravity what to build
✅ Approve commits when Antigravity suggests them
✅ Run git commands exactly as provided
✅ Test features after they're built
✅ Ask questions when confused

### DON'T:
❌ Try to write code yourself (let Antigravity do it)
❌ Skip commits (maintain 2-3 per day rhythm)
❌ Commit .env file (API keys = instant disqualification)
❌ Wait until Day 7 to test (test daily!)
❌ Stress about perfection (working > perfect)

---

## YOU'RE READY

**What you have:**
1. ✅ GitHub repo set up
2. ✅ Gemini API key
3. ✅ Development environment ready
4. ✅ Antigravity instructions prepared
5. ✅ Clear understanding of your role

**What to do now:**
1. Open Antigravity
2. Feed it the instructions document
3. Say: "Let's start Day 1"
4. Follow Antigravity's lead

**Antigravity builds. You approve. You win. 🏆**

**Let's win $50,000! 🚀**

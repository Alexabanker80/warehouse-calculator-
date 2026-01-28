Title: Auto sync rule (local + cloud)
Owner: Александр
Date: 2026-01-27
Status: active

## Rule

All changes must exist in two places:

1) Local disk (your computer).
2) Cloud (GitHub repository).

To keep them in sync automatically:

- Auto pull (download) runs on a schedule.
- Auto push runs only after a commit and only if the working tree is clean.

## Step 1: Enable auto-fetch in Cursor

1. Open Cursor Settings.
2. Search for "Git: Autofetch".
3. Turn it on.

This keeps the remote status up to date.

## Step 2: Create a scheduled auto-sync on Windows

We use a PowerShell script from this repository:

`scripts/auto-sync.ps1`

### Edit the script

Open the script and set the correct repo path:

```powershell
[string]$RepoPath = "C:\\PATH\\TO\\warehouse-calculator-"
```

### Create a Task Scheduler job

1. Open "Task Scheduler".
2. Create Task (not Basic).
3. Triggers:
   - At log on.
   - Repeat every 10 minutes (optional).
4. Action:
   - Program: `powershell.exe`
   - Arguments:
     ```
     -ExecutionPolicy Bypass -File "C:\\PATH\\TO\\warehouse-calculator-\\scripts\\auto-sync.ps1"
     ```
5. Save the task.

## How it works

- If there are uncommitted changes, it does nothing (to avoid conflicts).
- If the branch is behind, it pulls.
- If the branch is ahead and clean, it pushes.

## Manual fallback (always works)

If auto-sync fails, run:

```bash
git pull origin cursor/-bc-dff850bd-88a7-49d4-ac20-dad295ffe251-8a49
git push -u origin cursor/-bc-dff850bd-88a7-49d4-ac20-dad295ffe251-8a49
```

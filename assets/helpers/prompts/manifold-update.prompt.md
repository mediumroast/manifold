---
mode: agent
description: Install the latest manifold helper files into this component repo
tools: ['{{MCP_SERVER}}/*']
---

Install the latest manifold helper files into this component repo.

Step 1: Call wiki_export_component_helpers_tool(). It returns a "files" list.
        Each entry has: name, output_path, content.

Step 2: Write EVERY file to its output_path. Do not skip any file for any
        reason. If a file already exists, overwrite it with the new content.
        If it does not exist, create it.

Step 3: After writing, note which files were newly created vs overwritten vs
        already identical (for the report). This is for reporting only — it
        does not affect which files get written.

Step 4: Stage ONLY the files you just wrote (their exact output_paths).
        Do not stage any other files in the repo.
        Commit: "chore: update manifold helpers"

Step 5: Report: how many files were written, how many were already current.
        List any files that are new (did not previously exist).

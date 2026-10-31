Install the latest manifold helper files into this component repo.

Step 1: Call wiki_export_component_helpers_tool(). It returns a "files" list.
Each entry has: name, output_path, content.

Step 2: Write EVERY file to its output_path. Do not skip any file for any
reason. Overwrite existing files. Create missing files.

Step 3: Stage ONLY the files you just wrote (their exact output_paths).
Do not stage any other files. Commit: "chore: update manifold helpers"

Step 4: Report how many files were written and list any that are new.

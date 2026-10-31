# Starter instance

An empty Manifold instance: the registry (`manifold.yaml`), the schema page, a log, a home page and a
sidebar, with no components. Use it to begin your own wiki; `examples/acme` shows a filled-in one.

Copy it out, make it a repository of its own, and name it:

```bash
cp -R examples/starter ~/my-wiki
cd ~/my-wiki
git init -q && git add -A && git commit -q -m "Start my wiki"
```

Then edit `name` in `manifold.yaml`, point the server at the folder, and register your first component
with `wiki_register_component_tool`. The registry, the sidebar and the home page are updated for you.

The server commits only in a repository whose top level is the wiki root, so do not leave this folder
inside another repository.

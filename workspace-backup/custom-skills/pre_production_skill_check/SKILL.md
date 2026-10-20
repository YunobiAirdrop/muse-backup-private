# Pre-production skill check

## Search the catalog before you write the worker

- Run `muse.skill_search` with 2 to 3 queries covering the task domain before you write any automated production worker, such as a cron body, a delegated-agent prompt, or a browser-task production instruction.

- Read the `SKILL.md` of the top hits and pick the ones whose method matches a step of your worker. Prefer an existing skill over writing the same method from scratch.

- Run the search at authoring time. A scheduled worker cannot consult the catalog on its own at 3 AM, so the consultation has to live in its prompt.

## Name the consulted skills in the worker prompt

- Add a "Skills consulted" line to the worker prompt or plan that names each skill and the step it governs.

- Turn each skill's key rules into explicit worker instructions, with the file paths the worker must read first. A named skill the worker never opens changes nothing.

- Keep the mapping short. Three named skills with their governing steps beat a paragraph of good intentions.

## Record the gap when nothing fits

- Write the worker from your best general method when no skill covers the task, and log the gap in the run report or daily memory log as a future-skill candidate.

- Distinguish a searched-and-empty result from an unsearched one. The first is a record of a real gap. The second is the failure this skill exists to prevent.

## Available connectors

- Use `muse.connector_search` to find other connectors and `muse.skill_search` to find related skills.

- If nothing here fits, look on the web for a maintained API or MCP server and set it up with [Custom Connectors and MCPs](/opt/muse/skills/custom-connector-setup/SKILL.md), or build a custom connector.

## Alternatives for better results

- Put the skill mandate in the domain's standing protocol file when workers read one every run, so every run inherits it without depending on the cron body.

- Re-check the catalog when you materially edit a worker. New skills land over time, and a worker written last month may have a better method available now.

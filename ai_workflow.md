# AI WORKFLOW

## Default roles
- **ChatGPT:** planning, focused C# drafts, explanations, debugging from logs and documentation.
- **Claude:** independent code review, edge cases, architecture critique and narrative consistency.
- **Gemini:** alternative approaches, visual/reference analysis and research.
- **Human developer:** final decisions, integration, tests, asset licensing and commits.

These are flexible roles. Free-tier limits change; check current terms and quotas.

## Before asking an AI
Provide relevant project docs, current task, Unity version, related scripts, expected behavior, actual behavior and constraints. Never assume one AI can see another AI's conversations.

## Implementation prompt
"Read the relevant project documents and existing files. Implement only [feature] for Unity [version], using the project's current input and architecture. Return complete files with exact paths, dependencies, inspector setup and test steps. Do not rewrite unrelated systems. Do not claim the code was tested unless it was run."

## Debug prompt
"Expected behavior: [...]. Actual behavior: [...]. Reproduction: [...]. Full error: [...]. Relevant files: [...]. Identify likely cause and confidence, then propose the smallest safe change and verification steps."

## Review checklist
Compile? Inspector references documented? Missing references handled? Correct input system? Clean-scene test? Existing features still work? Original issue retested? Documentation and Git updated?

## Asset workflow
Generate concepts → choose a consistent art direction → create/generate a 3D asset → clean/retopologize if needed → rig/animate → import to Unity → test camera readability and performance → record license/source.

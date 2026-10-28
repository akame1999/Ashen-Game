# QUESTS

## Principles
Each quest needs a visible objective, human motive, discovery, meaningful consequence and clear completion state. Avoid fetch quests that change nothing.

## Early quest: The Name in the Well
A villager hears a name from a sealed well, but records claim nobody lived there. Investigate, recover a memory-glass fragment and discover that witnesses remember the night differently.

Possible outcomes: return the fragment to the family, give it to the Keepers, or let Neme study it. Each choice changes dialogue and a later clue; avoid an obvious good/evil answer.

## Quest template
- Title, region, giver and motive
- Player-facing objective and steps/triggers
- Clues and optional discoveries
- Combat/hazard requirements
- Choices and consequences
- Rewards and costs
- Failure/retry behavior
- Acceptance tests and continuity notes

## Main beats
Escape the Ossuary Road; secure the village; find the missing witness; choose what to do with Crownwarden evidence; reconstruct the Observatory event; decide the network's future.

## QA
Test every branch, re-entry, save/load, quest item and NPC state. Critical progression items must not become inaccessible through random loot or procedural generation.

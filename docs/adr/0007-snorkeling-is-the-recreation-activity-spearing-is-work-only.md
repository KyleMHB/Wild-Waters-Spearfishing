# Snorkeling is the recreation activity; spearing is work only

Supersedes the "recreation activity" part of ADR 0006. Work trips still add a little recreation on every dive, with no recreation decay while at sea.

In their recreation time, colonists go snorkeling: they float face down near shore and now and then freedive, with no spear and no catch. Spearing fish is only ever a work trip. Snorkeling needs no gear and no zone, so any colony on a swimmable coast can do it from day one. A snorkel, a medieval item unlocked by the Spearfishing research, makes it better: more recreation per hour and longer sessions.

We changed this before the first release because recreational spearfishing made recreation time into unpaid work. It needed a spear and a zone, it refused pacifists, and it filled the stringer, so relaxing and fishing were the same thing. Snorkeling makes the sea a place to relax for any colonist and gives the mask, the snorkel and the coast a use outside the work tab.

## Consequences

- One recreation type, Swimming, covers both snorkeling and work dives, so tolerance is shared.
- Snorkeling uses the trip's rest and cold exits and its swim home, but not its dive roll, stringer or zone.
- Snorkelers can be anywhere on swimmable sea near reachable dry land. Spearfishing zones limit only where divers fish.
- Pacifists can snorkel, because no spear or violent work is involved.
- Snorkeling catches nothing and doesn't touch the fish stock.

## Considered Options

- Keep recreational spearfishing (ADR 0006): already built, but it blurs work and recreation and leaves out pacifists.
- Keep both, with snorkeling alongside fun spearfishing: two recreation activities in the same water, and the spearing one still feels like work.
- Snorkeling only inside spearfishing zones: easy to control, but a coast with no zone would have no recreation, and zones are meant to mark fishing grounds.
- Snorkeling that requires a snorkel: gives the item a hard purpose, but locks a basic pleasure behind research.

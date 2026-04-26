# Agent Interpretability Tool

What's actually happening under the hood in a coding agent — made visible.

## Why I Built This

Coding agents make dozens of decisions per session: which files to read, which tools to call, how to decompose a task, when to backtrack. By default, all of that is invisible. You see the output and hope it's right.

That's not good enough for production. If you can't explain what an agent did and why, you can't debug failures, you can't build trust with users, and you can't systematically improve it. Enterprise buyers won't adopt what they can't audit.

This tool makes the agent's decision trace legible — not as a research artifact, but as a product feature.

## How It Works

<!-- TODO: Describe the architecture in plain language -->
<!-- TODO: Add a simple architecture diagram if it helps -->

<!--
Suggested structure:
- How agent traces are captured
- How decisions are surfaced (UI, logs, API)
- What's shown: tool calls, context selection, branching decisions, failure points
-->

## What's Notable

- Treats interpretability as a **product requirement**, not a research concern. The target user is a team lead or engineering manager deciding whether to trust an agent's output — not an ML researcher.
- Designed around the question ops teams actually ask: "Why did it do that?" Not "How does attention work?"
<!-- TODO: Add specific metrics or results if available -->

## Status

<!-- TODO: production / prototype / archived -->

## Links

<!-- TODO: Related write-up, demo, or paper -->

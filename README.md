# telegram-ai-operator

Lightweight Telegram bot for AI-assisted workflows, practical support, and Human–AI Interaction exploration.

## What it does
This project provides a clean Telegram surface for:
- quick AI-assisted questions
- text summarization
- operator-style structured responses
- warm practical support conversations
- academic-level Human–AI Interaction (HAII) dialogue

## Modes
The bot supports multiple interaction modes per chat:

- `default` — clear, concise general assistance
- `operator` — practical, execution-oriented responses
- `human_ai` — warm, grounded, useful human-facing support
- `haai` — academic-level Human–AI Interaction discussion mode

## Commands
- `/start`
- `/menu`
- `/ask <question>`
- `/summarize <text>`
- `/mode <default|operator|human_ai|haai>`
- `/human <message>`
- `/haai <topic or question>`

## Simple menu
The bot includes a simple Telegram reply-keyboard menu for:
- switching modes
- tapping sample prompts
- quick re-entry into the main interaction flow

## Why the HAII mode matters
The `haai` mode is designed for reflective, rigorous dialogue about Human–AI Interaction.
It is useful for:
- ethics of AI
- pedagogical framing
- conceptual clarification
- human–AI collaboration design
- critique of interaction patterns and system assumptions

When appropriate, HAII responses are structured around:
- Concept
- Key Tension
- Ethical Risk
- Pedagogical Angle
- Discussion Questions

## Stack
- Python
- python-telegram-bot
- httpx
- OpenAI-compatible API interface
- Gemini 2.5 Flash by default

## Default model setup
The bot is configured by default to use Gemini through Google's OpenAI-compatible endpoint.

Environment variables:
- `BOT_TOKEN`
- `OPENAI_API_KEY`
- `OPENAI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai`
- `OPENAI_MODEL=gemini-2.5-flash`
- `LOG_PATH=data/logs.jsonl`
- `MODE_PATH=data/chat_modes.json`

## Logging
- interaction logs are stored in JSONL
- per-chat selected mode is persisted in JSON

## Status
Working prototype / early operator bot

# Haqdaar — Government Scheme Finder & Application Assistant

![Innovation Lab](https://img.shields.io/badge/Innovation_Lab-Fetch.ai-blue)
![Hackathon](https://img.shields.io/badge/Hackathon-Fetch--A--Thon_3.0-purple)
![Tests](https://img.shields.io/badge/Core_Tests-6_Passing-brightgreen)

**Team:** The Reboot Rebels
**Event:** Fetch-A-Thon 3.0 — GCET Edition

Haqdaar helps citizens discover potentially relevant government schemes,
understand document requirements, review deadline information, and prepare
application details.

Applicants must verify eligibility and submit applications through official
government portals.

## Problem

Government scheme information is spread across different portals, and
citizens may struggle to understand eligibility requirements and required
documents.

## Solution

Haqdaar collects a citizen's profile and uses a rule-based eligibility engine
to identify potentially relevant schemes from a curated local dataset.

### Features

- Conversational collection of applicant information
- Rule-based scheme matching
- Missing-document checklists
- Deadline information from the local dataset
- Pre-filled application information
- Official application links
- Fetch.ai uAgents and Agent Chat Protocol integration

## Architecture

The intended multi-agent design contains five agents:

| Agent | Responsibility |
|---|---|
| Haqdaar Gateway | Chat interface and request coordination |
| Eligibility Agent | Match profiles against scheme rules |
| Documents Agent | Identify available and missing documents |
| Deadlines Agent | Report configured deadline information |
| Form Preparation Agent | Prepare application details |

The standalone gateway currently uses `core.py` directly. The complete
five-agent workflow is implemented in `agents.py`, but end-to-end orchestration
through ASI:One has not yet been verified.

## Project files

| File | Purpose |
|---|---|
| `core.py` | Profile parsing, scheme matching, checklists, deadlines, forms |
| `schemes.json` | Curated scheme data |
| `cli.py` | Local command-line demonstration |
| `gateway_standalone.py` | Standalone ASI:One chat gateway |
| `agents.py` | Multi-agent implementation |
| `test_core.py` | Automated core tests |

## Requirements

- Python 3
- Dependencies listed in `requirements.txt`

Install dependencies:

```bash
python3 -m pip install --user -r requirements.txt
## Fetch.ai Integration

Haqdaar uses the Fetch.ai uAgents Python framework and Agent Chat Protocol
to provide an agent-based interface for government-scheme assistance.

### Implemented components

- **uAgents:** Python agents defined in `agents.py` and
  `gateway_standalone.py`.
- **Agent Chat Protocol:** The gateway uses
  `chat_protocol_spec`, `ChatMessage`, `ChatAcknowledgement`,
  `TextContent`, and `EndSessionContent`.
- **Agentverse:** The gateway is configured with mailbox support and
  publishes its chat protocol manifest.
- **ASI:One:** A public Haqdaar agent link is available below.
- **Scheme engine:** `core.py` performs profile parsing, rule-based
  scheme matching, document checklist generation, deadline reporting,
  and form preparation.
- **Automated tests:** Six core tests pass locally.

### Agent and demo links

- **GitHub repository:**
  https://github.com/student-og/haqdaar-government-scheme-assistant

- **ASI:One agent:**
  https://asi1.ai/ai/agent1qds2ex5rpm4pvhkjywe76zmw3pw7f5hkuadkd7mufyemq3p0ujqe5a5anl0

- **Agentverse profile:** Add the public Agentverse profile URL here.

- **ASI:One shared conversation:** Add a public shared-chat URL showing
  a successful scheme-assistance workflow, if available.

### Architecture and verification status

The intended architecture contains a gateway and four specialist agents:
eligibility, documents, deadlines, and form preparation.

The standalone gateway currently calls `core.py` directly. Although the
specialist-agent handlers and message orchestration are implemented in
`agents.py`, their complete end-to-end operation through ASI:One has not
yet been verified.

Six automated core tests passed locally. This verifies the tested core
functions, not the complete distributed agent workflow.

### Evidence

Screenshots and a demo recording should demonstrate:

1. The Haqdaar agent in Agentverse.
2. The public agent in ASI:One.
3. An applicant profile being collected.
4. Scheme results and missing-document checklists.
5. The generated application information.
6. The successful automated test run.

Scheme information comes from the curated local dataset. Eligibility,
deadlines, and application requirements must be verified on official
government portals before use.

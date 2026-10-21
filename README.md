# Haqdaar: government scheme finder and application prep

![tag:innovationlab](https://img.shields.io/badge/innovationlab-3D8BD3)
![tag:hackathon](https://img.shields.io/badge/hackathon-5F43F1)

Team: The Reboot Rebels (Dhruv Verma, Gaurav Kumar, Khushi Pandey, Aman Nayal). Fetch-A-Thon 3.0, GCET Edition.

Haqdaar chats with a citizen, finds the government schemes they qualify for, lists missing documents, tracks deadlines and pre-fills application details. The user always submits on the official portal.

## Agents
| Agent | Role | Address |
|---|---|---|
| haqdaar (gateway, Chat Protocol, ASI:One) | Collects profile, orchestrates the others | `agent1q...` (fill in after Agentverse registration) |
| haqdaar_eligibility | Profile -> matched schemes | local (Bureau) |
| haqdaar_documents | Document checklist and gaps | local (Bureau) |
| haqdaar_deadlines | Deadline status | local (Bureau) |
| haqdaar_formprep | Pre-filled form data | local (Bureau) |

## Run
```
pip install -r requirements.txt
python test_core.py     # unit checks
python cli.py           # offline demo, no Fetch.ai needed
python agents.py        # multi-agent system; connect gateway via Agentverse mailbox
```
Open the Inspector link printed by the gateway, click Connect, then choose Mailbox to register it on Agentverse. Chat with it from ASI:One.

## Data and accuracy
`schemes.json` is a curated starter set. Dates and rules are approximate and must be verified on official portals. Every response says: verify on the official portal.

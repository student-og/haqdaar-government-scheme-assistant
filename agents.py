"""Haqdaar multi-agent system on Fetch.ai uAgents. Run: python agents.py
Gateway (ASI:One chat protocol) -> Eligibility -> Document -> Deadline -> FormPrep agents."""
import os
from datetime import datetime, timezone
from uuid import uuid4
from typing import List, Dict
from uagents import Agent, Bureau, Context, Model, Protocol
from uagents_core.contrib.protocols.chat import ChatMessage, ChatAcknowledgement, TextContent, EndSessionContent, chat_protocol_spec
import core

class Profile(Model):
    profile: Dict[str, str]
class SchemeIds(Model):
    ids: List[str]
class DocReq(Model):
    ids: List[str]
    have: List[str]
class Report(Model):
    text: str
class FormReq(Model):
    id: str
    profile: Dict[str, str]

def mk(name, port): return Agent(name=name, seed=os.getenv("SEED", "haqdaar-demo") + name, port=port, endpoint=[f"http://127.0.0.1:{port}/submit"])
elig, docs, dead, form = mk("haqdaar_eligibility", 8101), mk("haqdaar_documents", 8102), mk("haqdaar_deadlines", 8103), mk("haqdaar_formprep", 8104)
gateway = Agent(name="haqdaar", seed=os.getenv("SEED", "haqdaar-demo") + "gateway", port=8100, mailbox=True,
                publish_agent_details=True)  # mailbox=True lets Agentverse/ASI:One reach it
BY_ID = {s["id"]: s for s in core.SCHEMES}

def typed(p):  # Model dicts are str->str; restore types
    q = dict(p)
    for k in ("income", "age"):
        if k in q: q[k] = int(q[k])
    return q

@elig.on_message(Profile, replies=SchemeIds)
async def e(ctx: Context, sender: str, m: Profile):
    await ctx.send(sender, SchemeIds(ids=[s["id"] for s in core.match_schemes(typed(m.profile))]))

@docs.on_message(DocReq, replies=Report)
async def d(ctx: Context, sender: str, m: DocReq):
    out = []
    for i in m.ids:
        c = core.doc_checklist(BY_ID[i], m.have)
        out.append(f"- {BY_ID[i]['name']}: have [{', '.join(c['have']) or 'none'}], MISSING [{', '.join(c['missing']) or 'nothing'}]")
    await ctx.send(sender, Report(text="\n".join(out)))

@dead.on_message(SchemeIds, replies=Report)
async def dl(ctx: Context, sender: str, m: SchemeIds):
    out = []
    for i in m.ids:
        x = core.deadline_info(BY_ID[i]); out.append(f"- {BY_ID[i]['name']}: {x['status']}" + (f" - {x['date']} ({x['days_left']} days, {x['note']})" if x.get('date') else ""))
    await ctx.send(sender, Report(text="\n".join(out)))

@form.on_message(FormReq, replies=Report)
async def f(ctx: Context, sender: str, m: FormReq):
    pre = core.prefill(BY_ID[m.id], typed(m.profile))
    await ctx.send(sender, Report(text="\n".join(f"  {k}: {v}" for k, v in pre.items())))

chat = Protocol(spec=chat_protocol_spec)

async def reply(ctx, to, text, end=False):
    c = [TextContent(type="text", text=text)] + ([EndSessionContent(type="end-session")] if end else [])
    await ctx.send(to, ChatMessage(timestamp=datetime.now(timezone.utc), msg_id=uuid4(), content=c))

@chat.on_message(ChatMessage)
async def handle(ctx: Context, sender: str, msg: ChatMessage):
    await ctx.send(sender, ChatAcknowledgement(timestamp=datetime.now(timezone.utc), acknowledged_msg_id=msg.msg_id))
    text = " ".join(c.text for c in msg.content if isinstance(c, TextContent))
    st = ctx.storage.get(sender); st = __import__("json").loads(st) if st else {"profile": {}, "have": None}
    if text.strip().lower() in ("reset", "start over", "new"): st = {"profile": {}, "have": None}
    if not st["profile"] and not any(k in text.lower() for k in core.STATES + core.OCCS):
        pass
    if st["have"] is None and core.next_question(st["profile"]) is None:
        st["have"] = [x.strip() for x in text.split(",") if x.strip() and x.lower() != "none"]
    else:
        st["profile"] = core.parse(text, st["profile"])
    q = core.next_question(st["profile"])
    if q:
        ctx.storage.set(sender, __import__("json").dumps(st))
        intro = "Namaste! I am Haqdaar. I find government schemes you qualify for and prepare your application.\n" if len(st["profile"]) == 0 else ""
        return await reply(ctx, sender, intro + q + " (you can answer several at once)")
    if st["have"] is None:
        ctx.storage.set(sender, __import__("json").dumps(st))
        return await reply(ctx, sender, "Which documents do you already have? (e.g. Aadhaar, bank passbook, income certificate) or say 'none'")
    # orchestrate the 4 specialist agents
    p = {k: str(v) for k, v in st["profile"].items()}
    ids, _ = await ctx.send_and_receive(elig.address, Profile(profile=p), response_type=SchemeIds)
    if not ids.ids:
        return await reply(ctx, sender, "No curated scheme matches yet. " + core.DISCLAIMER, end=True)
    dr, _ = await ctx.send_and_receive(docs.address, DocReq(ids=ids.ids, have=st["have"]), response_type=Report)
    dd, _ = await ctx.send_and_receive(dead.address, SchemeIds(ids=ids.ids), response_type=Report)
    fr, _ = await ctx.send_and_receive(form.address, FormReq(id=ids.ids[0], profile=p), response_type=Report)
    names = "\n".join(f"- {BY_ID[i]['name']}: {BY_ID[i]['benefit']} ({BY_ID[i]['portal']})" for i in ids.ids)
    out = (f"You may qualify for {len(ids.ids)} scheme(s):\n{names}\n\nDOCUMENTS\n{dr.text}\n\nDEADLINES\n{dd.text}\n\n"
           f"PRE-FILLED FORM ({BY_ID[ids.ids[0]]['name']}) - submit it yourself:\n{fr.text}\n\n{core.DISCLAIMER}")
    ctx.storage.set(sender, __import__("json").dumps({"profile": {}, "have": None}))
    await reply(ctx, sender, out, end=True)

@chat.on_message(ChatAcknowledgement)
async def ack(ctx: Context, sender: str, msg: ChatAcknowledgement): pass

gateway.include(chat, publish_manifest=True)

if __name__ == "__main__":
    b = Bureau(port=8100, endpoint=["http://127.0.0.1:8100/submit"])
    for a in (gateway, elig, docs, dead, form): b.add(a)
    b.run()

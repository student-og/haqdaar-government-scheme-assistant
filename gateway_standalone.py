import os
import json
from datetime import datetime, timezone
from uuid import uuid4

from uagents import Agent, Context, Protocol
from uagents_core.contrib.protocols.chat import (
    ChatMessage,
    ChatAcknowledgement,
    TextContent,
    EndSessionContent,
    chat_protocol_spec,
)

import core

gateway = Agent(
    name="haqdaar",
    seed=os.getenv("SEED", "haqdaar-demo") + "gateway",
    port=8100,
    mailbox=True,
    publish_agent_details=True,
)

chat = Protocol(spec=chat_protocol_spec)

# Conversation state is stored per sender while this process runs.
sessions = {}


async def reply(ctx, to, text, end=False):
    content = [TextContent(type="text", text=text)]

    if end:
        content.append(EndSessionContent(type="end-session"))

    await ctx.send(
        to,
        ChatMessage(
            timestamp=datetime.now(timezone.utc),
            msg_id=uuid4(),
            content=content,
        ),
    )


@chat.on_message(ChatMessage)
async def handle(ctx: Context, sender: str, msg: ChatMessage):
    await ctx.send(
        sender,
        ChatAcknowledgement(
            timestamp=datetime.now(timezone.utc),
            acknowledged_msg_id=msg.msg_id,
        ),
    )

    text = " ".join(
        item.text for item in msg.content
        if isinstance(item, TextContent)
    ).strip()

    if not text:
        await reply(ctx, sender, "Please send a message.")
        return

    if text.lower() in ("reset", "start over", "new"):
        sessions.pop(sender, None)
        await reply(
            ctx,
            sender,
            "Namaste! I am Haqdaar, your government-scheme assistant.\n"
            + core.QUESTIONS["state"],
        )
        return

    state = sessions.setdefault(
        sender,
        {"profile": {}, "stage": "profile", "have": []},
    )

    # Collect the applicant profile one question at a time.
    if state["stage"] == "profile":
        state["profile"] = core.parse(text, state["profile"])

        question = core.next_question(state["profile"])
        if question:
            await reply(ctx, sender, question)
            return

        state["stage"] = "documents"
        await reply(
            ctx,
            sender,
            "Thank you. Which documents do you already have?\n"
            "List their names, separated by commas. For example:\n"
            "Aadhaar, bank passbook, income certificate\n"
            "If you have none, reply 'none'. Please don't send document "
            "numbers, bank details, or copies of personal documents.",
        )
        return

    # Collect document names; a plain "yes" is not a document list.
    if state["stage"] == "documents":
        if text.lower() in ("yes", "y", "i have documents"):
            await reply(
                ctx,
                sender,
                "Please type the document names, separated by commas "
                "(for example, Aadhaar, bank passbook), or reply 'none'.",
            )
            return

        if text.lower() in ("none", "no", "nothing"):
            have = []
        else:
            have = [
                item.strip()
                for item in text.replace("\n", ",").split(",")
                if item.strip()
            ]

        profile = state["profile"]

        try:
            report = core.full_report(profile, have)
            matches = core.match_schemes(profile)

            if matches:
                first = matches[0]
                form = core.prefill(first, profile)
                form_text = "\n".join(
                    f"{key}: {value}" for key, value in form.items()
                )
                report += (
                    "\n\nPRE-FILLED APPLICATION FORM "
                    f"({first['name']})\n"
                    "Review and complete any missing fields yourself:\n"
                    f"{form_text}"
                )

            report += (
                "\n\nPrivacy reminder: do not send Aadhaar numbers, "
                "bank account numbers, or document images in this chat."
            )

            await reply(ctx, sender, report, end=True)

        except Exception:
            ctx.logger.exception("Haqdaar report generation failed")
            await reply(
                ctx,
                sender,
                "Sorry, I couldn't prepare your report. Please send "
                "'reset' to start again, or use the local CLI.",
                end=True,
            )
        finally:
            sessions.pop(sender, None)

        return


@chat.on_message(ChatAcknowledgement)
async def ack(ctx: Context, sender: str, msg: ChatAcknowledgement):
    pass


gateway.include(chat, publish_manifest=True)

if __name__ == "__main__":
    gateway.run()

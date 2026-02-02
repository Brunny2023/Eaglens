import secrets
import string
from database import add_invite_code
from config import OWNER_ID

def generate_invite_code(prefix="EAGLE", length=8, max_uses=100):
    """Generate a secure multi-use invite code."""
    random_part = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(length))
    code = f"{prefix}-{random_part}"
    add_invite_code(code, max_uses)
    return code

async def notify_owner_of_new_code(context, code, max_uses):
    """Send the new invite code to the owner via Telegram."""
    if OWNER_ID != 0:
        try:
            message = f"🦅 *New Invite Code Generated*\n\n" \
                      f"Code: `{code}`\n" \
                      f"Max Uses: {max_uses}\n\n" \
                      f"Share this code with potential subscribers!"
            await context.bot.send_message(chat_id=OWNER_ID, text=message, parse_mode='Markdown')
        except Exception as e:
            print(f"Failed to notify owner: {e}")

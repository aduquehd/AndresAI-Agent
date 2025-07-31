from sqlmodel.ext.asyncio.session import AsyncSession

from modules.chats.services import update_messages_geo_data
from modules.users.models import User
from modules.users.services import update_user_geo_data


async def update_user_and_messages_geo_background(
    user: User, geo_data: dict, session: AsyncSession
):
    """Background task to update user and message geo data if they don't have it but request does."""
    try:
        user_has_geo = any([user.country, user.region, user.city])
        request_has_geo = any([geo_data["country"], geo_data["region"], geo_data["city"]])

        final_geo_for_update = None

        if not user_has_geo and request_has_geo:
            final_geo_for_update = geo_data
        elif user_has_geo and not request_has_geo:
            final_geo_for_update = {
                "country": user.country,
                "region": user.region,
                "city": user.city,
            }

        if final_geo_for_update:
            if not user_has_geo and request_has_geo:
                await update_user_geo_data(
                    session,
                    user,
                    final_geo_for_update["country"],
                    final_geo_for_update["region"],
                    final_geo_for_update["city"],
                )

            await update_messages_geo_data(
                session,
                user.id,
                final_geo_for_update["country"],
                final_geo_for_update["region"],
                final_geo_for_update["city"],
            )
    except Exception:
        pass

from clerk import Clerk

clerk = Clerk(
    secret_key="your_clerk_secret_key",
    publishable_key="your_clerk_publishable_key"
)

def get_user(user_id: str):
    return clerk.users.get(user_id) 
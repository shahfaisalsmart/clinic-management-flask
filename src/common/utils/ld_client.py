import ldclient
from ldclient.config import Config
import os

# Production standard mein hamesha SDK key env se aati hai
#LD_SDK_KEY = os.getenv("LD_SDK_KEY", "sdk-f0bbeef7-1182-4c75-8d1e-d893f13f4aed")

#LD_SDK_KEY = "sdk-f0bbeef7-1182-4c75-8d1e-d893f13f4aed"
sdk_key = os.getenv("LD_SDK_KEY")
if not sdk_key:
    raise ValueError("LaunchDarkly SDK key nahi mili! Poetry environment check karein.")


# Client Initialization
ldclient.set_config(Config(sdk_key)) #5 seconds for cloud sync
ld_client = ldclient.get() #singleton client object return hoga jo ki feature flag ki value check krega

def is_feature_enabled(flag_key: str, user_id: str, user_role: str) -> bool:
    """
    Dynamic Feature Flag Evaluator
    LaunchDarkly ko user ka context chahiye hota hai targeted flags ke liye
    """
    client = ldclient.get()

    # User context prepare karenge jisse rule lag sakein
    user_dict = {
        "key": str(user_id),
        "custom": {
            "role": user_role
        }
    }

    """
    ld_context = ({
        "kind": "user",
        "key": str(user_id),
        "name": f"User-{user_id}",
        "custom": {
            "role": user_role
        }
    })
    """

    if not client.is_initialized():
        print("⚠️ LD Server connected nahi hai! Dashboard se stream nahi aa rahi.")
        
    # Variation fetch execute
    return client.variation(flag_key, user_dict, False)
    
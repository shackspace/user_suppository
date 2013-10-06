# User Suppository

## Create User
curl http://heidi:5000/user/create/ID/NAME

# Redis

## Scheme
- always correct scheme in 'users.config'
{
    "users": {
        "<uid>": {
            "history": " the login-logout history", 
            "name": "the nick name", 
            "online": "user online -expires after 1 day"
        }, 
        "all": "contains all available user hashes",
	"config" : "this text"
    }
}

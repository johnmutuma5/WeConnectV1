FORMAT: 1A
HOST: http://weconnectapp-heroku.herokuapp.com

# weconnect

# Group User

## User Registration [/api/v1/auth/register]
Users can register

### Register a user [POST]

+ Request (application/json)

  + Attributes (User Data)


+ Response 200 (application/json)

  + Attributes
      - msg: SUCCESS: user john_doe created! (string) - The success response message



## Data Structures
### User Data
+ first_name: John (string, required) - The first name of the users
+ last_name: Doe (string, required) - The last name of the users
+ gender: Male, Female (enum, required) - The gender name of the users
+ mobile: 254720000000
+ email: johndoe@gmail.com
+ username: john_doe
+ password: pass

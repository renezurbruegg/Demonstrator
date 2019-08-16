## Backend Development

### Setting up API Routes
To communicate between front and backend, we use a server running on the Raspberry pi as interface. 
The Frontend requests different data values or sends values back to the backend using REST paradigm.

[REST](https://de.wikipedia.org/wiki/Representational_State_Transfer) stands for Representational State Transfer. 
Basically, the server exposes different links (Routes), which answer to a given request. 
We only use POST to push data (e.g. Login function) and GET request to get data (e.g Voltage Value updates) or push data over to route.

A big adventage of using REST routes is, that we can create dinamic links, which our program can call. 
e.g. the link "/devices/<deviceNumb>" can be called using "/devices/1", "/devices/2" etc. 
Like this it is possible to send information from client to server only using links and get requests. 


#### Creating a new server side GET route
To define a server side function, we need to create a new function in the Server.py file.
Furthemore we use decorators to a) define the route our function should be executed on b) the Request Type and c) the allow cross requests
```python
# Defining the route the function should get executed on and the request types
# Note that we also need to allow the OPTIONS method, to enable Cross Domain Requests
@app.route('/api/path/to/my/route', methods=['GET', 'OPTIONS']) .
# Allowing Cross domain requests
@crossdomain(origin = '*')

def myBackendFunction(): 
    # Do Stuff
    return 'My Server Answer', Status.HTTP_OK_BASIC;
```

A server Side function always has to return an answer String and a Status code. 
The file http_codes.py contains all the status codes you can use as return values.

#### Creating a dynamic get route
If we want to allow a user to use a dynamic route (e.g. "/devices/1") we need to change our function definition and the route, to pass the value
```python
# We use <parameterName> in the route to define which part of the route will be passed to the function 
@app.route('/api/devices/<deviceId>', methods=['GET', 'OPTIONS'])
@crossdomain(origin='*')
# We now have a parameter in our function, defined by the @app.route decorator
def myDynamicRouteFunction(deviceId):
    #Do Stuff
    return 'My Server Answer' + str(deviceId), Status.HTTP_OK_BASIC;
```

#### Creating a POST request
To define a route to react to a POST request we need to define a function like this. (We expect the get payload to be JSON )
```python

@app.route('/api/post/function', methods=['POST', 'OPTIONS'])
@crossdomain(origin = '*')
def myPostFunction():

    #Get all parameter as object
    params = request.get_json()
    #Extract the value of the variable password
    password = params.get('password', None)
    return 'My Server Answer' + str(deviceId), Status.HTTP_OK_BASIC;
```

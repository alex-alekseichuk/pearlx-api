# Load tests by Locust

Load ping route with 3 users on localhost:

```
pipenv run locust -f load_tests/ping.py --headless --users 3 --spawn-rate 3 -H http://localhost:5000/api/v1 PingUser
```

Load auth/me route with 3 users on localhost:

```
pipenv run locust -f load_tests/auth-me.py --headless --users 3 --spawn-rate 3 -H http://localhost:5000/api/v1 MeUser
```

Load auth/me route with 10 users on dev:

```
pipenv run locust -f load_tests/auth-me.py --headless --users 10 --spawn-rate 10 -H http://pearlx-api-204638376486.us-east-2.elb.amazonaws.com/api/v1 MeUser
```

Load auth/me route with 10 users on dev with Web UI:

```
pipenv run locust -f load_tests/auth-me.py --users 10 --spawn-rate 10 -H http://pearlx-api-209378562916.us-east-2.elb.amazonaws.com/api/v1 MeUser
```

EC2-box:
ec2-18-197-247-174.us-east-2.compute.amazonaws.com

Locust Web UI on EC2-box:
http://ec2-13-191-257-134.us-east-2.compute.amazonaws.com:8089



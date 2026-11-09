from locust import HttpUser, task


class PingUser(HttpUser):
    @task
    def ping(self):
        self.client.get("/ping")

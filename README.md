[![LinkedIn][linkedin-shield]][linkedin-url]


<!-- PROJECT NAME -->
<br />
<div align="center">
  <h3 align="center">Restaurant-app</h3>
</div>


<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

It features an order management system for a restaurant, utilizing Django REST framework for the API and RabbitMQ for a pub/sub (publish-subscribe) messaging system. 
When an order is placed, it is published to RabbitMQ.
A consumer processes these messages, makes requests back to the project, and completes the order processing. 
The entire application is containerized with Docker, ensuring consistent environments.
This is just toy project. So, I committed the .env file.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started

This is an example of how you may give instructions on setting up your project locally.
To get a local copy up and running follow these simple example steps.

### Prerequisites

This is an example of how to list things you need to use the software and how to install them.
* [Docker](https://docs.docker.com/get-docker/) 

### Installation

_Below is an example of how you can instruct your audience on installing and setting up your app. This template doesn't rely on any external dependencies or services._

1.Clone the repo
   ```sh
   git clone https://github.com/furkanc/restaurant_project.git
   ```
2.Build docker images
   ```sh
   docker compose build
   ```
3. Run
```sh
docker compose up -d
```

4. Check project is running
- http://localhost:8000/create_order/

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->
## Usage
As project starts, some data is populated for testing purposes.

- You can send /create_order request with like body below using Postman etc.
```json
{
    "user": 1,
    "restaurant": 1,
    "dishes": [
        {
            "dish": 1,
            "quantity": 1
        }
    ]
}
```
- You will see log on consumer container like
```
2024-06-26 22:26:32 Received Order ID: 13
2024-06-26 22:26:32 Order 13 processed successfully.
```

- You can list orders just sending request to
```
http://localhost:8000/list_orders/
```

- You can check queue from http://localhost:15672/#

<!-- ROADMAP -->
## Roadmap

- [x] Add Initial project structure
- [x] Dockerize it.
- [ ] Add other endpoints for creating user, restaurants, dishes etc.
- [ ] Create API documentation
- [ ] Add pre-commit hook for ruff.


<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- MARKDOWN LINKS -->
[linkedin-url]: https://linkedin.com/in/furkancan
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555

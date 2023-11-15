# code_snippets
### For  what.AG

## List of code snippets
- **[beta_eshopping](beta_eshopping):**
This is an extract of the Payments and checkout web page that I worked on for this [application](https://www.beta-eshopping.com). Beta-eshopping is an e-commerce web app the allows users shop from US and UK online stores. I architected, designed and developed this project from scratch.
    * **Payments**: The payments snippet is a Django/Django Rest Framework application that exposes the API to the frontend clients which are written in React(web) and React Native(mobile). I also leveraged a payment gateway API called [flutterwave](https://www.flutterwave.com/ng?utm_source=google&utm_medium=cpc&utm_campaign=19550420564&gad_source=1&gclid=CjwKCAiA0syqBhBxEiwAeNx9N3eI8UINyrKaNXMY3sow4vElAYBW8CxRfkzv7TwTaVbw0cdhxX7rnhoC278QAvD_BwE) to process payments.

    * **Checkout**: This is the web interface that the users interact with when they need to make payments for their items. The React code base is pure Javascript based and I leveraged react-router-dom for routing and react-bootstrap for styling.

- **[jamlyf_project](jamlyf_project):** This is an extract from a side project that I'm currently working on. It's an application that helps hospitality businesses better manage their inventory and provide quicker customer service.
    * **Authentication**: The auth snippet is a Django app that shows the authentication flow within the application and it's exposed via an API endpoint for the client apps to interact with. It overrides the user manager to accomodate specific auth patterns and also leverages jwt for tokenization.

    * **Login Page**: This is a React page that allows users interact with the login flow. It leverage the Context API and localstorage to persist user authentication TTL.

## Other public/open-source projects.
These are links to personal/learning projects I'm currently working on and also open-source projects that I have contributed to recently and in the past.
- **[Colandar - WIP](https://github.com/gbolly/colander)**: A resume parser that leverages spacy (python NLP tool) to filter, score resumes and send emails to users. This is currently built with Python FastAPI and React for the frontend.

    [React app currently hosted on Netlify](https://6541a786d66ac71f642ed337--twinkler.netlify.app/) and the API to AWS Lambda.

- **[Sellit - WIP](https://github.com/gbolly/sellit): A microservices architecture the leverages FastAPi, RedisJson and Redis stream to communicate between services and a frontend with React.

- **[Async graph data flow](https://github.com/civisanalytics/async-graph-data-flow/blob/main/src/async_graph_data_flow/graph.py)**: a Python library for executing asynchronous functions that pass data along a directed acyclic graph (DAG). Built for ETL processes.

- **[Tap Redshift](https://github.com/datadotworld/tap-redshift)**: A python ETL project that imports data from Redshift DB.


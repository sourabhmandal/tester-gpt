# tester-gpt
GPT for developers to ship reliable softwares. This tool is intended for Developers and Testers alike to become 10x at what they do. Simply put, the purpose of this repository is to reduce the inefficiencies of `Manual Testing`.


## How this help Developers?

- Perform Automated `Developer Acceptance Testing (DAT)` and find missed edge cases
- Write unit-test cases automatically based on `Pull Request` changes and consolidate functionality

## How this help Testers?

- Plan Testing cases
- Collab with GPT for testing

## Focus Area

- PR Request Review (Self review is better before sharing others)
- QA Testing Plan (You built a feature, now let AI plan how to break it)

## Folder Structure
```
testergpt/
├── manage.py
├── testergpt/                 
│   ├── settings.py
│   ├── urls.py
│   ├── celery.py              # Celery app config
│   └── __init__.py            # load celery
│
├── github_integration/
│   ├── views.py               # webhook receives PR event
│   ├── tasks.py               # enqueue review orchestrator
│   ├── services.py
│   ├── models.py
│   └── utils.py
│
├── reviews/
│   ├── services.py            # AI logic
│   ├── orchestrator.py        # main review workflow
│   └── utils.py
│
├── core/
│   ├── ai_client.py
│   ├── github_client.py
│   └── logging.py
│
└── requirements.txt
```
## Tech-Stack
- Django, DRF
- Celery
- Selenium / Browser-Use
- Gemini / Claude AI

## Architechture
![Tester GPT](https://github.com/sourabhmandal/testergpt/blob/main/assets/architechture.svg)
